import shlex
from ..utils import color, Fore
from .commands import build_parser

LOGO = r"""
  ___        __  __
 |_ _|_ _   |  \/  |__ _ _ _  __ _ ___
  | || ' \  | |\/| / _` | ' \/ _` (_-<
 |___|_||_| |_|  |_\__,_|_||_\__,_/__/
"""

COMMAND_HELP = """Available commands:
  add-project NAME [--description DESC --priority N --deadline YYYY-MM-DD]
  list-projects
  update-project ID [--description DESC --priority N --deadline YYYY-MM-DD]
  delete-project ID
  add-task PROJECT_ID NAME [--estimated H] [--deadline YYYY-MM-DD] [--importance N]
  list-tasks PROJECT_ID [--status STATUS] [--importance N]
  update-task PROJECT_ID TASK_ID [--status STATUS] [--name NAME] [--estimated H]
                               [--deadline YYYY-MM-DD] [--importance N]
  delete-task PROJECT_ID TASK_ID
  plan
  calendar
  help
  quit
"""

def interactive_loop():
    parser = build_parser()
    print(color(LOGO, Fore.CYAN))
    print(color(COMMAND_HELP, Fore.YELLOW))
    while True:
        try:
            raw = input(color("ia> ", Fore.GREEN)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in {"quit", "exit", "q"}:
            break
        if raw.lower() == "help":
            print(COMMAND_HELP)
            continue
        try:
            args = parser.parse_args(shlex.split(raw))
            if hasattr(args, 'func'):
                args.func(args)
            else:
                parser.print_help()
        except SystemExit:
            # argparse errors
            pass
    print(color("Bye!", Fore.CYAN))

