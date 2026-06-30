from llm_engine import generate

class AutoPlanner:

    def generate_plan(self, emails, meetings):

        prompt = f"""
You are Cortex AI, a smart productivity assistant.

Based on:

Emails:
{emails}

Meetings:
{meetings}

Create a structured daily schedule.

Rules:
- Use time slots (9:00, 10:00, etc.)
- Balance work + meetings
- Add focus time
- Keep it practical

Format:
Time → Task
"""

        return generate(prompt)