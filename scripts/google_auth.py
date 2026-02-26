#!/usr/bin/env python3
"""
Run once to obtain OAuth tokens for Google Calendar API.
Saves credentials to backend/token.json. Verifies token with a test calendar API call.
"""
import os
import sys

BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)

creds_path = os.path.join(os.path.dirname(__file__), "..", "backend", "credentials.json")
token_path = os.path.join(os.path.dirname(__file__), "..", "backend", "token.json")


def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError:
        print("Install: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        sys.exit(1)

    print("MeetEdge — Google Calendar + Gmail OAuth")
    print("Ensure credentials.json is in the backend folder.")
    print("Get OAuth client credentials from: https://console.cloud.google.com/apis/credentials")
    print()

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    if not os.path.exists(creds_path):
        print(f"Place your Google OAuth client credentials at: {creds_path}")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_path, "w") as f:
        f.write(creds.to_json())

    print(f"Tokens saved to {token_path}")
    print("Verifying with a test calendar API call...")

    try:
        service = build("calendar", "v3", credentials=creds)
        events = service.events().list(calendarId="primary", maxResults=1).execute()
        print("Success: Calendar API is accessible.")
    except Exception as e:
        print(f"Warning: Test call failed: {e}")

    print()
    print("Next steps:")
    print("  1. Add GOOGLE_TOKEN_PATH=token.json to backend/.env (optional; default is token.json).")
    print("  2. For Gmail: set GMAIL_PUBSUB_TOPIC and GMAIL_WEBHOOK_SECRET in backend/.env, then POST /api/v1/gmail/setup-watch")


if __name__ == "__main__":
    main()
