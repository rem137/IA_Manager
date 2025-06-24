import argparse
from typing import List, Optional
from ..models.project import Project
from ..models.task import Task
from ..services import storage, logger, planner, memory
from ..utils import color, Fore
from .. import personality
import calendar
from datetime import datetime, date


def _find_project(projects: List[Project], ident) -> Optional[Project]:
    """Return project by id or name"""
    for p in projects:
        if p.id == ident or p.name == ident:
            return p
    return None


def add_project(args):
    projects = storage.load_projects()
    project_id = max([p.id for p in projects], default=0) + 1
    project = Project(
        id=project_id,
        name=args.name,
        description=args.description,
        priority=args.priority,
        deadline=args.deadline,
    )
    projects.append(project)
    storage.save_projects(projects)
    logger.log(f"Added project {project.name}")
    print(f"Project '{project.name}' added with id {project.id}")


def list_projects(_args):
    projects = storage.load_projects()
    for p in projects:
        status_text = color(f"[{p.status}]", Fore.GREEN if p.status == "termine" else Fore.YELLOW if p.status == "en pause" else Fore.CYAN)
        bar = "█" * (p.progress() // 10)
        print(f"{p.id}: {p.name} {status_text} priority:{p.priority} {bar:<10} {p.progress()}%")


def update_project(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.id)
    if not project:
        print("Project not found")
        return
    if args.description is not None:
        project.description = args.description
    if args.deadline is not None:
        project.deadline = args.deadline
    if args.priority is not None:
        project.priority = args.priority
    storage.save_projects(projects)
    logger.log(f"Updated project {project.name}")
    print("Project updated")


def delete_project(args):
    projects = storage.load_projects()
    proj = _find_project(projects, args.project)
    if not proj:
        print("Project not found")
        return
    projects = [p for p in projects if p.id != proj.id]
    storage.save_projects(projects)
    logger.log(f"Deleted project {proj.id}")
    print("Project deleted")


def rename_project(args):
    projects = storage.load_projects()
    proj = _find_project(projects, args.project)
    if not proj:
        print("Project not found")
        return
    proj.name = args.new_name
    storage.save_projects(projects)
    logger.log(f"Renamed project {proj.id} to {proj.name}")
    print("Project renamed")


def archive_project(args):
    projects = storage.load_projects()
    proj = _find_project(projects, args.project)
    if not proj:
        print("Project not found")
        return
    proj.status = "archive"
    storage.save_projects(projects)
    logger.log(f"Archived project {proj.id}")
    print("Project archived")


def add_task(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project)
    if not project:
        print("Project not found")
        return
    task_id = max([t.id for t in project.tasks], default=0) + 1
    due_iso = None
    if args.due:
        try:
            due_iso = datetime.strptime(args.due, "%d/%m").replace(year=date.today().year).date().isoformat()
        except ValueError:
            print("Invalid due date format. Use JJ/MM")
            return
    task = Task(
        id=task_id,
        name=args.name,
        estimated=args.estimated,
        deadline=due_iso,
        importance=args.importance,
        description=args.description or "",
    )
    project.tasks.append(task)
    storage.save_projects(projects)
    logger.log(f"Added task {task.name} to project {project.name}")
    print(f"Task '{task.name}' added with id {task.id}")


def list_tasks(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project)
    if not project:
        print("Project not found")
        return
    status_filter = None
    if args.all:
        status_filter = None
    elif args.done:
        status_filter = "done"
    else:
        status_filter = "todo"
    for t in project.tasks:
        if status_filter and t.status != status_filter:
            continue
        status_col = Fore.GREEN if t.status == "done" else Fore.CYAN
        status_text = color(f"[{t.status}]", status_col)
        print(f"{t.id}: {t.name} {status_text} importance:{t.importance}")


def update_task(args):
    projects = storage.load_projects()
    project = None
    task = None
    for p in projects:
        for t in p.tasks:
            if t.id == args.task_id:
                project = p
                task = t
                break
        if task:
            break
    if not task:
        print("Task not found")
        return
    if args.status:
        task.status = args.status
    if args.title:
        task.name = args.title
    if args.estimated is not None:
        task.estimated = args.estimated
    if args.due is not None:
        try:
            task.deadline = datetime.strptime(args.due, "%d/%m").replace(year=date.today().year).date().isoformat()
        except ValueError:
            print("Invalid due date format")
            return
    if args.importance is not None:
        task.importance = args.importance
    if args.desc is not None:
        task.description = args.desc
    if args.planned_start is not None:
        task.planned_start = args.planned_start
    if args.planned_end is not None:
        task.planned_end = args.planned_end
    if args.planned_hours is not None:
        task.planned_hours = args.planned_hours
    storage.save_projects(projects)
    logger.log(f"Updated task {task.id} in project {project.name}")
    print("Task updated")


def delete_task(args):
    projects = storage.load_projects()
    for p in projects:
        for t in list(p.tasks):
            if t.id == args.task_id:
                p.tasks.remove(t)
                storage.save_projects(projects)
                logger.log(f"Deleted task {args.task_id} from project {p.name}")
                print("Task deleted")
                return
    print("Task not found")


def mark_done(args):
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == args.task_id:
                t.status = "done"
                storage.save_projects(projects)
                logger.log(f"Marked task {t.id} as done")
                print("Task marked as done")
                return
    print("Task not found")


def schedule_task(args):
    """Plan start/end dates or duration for a task."""
    projects = storage.load_projects()
    for p in projects:
        for t in p.tasks:
            if t.id == args.task_id:
                if args.start:
                    t.planned_start = args.start
                if args.end:
                    t.planned_end = args.end
                if args.hours is not None:
                    t.planned_hours = args.hours
                if args.start or args.end or args.hours is not None:
                    t.status = 'planned'
                storage.save_projects(projects)
                logger.log(f"Scheduled task {t.id}")
                print("Task scheduled")
                return
    print("Task not found")


def list_schedule(_args):
    projects = storage.load_projects()
    entries = []
    for p in projects:
        for t in p.tasks:
            if t.planned_start:
                entries.append((t.planned_start, p.name, t))
    entries.sort(key=lambda x: x[0])
    for start, pname, t in entries:
        end = f" -> {t.planned_end}" if t.planned_end else ""
        dur = f" ({t.planned_hours}h)" if t.planned_hours else ""
        print(f"{start}{end} {pname}: {t.name}{dur}")


def show_status(_args):
    projects = storage.load_projects()
    for p in projects:
        status_text = color(f"[{p.status}]", Fore.GREEN if p.status == "termine" else Fore.YELLOW if p.status == "en pause" else Fore.CYAN)
        print(f"{p.name} {status_text} {p.progress()}% done")


def plan_day(args):
    target = date.today()
    if args.date:
        try:
            target = datetime.strptime(args.date, "%d/%m").replace(year=date.today().year).date()
        except ValueError:
            print("Invalid date format")
            return
    suggestions = planner.suggest_tasks(storage.load_projects())
    print(f"Plan for {target}:")
    for s in suggestions[:5]:
        print(f"- {s}")


def doc_update(args):
    projects = storage.load_projects()
    proj = _find_project(projects, args.project)
    if not proj:
        print("Project not found")
        return
    path = storage.DOCS_DIR / f"{proj.name}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {proj.name}\n\n{proj.description}\n\n## Tasks\n")
        for t in proj.tasks:
            mark = "x" if t.status == "done" else " "
            f.write(f"- [{mark}] {t.name}\n")
    print(f"Documentation written to {path}")


