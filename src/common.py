# This conversation type should exclude the system message _and_ the first user message (containing information specific to each AI)
from typing import Dict, List


MODEL = "gpt-3.5-turbo"
Conversation = List[Dict[str, str]]
PROJECT = "a powerful GPT-based chatbot API for generating data visualizations on-the-fly. This API enables users to import datasets in various formats, ask natural language queries, and receive tailored graphs in response. With customizable graph types, data filtering and aggregation, and AI-driven insights, the chatbot makes it easy to visualize and analyze data. Integration with popular messaging platforms and export options for sharing the generated graphs ensure seamless collaboration"


def print_message(message: Dict[str, str], role: str = None):
    write_message(message, role)
    print(f"{role}: {message['content']}")
    print()

def write_message(message: dict, role: str = None):
    """
    Writes a message to a file called 'conversation.log'
    Code messages have a [CODE] prefix to distinguish them from other messages
    """
    with open("tests/conversation.log", "a") as f:
        if "```" in message["content"]:
            f.write("[CODE] ")
        f.write(f"{role.upper()}: {message['content']}\n")

