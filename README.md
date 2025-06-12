# ia_manager

A minimal command-line tool to manage personal projects with a simple AI-based planner.

The interactive shell uses ANSI colors when supported. Install `colorama` with
`pip install colorama` for the best experience. Colors are disabled when the
terminal does not support them.

Run `python -m ia_manager` to start the interactive shell. Type `help` inside
the shell to see available commands. The main commands include creating and
listing projects, managing tasks, showing the status, planning a day and
generating documentation.

## Task scheduling

Tasks now support planned start and end times as well as an optional duration.
Use the `schedule_task` command or update a task with `update_task` to set these
fields. The `list_schedule` command prints the current planning ordered by
start time.

## OpenAI assistant (beta)

If an OpenAI API key is available via the `OPENAI_API_KEY` environment variable
(or `Assistant_Token` for backward compatibility), you can chat with the beta
Assistant API to control the CLI. `Assistant_Token` can also hold a published
assistant ID (value starting with `asst_`). In that case the existing assistant
is used instead of creating one. Run:

```
python -m ia_manager assistant
```

The assistant decides which CLI function to call in order to manage your
projects and tasks. Install the latest `openai` package to enable this feature.
Set your API key in `OPENAI_API_KEY`. If that variable is not available,
`Assistant_Token` may contain either an API key or an assistant ID and will be
used as a fallback:

```
pip install openai
```

## Web interface

A Flask-based web UI is available for managing projects and tasks. The
interface uses a dark futuristic theme with red accents. It is organised in
three columns:

* a menu sidebar on the left
* a central area displaying the task currently recommended by the AI
* a right column listing upcoming deadlines and notifications
Run it with:

```
python -m ia_manager.web.server
```

The interface lists projects and their tasks and includes a chat area.
Projects can be renamed or deleted directly in the list.
Click a task to open a detail modal where you can start/stop the timer or mark it done.
New tasks are added through a dedicated form with name, description and deadline fields.
Action notifications suggested by the AI appear in the bottom right corner with accept/decline buttons.
The right column lists upcoming deadlines while the centre shows the task the AI recommends to start now.
Navigate using the left menu to switch between the dashboard, project view,
global tasks list, calendar, chat and settings.

The calendar view displays the current week's schedule. Tasks are grouped by day
and show the time when provided. Data for a full week can be obtained via the
`/api/calendar/week` endpoint which accepts an optional `start` parameter in
`YYYY-MM-DD` format.
