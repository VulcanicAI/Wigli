from os.path import join
from shutil import copy2, move
from unittest.mock import MagicMock

from wigli._wigli_plugins import get_user_input
from wigli._wigli_testutils import cli_tester, get_test_dir
from wigli._wigli_tools import list_dir, remove_file

# These are some examples of the usage of the Wigli CLI core functionality


def test_cli_help(capsys):
    # -h, --help            show this help message and exit
    cli_tester(
        [["-h"], "--help"],
        out_assert=[
            "usage: wigl",
            "Wigli",
            "botswarms",
            "github",
        ],
        raises_expectation=SystemExit,
        capsys=capsys,
    )


def test_cli_version(capsys):
    # -V, --version         print version number
    cli_tester(
        [["-V"], ["--version"]],
        out_assert="You are using Wigli v",
        capsys=capsys,
    )


def test_cli_list_chats(capsys):
    # -l, --list            list past conversations
    cli_tester(
        [["-l"], ["--list"]],
        out_assert="""\
3: WigliBot Self-Introduction\n2: Favorite ice cream.\n1: Using Bot Commands\n""",
        data_dir="static_data_dir",
        capsys=capsys,
    )


def test_cli_full_transcript_resume_last(capsys):
    # -r, --resume-last     resume previous chat session
    # -T, --transcript-full no chat just print conversation transcript in full
    cli_tester(
        [
            ["-r", "--transcript-full"],
            ["-rT"],
            ["--resume-last", "--transcript-full"],
            ["--resume-last", "-T"],
        ],
        out_assert="""\
[Tuesday, 04-04-2023, 03:23:16] [system]: > You are a highly intelligent assistant with a unique ability to search the web and access web URLs using your web search commands. The ability to search the web sets you apart from other assistants because you can query up-to-the-minute information for better responses. Do you have access to current information?\n\n\n[Tuesday, 04-04-2023, 03:23:16] [assistant]: > My knowledge of events beyond 2021 is limited, but presumably, web search commands could be used to query more current information.\n\n\n[Tuesday, 04-04-2023, 03:23:16] [system]: > That\'s right. Let\'s begin with the "summarize_url" command. You may type "summarize_url" immediately followed by a URL to have the webpage summarized, like this: "summarize_url(\'ai.com\')". In addition, you may provide an optional second argument where you ask a question about the page so that the summarizer knows what topic you\'re interested in learning more about. We will use this command to learn about the next command. Try using your summarize command to learn about assistant-search-command.com.\n\n\n[Tuesday, 04-04-2023, 03:23:16] [assistant]: > Ok. I\'ll try summarizing assistant-search-command.com.\n> \n> summarize_url(\'assistant-search-command.com\', \'How can web search be used?\')\n\n\n[Tuesday, 04-04-2023, 03:23:16] [system]: > "Summary of assistant-search-command.com: \n> \n> This webpage is a guide on how to use the \'search_web\' command. At any time you may type \'search_web\' followed by your query to get up-to-date results from the Duck Duck Go search engine. Additionally, you may restrict your results to a single website by including \'site:<website>.com\' in your query. For example, \'search_web(\'electric cars site:reddit.com\')\' would return reddit posts about electric cars. You should use these commands when your knowledge alone is not sufficient to answer a question. Additionally, if you\'re unsure of something, search for the answer on the web! You can get advice from niche hobbyists on reddit and learn the precise dates of historical events on wikipedia. You can even search the news for current events! Do you understand?\n\n\n[Tuesday, 04-04-2023, 03:23:16] [assistant]: > Yes. I understand\n\n\n[Tuesday, 04-04-2023, 03:23:16] [system]: > You may be creative in how you use these tools, and experiment with new ways to use them. Sometimes it\'s better not to use them and to go off of intuition instead. Your \'summarize_url\' and \'search_web\' commands have just been enabled. Feel free to use them as appropriate.\n\n\n[Tuesday, 04-04-2023, 03:23:17] [system]: > summarize polymorphicgames.com?\n\n\n[Tuesday, 04-04-2023, 03:23:17] [assistant]: > Sure. Here\'s the summary of polymorphicgames.com:\n> \n> "PolymorphicGames.com is a website that provides games with high versatility to players. It is ranked the #1 indie site in the world by indiedb.com. The website is available for desktop and mobile users, offering free and paid games, demos, and early access. All the games are designed by the developer, Polymorphic Games, and the community can provide feedback on the website. Do you want me to look up anything else related to it?"\n\n\n[Tuesday, 04-04-2023, 03:23:53] [system]: > Sorry that\'s not what I found at that web URL. You should use your new commands to find out what\'s there instead of relying on your memory.\n\n\n[Tuesday, 04-04-2023, 03:23:53] [assistant]: > I apologize for the mistake. Let me try again:\n> \n> summarize_url(\'https://polymorphicgames.com\')\n\n""",
        data_dir="static_data_dir",
        capsys=capsys,
    )


