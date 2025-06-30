from flask import Flask, request, jsonify
from .services import local_model

app = Flask(__name__)

@app.route('/pensee', methods=['POST'])
def pensee_api():
    data = request.get_json(silent=True) or {}
    souvenirs = data.get('souvenirs', [])
    derniers = data.get('derniers_messages', [])

    parts = []
    if souvenirs:
        parts.append("Souvenirs:\n" + "\n".join(f"- {s}" for s in souvenirs))
    if derniers:
        parts.append("Derniers messages:\n" + "\n".join(derniers))
    parts.append("Quelle est la pens\u00e9e actuelle de l'IA ?")
    prompt = "\n\n".join(parts)

    text = local_model.process_message(prompt) or ""
    return jsonify({'pensee': text})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
