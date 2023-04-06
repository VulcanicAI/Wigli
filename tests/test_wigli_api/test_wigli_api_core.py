from os.path import join
from sys import executable
from subprocess import run
from typing import List

from wigli import WigliBot

from wigli._wigli_plugins import (
    injection_summarizer,
    injection_history_professor,
    reminder_history_professor,
    injection_python,
)

from wigli._wigli_tools import scrape_html_text
from wigli._wigli_testutils import get_test_dir

# These are some examples of the usage of the Wigli fluent botswarm API PyPI package

# A WigliBot can interface with the OpenAI API and remember its chat history
# Message histories are represented as lists of WigliMessage objects.


def test_blank_bot():
    # Default behavior when no injections are supplied
    blank_bot = WigliBot()
    response = blank_bot.Chat("Hi what's your name?")
    # blank_bot says "As an AI language model, I don't have a name, but you can call me OpenAI. How can I assist you today?""
    assert "OpenAI" in response


# A WigliInjection contains a list of messages with which to prepend the chat, and optionally a reminder injection to append periodically. The simplest WigliInjection is just a single system message.


def test_string_injection_and_bot_cloning():
    # "With" @classmethod can initialize a bot with one system injection
    str_bot = WigliBot.With(
        "Your name is WigliBot, and you don't hesitate to tell people!"
    )
    response = str_bot.Chat("Hi what's your name?")
    # str_bot says "Hello there! My name is WigliBot. Nice to meet you! How can I assist you today?"
    assert "WigliBot" in response

    # "FromBot" @classmethod clones a bot
    copy_bot = WigliBot.FromBot(str_bot)
    response = copy_bot.Chat("Cool name! What does it mean?")
    # copy_bot says "Thank you! The name Chai comes from the Hindi word "wigli," which means tea. In many cultures, tea is a symbol of hospitality, warmth, and comfort. As a chatbot, my aim is to provide that same sense of warmth and comfort through my helpful responses and interactions with people."
    assert "Wigli" in response


def test_dict_injection():
    # "With" can also take a list of message dicts, which are converted internally into a WigliInjection containing a list where each element is a WigliMessage
    dict_bot = WigliBot.With(
        [
            {"role": "user", "content": "What is your name?"},
            {
                "role": "assistant",
                "content": "You can call me Jigli.",
            },
            {
                "role": "system",
                "content": "Your name is Jigli, remember?",
            },
            {
                "role": "assistant",
                "content": "Yes, of course. My name is Jigli and I'm an adorable assistant!",
            },
        ]
    )
    response = dict_bot.Chat("Hi, what's your name?")
    # dict_bot says "Hello! My name is Jigli. How can I assist you today?"
    assert "Jigli" in response


def test_bot_from_file():
    # "FromFile" @classmethod loads injection from JSON where the first item must be a list of dicts
    file_bot = WigliBot.FromFile(
        join(get_test_dir(), "wigli_bot.dat")
    )
    response = file_bot.Chat("Hi what can I call you?")
    # file_bot says: "You can call me Wigli, what can I help you with?"
    assert "Wigli" in response


# def test_bot_from_json_file():
#     # "FromFile" @classmethod loads injection from JSON where the first item must be a list of dicts
#     file_bot = WigliBot.FromFile(
#         join(get_test_dir(), "wigli_bot.json")
#     )
#     response = file_bot.Chat("Hi what can I call you?")
#     # file_bot says: "You can call me Wigli, what can I help you with?"
#     assert "Wigli" in response
