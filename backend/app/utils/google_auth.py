import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


def get_credentials_path(credentials_path: str | None = None, token_path: str | None = None) -> tuple[Path | None, Path | None]:
    from app.core.config import get_settings
    settings = get_settings()
    creds_file = credentials_path or settings.google_credentials_path or "credentials.json"
    token_file = token_path or settings.google_token_path or "token.json"
    base = Path(__file__).resolve().parent.parent.parent
    creds_path = base / creds_file if not os.path.isabs(creds_file) else Path(creds_file)
    token_path_resolved = base / token_file if not os.path.isabs(token_file) else Path(token_file)
    return creds_path if creds_path.exists() else None, token_path_resolved


def load_credentials(credentials_path: str | None = None, token_path: str | None = None) -> Credentials | None:
    creds_path, token_path_resolved = get_credentials_path(credentials_path, token_path)
    if not creds_path or not creds_path.exists():
        return None
    creds = None
    if token_path_resolved.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path_resolved), SCOPES)
        except Exception:
            pass
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        if token_path_resolved:
            with open(token_path_resolved, "w") as f:
                f.write(creds.to_json())
    return creds
