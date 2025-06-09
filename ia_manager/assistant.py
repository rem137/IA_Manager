import os
import json
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
                "due": {"type": "string", "description": "Date limite JJ/MM"},
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
                "due": {"type": "string", "description": "Nouvelle date limite JJ/MM"},
                "desc": {"type": "string", "description": "Nouvelle description"},
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


def _execute(func_name: str, params: dict) -> str:
    func = FUNC_MAP.get(func_name)
    if not func:
        return f"Unknown function {func_name}"
    args = SimpleNamespace(**params)
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(args)
    return buf.getvalue().strip()


def chat_loop() -> None:
    token = os.getenv("Assistant_Token")
    if not token:
        print("Assistant_Token environment variable not set")
        return
    client = openai.OpenAI(api_key=token)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Type 'quit' to exit")
    while True:
        user = input("you> ").strip()
        if not user:
            continue
        if user.lower() in {"quit", "exit"}:
            break
        messages.append({"role": "user", "content": user})
        while True:
            resp = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages,
                functions=FUNCTIONS,
                function_call="auto",
            )
            msg = resp.choices[0].message.model_dump()
            if msg.get("function_call"):
                name = msg["function_call"]["name"]
                try:
                    args = json.loads(msg["function_call"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                result = _execute(name, args)
                messages.append(msg)
                messages.append({"role": "function", "name": name, "content": result})
                continue
            else:
                print(f"assistant> {msg.get('content', '')}")
                messages.append(msg)
                break
