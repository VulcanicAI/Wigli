# wigli _wigli_tools.py

from bs4 import BeautifulSoup
from os import listdir, makedirs, remove
from os.path import exists, splitext
from shutil import copy2
from tiktoken import get_encoding, encoding_for_model
from time import localtime, strftime
from typing import Iterable
from urllib3 import PoolManager


def backup_file(filepath: str) -> None:
    backup_path = (
        f"{splitext(filepath)[0]}_backup{splitext(filepath)[1]}"
    )
    copy2(filepath, backup_path)


def restore_file(filepath: str) -> None:
    backup_path = (
        f"{splitext(filepath)[0]}_backup{splitext(filepath)[1]}"
    )
    copy2(backup_path, filepath)
    remove_file(backup_path)


def format_timestamp(timestamp):
    return strftime(
        "[%A, %m-%d-%Y, %H:%M:%S]", localtime(timestamp)
    )


def clamp(a, b, c):
    if a < b:
        return b
    if a > c:
        return c
    return a


def list_dir(dir):
    if not exists(dir):
        return []
    return listdir(dir)


def make_dir(dir):
    makedirs(dir, exist_ok=True)


def remove_file(file):
    if exists(file):
        remove(file)


def contains_any(list, any):
    return len([f for f in any if f in list]) > 0


def contains_all(list, all):
    return len([f for f in all if f in list]) == len(all)


def is_char(subject):
    return type(subject) is str and len(subject) == 1


def is_upper(char):
    if not is_char(char):
        return False
    return char >= "A" and char <= "Z"


def is_lower(char):
    if not is_char(char):
        return False
    return char >= "a" and char <= "z"


def alternating_caps(
    word: str, is_first_char_lower: bool = True
) -> str:
    """
    Alternates the case of each character in the input word beginning
    with a lowercase or uppercase letter as specified.

    Parameters
    ----------
    word: str
        The word whose case we want to alternate.
    is_first_char_lower: bool
        Whether the first character in the original word is lowercase or
        uppercase. Default is True (first character is lowercase).

    Returns
    -------
    str
        The input word with alternating case beginning with a lowercase
        or uppercase letter as specified.
    """
    if not isinstance(word, str):
        raise TypeError("word must be a string")
    new_word = ""
    for ch in word:
        if is_first_char_lower:
            new_word += ch.lower()
        else:
            new_word += ch.upper()
        is_first_char_lower = not is_first_char_lower
    return new_word


# def pytest_alternating_caps():
#     # Test working - all lowercase
#     assert alternating_caps("hello world") == "hElLo wOrLd"
#     # Test working - all uppercase
#     assert alternating_caps("HELLO WORLD", False) == "HeLlO WoRlD"
#     # Test non-string input
#     with raises(TypeError):
#         alternating_caps(100, True)

# # Append testing function to testing suite
# pytest_functions.append(pytest_alternating_caps)


def similar_capitalization(word_to_modify, word_to_emulate):
    # Check for all-lowercase
    if word_to_emulate == word_to_emulate.lower():
        return word_to_modify.lower()

    # Check for all-caps
    if word_to_emulate == word_to_emulate.upper():
        return word_to_modify.upper()

    # Check for alternating caps
    has_alternating_caps = True
    was_last_char_lower = was_first_char_lower = is_lower(
        word_to_emulate[0]
    )
    for char in word_to_emulate[1:]:
        if is_lower(char) == was_last_char_lower:
            has_alternating_caps = False
            break
        was_last_char_lower = not was_last_char_lower
    if has_alternating_caps:
        return alternating_caps(
            word_to_modify,
            is_first_char_lower=was_first_char_lower,
        )

    # Match capitalization
    new_word = ""
    for n in range(len(word_to_modify)):
        if n >= len(word_to_emulate):
            new_word += word_to_modify[n:]
            break
        char_to_modify = word_to_modify[n]
        char_to_emulate = word_to_emulate[n]
        if char_to_modify.lower() != char_to_emulate.lower():
            new_word += word_to_modify[n:]
            break  # The words' spellings have diverged

        new_word += char_to_emulate  # word_to_emulate[n]

    return new_word


weird_pluralizations = {
    "octopus": "octopi",
    "child": "children",
}


def pluralize(word):
    if len(word) < 1:
        return word

    if word.lower() in weird_pluralizations.keys():
        pluralized_word = weird_pluralizations[word.lower()]
    elif word[-1].lower() == "s":
        pluralized_word = word + "es"
    elif word[-1].lower() == "y":
        pluralized_word = word[:-1] + "ies"
    else:
        pluralized_word = word + "s"

    pluralized_word = pluralized_word.lower()

    return similar_capitalization(pluralized_word, word)


def plural(word, num, plural=None):
    if num == 1:
        return word
    if plural is not None:
        return plural
    return pluralize(word)


def scrape_html_text(url):
    http = PoolManager()
    try:
        response = http.request("GET", url)
        soup = BeautifulSoup(
            response.data,
            "html.parser",
        )
        return soup.get_text()
    except BaseException:
        return "Error parsing URL\n"


def count_tokens(messages, model="gpt-3.5-turbo-0301"):
    if isinstance(messages, str):
        messages = [
            {
                "role": "user",
                "content": messages,
            }
        ]
    if not isinstance(messages, Iterable):
        return 0
    try:
        encoding = encoding_for_model(model)
    except KeyError:
        encoding = get_encoding("cl100k_base")
    if (
        model == "gpt-3.5-turbo-0301"
        or model == "gpt-3.5-turbo"
    ):
        num_tokens = 0
        for message in messages:
            num_tokens += (
                4  # Every message follows {role/name}{content}
            )
            for (
                key,
                value,
            ) in message.items():
                num_tokens += len(encoding.encode(value))
                if (
                    key == "name"
                ):  # If there's a name, the role is omitted
                    num_tokens += (
                        -1
                    )  # Role is always required and always 1 token
        num_tokens += 2  # Every reply is primed with assistant
        return num_tokens
    else:
        raise NotImplementedError(
            f"""\
num_tokens_from_messages() is not presently implemented for model {model}. \
See https://github.com/openai/openai-python/blob/main/chatml.md \
for information on how messages are converted to tokens."""
        )