def doc_show_cmd(args):
    path = storage.DOCS_DIR / f"{args.project}.md"
    if not path.exists():
        print("No documentation found")
        return
    print(path.read_text())


def list_improvements(_args):
    items = storage.load_improvements()
    for i, imp in enumerate(items, 1):
        print(f"{i}. {imp}")


def add_improvement(args):
    items = storage.load_improvements()
    items.append(args.desc)
    storage.save_improvements(items)
    print("Improvement added")


def plan_self_update(_args):
    items = storage.load_improvements()
    items.append("Improve the IA manager itself")
    storage.save_improvements(items)
    print("Self update planned")


def recommend_task(_args):
    projects = storage.load_projects()
    suggestions = planner.suggest_tasks(projects)
    print("Suggested tasks:")
    for s in suggestions:
        print(color(f"- {s}", Fore.MAGENTA))


def remember_note(args):
    notes = memory.load_notes()
    note_id = max([n.get("id", 0) for n in notes], default=0) + 1
    note = {
        "id": note_id,
        "text": args.text,
        "tags": args.tags or [],
        "project": args.project,
    }
    notes.append(note)
    memory.save_notes(notes)
    personality.say("Note saved")


def recall_notes(args):
    notes = memory.load_notes()
    key = args.keyword.lower()
    matches = [n for n in notes if key in n.get("text", "").lower() or any(key == t.lower() for t in n.get("tags", []))]
    if not matches:
        personality.say("No matching notes")
        return
    for n in matches:
        tagstr = ",".join(n.get("tags", []))
        print(f"[{n['id']}] {n['text']} {f'({tagstr})' if tagstr else ''}")


def set_sarcasm(args):
    user = memory.load_user()
    user["sarcasm"] = args.level
    memory.save_user(user)
    personality.say(f"Sarcasm set to {args.level}")


def set_username(args):
    user = memory.load_user()
    user["name"] = args.name
    memory.save_user(user)
    personality.say(f"Nice to meet you, {args.name}")


def show_calendar(_args):
    projects = storage.load_projects()
    today = date.today()
    tasks_by_day = {}
    for proj in projects:
        for task in proj.tasks:
            if task.deadline:
                try:
                    d = datetime.fromisoformat(task.deadline)
                except ValueError:
                    continue
                if d.year == today.year and d.month == today.month:
                    tasks_by_day.setdefault(d.day, []).append(f"{proj.name}: {task.name}")
    cal = calendar.Calendar().monthdayscalendar(today.year, today.month)
    print(f"{calendar.month_name[today.month]} {today.year}")
    print("Mo Tu We Th Fr Sa Su")
    for week in cal:
        line = []
        for day in week:
            if day == 0:
                line.append("  ")
            else:
                mark = "*" if day in tasks_by_day else " "
                cell = f"{day:2d}{mark}"
                if day in tasks_by_day:
                    cell = color(cell, Fore.GREEN)
                line.append(cell)
        print(" ".join(line))
    if tasks_by_day:
        print("\nLegend: * task due")
        for day in sorted(tasks_by_day):
            for t in tasks_by_day[day]:
                print(f"{day:02d}: {t}")


