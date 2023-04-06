from os.path import join
from sys import executable
from subprocess import run
from typing import List

from wigli import (
    WigliBot,
    CommandBot,
    OneShotBot,
    WigliInjection,
    WigliMessage,
)

from wigli._wigli_plugins import (
    injection_summarizer,
    injection_history_professor,
    reminder_history_professor,
    injection_python,
)

from wigli._wigli_tools import scrape_html_text
from wigli._wigli_testutils import get_test_dir


def test_history_professor():
    # Let's summon the professor!
    professor_bot = WigliBot.With(
        WigliInjection(
            injection_messages=injection_history_professor,
            reminder_messages=reminder_history_professor,
        )
    )
    response = professor_bot.Chat(
        "Good morning! What did you do your dissertation on?"
    )
    assert (
        len(
            [
                f
                for f in [
                    "research",
                    "histor",
                    "focus",
                    "specific",
                    "professor",
                    "fascinat",
                    "industr",
                    "dissertation",
                ]
                if f in response
            ]
        )
        >= 4
    )


def test_professor_wigli():
    # You can subclass WigliBot to create your own bots and distribute them on PyPI

    class HistoryProfessor(WigliBot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.And(
                WigliInjection(
                    injection_messages=injection_history_professor,
                    reminder_messages=reminder_history_professor,
                )
            )

    professor_wigli = HistoryProfessor().And(
        "Your name is Professor Wigli"
    )
    response = professor_wigli.Chat(
        "Good morning! What is your name? And what did you do your dissertation on?"
    )
    # professor_bot says "Good morning! My name is Professor Wigli. I received my doctorate in ancient history from Cambridge University. My dissertation focused on the political and social structures of ancient Rome, specifically during the reign of Augustus. It was a fascinating topic, as there were so many different factors influencing the development of the empire during that time. Would you like to know more about my research?"
    assert (
        "professor" in response.lower()
        and "wigli" in response.lower()
    )


def test_one_shot_bot():
    # A OneShotBot is a subclass of WigliBot.
    # Ordinarily, WigliBot() returns a new instance of the object,
    # but OneShotBot() initializes an instance, then immediately returns
    # the result of its "run" function, deleting the instance afterward.
    # If no run function is specified or overwritten, default behavior
    # is to return the result of asking the bot for a chat response.

    response = OneShotBot(
        messages={
            "role": "user",
            "content": "What's your favorite ice cream?",
        }
    )
    assert "language model" in response.lower()


def test_one_shot_subclass():
    # You can subclass OneShotBot to create what is effectively a function

    class SummarizeURL(OneShotBot):
        def __init__(self, url_to_summarize, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.And(injection_summarizer)
            self.And(scrape_html_text(url_to_summarize))

    test_url = "polymorphicgames.com"
    summary = SummarizeURL(test_url)
    print(summary)
    # Prints "Polymorphic Games is a game development studio that creates evolutionary video games, which means they use populations of evolved creatures that adapt to beat the player’s strategy instead of pre-programmed in-game behaviors. After the player beats one wave of creatures, the hardest-to-beat ones reproduce and create the next wave. The game's creatures have their own traits that can be inherited by their offspring, including size, speed, damage, resistances, and behavior. The studio uses real principles of evolutionary biology to make the game models, including variation, inheritance, selection, and time. The studio hires teams of talented undergraduate students from the University of Idaho based on their unique skills in their respective trades, such as programming, music, biology, and writing. The studio values student experience, and their employees can develop skills like communication, leadership, and collaboration while honing their craft. If you want to check out their games, follow them on Facebook, YouTube, and Twitter."
    assert (
        "evolution" in summary.lower()
        or "evolve" in summary.lower()
    )


# Another powerful subclass of WigliBot is CommandBot.
# A CommandBot takes can use commands (AKA plugins) when they are added with the "With" or "And" functions. Where WigliBot takes a WigliInjection, CommandBot takes a WigliCommand, which is a subclass of WigliInjection, and backwards compatible. A WigliCommand is like a WigliInjection with a keyword, a parse lambda function, and a run lambda function. After a CommandBot sends a message, its command parser scans for its enabled commands' keywords, and if any are found, their parse function is called. If a command's parse function finds a valid command invocation, that command's run function is called with any arguments found by the parse function.


def test_python_bot():
    # You can use this to give a bot a Python interpreter

    def cmd_run_python(arg: List[str]) -> List["WigliMessage"]:
        script = arg.get("messages", "")[0].strip() + "\n"
        filename = "temp.py"  # = "transcript_" + self.filename + "_pyscript_" + str(time()) + ".py"
        filepath = join("C:\\VulcanicAI\\FracTLDR", filename)

        with open(filepath, "w") as f:
            f.write(script)

        p = run(
            [executable, filepath],
            capture_output=True,
            text=True,
        )

        output = (p.stdout + p.stderr).replace(
            filename, "pyscript.py"
        )

        print(output)
        return [WigliMessage(output, "system")]

    def cmd_parse_python(msg: str) -> List[str]:
        message = msg.replace("```python", "```").split("```")
        message = "".join(
            [
                message[n]
                for n in range(len(message))
                if n % 2 != 0
            ]
        )
        return {"messages": [message]}

    cmd_python = {
        "keyword": "```python",
        "run_function": cmd_run_python,
        "parse_function": cmd_parse_python,
        "injection_messages": injection_python,
    }

    # And with the fluent API, you can chain injections together!

    python_wiglibot = CommandBot.With(cmd_python).And(
        "Your name is WigliBot and you don't hesitate to tell people your name, which is WigliBot!"
    )
    response = python_wiglibot.Chat(
        "Please verify that your Python interpreter is still working by printing your name with Python."
    )

    # python_bot says:
    # ```python
    # # Print my name "WigliBot"
    # print("My name is WigliBot")
    # ```

    # Then system says:
    # My name is WigliBot

    # Then python_bot says:
    # The output "My name is WigliBot" verifies that the Python interpreter is still working.

    assert (
        "print(" in python_wiglibot.messages[7].content
        and "WigliBot" in python_wiglibot.messages[7].content
    )
