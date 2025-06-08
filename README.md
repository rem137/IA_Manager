# ia_manager

A minimal command-line tool to manage personal projects with a simple AI-based planner.

The interactive shell uses ANSI colors when supported. Install `colorama` with
`pip install colorama` for the best experience. Colors are disabled when the
terminal does not support them.

Run `python -m ia_manager` to start the interactive shell. Type `help` inside
the shell to see available commands. The main commands include creating and
listing projects, managing tasks, showing the status, planning a day and
generating documentation.

## Web interface

A Flask-based web UI is available for managing projects and tasks. The
interface features a dark futuristic theme with red accents and a central chat
box. A light/dark toggle is available in the header.
Run it with:

```
python -m ia_manager.web.server
```

The interface lists projects and their tasks and includes a chat area.
Projects can be renamed or deleted directly in the list.
Click a task to view its details, mark it as done or delete it. A deadline can be entered when creating a task.
Action notifications suggested by the AI appear in the bottom right corner with accept/decline buttons.
Use the **Planning** panel to pick a day and see tasks due that day.
Press **What now?** to get an immediate recommendation from the planner.
