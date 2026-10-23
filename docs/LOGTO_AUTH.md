# Logto authentication

LiveEdit uses Logto for authentication. The React app stores the Logto session and
sends its ID token to Flask.
Flask validates the token signature with the tenant's JWKS, checks its issuer and
application audience, then creates or resolves the local LiveEdit account. The
development tenant currently signs ID tokens with ES384, which the backend
explicitly allows.

## Configure Logto

1. In the Logto Console, enable the Google social connector and configure its
   Google OAuth credentials.
2. Configure the React application with these redirect URIs:
   `http://localhost:3000/callback` and your deployed frontend origin followed by
   `/callback`.
3. Configure post-sign-out redirect URIs:
   `http://localhost:3000/` and your deployed frontend origin.
4. Set the frontend environment variables `VITE_LOGTO_ENDPOINT` and
   `VITE_LOGTO_APP_ID`. The example values use the provided development tenant.
5. Set `LOGTO_ENDPOINT` and `LOGTO_APP_ID` in the backend environment to the same
   tenant endpoint and application ID. Configure production values in the
   deployment environment rather than committing production configuration.
6. Set `VITE_BACKEND_URL` (or `VITE_API_URL`) in the frontend deployment and
   set backend CORS origins with `FRONTEND_URL` (single origin) or
   `FRONTEND_URLS` (comma-separated list) to the deployed app origins
   (for example: `https://livedit.space,https://www.livedit.space`).

The Google sign-in button requests the `social:google` connector directly. The
Logto application must have that connector enabled. The email sign-in button
opens Logto's hosted sign-in screen. The **Forgot your password?** action opens
Logto's hosted reset-password screen directly. Logto sends the recovery
verification code to the user's email and lets them set a new password; LiveEdit
does not handle or store password-reset tokens. Enable the required identifier,
password, and email connector settings in Logto for these options to work.
Email scope is requested, and the backend requires a verified email claim before
creating or linking a LiveEdit account.

Restart the local API and Vite server after setting environment variables.
`GET /health` remains public; all other `/api/*` endpoints require a valid
Logto ID token except the public subscription-plan catalog.

## Existing LiveEdit accounts

On the first Logto sign-in, a verified email matching an existing LiveEdit
account links that identity to the existing row, preserving subscription and
transaction records. Otherwise, a new account is created. If the email is
already linked to a different Logto identity, sign-in is rejected rather than
merging accounts.

The schema adds a `logto_user_id` column and keeps legacy identity columns
untouched, so existing data is not discarded during the provider change.
Existing password hashes are retained but unused. After confirming the
migration, they can be cleared with `UPDATE users SET password_hash = NULL`.
