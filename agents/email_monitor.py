import time
from agents.email_agent import EmailAgent

class EmailMonitor:

    def __init__(self):
        self.agent = EmailAgent()
        self.last_email_id = None

    def check_new_email(self):
        try:
            creds = self.agent.authenticate()
            service = self.agent.build_service(creds)

            results = service.users().messages().list(
                userId='me', maxResults=1
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return None

            latest_id = messages[0]['id']

            if self.last_email_id is None:
                self.last_email_id = latest_id
                return None

            if latest_id != self.last_email_id:
                self.last_email_id = latest_id
                return "📧 New email received!"

            return None

        except Exception as e:
            return f"Error: {e}"