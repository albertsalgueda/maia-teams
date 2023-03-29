"""
This program is a function called run_program that uses a ChatGPT model to test some Python code.

The run_program function takes a Python program as input and returns a string with the final message from the AI, or the traceback from the program if an error occurred.

The program works by using a conversation between a system tester (the AI) and the program being tested. The conversation is stored in a Conversation list. The tester provides input to the program as if it were being run in the console, and the AI waits for the output from the program before providing the next input.

The run_program function replaces the built-in input function with a custom one that gets input from the AI instead of the console. It then runs the main function of the provided Python program using the redirect_stdout context manager to capture the output from the program.

Once the program has finished running or has been interrupted, the run_program function restores the original input function and returns the conversation with the AI as a string. The AI also provides a summary of any problems and what improvements could be made

"""

import builtins
from contextlib import redirect_stdout
import os
import io
from typing import Optional

import openai
from dotenv import load_dotenv

from common import MODEL, Conversation, print_message, PROJECT

load_dotenv()

openai.organization = os.getenv("OPENAI_ORG")
openai.api_key = os.getenv("OPENAI_API_KEY")


SYSTEM_TESTER = f"""
You are a code tester, tasked with testing {PROJECT} in python. Each user message will be output from the console,
 where this program is run. Write a response as a user so as to test the program. The program may fail, in which case you will get a
 syntax error and you should write a summary of what happened before the failure. Respond with "KeywordDone" when you have finished
 testing (at any point), along with a summary of any problems and improvements that could be made.
"""


def run_program(program: dict) -> str:
    """
    Use a chatGPT model to test some python code. Currently supports 1 run programs and programs with console input.

    TODO: Allow the AI to try rerunning if it gets an error, so that it can test multiple failure modes
    
    Returns:
        A string with the final message from the AI, or the traceback from the program
    """
    print("#### Starting testing! #### ")
    messages: Conversation = [
        {"role": "system", "content": SYSTEM_TESTER},
    ]
    f = io.StringIO()
    input_calls = 0
    full_convo = ""

    # we swap out the definition of input, so that we can get an input from the AI instead of console
    def get_ai_input(prompt: Optional[str] = None):
        """Use the same signature as input to get input from a ChatGPT instance"""
        nonlocal f
        nonlocal input_calls
        nonlocal messages
        nonlocal full_convo
        s = f.getvalue()
        if prompt:
            s = s + prompt
        full_convo += s + "\n"
        
        # we reset f so that it only contains one bit of stdout. the full history will be stored in messages
        f.truncate(0)
        f.seek(0)  

        if input_calls >= 10:
            raise KeyboardInterrupt()
        
        messages.append({
            "role": "user",
            "content": s  # the last message isnt actually sent to the AI
        })
        completion = openai.ChatCompletion.create(model=MODEL, messages=messages)
        message = completion.choices[0]["message"]
        response = message["content"]
        full_convo += response + "\n"
        messages.append(message)
        
        if "keyworddone" in response.lower() or input_calls >= 10:
            # we return a keyboard interrupt here, just like if it was in a real console!
            raise KeyboardInterrupt()
        
        input_calls += 1
        return response
        
    # Save the original input function
    original_input = builtins.input

    # Replace the built-in input function with the custom one
    builtins.input = get_ai_input
    
    interrupt = False
    with redirect_stdout(f):
        try:
            program["main"]()  # run main!
            # if we get here, then the program ended itself before the message timeout (eg the ai used an exit call)
        except KeyboardInterrupt:
            interrupt = True
    
    print(full_convo)
    
    # Restore the original input function
    builtins.input = original_input
    
    reason = "was interrupted" if interrupt else "exited"
    print("Ending test session.")
    messages.append({
        "role": "user",
        "content": f"""
            SYSTEM: The program {reason}. This test session will now end. Please respond with a summary of any problems,
                and what improvements could be made.
        """
    })
    completion = openai.ChatCompletion.create(model=MODEL, messages=messages)
    message = completion.choices[0]["message"]
    print_message(message)
    return message["content"]
    
