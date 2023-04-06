# wigli wigli_bots.py

import openai

from copy import deepcopy
from dotenv import load_dotenv
from json import load
from os import getenv
from os.path import join
from slugify import slugify
from time import time
from typing import Any, Callable, Iterable, List, TYPE_CHECKING

from wigli._wigli_tools import (
    clamp,
    count_tokens,
    format_timestamp,
    plural,
    pluralize,
)

if TYPE_CHECKING:
    from wigli._wigli_data import WigliData

MAX_COMMANDS = 8
DEFAULT_TEMPERATURE = 1
MAX_TOKENS = 2**12
CH_PER_TOK = 4


def format_message(
    message: str | dict or "WigliMessage", role: str = "system"
) -> "WigliMessage":
    if isinstance(message, str):
        message = {"role": role, "content": message}
    if not isinstance(message, WigliMessage):
        message = WigliMessage(message)
    return message


def format_messages(
    messages: str
    | dict
    | Iterable[str | dict or "WigliMessage"]
    or "WigliMessage" = [],
    role="system",
) -> List["WigliMessage"]:
    """
    Takes messages in any compatible format, performs robust \
    type checking, and converts them to a list of WigliMessage objects
    """
    if (
        not isinstance(messages, Iterable)
        or isinstance(messages, str)
        or isinstance(messages, dict)
    ):
        messages = [messages]

    return [format_message(msg, role=role) for msg in messages]


def assert_type(
    subject: Any,
    name: str,
    expected_types: type | Iterable[type],
    error: Exception = TypeError,
    msg: str = None,
):
    if not isinstance(expected_types, Iterable):
        expected_types = [expected_types]
    for n, expected_type in enumerate(expected_types):
        # if not isinstance(expected_type, type):
        #     raise TypeError(
        #         f"expected_types must contain only elements of type type but the element at index {n} is of type {type(expected_type)}"
        #     )
        if isinstance(subject, expected_type):
            break
    else:
        if msg is not None:
            raise error(msg)
        else:
            raise error(
                f"""{name} must be of type {" or ".join(expected_types)}"""
            )


## Objects


class WigliMessage(object):
    def __init__(
        self,
        message: str | dict = None,
        role: str = None,
        timestamp: float = None,
    ):
        self.role = "user"
        self.content = ""
        self.timestamp = None

        if isinstance(message, dict):
            temp_role = message.get("role")
            if isinstance(temp_role, str):
                self.role = temp_role
            message = message.get("content")
        if isinstance(message, str):
            self.content = message
        if isinstance(role, str):
            self.role = role
        if isinstance(timestamp, float):
            self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = time()

    def __str__(self) -> str:
        return f"""{self.role.title()}, {format_timestamp(self.timestamp)}: {self.content}"""

    def md(self, truncation: int = None):
        if isinstance(truncation, int):
            message = "> " + self.content[
                :truncation
            ].strip().replace("\n", "\n> ")
        else:
            message = "> " + self.content.strip().replace(
                "\n", "\n> "
            )
        return f"""\
#### [{self.role.title()}](##### "{format_timestamp(self.timestamp)}"):\n\n{message}"""

    def items(self):
        return [("role", self.role), ("content", self.content)]


class WigliInjection(object):
    def __init__(
        self,
        injection_messages: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | str | dict],
        reminder_messages: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | str | dict] = None,
        reminder_period: int = 5,
        set_timer: int = 0,
        role="system",
    ):
        self.injection_messages = format_messages(
            injection_messages,
            role=role,
        )

        assert_type(reminder_period, "reminder_timer", int)
        self.reminder_period = reminder_period
        assert_type(set_timer, "set_timer", int)

        self.reminder_timer = set_timer
        self.reminder_period = reminder_period
        self.reminder_messages = reminder_messages

        if self.reminder_messages is None:
            return

        self.reminder_messages = format_messages(
            self.reminder_messages
        )

    def do_reminder_tick(self):
        self.reminder_timer += 1
        if self.reminder_timer >= self.reminder_period:
            self.reminder_timer = 0
            return self.reminder_messages
        return []

    def __hash__(self):
        return hash(
            "\n".join(
                [str(msg) for msg in self.injection_messages]
            )
        )


