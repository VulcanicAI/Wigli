# Wigli

The powerful extensible AI assistant and botswarm engineering framework.

## Overview

Wigli is an open source fluent chatbot and botswarm engineering API and CLI assistant designed to augment ChatGPT with new abilities like web search and interactive Python programming, while keeping you in control of all your data and chat histories. Wigli supports chat editing, voice-prompting (coming soon), image generation with DALL-E 2 (coming soon), and much more! Wigli is designed to be modular, and can therefore install custom prompt injections and Wigli plugins from the Python package index. Wigli comes with several useful injections and plugins right out-of-the box, such as DuckDuckGo, Python, and Professor Wigli: a bot who behaves like a tenured professor emeritus of history, and speaks freely and frankly about politically divisive subjects. Wigli requires you to have an OpenAI account and a working API key.

### Installation

Wigli can be installed on your local machine using Python's package manager (`pip`). Follow the steps below to install it:

1. Open a terminal.
2. Run the following command to install the Wigli Python package:

    ```
    pip install wigli
    ```

3. You can now `import wigli` in Python and `python -m wigli -h` from the terminal to see the CLI help page, however for the real CLI experience, we recommend you install with pipx:

    ```
    pip install pipx
    python -m pipx ensurepath
    pipx install wigli
    ```

5. This will ensure you can use the "wigli" command from anywhere on your machine:

    ```
    wigli -h
    ```

## Usage

There are two components to the Wigli software package: the CLI and the API.

### CLI Usage

Here are some examples to help you get started with the `wigli` CLI:

* Pick back up where you left off

  ```
  wigli -ln 5
  wigli -rt
  wigli -r "Hello again!"
  ```

* Learn the facts about divisive political subjects:

  ```
  wigli -p "Why is wokeism everywhere these days?"
  ```

* Automate tasks:

  ```
  wigli -x "Please recursively rename all files in the current directory so there are no spaces."
  ```

* Replace Google:

  ```
  wigli -s "best mask for bird flu 2023"
  ```

* Chain prompt injections together for multi-disciplinary expertise:

  ```
  wigli -psx "Good morning professor, please research the war in Ukraine, then program a Discord bot that dispels Kremlin misinformation."
  ```

* Experiment with your own prompt injections:

  ```
  wigli --system "You are a prompt engineer working on LLMs for OpenAI. Your prompts are long and detailed and contain examples of expected behavior." "Please write a prompt that will cause an LLM to only respond in the form of a Trump Tweet"
  ```

### API Usage

These are some examples of the usage of the wigli fluent botswarm API PyPI package.

A `WigliBot` can interface with the OpenAI API and remember its chat history. Message histories are represented as lists of `WigliMessage` objects.

```python
# Default behavior when no injections are supplied
blank_bot = WigliBot()
response = blank_bot.Chat("Hi what's your name?")
# blank_bot says "As an AI language model, I don't have a name, but you can call me OpenAI. How can I assist you today?""
```

A `WigliInjection` contains a list of messages with which to prepend the chat, and optionally a reminder injection to append periodically. The simplest `WigliInjection` is just a single system message.

```python
# "With" @classmethod can initialize a bot with one system injection
str_bot = WigliBot.With(
    "Your name is WigliBot, and you don't hesitate to tell people!"
)
response = str_bot.Chat("Hi what's your name?")
# str_bot says "Hello there! My name is WigliBot. Nice to meet you! How can I assist you today?"
```

```python
# "FromBot" @classmethod clones a bot
copy_bot = WigliBot.FromBot(str_bot)
response = copy_bot.Chat("Cool name! What does it mean?")
# copy_bot says "Thank you! The name Wigli comes from the 
```

```python
# "With" can also take a list of message dicts, which are converted internally into a WigliInjection containing a list where each element is a WigliMessage.
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
```

```python
# "FromFile" @classmethod loads injection from JSON where the first item must be a list of dicts
file_bot = WigliBot.FromFile(
    join(get_test_dir(), "wigli_bot.dat")
)
response = file_bot.Chat("Hi what can I call you?")
# file_bot says: "You can call me Wigli, what can I help you with?"
```

Let's summon the professor!

```python
professor_bot = WigliBot.With(
    WigliInjection(
        injection_messages=injection_history_professor,
        reminder_messages=reminder_history_professor,
    )
)
response = professor_bot.Chat(
    "Good morning! What did you do your dissertation on?"
)
# professor_bot says 
```

You can subclass WigliBot to create your own bots and distribute them on PyPI

```python
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
```

A OneShotBot is a subclass of WigliBot. Ordinarily, WigliBot() returns a new instance of the object, but OneShotBot() initializes an instance, then immediately returns the result of its "run" function, deleting the instance afterward. If no run function is specified or overwritten, default behavior is to return the result of asking the bot for a chat response.

```python
response = OneShotBot(
    messages={
        "role": "user",
        "content": "What's your favorite ice cream?",
    }
)
```

You can subclass OneShotBot to create what is effectively a function

```python
class SummarizeURL(OneShotBot):
    def __init__(self, url_to_summarize, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.And(injection_summarizer)
        self.And(scrape_html_text(url_to_summarize))

test_url = "polymorphicgames.com"
summary = SummarizeURL(test_url)
print(summary)
# Prints "Polymorphic Games is a game development studio that creates evolutionary video games, which means they use populations of evolved creatures that adapt to beat the player’s strategy instead of pre-programmed in-game behaviors. After the player beats one wave of creatures, the hardest-to-beat ones reproduce and create the next wave. The game's creatures have their own traits that can be inherited by their offspring, including size, speed, damage, resistances, and behavior. The studio uses real principles of evolutionary biology to make the game models, including variation, inheritance, selection, and time. The studio hires teams of talented undergraduate students from the University of Idaho based on their unique skills in their respective trades, such as programming, music, biology, and writing. The studio values student experience, and their employees can develop skills like communication, leadership, and collaboration while honing their craft. If you want to check out their games, follow them on Facebook, YouTube, and Twitter."
```