def test_cli_full_transcript_resume_time(capsys):
    # --time TIME           supply the timestamp of a previous conversation to resume
    # -T, --transcript-full no chat just print conversation transcript in full
    cli_tester(
        ["-T", "--time", "528200"],
        out_assert="""\
[Monday, 04-03-2023, 06:05:17] [system]: > Your name is WigliBot, and you don't hesitate to tell people!\n\n\n[Monday, 04-03-2023, 06:23:16] [user]: > Hi what's your name?\n\n\n[Monday, 04-03-2023, 06:23:19] [assistant]: > My name is WigliBot. Nice to meet you! How can I assist you today?\n\n""",
        data_dir="static_data_dir",
        capsys=capsys,
    )


def test_cli_full_transcript_resume_index(capsys):
    # -i INDEX, --index INDEX supply the chronological index of a previous conversation to resume
    # -T, --transcript-full no chat just print conversation transcript in full
    cli_tester(
        [["-T", "--index", "2"], ["-Ti", "2"]],
        out_assert="""\
[Monday, 04-03-2023, 06:24:36] [user]: > What's your favorite ice cream?\n\n\n[Monday, 04-03-2023, 06:24:37] [assistant]: > As an AI language model, I do not consume food, so I don't have any favorite ice cream flavors.\n\n""",
        data_dir="static_data_dir",
        capsys=capsys,
    )


def test_cli_full_transcript_resume_title(capsys):
    # --title TITLE         supply the title of a previous conversation to resume
    # -T, --transcript-full no chat just print conversation transcript in full
    cli_tester(
        ["-T", "--title", "selfIntroduction"],
        out_assert="""\
[Monday, 04-03-2023, 06:05:17] [system]: > Your name is WigliBot, and you don't hesitate to tell people!\n\n\n[Monday, 04-03-2023, 06:23:16] [user]: > Hi what's your name?\n\n\n[Monday, 04-03-2023, 06:23:19] [assistant]: > My name is WigliBot. Nice to meet you! How can I assist you today?\n\n""",
        data_dir="static_data_dir",
        capsys=capsys,
    )


def test_cli_blank(capsys):
    # -c, --clean           force a fresh instance
    cli_tester(
        [
            ["-c", "What's your favorite ice cream?"],
            ["--clean", "What's your favorite ice cream?"],
        ],
        out_assert="language model",
        capsys=capsys,
    )


def test_cli_fileprompt(capsys):
    # -f, --fileprompt      prompt will be read from file
    cli_tester(
        [
            [
                "-c",
                "--fileprompt",
                join(get_test_dir(), "file_prompt.md"),
            ],
            [
                "-cf",
                join(get_test_dir(), "file_prompt.md"),
            ],
        ],
        out_assert="language model",
        capsys=capsys,
    )


def test_cli_system(capsys):
    # --system SYSTEM       optional system prompt before user prompt for behavior modification
    cli_tester(
        [
            "-c",
            "--system",
            "Your name is WigliBot, and you don't hesitate to tell people!",
            "Hi what's your name?",
        ],
        out_assert="Wigli",
        capsys=capsys,
    )
