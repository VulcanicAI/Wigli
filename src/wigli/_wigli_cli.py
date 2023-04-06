# wigli _wigli_cli.py

from jsonpickle import decode
from math import floor
from os.path import join
from sys import version_info, argv
from time import time
from typing import List

from wigli import WigliBot, CommandBot, WigliMessage
from wigli._wigli_argparser import fetch_args
from wigli._wigli_version import VERSION
from wigli._wigli_data import WigliData
from wigli._wigli_tools import clamp

# if version_info < (3, 10):
#     from importlib_metadata import entry_points
# else:
#     from importlib.metadata import entry_points

from wigli._wigli_plugins import (
    Doctest,
    HistoryProfessor,
    PythonBot,
    SearchBot,
)


def wigli_cli(
    argv_: List[str] | None = argv[1:],
    data_dir: str | None = None,
    verbosity: int = 0,
):
    """
    This is the main entry point to the program from the
    command-line. It uses sys.argv to create and run an instance of
    WigliInvocation in accordance with the user's command-line arguments.
    """

    invocation = WigliInvocation(
        argv_, data_dir=data_dir, verbosity=verbosity
    )
    if invocation.prompt is None:
        return

    invocation.log("Starting chat")
    invocation.Chat()


class WigliInvocation(object):
    def __init__(
        self,
        argv: List[str],
        data_dir: str | None = None,
        verbosity: int = 0,
    ):
        self.archive = None
        self._timestamp = time()

        self.data = WigliData(
            self._get_timestamp,
            data_dir=data_dir,
            verbosity=verbosity,
        )

        self.log = self.data.log
        self.log("Hello, logger!")
        self.bot = None
        self.argv = argv
        self.args = fetch_args(argv)
        self.prompt = self._handle_args()
        self.log(f"fetched args for argv: {argv}")

    def Chat(self) -> str:
        return self.bot.Chat(self.prompt)

    def _get_timestamp(self):
        return self._timestamp

    def _bot_from_args(self) -> str:
        injection = []

        if self.args.system is not None:
            injection = [
                WigliMessage(self.args.system, "system")
            ] + injection

        if self.bot is None:
            self.bot = WigliBot(data=self.data)

        if self.args.professor:
            self.log("Summoning Professor Wigli", v=0)
            self.bot = HistoryProfessor.FromBot(self.bot)

        if self.args.python:
            self.log("Injecting Python capabilities", v=0)
            self.bot = PythonBot.FromBot(self.bot)

        if self.args.search:
            self.log("Injecting web search capabilities", v=0)
            self.bot = SearchBot.FromBot(self.bot)

        self.bot.Inject(injection)

        return self.args.prompt

    def _handle_args(self):
        """
        Handles args and modifies the state of this instance accordingly.
        """

        self.data.verbosity = self.args.verbosity

        if self.args.version:
            print(f"You are using Wigli v{VERSION}")
            return
    
        if self.args.set_api_key is not None:
            with open(join(self.data.data_dir, ".env"), "w") as f:
                f.write(
                    f"""\
# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.
OPENAI_API_KEY={self.args.set_api_key}
"""
                )
            self.log(f"Saved API key at {join(self.data.data_dir, '.env')}", v=0)
            return
        
        # if self.args.list_installed_plugins:
        #     discovered_plugins = entry_points(group='wigli._wigli_plugins')
        #     for discovered_plugin in discovered_plugins:
        #         print(f"    {discovered_plugin}")
        #     return

        # List previous chats
        if self.args.list:  # or self.args.transcriptbrief:
            self.log(
                "self.args.list was True, printing history then exiting"
            )
            self.data.print_chat_history_oneline()
            return

        # Load previous chat
        self.bot = None
        if not self.args.clean:
            self.bot = self._load_chat()
            if isinstance(self.bot, WigliBot):
                self.log(
                    f"""
Loaded previous chat: {getattr(self.bot, "title", "No title")}""",
                )
                self.bot.data = self.data
                self.bot.log = self.data.log
                if self.args.erase is not None:
                    self.bot.erase_messages(self.args.erase)
            else:
                self.bot = None

        # Now everything is initialized

        # No chat, just print transcripts
        if self.args.transcript_full:
            self.log("Printing transcript then exiting")
            if self.bot is not None:
                print(self.bot.format_transcript())
            else:
                print("No chat for which to print transcript")
            return

        # Parse the last message for commands and prompt
        if self.args.botcommands and isinstance(
            self.bot, CommandBot
        ):
            self.log(
                "Parsing last message for commands, then reprompting with output"
            )
            self.bot.Chat(nochat=True)
            return

        # # # if self.args.audio:
        # # #     if self.args.fileprompt:
        # # #         print("Loading audio prompt from file")
        # # #     else:
        # # #         self.args.prompt = record_prompt()
        # # #     prompt = ""
        # # #     with open(self.args.prompt, "rb") as f:
        # # #         prompt = Audio.transcribe("whisper-1", f).text
        # # #     self.args.prompt = prompt
        # # #     if self.args.prompt != "":
        # # #         print(f"Heard:\n{self.args.prompt}")
        # # # elif self.args.fileprompt:  # Load prompt from file

        if self.args.fileprompt:  # Load prompt from file
            filepath = self.args.prompt
            self.args.prompt = ""
            with open(filepath) as f:
                self.log(
                    ("Reading text prompt from file:", filepath)
                )
                self.args.prompt = f.read()

        # Treat the prompt as code, invoke the headless doctest bot, don't prompt
        if self.args.doctest:
            self.log(
                "Invoking the headless DocTest bot on the following code:\n\n{self.args.prompt}"
            )
            self.log(Doctest(self.args.prompt), v=0)
            return

        prompt = self._bot_from_args()

        if self.bot is None:
            self.log(
                "No previous chat to load, starting a new one"
            )
            self.bot = WigliBot(data=self.data)

        # Parse the last message for commands and don't prompt
        if self.args.usercommands and isinstance(
            self.bot, CommandBot
        ):
            self.log(
                "Parsing last message for commands, then exiting"
            )
            self.bot.Chat(
                self.args.prompt, nochat=True, reprompt=False
            )
            return

        return prompt

    def _load_chat(self):
        """
        Searches the archive for a valid chat
        to load based on the arguments provided

        Returns
        -------
        dict
            The dict object that was loaded, or None
        """
        logs = self.data.list_chats()

        if len(logs) == 0:
            return

        if self.args.resume_last:
            # Load the previous conversation
            with open(
                join(
                    self.data.convos_dir,
                    logs[len(logs) - 1],
                )
            ) as f:
                return decode(f.read())

        if self.args.index is not None:
            # Load a previous conversation by reverse chronological index
            self.args.index = clamp(
                self.args.index, 1, len(logs)
            )
            with open(
                join(
                    self.data.convos_dir,
                    logs[len(logs) - self.args.index],
                )
            ) as f:
                return decode(f.read())

        if self.args.time is not None:
            # Load a previous conversation by timestamp
            files = [
                log for log in logs if self.args.time in log
            ]
            if len(files) > 0:
                with open(
                    join(
                        self.data.convos_dir,
                        files[len(files) - 1],
                    )
                ) as f:
                    return decode(f.read())

        if self.args.title is not None:
            # Load a previous conversation by title
            files = [
                log
                for log in logs
                if self.args.title.replace(" ", "").lower()
                in log.replace("_", "").lower()
            ]
            if len(files) > 0:
                with open(
                    join(
                        self.data.convos_dir,
                        files[len(files) - 1],
                    )
                ) as f:
                    return decode(f.read())

        # Check for chat in the last 5 minutes
        max_timestamp = floor(float(logs[0].split("_")[1]))
        max_index = 0
        for i in range(1, len(logs)):
            timestamp = floor(float(logs[i].split("_")[1]))
            if timestamp > max_timestamp:
                max_timestamp = timestamp
                max_index = i

        if self._timestamp - max_timestamp < 300:
            # Time since chat is fewer than 5 minutes
            with open(
                join(self.data.convos_dir, logs[max_index])
            ) as f:
                return decode(f.read())
