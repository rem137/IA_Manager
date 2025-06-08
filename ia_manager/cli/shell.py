import shlex
from .commands import build_parser

LOGO = r"""
  ___ ___    ___  ___  _   _            
 |_ _|_ _|  / _ \| _ )| | | | __ _ _ __ 
  | | | |  | (_) | _ \| |_| |/ _` | '_ \
 |___|___|  \___/|___/ \___/| (_|_| .__/
                                  |_|   
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
    print(LOGO)
    print(COMMAND_HELP)
    while True:
        try:
            raw = input("ia> ").strip()
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
    print("Bye!")