class WigliCommand(WigliInjection):
    def __init__(
        self,
        cmd: dict,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        keyword = cmd.get("keyword")
        assert_type(keyword, "keyword", str)
        self.keyword = keyword
        run_function = cmd.get("run_function")
        assert_type(run_function, "run", Callable)
        self.run = run_function
        parse_function = cmd.get("parse_function")
        assert_type(parse_function, "parse", Callable)
        self.parse = parse_function


class WigliBot(object):
    TIMEOUT = 10

    LIMIT_MSG = "[ERROR: CONVERSATION LIMIT REACHED]"
    EMPTY_MSG = "[ERROR: NO PROMPT]"
    KEY_ERR_MSG = "[ERROR: NO OPENAI API KEY]"
    TIMEOUT_MSG = f"[ERROR: OPENAI FAILED TO RESPOND FOR {TIMEOUT} SECONDS]"

    def __init__(
        self,
        messages: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection
        | None = None,
        data: None or "WigliData" = None,
        prompt: str | None = None,
        title: str | None = None,
        filename: str | None = None,
        birthstamp: float = time(),
        touchstamp: float | None = None,
        stream: bool = True,
        reminders: set | None = set(),
    ):
        # Default class attribute values
        self.messages = []
        self.reminders = reminders
        self.stream = stream

        self.data = data
        if self.data is not None:
            self.log = self.data.log

        self.title = title
        self.filename = filename
        self.birthstamp = birthstamp
        self.touchstamp = (
            self.birthstamp
            if touchstamp is None
            else touchstamp
        )

        if openai.api_key is None:
            self.log("No openai.api_key found")
            self.log("Attempting load_dotenv()")
            load_dotenv()
            openai.api_key = getenv("OPENAI_API_KEY")

        if openai.api_key is None:
            self.log("No openai.api_key found")
            dotenv_path = join(self.data.data_dir, ".env")
            self.log(f"Attempting load_dotenv(dotenv_path={dotenv_path})")
            load_dotenv(dotenv_path=dotenv_path)
            openai.api_key = getenv("OPENAI_API_KEY")

        if messages is not None:
            self.Inject(messages)
        if prompt is not None:
            self.Inject(prompt)

    @classmethod
    def FromBot(cls, bot, *args, **kwargs):
        copied_attrs = {}
        for attr in vars(bot).keys():
            if attr != "log":
                value = getattr(bot, attr)
                copied_attrs[attr] = deepcopy(value)

        # Update copied_attrs with kwargs, overwriting any conflicting keys
        copied_attrs.update(kwargs)
        return cls(*args, **copied_attrs)

    # @classmethod
    # def FromJsonFile(cls, filename, *args, **kwargs):
    #     json_obj = {}
    #     with open(filename) as file:
    #         json_obj = load(file)
    #         bot = decode(json_obj)
    #         if isinstance(bot, WigliBot):
    #             return cls.FromBot(bot, *args, **kwargs)
    #     obj = cls(*args, **kwargs)
    #     obj.log(f"There was a problem loading {filename}", v=1)
    #     return obj

    @classmethod
    def FromFile(cls, filename, *args, **kwargs):
        json_obj = {}
        with open(filename) as file:
            json_obj = load(file)
            return cls.With(
                json_obj.get("messages", []), *args, **kwargs
            )
        obj = cls(*args, **kwargs)
        obj.log(f"There was a problem loading {filename}", v=1)
        return obj

    @classmethod
    def With(
        cls,
        prompt: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection = None,
        *args,
        **kwargs,
    ) -> "CommandBot":
        obj = cls(*args, **kwargs)
        if prompt is not None:
            obj.Inject(prompt)
        return obj

    def Inject(self, *args, **kwargs) -> "WigliBot":
        return self.And(*args, *kwargs)

    def And(
        self,
        messages: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection,
        role: str = "system",
    ) -> "WigliBot":
        if (
            isinstance(messages, Iterable)
            and len(messages) <= 0
        ):
            return self
        if not isinstance(messages, WigliInjection):
            messages = WigliInjection(messages, role=role)
        self.messages += messages.injection_messages
        if messages.reminder_messages is not None:
            self.reminders |= {messages}
        if self.data is not None:
            self.data.archive_chat(self)
        return self

    def make_filename(self):
        filename = slugify(
            self.title, ok="_", only_ascii=True, lower=False
        )
        self.filename = str(self.touchstamp) + "_" + filename

    def set_logger(self, logger: "WigliData"):
        self.data = logger
        self.log = logger.log

    def do_reminders_tick(self):
        for reminder in self.reminders:
            self.Inject(reminder.do_reminder_tick())

    def Chat(
        self,
        prompt: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection = None,
        stream: bool = None,
        model: str = "gpt-3.5-turbo",
        temperature: float = DEFAULT_TEMPERATURE,
        n: int = 1,
        stop: str | list = None,
        max_tokens: int = None,
        presence_penalty: float = 0,
        frequence_penalty: float = 0,
        logit_bias: dict = {},
        user: str = None,
        nochat: bool = False,
    ) -> str:
        if stream is None:
            stream = self.stream
        if prompt is not None:
            self.And(prompt, role="user")
        if nochat:
            return ""

        def dummy_message():
            dummy_message = "Let me think about that..."
            if stream:
                print(dummy_message)
            return dummy_message

        # return dummy_message() # Debug option for no API calls

        # Check if any messages exist
        if len(self.messages) <= 0:
            if stream:
                print(self.EMPTY_MSG, flush=True)
            return self.EMPTY_MSG

        # Check if messages will fit in model
        tokens = count_tokens(self.messages, model)
        self.log(
            f"Counted {tokens} {pluralize('token')} in self.messages"
        )
        if tokens > MAX_TOKENS:
            if stream:
                print(self.LIMIT_MSG, flush=True)
            return self.LIMIT_MSG

        # Convert _WigliMessages into dicts
        dict_messages = [
            {key: val for key, val in m.items()}
            for m in self.messages
        ]

        try:
            # OpenAI API request
            completion = openai.ChatCompletion.create(
                model=model,
                messages=dict_messages,
                temperature=temperature,
                # n=n,
                stream=stream,
                # stop=stop,
                # max_tokens=max_tokens,
                # presence_penalty=presence_penalty,
                # frequence_penalty=frequence_penalty,
                # logit_bias=logit_bias,
                # user=user,
            )
        except openai.error.AuthenticationError as e:
            self.log(
                f'OpenAI API Key AuthenticationError... Run "wigli --set-api-key <your_openai_api_key>" to fix this.\n\n{e}',
                v=0,
            )
            return self.KEY_ERR_MSG

        if not stream:
            finish_reason = completion.choices[0].finish_reason
            response = WigliMessage(
                completion.choices[0].message
            )
        else:
            finish_reason = "stop"
            response = WigliMessage(role="assistant")

            for event in completion:
                choice = event.choices[0]
                if "content" in choice.delta.keys():
                    response.content += choice.delta.content
                    print(
                        choice.delta.content, end="", flush=True
                    )
                finish_reason = choice.finish_reason

        if finish_reason == "length":
            if stream:
                print(self.LIMIT_MSG, flush=True)
            response.content += self.LIMIT_MSG
            return response.content

        if stream:
            print("")

        self.And(response)
        self.do_reminders_tick()
        return response.content

    def extract_transcript(
        self, limit=None, truncation=None, start=0
    ):
        archive_len = len(self.messages) - start
        if limit is not None and limit < archive_len - start:
            script_len = limit
        else:
            script_len = archive_len

        dates = []
        roles = []
        messages = []
        for n in range(
            archive_len - start - script_len,
            archive_len - start,
        ):
            message = self.messages[n]
            dates.append(format_timestamp(message.timestamp))
            roles.append(message.role)
            if truncation is not None:
                messages.append(
                    "> "
                    + message.content[:truncation]
                    .strip()
                    .replace("\n", "\n> ")
                )
            else:
                messages.append(
                    "> "
                    + message.content.strip().replace(
                        "\n", "\n> "
                    )
                )

        return dates, roles, messages

    def format_transcript(
        self,
        limit=None,
        truncation=None,
        linestart="",
    ):
        """
        Returns a transcript of the chat in plain text format.
        Each message is prefaced by the date, time, and sender"s name.

        Parameters
        ----------
        limit: int
            The amount of messages to limit the transcription to.
        truncation: int
            The amount of characters to limit each message to.
        linestart: str
            What to start each message with.

        Returns
        -------
        str
            The entire chat history in plain human-readable text.
        """

        archive_len = len(self.messages)
        self.log(f"archive_len is {archive_len}")
        if limit is not None and limit < archive_len:
            script_len = limit
        else:
            script_len = archive_len
        dates, roles, messages = self.extract_transcript(
            limit=limit
        )

        return "\n\n".join(
            [
                f"""\
{linestart}{dates[n]} [{roles[n]}]: \
{
    (
        (messages[n][:truncation] + '...')
        if truncation and len(messages[n]) > truncation
        else messages[n]
    ) 
}
"""
                for n in range(
                    archive_len - script_len, archive_len
                )
            ]
        )

    def format_transcript_markdown(self, limit=None):
        """
        Returns a transcript of the chat in markdown format.
        Each message is a blockquote with the date, time, and sender"s
        name in a level 5 header in the top of the blockquote.

        Parameters
        ----------
        limit: int
            The amount of messages to limit the transcription to.
        truncation: int
            The amount of characters to limit each message to.

        Returns
        -------
        str
            The entire chat history formatted in markdown.
        """

        dates, roles, messages = self.extract_transcript(
            limit=limit
        )

        return "\n\n".join(
            [
                f"""\
#### [{roles[n].title()}](##### "{dates[n]}"):\n\n{messages[n]}"""
                for n in range(len(messages))
            ]
        )

    def erase_messages(self, num_messages_to_erase):
        """
        Removes messages from the end of the chat and updates the birthstamp.

        Parameters
        ----------
        num_messages_to_erase: int
            How many messages to erase.
        """
        # Clamp the argument to valid values
        num_messages_to_erase = clamp(
            num_messages_to_erase, 0, len(self.messages)
        )
        # Only trim if the argument is nonzero
        if num_messages_to_erase > 0:
            self.log(
                (
                    "Trimming last",
                    num_messages_to_erase,
                    plural("message", num_messages_to_erase),
                    "from chat",
                )
            )
            self.messages = self.messages[
                :-num_messages_to_erase
            ]
            # Update birthstamp so original doesn't get deleted
            self.birthstamp = self.touchstamp

    def _last_message(self) -> str:
        if len(self.messages) > 0:
            return self.messages[-1].content
        return ""

    def log(self, s, end="\n", sep=" ", v=3):
        pass


class OneShotBot(WigliBot):
    def __init__(self, *args, **kwargs):
        stream = kwargs.get("stream", None)
        if stream is None:
            kwargs["stream"] = False
        self.run_args = kwargs.pop("run_args", {})
        assert_type(self.run_args, "run_args", dict)
        run_method = kwargs.pop("run_method", None)
        if run_method is not None:
            assert_type(run_method, "run_method", Callable)
            self.run = run_method
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.run(instance.run_args)

    def run(self, run_args):
        return self.Chat()


class CommandBot(WigliBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_cmds = set()

    def Chat(
        self,
        prompt: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection = None,
        *args,
        **kwargs,
    ) -> str:
        reprompt = kwargs.pop("reprompt", True)
        nochat = kwargs.pop("nochat", False)
        if nochat:
            if prompt is not None:
                self.And(prompt, role="user")
            if len(self.messages) < 1:
                return ""
            response = self.messages[-1].content
        else:
            response = super().Chat(prompt, *args, **kwargs)

        args = []
        for num_commands in range(MAX_COMMANDS):
            self.log("Parsing message for commands")
            for cmd in self.active_cmds:
                if cmd.keyword in response:
                    arg = cmd.parse(response)
                    if arg is not None:
                        arg["stream"] = self.stream
                        result = cmd.run(arg)
                        break
            else:
                break

            if result[-1].role == "quit":
                break

            if not reprompt:
                break

            self.log("Reprompting with command output")
            kwargs["prompt"] = result

            response = super().Chat(*args, **kwargs)
        else:
            print(
                f"""\
The maximum allowed number of bot commands in a row is {MAX_COMMANDS}, \
but Wigli would like to keep going. To allow {MAX_COMMANDS} more \
bot {plural('command', MAX_COMMANDS)}, use the -b flag."""
            )

        return self.messages[-1].content

    def And(
        self,
        messages: str
        | dict
        | WigliMessage
        | Iterable[WigliMessage | dict]
        | WigliInjection
        or WigliCommand,
        role: str = "system",
    ) -> "CommandBot":
        if (
            isinstance(messages, dict)
            and messages.get("parse_function", None) is not None
            and messages.get("injection_messages", None)
            is not None
        ):
            messages = WigliCommand(
                messages, messages.get("injection_messages", [])
            )
        if isinstance(messages, WigliCommand):
            if messages not in self.active_cmds:
                super().And(messages)
            self.active_cmds |= {messages}
        elif messages is not None:
            super().And(messages)
        return self
