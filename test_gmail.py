import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

async def test_gmail():
    from app.utils.google_auth import load_credentials
    from googleapiclient.discovery import build
    
    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds)
    
    results = service.users().messages().list(userId='me', maxResults=5).execute()
    messages = results.get('messages', [])
    
    print("Recent emails:")
    for msg in messages:
        m = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = m.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        print(f"- {subject} (From: {sender})")

if __name__ == "__main__":
    asyncio.run(test_gmail())
