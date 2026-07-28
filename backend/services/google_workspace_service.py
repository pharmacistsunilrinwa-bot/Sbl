import os
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class GoogleWorkspaceService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        self.client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def get_auth_url(self):
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        return auth_url

    def get_credentials(self, auth_code):
        flow = Flow.from_client_config(
            self.client_config,
            scopes=self.scopes,
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        flow.fetch_token(code=auth_code)
        return flow.credentials

    async def list_gmail_messages(self, creds_json):
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        return results.get('messages', [])

    async def list_drive_files(self, creds_json):
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        return results.get('files', [])

google_workspace_service = GoogleWorkspaceService()
