from llm_engine import generate

class ConversationAgent:

    def respond(self, user_input, context=""):

        prompt = f"""
Context:
{context}

User: {user_input}
Assistant:
"""

        return generate(prompt)