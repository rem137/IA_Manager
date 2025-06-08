import argparse
from typing import List, Optional
from ..models.project import Project
from ..models.task import Task
from ..services import storage, logger, planner
import calendar
from datetime import datetime, date


def _find_project(projects: List[Project], project_id: int) -> Optional[Project]:
    for p in projects:
        if p.id == project_id:
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
        print(f"{p.id}: {p.name} [{p.status}] priority:{p.priority} progress:{p.progress()}%")


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
    projects = [p for p in projects if p.id != args.id]
    storage.save_projects(projects)
    logger.log(f"Deleted project {args.id}")
    print("Project deleted")


def add_task(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project_id)
    if not project:
        print("Project not found")
        return
    task_id = max([t.id for t in project.tasks], default=0) + 1
    task = Task(
        id=task_id,
        name=args.name,
        estimated=args.estimated,
        deadline=args.deadline,
        importance=args.importance,
    )
    project.tasks.append(task)
    storage.save_projects(projects)
    logger.log(f"Added task {task.name} to project {project.name}")
    print(f"Task '{task.name}' added with id {task.id}")


def list_tasks(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project_id)
    if not project:
        print("Project not found")
        return
    tasks = project.tasks
    for t in tasks:
        if args.status and t.status != args.status:
            continue
        if args.importance and t.importance != args.importance:
            continue
        print(f"{t.id}: {t.name} [{t.status}] importance:{t.importance}")


def update_task(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project_id)
    if not project:
        print("Project not found")
        return
    task = next((t for t in project.tasks if t.id == args.task_id), None)
    if not task:
        print("Task not found")
        return
    if args.status:
        task.status = args.status
    if args.name:
        task.name = args.name
    if args.estimated is not None:
        task.estimated = args.estimated
    if args.deadline is not None:
        task.deadline = args.deadline
    if args.importance is not None:
        task.importance = args.importance
    storage.save_projects(projects)
    logger.log(f"Updated task {task.id} in project {project.name}")
    print("Task updated")


def delete_task(args):
    projects = storage.load_projects()
    project = _find_project(projects, args.project_id)
    if not project:
        print("Project not found")
        return
    project.tasks = [t for t in project.tasks if t.id != args.task_id]
    storage.save_projects(projects)
    logger.log(f"Deleted task {args.task_id} from project {project.name}")
    print("Task deleted")


def plan(_args):
    projects = storage.load_projects()
    suggestions = planner.suggest_tasks(projects)
    print("Suggested tasks:")
    for s in suggestions:
        print(f"- {s}")


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
                line.append(f"{day:2d}{mark}")
        print(" ".join(line))
    if tasks_by_day:
        print("\nLegend: * task due")
        for day in sorted(tasks_by_day):
            for t in tasks_by_day[day]:
                print(f"{day:02d}: {t}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ia_manager")
    sub = parser.add_subparsers(dest="command")

    # Project commands
    p_add = sub.add_parser("add-project")
    p_add.add_argument("name")
    p_add.add_argument("--description", default="")
    p_add.add_argument("--priority", type=int, default=3)
    p_add.add_argument("--deadline")
    p_add.set_defaults(func=add_project)

    p_list = sub.add_parser("list-projects")
    p_list.set_defaults(func=list_projects)

    p_upd = sub.add_parser("update-project")
    p_upd.add_argument("id", type=int)
    p_upd.add_argument("--description")
    p_upd.add_argument("--deadline")
    p_upd.add_argument("--priority", type=int)
    p_upd.set_defaults(func=update_project)

    p_del = sub.add_parser("delete-project")
    p_del.add_argument("id", type=int)
    p_del.set_defaults(func=delete_project)

    # Task commands
    t_add = sub.add_parser("add-task")
    t_add.add_argument("project_id", type=int)
    t_add.add_argument("name")
    t_add.add_argument("--estimated", type=int)
    t_add.add_argument("--deadline")
    t_add.add_argument("--importance", type=int, default=3)
    t_add.set_defaults(func=add_task)

    t_list = sub.add_parser("list-tasks")
    t_list.add_argument("project_id", type=int)
    t_list.add_argument("--status")
    t_list.add_argument("--importance", type=int)
    t_list.set_defaults(func=list_tasks)

    t_upd = sub.add_parser("update-task")
    t_upd.add_argument("project_id", type=int)
    t_upd.add_argument("task_id", type=int)
    t_upd.add_argument("--status")
    t_upd.add_argument("--name")
    t_upd.add_argument("--estimated", type=int)
    t_upd.add_argument("--deadline")
    t_upd.add_argument("--importance", type=int)
    t_upd.set_defaults(func=update_task)

    t_del = sub.add_parser("delete-task")
    t_del.add_argument("project_id", type=int)
    t_del.add_argument("task_id", type=int)
    t_del.set_defaults(func=delete_task)

    plan_cmd = sub.add_parser("plan")
    plan_cmd.set_defaults(func=plan)

    cal_cmd = sub.add_parser("calendar")
    cal_cmd.set_defaults(func=show_calendar)

    return parser
