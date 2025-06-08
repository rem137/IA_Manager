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
interface uses a dark futuristic theme with red accents and features a left
navigation bar, a dynamic central area and a context panel with the daily
planning.
Run it with:

```
python -m ia_manager.web.server
```

The interface lists projects and their tasks and includes a chat area.
Projects can be renamed or deleted directly in the list.
Click a task to open a detail modal where you can start/stop the timer or mark it done.
New tasks are added through a dedicated form with name, description and deadline fields.
Action notifications suggested by the AI appear in the bottom right corner with accept/decline buttons.
Use the **Planning** panel to pick a day and see tasks due that day.
The dashboard now displays the recommended next task automatically as well as overall progress.
Navigate using the left menu to switch between the dashboard, project view,
global tasks list, chat and settings.
