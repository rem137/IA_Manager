import shlex
from ..utils import color, Fore
from .commands import build_parser
from ..services import memory, storage

LOGO = r"""
  ___        __  __
 |_ _|_ _   |  \/  |__ _ _ _  __ _ ___
  | || ' \  | |\/| / _` | ' \/ _` (_-<
 |___|_||_| |_|  |_\__,_|_||_\__,_/__/
"""

COMMAND_HELP = """Available commands:
  create_project NAME [--description DESC --priority N --deadline YYYY-MM-DD]
  list_projects
  delete_project ID|NAME
  rename_project ID|NAME NEW_NAME
  archive_project ID|NAME
  add_task PROJECT TITLE [--due JJ/MM]
  list_tasks PROJECT [--all|--done]
  mark_done TASK_ID
  delete_task TASK_ID
  update_task TASK_ID [--title NAME --due JJ/MM --desc TEXT \
                       --planned_start TS --planned_end TS --planned_hours H]
  schedule_task TASK_ID [--start TS --end TS --hours H]
  list_schedule
  show_status
  plan_day [JJ/MM]
  recommend_task
  calendar
  assistant
  help
  quit
"""

def interactive_loop():
    parser = build_parser()
    user = memory.load_user()
    projects = storage.load_projects()
    notes = memory.load_notes()
    custom = memory.load_custom_session_note()
    note = custom or memory.generate_session_note(projects, notes, user)
    if note:
        print(color(f"[Note] {note}", Fore.MAGENTA))
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

