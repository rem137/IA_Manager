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

Set an OpenAI API key in the `OPENAI_API_KEY` environment variable to enable the
assistant. The old `Assistant_Token` variable is still accepted as a fallback
for the API key or to provide a pre‑existing assistant ID (values beginning with
`asst_`). If no ID is supplied via `OPENAI_ASSISTANT_ID`, a new assistant is
created automatically. Run:

```
python -m ia_manager assistant
```

The assistant decides which CLI function to call in order to manage your
projects and tasks. Install the latest `openai` package to enable this feature.
`OPENAI_API_KEY` **must** contain a valid API key. `Assistant_Token` can be used
instead for backward compatibility or to specify the assistant ID. Example
installation:

```
pip install openai
```

## Web interface

A Flask-based web UI is available for managing projects and tasks. Make sure the
`flask` package is installed:

```
pip install flask
```

The interface uses a dark futuristic theme with red accents. It is organised in
three columns:

* a menu sidebar on the left
* a central area displaying the task currently recommended by the AI
* a right column listing upcoming deadlines and notifications
Run it with:

```
python -m ia_manager.web.server
```

The interface lists projects and their tasks and includes a chat area.
Messages typed in this chat are sent to the OpenAI assistant via the
`/api/chat` endpoint.
Projects can be renamed or deleted directly in the list.
Click a task to open a detail modal where you can start/stop the timer or mark it done.
New tasks are added through a dedicated form with name, description and deadline fields.
Action notifications suggested by the AI appear in the bottom right corner with accept/decline buttons.
The right column lists upcoming deadlines while the centre shows the task the AI recommends to start now.
The **Browser** page now acts as a search engine over your notes and past messages. Enter a few keywords to get a short paragraph summarising the most relevant texts (max 500 characters).
Navigate using the left menu to switch between the dashboard, project view,
global tasks list, calendar, chat, the built-in browser and settings.

The calendar view displays the current week's schedule. Tasks are grouped by day
and show the time when provided. Data for a full week can be obtained via the
`/api/calendar/week` endpoint which accepts an optional `start` parameter in
`YYYY-MM-DD` format.

## Persistent memory and notes

KroniX now keeps a small database in `ia_manager/data/memory.json`. Notes can be
added with:

```
python -m ia_manager add_note "My note" --tags idea,urgent --project 1
```

List or search notes using `list_notes` and `search_notes`. The personality of
the assistant is configured in `ia_manager/data/personality.json`. Adjust the
sarcasm level with:

```
python -m ia_manager set_personality --sarcasm 0.7
```
You can also change how much context is returned before each message with:

```
python -m ia_manager set_personality --context_chars 300
```

At the beginning of each CLI session a contextual summary is displayed. You can
set your own message with `set_session_note` and clear it by setting an empty
string.

In the web interface, open the **Settings** page to adjust the assistant
sarcasm level, the maximum length of search snippets and your custom session
note.

When chatting with the assistant, each message is stored in the memory file and
automatically searched to provide context. The search engine now scores each
note or past message based on how many query keywords it contains,
similar to a web browser. The most relevant snippets are summarised and
prepended before each request to keep token usage low.

The assistant can also store private notes using the `remember_note` function.
These internal notes are indexed for context but hidden from CLI commands and
web search results.

A developer mode can be enabled in the personality settings. When activated,
each chat displays the raw search snippets and the generated internal thought
before sending the request to OpenAI.

All chat messages are written to `ia_manager/data/log.txt` so you can audit the
conversation history if needed.

All callable functions are listed in `ia_manager/data/assistant_commands.json`
for reference.