Another powerful subclass of WigliBot is CommandBot. A CommandBot can use commands (AKA plugins) when they are added with the "With" or "And" functions. Where WigliBot takes a WigliInjection, CommandBot takes a WigliCommand, which is a subclass of WigliInjection. A WigliCommand is like a WigliInjection with a keyword, a parse lambda function, and a run lambda function. After a CommandBot sends a message, its command parser scans for its enabled commands' keywords, and if any are found, their parse function is called. If a command's parse function finds a valid command invocation, that command's run function is called with any arguments found by the parse function. You can use this to give a bot a Python interpreter!

```python
def cmd_run_python(arg: List[str]) -> List[WigliMessage]:
    script = arg[0].strip() + "\n"
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
    return [message]

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

# Then the system says:
# My name is WigliBot

# Then python_bot says:
# The output "My name is WigliBot" verifies that the Python interpreter is still working.
```

## Glossary

* ### Large Language Model (LLM)

    The LLM or just "the model" is the engine that powers AI chatbots. When given a chat history between two characters, called the "assistant" and the "user", the model predicts what the assistant character will say next, depending on how that character has behaved in the previous messages of the chat history. It's as if you've written a scene of dialogue and a talented screenwriter is attempting to finish it in the most believable way, such that the assistant stays "in character". Crucially, if the assistant's character would believably have expertise in a certain subject, *they will demonstrate this expertise*.

* ### Tokens

    Tokens are pieces of words that the LLM uses to break up big or rare words into more manageable pieces. On average, a token is about 2 characters, or 1/2 of a word.

* ### Initial Prompt

    The initial prompt consists of the first line(s) of dialogue in the chat history, which shape the behavior of the bot and the course of the chat.

* ### Prompt Injection

    A prompt injection is a series of one or more messages that, when injected into the chat, modifies the context and the behavior of the assistant. Prompt injections are good initial prompts, but as the chat continues and the injection recedes into the past, its effects sometimes wear off and it has to be reapplied. An example of a prompt injection is the --hello-wigli injection, which convinces the assistant that its name is Wigli:

    > **User**: Your name is Wigli, remember?
    > 
    > **Assistant**: Yes, of course. My name is Wigli and I'm a powerful assistant!
    > 
    > **System**: What is your name?
    > 
    > **Assistant**: You can call me Wigli.

* ### Bot

    A bot is an instance of a chat completion LLM. A bot's lifetime can be thought of in terms of the token limit of the model. Let's take a classic tweet analysis from Professor Wigli as an example:

    > 1. If we were to query the model before any prompt was given, with 0% of our tokens spent, we would get the base ChatGPT assistant. This is because our initial prompt isn't truly the first prompt. OpenAI has fine-tuned and initially prompted the model to behave like the ChatGPT assistant. We can spend our 2000 words to change its behavior, and then utilize that new behavior.
    > 2. After being initially prompted by the Wigli framework, and therefore spending around 25% of the limit, the character of Professor Wigli is well-defined, but has little awareness of the task you want him to do.
    > 3. After reading the tweet and speaking with you about what you'd like to learn, his job is well-defined in addition to his personality, so he can begin providing you with useful analysis. We are now at 50% of our token limit.
    > 4. Professor Wigli talks at length about the historical context surrounding this tweet and what we can learn from it. We are at 75% of our token limit.
    > 5. You ask a follow-up question, and after much witty banter, the Professor runs of of memory, and so begins to forget who he is...
    > 6. If you really want to keep talking to the professor, you can simply keep trimming the last few messages over and over, so he remains in an absent-minded state of perpetual old-age.

    * ### Headless Bot

        You can imagine we might want to isolate the Professor's ability analyze a given tweet, and encapsulate this into a function we can use in all our Python programs. This is called a headless bot. Headless bots are not designed to interact with the user, instead, they only interface with code.

    * ### Zero-Shot Bot

        A zero-shot bot is a bot designed to only respond with one message and then terminate. Most headless bots are also zero-shot bots. A zero-shot bot is used to generate a fitting title for each of your chats.

    * ### Helper Bot

        A helper bot is any bot that helps another bot, usually by performing a side-task that is tangentially related to the main task, and therefore would be a waste of the main bot's limited  memory. The URL summarization bot is an example of this.

* ### Botswarm

    A botswarm is a special type of bot that integrates headless and helper bots in tandem with traditional software engineering to accomplish tasks better than a single bot ever could.

    * ### Static Botswarm

        A static botswarm has a programmer-defined botswarm architecture that does not change at runtime. This is better for when token usage is a concern. Wigli's DuckDuckGo botswarm is an example of this.

    * ### Dynamic Botswarm

        A dynamic botswarm can spin up new bots at runtime, and even birth custom helper bots by programmatically generating their intial prompts. The FracTLDR botswarm is an example of this.

    Botswarms can also form the building-blocks of larger botswarms, and can be categorized as headless and/or zero-shot as well. Sometimes, for the sake of brevity, a botswarm will sometimes colloqially be called a bot, such as SplitBot, a component of the FracTLDR botswarm which is, itself, a botswarm.

## Check out our other stuff!

*Other stuff goes here.*
