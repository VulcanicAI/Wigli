# wigli _wigli_argparser.py

from argparse import ArgumentParser, RawTextHelpFormatter
from time import time

from wigli._wigli_tools import contains_any, format_timestamp
from wigli._wigli_version import VERSION

MAX_VERBOSITY = 3


def contains_any_flagargs(list, flags):
    for f in list:
        if f[0] == "-" and f[1] != "-":
            for flag in flags:
                if flag[1:] in f:
                    return True
    return False


def fetch_args(argv):
    no_prompt_args = [
        "--noprompt",
        # "--transcript",
        "--transcript-full",
        "--list",
        "--list-installed-plugins",
        "--list-plugins",
        "--version",
        "--botcommands",
        "--set-api-key",
        # "--audio",
    ]
    no_prompt_flags = [
        "-m",
        # "-t",
        "-T",
        "-l",
        "-V",
        "-b",
        "-L",
        "-K",
        # "-a",
    ]

    parser = ArgumentParser(
        prog="wigli",
        description=f"""\
      )  (              Wigli v{VERSION} - {format_timestamp(time())} its like ChatGPT but better!
     (   ) )
   (     (    )         Wigli is an extensible open source framework and CLI
 (____(___)_____)___    designed to support the development of SDX chatbots,
 |              |---\\\\  datamining botswarms, and other bleeding-edge AI tools.
 |              |    ||
 |              |___//  Wigli can already use DuckDuckGo, URL summarization and
  \            /----'   Python programming to better assist the user, with Voice
   \          /         and WebUI coming soon. Your chat history is saved locally,
    \________/          and you can use your own OpenAI API key. Happy chatting!""",
        epilog="""\
You can contribute new injections and extensions for Wigli!
Visit https://github.com/VulcanicAI/Wigli to learn more.
""",
        # conflict_handler="resolve",
        formatter_class=RawTextHelpFormatter,
    )

    parser_parse_cmds = parser.add_mutually_exclusive_group()
    parser_resume = parser.add_mutually_exclusive_group()

    if (
        "--fileprompt" in argv
        or contains_any_flagargs(argv, ["-f"])
        or not (
            contains_any(argv, no_prompt_args)
            or contains_any_flagargs(argv, no_prompt_flags)
        )
    ):
        parser.add_argument(  # Only require prompt if necessary
            "prompt",
            type=str,
            default="",
            help="the prompt to submit",
        )
    else:
        parser.set_defaults(prompt="")

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help=f"verbosity with which to print logs, cumulative up to {MAX_VERBOSITY}",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help=f"print version number",
    )
    parser.add_argument(
        "-K",
        "--set-api-key",
        metavar="API_KEY",
        type=str,
        help="Create a .env file with your OpenAI API Key to enable ChatGPT access",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list past conversations",
    )
    # parser.add_argument(
    #     "-n",
    #     "--num",
    #     type=int,
    #     default=None,
    #     help="the number of previous conversations to list",
    # )
    # parser.add_argument(
    #     "-p",
    #     "--preview",
    #     type=int,
    #     default=0,
    #     help="how many messages to preview in each list entry",
    # )
    parser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="force a fresh instance",
    )
    parser.add_argument(
        "-s",
        "--search",
        action="store_true",
        help="enable assistant to use search commands",
    )
    parser_resume.add_argument(
        "-r",
        "--resume-last",
        action="store_true",
        help="resume previous chat session",
    )
    parser_resume.add_argument(
        "--time",
        type=str,
        default=None,
        help="supply the timestamp of a previous conversation to resume",
    )
    parser_resume.add_argument(
        "-i",
        "--index",
        type=int,
        default=None,
        help="supply the chronological index of a previous conversation to resume",
    )
    parser_resume.add_argument(
        "--title",
        type=str,
        default=None,
        help="supply the title of a previous conversation to resume",
    )
    # parser.add_argument(
    #     "-t",
    #     "--transcript",
    #     action="store_true",
    #     help="no chat just print conversation transcript with one-line previews",
    # )
    parser.add_argument(
        "-T",
        "--transcript-full",
        action="store_true",
        help="no chat just print conversation transcript in full",
    )
    parser.add_argument(
        "--system",
        type=str,
        help="optional system prompt before user prompt for behavior modification",
    )
    parser.add_argument(
        "-m",
        "--noprompt",
        action="store_true",
        help="just complete the next chat based on the conversation history",
    )
    parser_parse_cmds.add_argument(
        "-b",
        "--botcommands",
        action="store_true",
        help="parse the last message for bot commands first",
    )
    parser_parse_cmds.add_argument(
        "-u",
        "--usercommands",
        action="store_true",
        help="No chat, just parse the last message for commands",
    )
    parser.add_argument(
        "-e",
        "--erase",
        type=int,
        help="erase a given number of messages from the conversation history",
    )
    parser.add_argument(
        "-x",
        "--python",
        action="store_true",
        help="enable python interpreter",
    )
    parser.add_argument(
        "-P",
        "--professor",
        action="store_true",
        help="summon the professor",
    )
    parser.add_argument(
        "-f",
        "--fileprompt",
        action="store_true",
        help="prompt will be read from file",
    )
    # parser.add_argument(
    #     "-D",
    #     "--datadir",
    #     type=str,
    #     help="specify a directory to save and load Wigli chat history",
    # )
    # parser.add_argument(
    #     "-a",
    #     "--audio",
    #     action="store_true",
    #     help="prompt will be transcribed from audio",
    # )
    parser.add_argument(
        "--doctest",
        action="store_true",
        help=f"interpret prompt as a Python function and invoke the headless DocTest bot",
    )
    # parser.add_argument(
    #     "-L",
    #     "--list-installed-plugins",
    #     action="store_true",
    #     help=f"list installed plugins",
    # )
    # parser.add_argument(
    #     "--list-plugins",
    #     action="store_true",
    #     help=f"list available plugins on PyPI",
    # )

    return parser.parse_args(argv)
