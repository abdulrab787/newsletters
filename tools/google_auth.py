"""Shared Google OAuth (Desktop app flow). First run opens a browser; token cached in token.json."""
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
CREDS = ROOT / "credentials.json"
TOKEN = ROOT / "token.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",      # only files this app creates
    "https://www.googleapis.com/auth/gmail.compose",   # create drafts (cannot read mail)
]


def get_credentials() -> Credentials:
    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = InstalledAppFlow.from_client_secrets_file(str(CREDS), SCOPES).run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


def gmail_service():
    return build("gmail", "v1", credentials=get_credentials())
