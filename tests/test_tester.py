import pytest
from chatgpteam.chatgptester import run_program


def func():
    print("Hello! this is a simple test of your ability to test! Please just enter your name")
    name = input("Your name:")
    print("Thank you " + name + "!")

# These tests partially written by ChatGPT 4!
def test_run_program_simple_program():
    program = {
        'main': func
    }

    result = run_program(program)
 