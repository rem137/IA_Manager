import os
import json
import time
import openai
from types import SimpleNamespace
from contextlib import redirect_stdout
import io

from .cli import commands

SYSTEM_PROMPT = (
    "Vous êtes \u00ab IA Manager \u00bb, un assistant destiné \u00e0 organiser mes projets et mes tâches.\n"
    "Votre rôle est de m’aider \u00e0 créer, planifier et suivre l’avancement de chaque tâche.\n"
    "Fiez-vous toujours aux fonctions disponibles pour manipuler les projets et les tâches.\n"
    "Lorsque l’utilisateur pose une question ou donne un ordre, décidez quelle fonction est la plus appropriée, appelez-la avec les bons paramètres, puis résumez le résultat.\n"
    "Si aucune fonction n’est adaptée, r\u00e9pondez directement \u00e0 l’utilisateur.\n"
    "Les dates doivent \u00eatre au format ISO (YYYY-MM-DD ou YYYY-MM-DDTHH:MM)."
)

FUNCTIONS = [
    {
        "name": "create_project",
        "description": "Créer un nouveau projet",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom du projet"},
                "description": {"type": "string", "description": "Description du projet"},
                "priority": {"type": "integer", "description": "Priorité (1-5)"},
                "deadline": {"type": "string", "description": "Date limite YYYY-MM-DD"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_projects",
        "description": "Lister tous les projets",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "add_task",
        "description": "Ajouter une tâche à un projet",
        "parameters": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "ID ou nom du projet"},
                "name": {"type": "string", "description": "Titre de la tâche"},
                "due": {"type": "string", "description": "Date limite YYYY-MM-DD"},
                "estimated": {"type": "integer", "description": "Durée estimée (heures)"},
                "importance": {"type": "integer", "description": "Importance 1-5"},
                "description": {"type": "string", "description": "Description de la tâche"},
            },
            "required": ["project", "name"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_tasks",
        "description": "Lister les tâches d’un projet",
        "parameters": {
            "type": "object",
            "properties": {
                "project": {"type": "string", "description": "ID ou nom du projet"},
                "status": {"type": "string", "enum": ["todo", "done", "all"], "description": "Filtre d’état"},
            },
            "required": ["project"],
            "additionalProperties": False,
        },
    },
    {
        "name": "update_task",
        "description": "Mettre à jour une tâche",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Identifiant de la tâche"},
                "title": {"type": "string", "description": "Nouveau titre"},
                "due": {"type": "string", "description": "Nouvelle date limite YYYY-MM-DD"},
                "description": {"type": "string", "description": "Nouvelle description"},
                "estimated": {"type": "integer", "description": "Durée estimée (heures)"},
                "importance": {"type": "integer", "description": "Importance 1-5"},
                "status": {"type": "string", "description": "Nouveau statut"},
                "planned_start": {"type": "string", "description": "Début planifié ISO"},
                "planned_end": {"type": "string", "description": "Fin planifiée ISO"},
                "planned_hours": {"type": "number", "description": "Durée planifiée en heures"},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "schedule_task",
        "description": "Planifier une tâche (début, fin ou durée)",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "Identifiant de la tâche"},
                "start": {"type": "string", "description": "Début planifié ISO"},
                "end": {"type": "string", "description": "Fin planifiée ISO"},
                "hours": {"type": "number", "description": "Durée planifiée en heures"},
            },
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "list_schedule",
        "description": "Afficher toutes les tâches planifiées",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "mark_done",
        "description": "Marquer une tâche comme terminée",
        "parameters": {
            "type": "object",
            "properties": {"task_id": {"type": "integer", "description": "Identifiant de la tâche"}},
            "required": ["task_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "recommend_task",
        "description": "Obtenir la tâche recommandée en priorité",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
]

TOOLS = [{"type": "function", "function": f} for f in FUNCTIONS]

FUNC_MAP = {
    "create_project": commands.add_project,
    "list_projects": commands.list_projects,
    "add_task": commands.add_task,
    "list_tasks": commands.list_tasks,
    "update_task": commands.update_task,
    "schedule_task": commands.schedule_task,
    "list_schedule": commands.list_schedule,
    "mark_done": commands.mark_done,
    "recommend_task": commands.recommend_task,
}

_client = None
_assistant_id = None
_thread = None

def _execute(func_name: str, params: dict) -> str:
    func = FUNC_MAP.get(func_name)
    if not func:
        return f"Unknown function {func_name}"
    args = SimpleNamespace(**params)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            func(args)
        return buf.getvalue().strip()
    except Exception as e:
        return f"Execution error: {e}"

def _ensure_client():
    global _client, _assistant_id, _thread
    if _client is not None and _thread is not None:
        return

    api_key = os.getenv("OPENAI_API_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")

    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY")

    print("[DEBUG] Initialisation du client OpenAI...")
    _client = openai.Client(api_key=api_key)

    if assistant_id:
        print(f"[DEBUG] Assistant ID fourni via env: {assistant_id}")
        _assistant_id = assistant_id
    else:
        print("[DEBUG] Création d'un nouvel assistant...")
        assistant = _client.beta.assistants.create(
            name="IA Manager",
            instructions=SYSTEM_PROMPT,
            tools=TOOLS,
            model="gpt-4-turbo",
        )
        _assistant_id = assistant.id

    print("[DEBUG] Création d'un nouveau thread...")
    _thread = _client.beta.threads.create()

def send_message(message: str) -> str:
    _ensure_client()
    try:
        print("[DEBUG] Envoi du message à l'assistant...")
        _client.beta.threads.messages.create(
            thread_id=_thread.id,
            role="user",
            content=message,
        )

            # openai>=1.2 returns a RequiredAction object, not a dict
            action = run.required_action
            if isinstance(action, dict):
                calls = action["submit_tool_outputs"]["tool_calls"]
            else:
                calls = action.submit_tool_outputs.tool_calls
        run = _client.beta.threads.runs.create(
            thread_id=_thread.id,
            assistant_id=_assistant_id,
        )
    except openai.OpenAIError as exc:
        return f"API error: {exc}"

    while True:
        try:
            run = _client.beta.threads.runs.retrieve(
                thread_id=_thread.id, run_id=run.id
            )
        except openai.OpenAIError as exc:
            return f"API error during run: {exc}"

        print(f"[DEBUG] Statut du run: {run.status}")
        if run.status == "failed":
            print("[DEBUG] Détails du run échoué:")
            print(json.dumps(run.model_dump(), indent=2))
            break

        if run.status == "completed":
            break
        elif run.status == "requires_action":
            print("[DEBUG] L'assistant demande une action...")
            calls = run.required_action["submit_tool_outputs"]["tool_calls"]
            outputs = []
            for call in calls:
                name = call["function"]["name"]
                try:
                    args = json.loads(call["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                print(f"[DEBUG] Appel de la fonction: {name} avec args: {args}")
                result = _execute(name, args)
                outputs.append({"tool_call_id": call["id"], "output": result})
            try:
                print("[DEBUG] Envoi des résultats des outils à l'assistant...")
                _client.beta.threads.runs.submit_tool_outputs(
                    thread_id=_thread.id,
                    run_id=run.id,
                    tool_outputs=outputs,
                )
            except openai.OpenAIError as exc:
                return f"API error submitting outputs: {exc}"
        else:
            print("[DEBUG] Attente...")
            time.sleep(1)

    try:
        print("[DEBUG] Récupération des messages de réponse...")
        messages = _client.beta.threads.messages.list(thread_id=_thread.id, order="desc")
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value
    except openai.OpenAIError as exc:
        return f"API error fetching messages: {exc}"
    return ""

def chat_loop() -> None:
    try:
        _ensure_client()
    except RuntimeError as exc:
        print(str(exc))
        return

    print("Type 'quit' to exit")
    while True:
        user = input("you> ").strip()
        if not user:
            continue
        if user.lower() in {"quit", "exit"}:
            break
        reply = send_message(user)
        print(f"assistant> {reply}")
