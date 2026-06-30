class PlannerAgent:

    def plan(self, user_input):
        text = user_input.lower()

        if "alarm" in text:
            return {"task": "set_alarm"}

        elif "reply" in text:
            return {"task": "reply_email"}

        elif "multiple" in text or "many emails" in text:
            return {"task": "multi_email_summary"}

        elif "email" in text:
            return {"task": "summarize_email"}

        elif "meeting" in text or "schedule" in text or "calendar" in text:
            return {"task": "calendar"}

        elif "smart" in text:
            return {"task": "smart_schedule"}

        elif "remind" in text:
            return {"task": "reminder"}

        elif "remember" in text:
            return {"task": "store_memory"}

        elif "what is my name" in text:
            return {"task": "recall_memory"}
        
        else:
            return {"task": "conversation"}