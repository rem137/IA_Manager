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

A simple Flask-based web UI is available for managing projects and tasks.
Run it with:

```
python -m ia_manager.web.server
```

The interface lists projects and their tasks and includes a chat area placeholder.
