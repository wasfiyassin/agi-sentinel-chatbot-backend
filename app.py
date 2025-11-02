from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests

app = Flask(__name__)

# 👇 mientras montamos todo: abierto
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ✅ ruta raíz para saber si la app está viva
@app.get("/")
def root():
    return jsonify({
        "status": "ok",
        "message": "AGi Sentinel backend activo",
        "endpoints": ["/chat", "/browse"]
    })


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


@app.post("/chat")
def chat():
    data = request.get_json() or {}
    messages = data.get("messages")

    # compatibilidad con { "message": "hola" }
    if not messages:
        user_message = data.get("message", "")
        messages = [
            {"role": "system", "content": "Eres un asistente de AGi Sentinel."},
            {"role": "user", "content": user_message},
        ]

    payload = {
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.7,
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(OPENAI_URL, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        return jsonify(r.json())
    except Exception as e:
        print("❌ Error llamando a OpenAI:", e)
        return jsonify({"error": "openai-error", "detail": str(e)}), 500


@app.post("/browse")
def browse():
    data = request.get_json() or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "missing-url"}), 400

    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "AGiSentinelBot/1.0"})
        return jsonify({
            "status": resp.status_code,
            "content": resp.text[:5000]
        })
    except Exception as e:
        return jsonify({"error": "browse-failed", "detail": str(e)}), 500


if __name__ == "__main__":
    # para local
    app.run(host="0.0.0.0", port=5000, debug=True)
