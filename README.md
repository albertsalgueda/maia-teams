# Maia Teams

Maia Teams, a Python library, leverages OpenAI's GPT-3.5-based AI chatbot, Maia, to create and test simple programs. It simulates Maia's self-conversations as a "programmer" and "product owner," iterating until completion or time expiration. A separate chat tests the code.


# Installation
To install Maia Teams, use pip:

```
pip install maiateams
```
# Usage
First, create a file called .env and enter your OpenAI API information:
```
OPENAI_API_KEY=sk-<YOUR-API-KEY>
OPENAI_ORG=org-<YOUR-ORG>
```
Then, set the project you would like Maia to work on by changing PROJECT in src/common.py. You can also change other settings there.

Finally, run the following command to start Maia:

```
python -m maiateams
```

# Issues
The main issue right now is that Maia seems to give up a little too easily, and
ends up just complimenting itself in circles, rather than continuing to improve
the program. She also doesn't seem to use the KeywordDone keyword often enough.

# Contributing
Contributions are welcome! Feel free to open an issue or pull request on GitHub