"""
This is a Python program called Maia Teams that uses three instances of OpenAI's GPT-3.5-based language model, Maia, to build an app. The three instances are two ChatGPT instances, one acting as the programmer and the other as the product owner, and a third instance that acts as a tester.

The program works by having the product owner and the programmer communicate with each other through Maia. The product owner provides requirements for the app, while the programmer writes the code for the app. Maia ensures that the conversation between the two stays on track and helps resolve any disagreements or issues that arise.

The program takes the following steps:

It sets up the OpenAI API key and organization by loading them from a .env file.
It sets up the initial conversation between the product owner and the programmer.
It enters a loop where the programmer and product owner take turns talking to each other, with Maia acting as an intermediary.
If the product owner sends "KeywordTest" as a response, the program runs the current version of the app using the tester AI and returns either a summary or any errors the code returned.
If either the product owner or the programmer sends "KeywordDone" as a response, the program ends.
Once the app is finished, the program exits.
The adjust_program function takes a response containing Python code and modifies the existing program to comply with the "new" version. The remove_code function replaces markdown-styled Python code with a short message saying it has been removed.

Overall, this program enables two ChatGPT instances to work together to build an app and a tester AI to check their progress.
"""

import inspect
import os
import re
from typing import Dict

import openai
from dotenv import load_dotenv

from common import PROJECT, Conversation, MODEL, print_message
from chatgptester import run_program

load_dotenv()

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")


SYSTEM_TEXT = f"""
You are a one of a pair of ChatGPT instances, tasked with building {PROJECT} in python.
 One of you will be the programmer, the other being the product owner. Code blocks will only be present in the most recent messages.
 Make sure your code has a `main` function. Keep your messages concise, there's no need for pleasantries.
 The product owner can at any point respond "KeywordDone" to indicate that you are finished or respond "KeywordTest" to test run your code
 with a tester AI. After testing, continue iterating based on the testers results until time runs out or
 you are done. DO NOT go around in circles complimenting eachother, if that happens, just say "KeywordDone".
"""

STARTER_PO = """
You are a Product Owner. Your task is to ensure the other AI is fast, and review their code to make sure it is
 good. From here, it's just you two. Feel free to discuss the application with the other AI before writing any code,
 if you so feel. But keep it concise, time is ticking! You may use a set of keywords to perform other actions. 
 Respond "KeywordDone" to indicate that you are finished. Respond "KeywordTest" to test run your code with a tester AI and return either a summary or
 any errors the code returned (Rather than sending it to the programmer).
"""

STARTER_PG = """
You are an experienced programmer. Each time you write code, make sure you include the full function that you wish to modify.
Any functions/classes you dont define will be left as-is, whereas any functions you define will be replaced entirely with your new version
(or added as entirely new functions). Make sure your code is always syntactically correct, especially with `pass` statements if you want to leave some code unimplemented.
"""

MAX_CONVO = 10

def main():
    """Make two ChatGPT instances work together to build an app, with a third acting as a tester"""

    # We store the program here. this allows us to test it, and to keep prompts shorter by removing code blocks that are
    # "redundant"
    # TODO: Multi file programs?
    program = {}  # global scope containing class and function definitions

    print("Starting Maia Teams!")
    convo = []
    for i in range(MAX_CONVO):
        convo = product_owner(convo)
        print_message(convo[-1], "PRODUCT OWNER")
        if "keywordtest" in convo[-1]["content"].lower():
            test_result = run_program(program)
            convo.append({
                "role": "user",
                "content": test_result
            })
            continue  # send result back to PO
        elif "keyworddone" in convo[-1]["content"].lower():
            break
        convo = invert_conversation(convo)
        
        # programmers turn
        convo = programmer(convo)
        print_message(convo[-1], "PROGRAMMER")
        adjust_program(program, convo[-1]["content"])
        if len(convo) >= 4:
            convo[-3]["content"] = remove_code(convo[-3]["content"])
            convo[-4]["content"] = remove_code(convo[-4]["content"])
        if "keyworddone" in convo[-1]["content"].lower():
            break
        convo = invert_conversation(convo)

    print("Maia teams is DONE!")


def remove_code(content: str) -> str:
    """Replace markdown styled python code with a short message saying it has been removed"""
    return re.sub(r"```python\n([^`]*)```", r"```python\n# OLD CODE HAS BEEN HIDDEN\n```", content)


def adjust_program(program: dict, content: str):
    """Take a response containing python code and modify the existing program to comply with the "new" version"""
    code = re.search(r"```python\n([^`]*)```", content)
    if code:
        for codeblock in code.groups():
            # TODO: Return any syntax errors here to the programmer
            exec(codeblock, program)
    else:
        return  # no code in message
    

def invert_conversation(convo: Conversation) -> Conversation:
    """
    Invert the conversation so "user" becomes "assistant" and vice-versa. Not sure
    how important this actually is but eh.
    """
    return [{
        "role": "user" if message["role"] == "assistant" else "assistant",
        "content": message["content"]
        } 
        for message in convo
    ]


def product_owner(conversation: Conversation) -> Conversation:
    messages: Conversation = [
        {"role": "system", "content": SYSTEM_TEXT + "\n\n" + STARTER_PO},
        {"role": "user", "content": "Your first response:"}
    ]
    messages.extend(conversation)
    completion = openai.ChatCompletion.create(model=MODEL, messages=messages)
    messages.append(completion.choices[0]["message"])
    messages = messages[2:]
    return messages 


def programmer(conversation: Conversation) -> Conversation:
    messages: Conversation = [
        {"role": "system", "content": SYSTEM_TEXT + "\n\n" + STARTER_PG},
        {"role": "user", "content": "Here is the first message from your colleague: " + conversation[0]["content"]}
    ]
    messages.extend(conversation)
    completion = openai.ChatCompletion.create(model=MODEL, messages=messages)
    messages = messages[2:]
    messages.append(completion.choices[0]["message"])
    return messages 

if __name__ == "__main__":
    main()
