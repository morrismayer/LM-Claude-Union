"""
Google OAuth2 helper.

Two credential modes are supported:

1. **Service account** (server-side / headless)
   Set ``GOOGLE_APPLICATION_CREDENTIALS`` to the path of a service-account
   JSON key file, or pass ``credentials_file`` pointing at one.

2. **OAuth 2.0 user credentials** (interactive / local)
   Run ``get_user_credentials(scopes)`` once in a browser-capable
   environment.  A ``token.json`` file is saved so subsequent runs are
   silent.
"""
from __future__ import annotations

import os
from pathlib import Path

SCOPES_READONLY = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/documents.readonly",
]


def get_credentials(
    credentials_file: str | Path | None = None,
    token_file: str | Path = "token.json",
    scopes: list[str] | None = None,
):
    """
    Return a valid Google ``Credentials`` object.

    Tries, in order:
    1. Service-account key at ``credentials_file`` or
       ``GOOGLE_APPLICATION_CREDENTIALS`` env var.
    2. Saved OAuth user token at ``token_file``.
    3. Interactive OAuth flow (opens browser).

    Parameters
    ----------
    credentials_file:
        Path to a service-account JSON key **or** an OAuth 2.0 client-secrets
        JSON (the file Google Cloud downloads as ``client_secret_*.json``).
    token_file:
        Where to cache the OAuth user token between runs.
    scopes:
        List of OAuth scopes.  Defaults to read-only Drive + Docs.
    """
    try:
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError as exc:
        raise ImportError(
            "Google auth packages are required.\n"
            "Install with: pip install google-api-python-client "
            "google-auth-httplib2 google-auth-oauthlib"
        ) from exc

    scopes = scopes or SCOPES_READONLY
    creds_path = credentials_file or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    # --- Service account ---
    if creds_path and Path(creds_path).exists():
        import json
        with open(creds_path) as f:
            info = json.load(f)
        if info.get("type") == "service_account":
            return service_account.Credentials.from_service_account_file(
                str(creds_path), scopes=scopes
            )

    # --- OAuth user credentials ---
    token_path = Path(token_file)
    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path:
                raise RuntimeError(
                    "No credentials found.  Either:\n"
                    "  • Set GOOGLE_APPLICATION_CREDENTIALS to a service-account key, or\n"
                    "  • Pass credentials_file= pointing to an OAuth client-secrets JSON."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), scopes)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds
