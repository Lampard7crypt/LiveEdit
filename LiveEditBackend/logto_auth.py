import os
from functools import lru_cache

import jwt
from jwt import PyJWKClient


def _required_setting(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be configured to use Logto authentication")
    return value.rstrip("/")


@lru_cache(maxsize=1)
def _jwks_client(endpoint: str) -> PyJWKClient:
    return PyJWKClient(f"{endpoint}/oidc/jwks")


def verify_logto_token(token: str) -> dict:
    endpoint = _required_setting("LOGTO_ENDPOINT")
    app_id = _required_setting("LOGTO_APP_ID")
    signing_key = _jwks_client(endpoint).get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES384"],
        issuer=f"{endpoint}/oidc",
        audience=app_id,
        options={"require": ["exp", "iss", "sub", "aud"]},
    )
    if not isinstance(claims["sub"], str) or not claims["sub"]:
        raise jwt.InvalidTokenError("Token subject is missing")
    return claims
