import os
import base64
from email import message_from_bytes

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from llm_engine import generate

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailAgent:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.credentials_path = os.path.join(BASE_DIR, "credentials.json")
        self.token_path = os.path.join(BASE_DIR, "token.json")

    def authenticate(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    def build_service(self, creds):
        return build('gmail', 'v1', credentials=creds)

    def _extract_text(self, email_msg):
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return email_msg.get_payload(decode=True).decode(errors="ignore")
        return ""

    def fetch_latest_email(self):
        try:
            creds = self.authenticate()
            service = self.build_service(creds)

            results = service.users().messages().list(
                userId='me', maxResults=1
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                return None

            msg = service.users().messages().get(
                userId='me',
                id=messages[0]['id'],
                format='raw'
            ).execute()

            raw_data = base64.urlsafe_b64decode(msg['raw'])
            email_msg = message_from_bytes(raw_data)

            return self._extract_text(email_msg)

        except Exception as e:
            return f"ERROR: {str(e)}"

    def summarize_multiple(self, count=3):
        try:
            creds = self.authenticate()
            service = self.build_service(creds)

            results = service.users().messages().list(
                userId='me', maxResults=count
            ).execute()

            messages = results.get('messages', [])
            summaries = []

            for m in messages:
                msg = service.users().messages().get(
                    userId='me', id=m['id'], format='raw'
                ).execute()

                raw_data = base64.urlsafe_b64decode(msg['raw'])
                email_msg = message_from_bytes(raw_data)

                text = self._extract_text(email_msg)[:1000]
                summary = generate(f"Summarize this email:\n{text}")
                summaries.append(summary)

            return "\n\n---\n\n".join(summaries)

        except Exception as e:
            return f"⚠ ERROR: {str(e)}"

    def generate_reply(self):
        email_text = self.fetch_latest_email()

        if not email_text or email_text.startswith("ERROR"):
            return "⚠ Cannot read email."

        email_text = email_text[:1500]

        return generate(f"""
Write a professional reply to this email:

{email_text}
""")

    def execute(self):
        email_text = self.fetch_latest_email()

        if not email_text:
            return "⚠ No email found."

        if email_text.startswith("ERROR"):
            return email_text

        return generate(f"Summarize this email:\n{email_text[:1500]}")