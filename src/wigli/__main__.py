# wigli __main__.py

from sys import exit, argv

from wigli._wigli_cli import wigli_cli

if __name__ == "__main__":
    exit(wigli_cli(argv_=argv[1:]))
