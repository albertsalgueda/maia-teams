# This conversation type should exclude the system message _and_ the first user message (containing information specific to each AI)
from typing import Dict, List

MODEL = "gpt-3.5-turbo"
Conversation = List[Dict[str, str]]
PROJECT = "A program to control stock using bar codes"
PROJECT_NAME = "stock_control"

def print_message(message: Dict[str, str], role: str = None):
    write_message(message, role)
    print(f"{role}: {message['content']}")
    print()

def write_message(message: dict, role: str = None):
    """
    Writes a message to a file called 'conversation.log'
    Code messages have a [CODE] prefix to distinguish them from other messages
    """
    with open(f"db/{PROJECT_NAME}.log", "a") as f:
        if "```" in message["content"]:
            f.write("[CODE] ")
        f.write(f"{role.upper()}: {message['content']}\n")

