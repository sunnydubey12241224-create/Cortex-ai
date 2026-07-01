import os
import json
import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ==========================================================
# Google Calendar Scope
# ==========================================================
SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


class CalendarAgent:

    def __init__(self):

        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        self.credentials_path = os.path.join(
            base_dir,
            "credentials.json"
        )

        self.token_path = os.path.join(
            base_dir,
            "calendar_token.json"
        )

    # ======================================================
    # Authenticate
    # ======================================================
    def authenticate(self):

        creds = None

        # ------------------------------------------
        # Railway Token
        # ------------------------------------------
        calendar_token = os.getenv(
            "GOOGLE_CALENDAR_TOKEN"
        )

        if calendar_token:

            try:

                creds = Credentials.from_authorized_user_info(
                    json.loads(calendar_token),
                    SCOPES
                )

            except Exception:

                creds = None

        # ------------------------------------------
        # Local Token
        # ------------------------------------------
        elif os.path.exists(self.token_path):

            try:

                creds = Credentials.from_authorized_user_file(
                    self.token_path,
                    SCOPES
                )

            except Exception:

                creds = None

        # ------------------------------------------
        # Refresh Expired Token
        # ------------------------------------------
        if (
            creds
            and creds.expired
            and creds.refresh_token
        ):

            try:

                creds.refresh(Request())

            except Exception:

                creds = None

        # ------------------------------------------
        # First Login
        # ------------------------------------------
        if not creds:

            google_credentials = os.getenv(
                "GOOGLE_CREDENTIALS"
            )

            if google_credentials:

                client_config = json.loads(
                    google_credentials
                )

                flow = InstalledAppFlow.from_client_config(
                    client_config,
                    SCOPES
                )

            else:

                if not os.path.exists(
                    self.credentials_path
                ):

                    raise FileNotFoundError(
                        "credentials.json not found."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    SCOPES
                )

            # NOTE:
            # This opens a browser and should only be used
            # during local development.
            creds = flow.run_local_server(
                port=0
            )

            try:

                with open(
                    self.token_path,
                    "w"
                ) as token:

                    token.write(
                        creds.to_json()
                    )

            except Exception:

                pass

        return creds

    # ======================================================
    # Calendar Service
    # ======================================================
    def build_service(self):

        creds = self.authenticate()

        return build(
            "calendar",
            "v3",
            credentials=creds
        )
    # ======================================================
    # Get Today's Events
    # ======================================================
    def get_events_today(self):

        try:

            service = self.build_service()

            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
            )

            events = events_result.get("items", [])

            if not events:
                return "📅 No meetings scheduled for today."

            output = "## 📅 Today's Meetings\n\n"

            for event in events:

                start = event["start"].get(
                    "dateTime",
                    event["start"].get("date")
                )

                summary = event.get(
                    "summary",
                    "Untitled Event"
                )

                output += (
                    f"• **{summary}**\n"
                    f"  - {start}\n\n"
                )

            return output

        except Exception as e:

            return f"⚠ Calendar Error: {e}"

    # ======================================================
    # Create Event
    # ======================================================
    def create_event(
        self,
        summary="Meeting",
        hour=15,
        minute=0,
        duration=1
    ):

        try:

            service = self.build_service()

            start = datetime.datetime.now().replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0
            )

            end = start + datetime.timedelta(
                hours=duration
            )

            event = {
                "summary": summary,
                "start": {
                    "dateTime": start.isoformat(),
                    "timeZone": "Asia/Kolkata"
                },
                "end": {
                    "dateTime": end.isoformat(),
                    "timeZone": "Asia/Kolkata"
                }
            }

            service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            return (
                f"✅ '{summary}' scheduled at "
                f"{start.strftime('%I:%M %p')}"
            )

        except Exception as e:

            return f"⚠ Unable to create meeting: {e}"

    # ======================================================
    # Smart Schedule
    # ======================================================
    def smart_schedule(
        self,
        summary="Smart Meeting"
    ):

        try:

            service = self.build_service()

            now = datetime.datetime.utcnow().isoformat() + "Z"

            events = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=20,
                    singleEvents=True,
                    orderBy="startTime"
                )
                .execute()
                .get("items", [])
            )

            busy_hours = set()

            for event in events:

                start = event["start"].get("dateTime")

                if start and "T" in start:
                    try:
                        hour = int(
                            start.split("T")[1].split(":")[0]
                        )
                        busy_hours.add(hour)
                    except Exception:
                        pass

            suggested_hour = 10

            while suggested_hour in busy_hours:
                suggested_hour += 1

                if suggested_hour >= 18:
                    suggested_hour = 10
                    break

            return self.create_event(
                summary=summary,
                hour=suggested_hour,
                minute=0
            )

        except Exception as e:

            return f"⚠ Smart Scheduling Failed: {e}"

    # ======================================================
    # Health Check
    # ======================================================
    def test_connection(self):

        try:

            service = self.build_service()

            service.calendarList().list().execute()

            return "✅ Google Calendar connected successfully."

        except Exception as e:

            return f"❌ Calendar connection failed: {e}"