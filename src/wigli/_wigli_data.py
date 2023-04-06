# wigli _wigli_data.py

from appdirs import user_data_dir
from jsonpickle import encode, decode
from os.path import abspath, join
from time import time
from typing import Callable

from wigli import WigliBot, OneShotBot

from wigli._wigli_tools import (
    list_dir,
    make_dir,
    remove_file,
)


class WigliData(object):
    """
    This class handles chat data for a WigliInvocation and its WigliBots.

    Attributes
    ----------
    get_time: Callable
        WigliData uses this callback function to name its log files.
    data_dir: str
        The directory for loading and saving chat history.
    convos_dir: str
        Beneath data_dir, stores full JSON chat history and data files.
    scripts_dir: str
        Beneath data_dir, stores pretty human-readable transcripts of chats.
    logs_dir: str
        Beneath data_dir, stores event log files.
    verbosity: int, optional
        Level of verbosity at which to log events.

    Methods
    -------
    __init__()
        Sets up the user data directory.
    list_chats()
        Returns all files in the
    print_chat_history_oneline()
        Prints a numbered list of conversations in the archive.
    log()
        Event logger with a range of verbosities.
        Always log to file and sometimes log to console too.
    """

    def __init__(
        self,
        get_time: Callable,
        data_dir: str | None = None,
        verbosity: int = 0,
    ):
        """
        Sets up the user data directory.

        Parameters
        ----------
        get_time: Callable
            WigliData uses this callback function to name its log files.
        data_dir: str, optional
            The directory for loading and saving chat history (defaults to appdirs.user_data_dir).
        verbosity: int, optional
            Level of verbosity at which to log events.
        """

        self.get_time = get_time
        self.verbosity = verbosity
        if data_dir is not None:
            self.data_dir = data_dir
        else:
            self.data_dir = user_data_dir(
                appname="Wigli", appauthor="VulcanicAI"
            )

        self.convos_dir = join(self.data_dir, "Wigli Files")
        self.scripts_dir = join(self.data_dir, "Pretty Chats")
        self.logs_dir = join(self.data_dir, "Debug Logs")

        make_dir(self.data_dir)
        make_dir(self.convos_dir)
        make_dir(self.scripts_dir)
        make_dir(self.logs_dir)

    def list_chats(self, suffix=".json"):
        """
        Returns a list of all chats in the archive.

        Parameters
        ----------
        suffix: str
            The pattern to filter by when listing the files.

        Returns
        -------
        list
            A list of all the files in the Wigli
            Data directory, in chronological order
            (because the filenames start with their touchstamps)
        """
        return sorted(
            [
                log
                for log in list_dir(self.convos_dir)
                if suffix in log
            ]
        )

    def print_chat_history_oneline(self, begin=0, end=None):
        """
        Prints a numbered list of conversations in the archive.

        Parameters
        ----------
        begin: int
            How many recent chats to skip.
        end: int
            How far back to go.
        """

        logs = self.list_chats()

        if end is None:
            end = len(logs)

        for n in range(end, begin, -1):
            with open(
                join(
                    self.convos_dir,
                    logs[len(logs) - n],
                )
            ) as json_file:
                chat = decode(json_file.read())
                if len(getattr(chat, "messages", [])) > 0:
                    print(
                        f"{n}: {getattr(chat, 'title', 'No Title')}\n",
                        sep="",
                        end="",
                    )

    def archive_chat(self, bot: WigliBot):
        if len(bot.messages) <= 0:
            return

        old_filename = bot.filename
        overwrite = False
        if old_filename is not None:
            with open(
                join(
                    self.convos_dir,
                    "chat_" + old_filename + ".json",
                )
            ) as f:
                old_archive = decode(f.read())
                assert isinstance(old_archive, WigliBot)
                if old_archive.birthstamp == bot.birthstamp:
                    overwrite = True

        bot.touchstamp = time()
        self.write_files(bot)
        if overwrite:
            remove_file(
                join(
                    self.convos_dir,
                    "chat_" + old_filename + ".json",
                )
            )
            remove_file(
                join(
                    self.scripts_dir,
                    "transcript_" + old_filename + ".md",
                )
            )

    def open_file(
        self, filepath, open_type="r", encoding="utf-16"
    ):
        try:
            return open(filepath, open_type, encoding=encoding)
        except BaseException:
            self.log(("Couldn't open file:", filepath))
            pass

    def title_transcript(self, transcript):
        injection_transcript_titler_bot = [
            {
                "role": "system",
                "content": """\
You are an expert at summarizing the purpose of a conversation in just a few words. The user will ask you to summarize a conversation and give you the transcript. You will only use about two to four words but the core themes of the conversation will be clearly communicated. If you understand, please respond with a summary of this conversation we are having in the style of these summaries. The next message will be the user's transcript.""",
            },
            {
                "role": "assistant",
                "content": "Titling Transcripts",
            },
            {
                "role": "user",
                "content": f"""\
Here is the transcript I would like you to title. Please just respond with the most concise title and nothing else.\n\n{transcript}""",
            },
        ]

        return OneShotBot(
            messages=injection_transcript_titler_bot,
        )

    def write_files(self, bot: WigliBot):
        script = bot.format_transcript_markdown()
        if bot.title is None:
            self.log("Auto-titling transcript")
            bot.title = self.title_transcript(script)
            self.log(("Auto-titled:", bot.title))
        bot.make_filename()
        json_filename = "chat_" + bot.filename + ".json"
        json_filepath = join(self.convos_dir, json_filename)
        abspath_json_filepath = abspath(json_filepath)
        with open(
            abspath_json_filepath,
            "w",
        ) as f:
            self.log(
                (
                    "Saving chat JSON file at",
                    abspath_json_filepath,
                )
            )
            f.write(encode(bot, f, indent=4))
        txt_filename = "transcript_" + bot.filename + ".md"
        txt_filepath = join(self.scripts_dir, txt_filename)
        with self.open_file(txt_filepath, open_type="w") as f:
            self.log(
                ("Saving transcript text file at", txt_filepath)
            )
            try:
                f.writelines([script])
            except BaseException:
                with self.open_file(
                    txt_filepath,
                    open_type="w",
                    encoding="utf-32",
                ) as f:
                    try:
                        f.writelines([script])
                    except BaseException:
                        self.log(
                            (
                                "Failed to write script: \n",
                                script,
                            ),
                            sep="",
                        )
                        pass
                pass

    def log(self, s, end="\n", sep=" ", v=3):
        """
        Event logger with a range of verbosities.
        Always log to file and sometimes log to console too.

        Parameters
        ----------
        s: str
            The message to log.
        end: str, optional
            What to end the string with.
        sep: str, optional
            What to separate tokens in the tuple with, if applicable.
        v: int, optional
            The level of verbosity of this message.
        """

        if type(s) == tuple:
            s = "".join([str(f) + sep for f in s])
        elif type(s) != str:
            s = str(s)

        s += end

        prefix = ""
        if v == 1:
            prefix = "LOG: "
        if v == 2:
            prefix = "Log: "
        if v == 3:
            prefix = "log: "

        # log = "LOG: "[: -v - 2] + "log: "[-v - 2 :]
        s = prefix + s

        if v <= self.verbosity:
            print(s, end="")
        with open(
            join(
                self.logs_dir,
                "log_" + str(self.get_time()) + ".log",
            ),
            "a",
        ) as f:
            f.write(s)
