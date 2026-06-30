from voice import listen, speak

from agents.planner_agent import PlannerAgent
from agents.memory_agent import MemoryAgent
from agents.alarm_agent import AlarmAgent
from agents.email_agent import EmailAgent
from agents.conversation_agent import ConversationAgent


planner = PlannerAgent()
memory = MemoryAgent()
alarm = AlarmAgent()
email = EmailAgent()
conversation = ConversationAgent()


def main():

    speak("Hello ! How can i help you")

    while True:

        user_input = listen()

        if user_input.lower() in ["exit", "quit"]:
            speak("Goodbye Sunny!")
            break

        plan = planner.plan(user_input)

        if plan["task"] == "set_alarm":
            response = alarm.execute(user_input)

        elif plan["task"] == "summarize_email":
            response = email.execute()

        elif plan["task"] == "store_memory":
            name = user_input.split("is")[-1].strip()
            response = memory.store("name", name)

        elif plan["task"] == "recall_memory":
            name = memory.recall("name")
            response = f"Your name is {name}" if name else "I don't know your name yet."

        else:
            response = conversation.respond(user_input)

        speak(response)


if __name__ == "__main__":
    main()