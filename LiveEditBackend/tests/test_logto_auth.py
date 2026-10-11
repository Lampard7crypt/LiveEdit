from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

import logto_auth


@pytest.fixture
def logto_key(monkeypatch):
    endpoint = "https://logto.example.test"
    issuer = f"{endpoint}/oidc"
    app_id = "logto-app-id"
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key = private_key.public_key()
    monkeypatch.setenv("LOGTO_ENDPOINT", endpoint)
    monkeypatch.setenv("LOGTO_APP_ID", app_id)
    monkeypatch.setattr(
        logto_auth,
        "_jwks_client",
        lambda _endpoint: SimpleNamespace(
            get_signing_key_from_jwt=lambda _token: SimpleNamespace(key=public_key)
        ),
    )
    return endpoint, issuer, app_id, private_key


def make_token(issuer, app_id, private_key, **claims):
    payload = {
        "iss": issuer,
        "sub": "logto-user-123",
        "aud": app_id,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        **claims,
    }
    return jwt.encode(payload, private_key, algorithm="ES384")


def test_verify_logto_token_accepts_valid_id_token(logto_key):
    _endpoint, issuer, app_id, private_key = logto_key

    claims = logto_auth.verify_logto_token(make_token(issuer, app_id, private_key))

    assert claims["sub"] == "logto-user-123"


def test_verify_logto_token_rejects_wrong_issuer(logto_key):
    _endpoint, _issuer, app_id, private_key = logto_key
    token = make_token("https://attacker.example.test/oidc", app_id, private_key)

    with pytest.raises(jwt.InvalidIssuerError):
        logto_auth.verify_logto_token(token)


def test_verify_logto_token_rejects_wrong_audience(logto_key):
    _endpoint, issuer, _app_id, private_key = logto_key
    token = make_token(issuer, "another-app", private_key)

    with pytest.raises(jwt.InvalidAudienceError):
        logto_auth.verify_logto_token(token)
