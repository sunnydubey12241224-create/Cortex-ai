import os
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarAgent:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.credentials_path = os.path.join(BASE_DIR, "credentials.json")
        self.token_path = os.path.join(BASE_DIR, "calendar_token.json")

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
        return build('calendar', 'v3', credentials=creds)

    def get_events_today(self):
        creds = self.authenticate()
        service = self.build_service(creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'

        events = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        if not events:
            return "📅 No meetings today."

        result = "📅 Today's meetings:\n\n"
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date'))
            result += f"- {e['summary']} at {start}\n"

        return result

    def create_event(self, summary="Meeting", hour=15, minute=0):
        creds = self.authenticate()
        service = self.build_service(creds)

        start = datetime.datetime.now().replace(hour=hour, minute=minute, second=0)
        end = start + datetime.timedelta(hours=1)

        event = {
            'summary': summary,
            'start': {'dateTime': start.isoformat()},
            'end': {'dateTime': end.isoformat()},
        }

        service.events().insert(calendarId='primary', body=event).execute()

        return f"✅ Meeting '{summary}' scheduled at {hour}:{minute}"

    def smart_schedule(self, summary="Smart Meeting"):
        creds = self.authenticate()
        service = self.build_service(creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'

        events = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        busy_hours = []

        for e in events:
            start = e['start'].get('dateTime', '')
            if "T" in start:
                busy_hours.append(int(start.split("T")[1].split(":")[0]))

        hour = 10
        while hour in busy_hours:
            hour += 1

        return self.create_event(summary, hour, 0)