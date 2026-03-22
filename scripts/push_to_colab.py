"""Push notebook to Google Colab via Drive API."""

import os
import json
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_PATH = Path.home() / ".uma_analyzer" / "token.json"


def get_credentials():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(TOKEN_PATH.read_text()), SCOPES
        )
    
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        TOKEN_PATH.write_text(creds.to_json())
    
    return creds


def push_notebook(notebook_path: str = "uma_analyzer.ipynb"):
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    
    creds = get_credentials()
    service = build("drive", "v3", credentials=creds)
    
    file_metadata = {
        "name": Path(notebook_path).name,
        "parents": ["appDataFolder"],
        "mimeType": "application/vnd.google.colab",
    }
    
    media = MediaFileUpload(notebook_path, mimetype="application/json")
    
    # Check if already exists
    results = (
        service.files()
        .list(
            q="name='uma_analyzer.ipynb' and parents in 'appDataFolder'",
            spaces="drive",
            fields="files(id, name)",
        )
        .execute()
    )
    
    existing = results.get("files", [])
    
    if existing:
        file_id = existing[0]["id"]
        service.files().update(
            fileId=file_id, body=file_metadata, media_body=media
        ).execute()
        print(f"Updated: {notebook_path}")
    else:
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"Created: {notebook_path} (ID: {file.get('id')})")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "uma_analyzer.ipynb"
    push_notebook(path)
