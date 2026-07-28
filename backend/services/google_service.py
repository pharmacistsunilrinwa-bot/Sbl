import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class GoogleService:
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/photoslibrary.readonly'
        ]

    def get_auth_url(self):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.scopes,
            redirect_uri=os.getenv("REDIRECT_URI")
        )
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url

    async def get_gmail_threads(self, credentials_dict):
        creds = Credentials.from_authorized_user_info(credentials_dict)
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().threads().list(userId='me', maxResults=5).execute()
        return results.get('threads', [])

google_service = GoogleService()
