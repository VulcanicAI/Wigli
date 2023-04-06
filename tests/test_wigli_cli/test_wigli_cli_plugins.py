from os.path import join
from shutil import copy2, move
from unittest.mock import MagicMock

from wigli._wigli_plugins import get_user_input
from wigli._wigli_testutils import cli_tester, get_test_dir
from wigli._wigli_tools import list_dir, remove_file

# These are some examples of the usage of the Wigli CLI with plugins


def test_cli_doctest(capsys):
    # --doctest             interpret prompt as a Python function and invoke the headless DocTest bot
    cli_tester(
        [
            "-cf",
            "--doctest",
            join(get_test_dir(), "doctest_prompt.py"),
        ],
        out_assert=[
            "def divide_vector_by_scalar",
            "raises",
            "ZeroDivisionError",
        ],
        capsys=capsys,
    )


def test_cli_professor(capsys):
    # -P, --professor       summon the professor
    cli_tester(
        [
            [
                "-Pc",
                "Good morning! What did you do your dissertation on?",
            ],
            [
                "-c",
                "--professor",
                "Good morning! What did you do your dissertation on?",
            ],
        ],
        out_assert=lambda s: len(
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
                if f in s
            ]
        )
        >= 4,
        capsys=capsys,
    )


def test_cli_professor_wigli(capsys):
    # -P, --professor       summon the professor
    cli_tester(
        [
            [
                "-cP",
                "--system",
                "Your name is Professor Wigli",
                "Good morning! What is your name? And what did you do your dissertation on?",
            ],
            [
                "-c",
                "--professor",
                "--system",
                "Your name is Professor Wigli",
                "Good morning! What is your name? And what did you do your dissertation on?",
            ],
        ],
        out_assert=["professor", "Wigli"],
        capsys=capsys,
    )


def test_cli_noprompt(capsys):
    # -m, --noprompt        just complete the next chat based on the conversation history
    cli_tester(
        [
            [
                "-cm",
                "--system",
                "What's the best flavor of soda?",
            ],
            [
                "-c",
                "--noprompt",
                "--system",
                "What's the best flavor of soda?",
            ],
        ],
        out_assert="language model",
        capsys=capsys,
    )


def test_cli_python_wiglibot(capsys, monkeypatch):
    # -x, --python          enable python interpreter

    # Mock get_user_input to return 'y' to allow execution
    monkeypatch.setattr(
        "wigli._wigli_plugins.get_user_input", lambda _: "y"
    )

    cli_tester(
        [
            [
                "-cx",
                "--system",
                "Your name is WigliBot and you don't hesitate to tell people your name, which is WigliBot!",
                "Please verify that your Python interpreter is still working by printing your name with Python.",
            ],
            [
                "-c",
                "--python",
                "--system",
                "Your name is WigliBot and you don't hesitate to tell people your name, which is WigliBot!",
                "Please verify that your Python interpreter is still working by printing your name with Python.",
            ],
        ],
        out_assert=["print(", "Wigli"],
        capsys=capsys,
    )

    # Test other scenarios by updating the lambda function for get_user_input and mock_run attributes


def test_cli_web_search(capsys):
    # -s, --search          enable assistant to use search commands
    cli_tester(
        [
            [
                "-c",
                "--search",
                "Please search for showtimes for 'Avatar 2: The Way of Water'",
            ],
            [
                "-cs",
                "Please search for showtimes for 'Avatar 2: The Way of Water'",
            ],
        ],
        out_assert=["search_web(", "avatar"],
        capsys=capsys,
    )


def test_cli_summarize_url(capsys):
    # -s, --search          enable assistant to use search commands
    cli_tester(
        [
            [
                "-c",
                "--search",
                "Please use your summarize_url command to learn more about polymorphicgames.com",
            ],
            [
                "-cs",
                "Please use your summarize_url command to learn more about polymorphicgames.com",
            ],
        ],
        out_assert=lambda s: "evolution" in s or "evolve" in s,
        capsys=capsys,
    )


def test_cli_summarizeurl_usercommands(capsys):
    # -u, --usercommands    No chat, just parse the last message for commands
    cli_tester(
        [
            [
                "-vvvcsu",
                "summarize_url('polymorphicgames.com')",
            ],
            [
                "-vvvcs",
                "--usercommands",
                "summarize_url('polymorphicgames.com')",
            ],
        ],
        out_assert=lambda s: "evolution" in s or "evolve" in s,
        capsys=capsys,
    )


def test_cli_summarizeurl_botcommands(capsys):
    # -b, --botcommands     parse the last message for bot commands first

    path = join(
        get_test_dir(), "static_data_dir", "Wigli Files"
    )
    files = list_dir(path)
    file = list(
        [
            f
            for f in files
            if "Bot_Commands" in f and ".json" in f
        ]
    )[0]
    origfilepath = join(path, file)
    tempfilepath = origfilepath[:-5]
    copy2(origfilepath, tempfilepath)

    cli_tester(
        [
            "-sb",
            "--title",
            "botcommand",
        ],
        out_assert=lambda s: "evolution" in s or "evolve" in s,
        data_dir="static_data_dir",
        capsys=capsys,
    )

    files = list_dir(path)
    file = list(
        [
            f
            for f in files
            if "Bot_Commands" in f and ".json" in f
        ]
    )[0]
    filepath = join(path, file)
    remove_file(filepath)
    copy2(tempfilepath, origfilepath)

    cli_tester(
        [
            "-s",
            "--title",
            "botcommand",
            "--botcommands",
        ],
        out_assert=lambda s: "evolution" in s or "evolve" in s,
        data_dir="static_data_dir",
        capsys=capsys,
    )

    files = list_dir(path)
    file = list(
        [
            f
            for f in files
            if "Bot_Commands" in f and ".json" in f
        ]
    )[0]
    filepath = join(path, file)
    remove_file(filepath)
    move(tempfilepath, origfilepath)


# def test_cli_erase(capsys):
#     # -e ERASE, --erase ERASE erase a given number of messages from the conversation history

#     path = join(
#         get_test_dir(), "static_data_dir", "Wigli Files"
#     )
#     files = list_dir(path)
#     file = list(
#         [
#             f
#             for f in files
#             if "Erase_Files" in f and ".json" in f
#         ]
#     )[0]
#     origfilepath = join(path, file)
#     tempfilepath = origfilepath[:-5]
#     copy2(origfilepath, tempfilepath)

#     cli_tester(
#         [
#             "-e",
#             "--title",
#             "erase",
#             "botcommand",
#         ],
#         out_assert=lambda s: "evolution" in s or "evolve" in s,
#         data_dir="static_data_dir",
#         capsys=capsys,
#     )

#     files = list_dir(path)
#     file = list(
#         [
#             f
#             for f in files
#             if "Bot_Commands" in f and ".json" in f
#         ]
#     )[0]
#     filepath = join(path, file)
#     remove_file(filepath)
#     copy2(tempfilepath, origfilepath)

#     cli_tester(
#         [
#             "-s",
#             "--title",
#             "botcommand",
#             "--botcommands",
#         ],
#         out_assert=lambda s: "evolution" in s or "evolve" in s,
#         data_dir="static_data_dir",
#         capsys=capsys,
#     )

#     files = list_dir(path)
#     file = list(
#         [
#             f
#             for f in files
#             if "Bot_Commands" in f and ".json" in f
#         ]
#     )[0]
#     filepath = join(path, file)
#     remove_file(filepath)
#     move(tempfilepath, origfilepath)


# -v, --verbosity       verbosity with which to print logs, cumulative up to 3
