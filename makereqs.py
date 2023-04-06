from sys import exit, argv
from os.path import join, split


def main():
    # Read pyproject.toml

    lines = None
    with open("pyproject.toml") as f:
        lines = f.readlines()

    if lines is None:
        return True

    # Parse requirements.txt

    dependencies = []
    with open(
        join(split(argv[0])[0], "requirements.txt")
    ) as reqs_file:
        dependencies = [
            line
            for line in reqs_file.readlines()
            if "==" in line
            and "pytest" not in line
            and "sphinx" not in line
        ]

    # Modify pyproject.toml

    a = None
    for i, line in enumerate(lines):
        if line.startswith("[tool.poetry.dependencies]"):
            a = i
        if line.startswith("[tool.poetry.dev-dependencies]") and a is not None:
            b = i
            break

    if a is None:
        return True

    a += 1 # Skip python = "^3.10"
    b -= 1 # Skip blank line

    result = lines[: a + 1]
    for dependency in dependencies:
        tokens = dependency.split("==")
        result += [
            f'{tokens[0]} = "*"\n'
        ]  # >={tokens[1].strip()}",\n']

    result += lines[b:]

    # Write modified pyproject.toml

    with open(
        join(split(argv[0])[0], "pyproject.toml"), "w"
    ) as f:
        f.write("".join(result))

    # # Read setup.cfg

    # lines = None
    # with open("setup.cfg") as f:
    #     lines = f.readlines()

    # if lines is None:
    #     return True

    # # Modify setup.cfg

    # a = None
    # for i, line in enumerate(lines):
    #     if line.startswith("install_requires"):
    #         a = i
    #     if line.startswith("python_requires") and a is not None:
    #         b = i
    #         break

    # if a is None:
    #     return True

    # result = lines[: a + 1]
    # for dependency in dependencies:
    #     tokens = dependency.split("==")
    #     result += [f'    {tokens[0]}>={tokens[1].strip()}\n']

    # result += lines[b:]

    # # Write modified setup.cfg

    # with open(
    #     join(split(argv[0])[0], "setup.cfg"), "w"
    # ) as f:
    #     f.write("".join(result))

    return False


if __name__ == "__main__":
    exit(main())
