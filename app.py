# ============================================================
#  app.py  —  Serene: AI Mental Health Chatbot
# ============================================================

import os

# ── PASTE YOUR GROQ API KEY HERE ────────────────────────────
os.environ["GEMINI_API_KEY"] = "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"   # paste Groq key: gsk_...
# ────────────────────────────────────────────────────────────

from flask import Flask, render_template, request, jsonify, session
from agent import MentalHealthAgent
import uuid

app = Flask(__name__)
app.secret_key = "serene-2024-secret"
agents: dict = {}


def get_agent() -> MentalHealthAgent:
    sid = session.get("sid")
    if not sid or sid not in agents:
        sid = str(uuid.uuid4())
        session["sid"] = sid
        agents[sid] = MentalHealthAgent()
    return agents[sid]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/status")
def status():
    has_key = bool(os.environ.get("GEMINI_API_KEY", "").strip())
    return jsonify({"api_enabled": has_key})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg  = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error": "empty"}), 400
    agent  = get_agent()
    result = agent.process(msg)
    return jsonify({**result, "summary": agent.get_summary()})


@app.route("/reset", methods=["POST"])
def reset():
    get_agent().reset()
    return jsonify({"status": "ok"})


@app.route("/quit", methods=["POST"])
def quit_app():
    import threading
    def shutdown():
        import time, os, signal
        time.sleep(0.5)
        os.kill(os.getpid(), signal.SIGTERM)
    threading.Thread(target=shutdown, daemon=True).start()
    return jsonify({"status": "shutting down"})


if __name__ == "__main__":
    key  = os.environ.get("GEMINI_API_KEY", "")
    mode = "🟢 Gemini API" if key else "🟡 Fallback (no key)"
    print(f"\n{'='*55}\n  🌿 Serene — AI Mental Health Chatbot\n  Mode: {mode}\n  URL:  http://127.0.0.1:5000\n{'='*55}\n")
    app.run(debug=True, port=5000)
