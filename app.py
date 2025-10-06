#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from datetime import datetime
import json, subprocess

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
FEEDBACK_FILE = ROOT/"user_feedback.jsonl"
REPORT_FILE = ROOT/"ai_test_report.json"
FEATURES_MD = ROOT/"ai_features.md"

@app.route("/")
def index():
    return render_template("index.html", title="openai-plus")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    has_image = bool(data.get("has_image"))
    has_audio = bool(data.get("has_audio"))
    reply = [f"You said: {message}" if message else "Hello!" ]
    if has_image: reply.append("I received an image.")
    if has_audio: reply.append("I received an audio clip.")
    return jsonify({"reply": " \\n".join(reply)})

@app.route("/api/feedback", methods=["POST"])
def feedback():
    payload = request.json or {}
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": payload.get("message"),
        "rating": payload.get("rating"),
        "feature_request": payload.get("feature_request"),
        "tags": payload.get("tags", []),
    }
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry)+"\n")
    return jsonify({"status": "ok"})

@app.route("/api/run_auto_ai", methods=["POST"]) 
def run_auto_ai():
    try:
        proc = subprocess.run(["python","auto_ai.py"], cwd=str(ROOT), capture_output=True, text=True, timeout=180)
        stdout = (proc.stdout or "")[-4000:]
    except Exception as e:
        stdout = f"Error: {e}"
    report = {}
    if REPORT_FILE.exists():
        try:
            report = json.loads(REPORT_FILE.read_text())
        except Exception:
            report = {"error": "failed to read report"}
    return jsonify({"stdout": stdout, "report": report})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
