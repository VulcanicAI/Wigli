# wigli __init__.py

from wigli._wigli_bots import (
    WigliMessage,
    WigliInjection,
    WigliCommand,
    WigliBot,
    OneShotBot,
    CommandBot,
)

from wigli._wigli_cli import WigliInvocation, wigli_cli

NOTES = f"""\
This command-line toolset implements the \
OpenAI API into several tools and bots.

For an up-to-date-list, run "ch -h". This \
header documents system conventions and to-dos.

TODO: Better titling
TODO: Assistant pip access
TODO: Automated tests
TODO: Search bot
TODO: Auto-git botswarm
    Commit decider, commit titler, FracTLDR_Code
TODO: transcriptbrief title search and timestamp search integration
TODO: AI-powered manual for this CLI
TODO: Ensure entire dependency tree is MIT license
TODO: Refactor history to inherit from OpenAI objects
TODO: Break out args handler
TODO: Break out command parser
TODO: Diagram for comparison to other assistants
TODO: generate_and_append_reply do_parse_cmds parameter seems hacky
TODO: Stacktrace summarizer
TODO: Automatic forgetting
TODO: Key input
TODO: ChatCompletion timeout watchdog
TODO: Chai house multi-chat protocol
TODO: handll house
\
"""