def assistant_chat(_args):
    """Start interactive chat with the OpenAI Assistant API."""
    from ..assistant import chat_loop
    chat_loop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ia_manager")
    sub = parser.add_subparsers(dest="command")

    # Project commands
    p_add = sub.add_parser("create_project")
    p_add.add_argument("name")
    p_add.add_argument("--description", default="")
    p_add.add_argument("--priority", type=int, default=3)
    p_add.add_argument("--deadline")
    p_add.set_defaults(func=add_project)

    p_list = sub.add_parser("list_projects")
    p_list.set_defaults(func=list_projects)

    p_del = sub.add_parser("delete_project")
    p_del.add_argument("project")
    p_del.set_defaults(func=delete_project)

    p_ren = sub.add_parser("rename_project")
    p_ren.add_argument("project")
    p_ren.add_argument("new_name")
    p_ren.set_defaults(func=rename_project)

    p_arc = sub.add_parser("archive_project")
    p_arc.add_argument("project")
    p_arc.set_defaults(func=archive_project)

    # Task commands
    t_add = sub.add_parser("add_task")
    t_add.add_argument("project")
    t_add.add_argument("name")
    t_add.add_argument("--due")
    t_add.add_argument("--estimated", type=int)
    t_add.add_argument("--importance", type=int, default=3)
    t_add.add_argument("--description")
    t_add.set_defaults(func=add_task)

    t_list = sub.add_parser("list_tasks")
    t_list.add_argument("project")
    t_list.add_argument("--all", action="store_true")
    t_list.add_argument("--done", action="store_true")
    t_list.set_defaults(func=list_tasks)

    t_mark = sub.add_parser("mark_done")
    t_mark.add_argument("task_id", type=int)
    t_mark.set_defaults(func=mark_done)

    t_del = sub.add_parser("delete_task")
    t_del.add_argument("task_id", type=int)
    t_del.set_defaults(func=delete_task)

    t_upd = sub.add_parser("update_task")
    t_upd.add_argument("task_id", type=int)
    t_upd.add_argument("--title")
    t_upd.add_argument("--due")
    t_upd.add_argument("--desc")
    t_upd.add_argument("--estimated", type=int)
    t_upd.add_argument("--importance", type=int)
    t_upd.add_argument("--status")
    t_upd.add_argument("--planned_start")
    t_upd.add_argument("--planned_end")
    t_upd.add_argument("--planned_hours", type=float)
    t_upd.set_defaults(func=update_task)

    t_sched = sub.add_parser("schedule_task")
    t_sched.add_argument("task_id", type=int)
    t_sched.add_argument("--start")
    t_sched.add_argument("--end")
    t_sched.add_argument("--hours", type=float)
    t_sched.set_defaults(func=schedule_task)

    sub.add_parser("list_schedule").set_defaults(func=list_schedule)

    sub.add_parser("show_status").set_defaults(func=show_status)

    p_day = sub.add_parser("plan_day")
    p_day.add_argument("date", nargs="?")
    p_day.set_defaults(func=plan_day)

    sub.add_parser("recommend_task").set_defaults(func=recommend_task)

    doc_upd = sub.add_parser("doc_update")
    doc_upd.add_argument("project")
    doc_upd.set_defaults(func=doc_update)

    doc_show = sub.add_parser("doc_show")
    doc_show.add_argument("project")
    doc_show.set_defaults(func=doc_show_cmd)

    sub.add_parser("list_improvements").set_defaults(func=list_improvements)

    imp_add = sub.add_parser("add_improvement")
    imp_add.add_argument("desc")
    imp_add.set_defaults(func=add_improvement)

    sub.add_parser("plan_self_update").set_defaults(func=plan_self_update)

    sub.add_parser("assistant").set_defaults(func=assistant_chat)

    # Memory and preferences
    mem_add = sub.add_parser("remember")
    mem_add.add_argument("text")
    mem_add.add_argument("--project")
    mem_add.add_argument("--tags", nargs="*")
    mem_add.set_defaults(func=remember_note)

    mem_get = sub.add_parser("recall")
    mem_get.add_argument("keyword")
    mem_get.set_defaults(func=recall_notes)

    sarc = sub.add_parser("set_sarcasm")
    sarc.add_argument("level", type=int)
    sarc.set_defaults(func=set_sarcasm)

    uname = sub.add_parser("set_name")
    uname.add_argument("name")
    uname.set_defaults(func=set_username)

    sub.add_parser("calendar").set_defaults(func=show_calendar)

    return parser
