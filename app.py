#!/usr/bin/env python3
"""
Flask Web Application for OpenAI-Plus (ai-test)

This module provides a ChatGPT-like web interface with the following features:
- Multi-modal chat interface (text, image, audio)
- User feedback collection system
- Automated AI testing integration via auto_ai.py
- Dark/light theme toggle support

The application serves as the main backend for the continuous improvement
feedback loop, storing user feedback and running automated code analysis.
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
from datetime import datetime
import json
import subprocess

# Initialize Flask application
app = Flask(__name__)

# Define file paths for various data storage locations
ROOT = Path(__file__).resolve().parent  # Project root directory
FEEDBACK_FILE = ROOT / "user_feedback.jsonl"  # User feedback storage (JSONL format)
REPORT_FILE = ROOT / "ai_test_report.json"  # AutoAI test report output
FEATURES_MD = ROOT / "ai_features.md"  # Feature roadmap document


@app.route("/")
def index():
    """
    Render the main chat interface.
    
    Returns:
        HTML: The main index page with the ChatGPT-like interface
    """
    return render_template("index.html", title="openai-plus")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Handle chat messages from the frontend.
    
    Accepts JSON payload with:
    - message: Text message from user
    - has_image: Boolean indicating if image was uploaded
    - has_audio: Boolean indicating if audio was uploaded
    
    Returns:
        JSON: Response containing a reply message
    """
    # Parse incoming JSON data, default to empty dict if none provided
    data = request.json or {}
    
    # Extract message and multi-modal flags
    message = data.get("message", "")
    has_image = bool(data.get("has_image"))
    has_audio = bool(data.get("has_audio"))
    
    # Build response based on input
    reply = [f"You said: {message}" if message else "Hello!"]
    
    # Acknowledge multi-modal inputs (image/audio processing is stubbed)
    if has_image:
        reply.append("I received an image.")
    if has_audio:
        reply.append("I received an audio clip.")
    
    return jsonify({"reply": " \\n".join(reply)})


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """
    Collect and store user feedback.
    
    Accepts JSON payload with:
    - message: Feedback text
    - rating: Numeric rating (optional)
    - feature_request: Feature request text (optional)
    - tags: Array of tags for categorization
    
    Feedback is stored in JSONL format (one JSON object per line)
    for easy parsing and analysis by auto_ai.py.
    
    Returns:
        JSON: Status confirmation
    """
    # Parse incoming feedback payload
    payload = request.json or {}
    
    # Structure feedback entry with timestamp
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": payload.get("message"),
        "rating": payload.get("rating"),
        "feature_request": payload.get("feature_request"),
        "tags": payload.get("tags", []),
    }
    
    # Append feedback to JSONL file (creates file if doesn't exist)
    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    
    return jsonify({"status": "ok"})


@app.route("/api/run_auto_ai", methods=["POST"])
def run_auto_ai():
    """
    Execute the auto_ai.py testing script and return results.
    
    This endpoint triggers the automated code analysis system which:
    1. Analyzes all Python files in the repository
    2. Checks syntax, code quality, and performance
    3. Generates improvement suggestions
    4. Saves a detailed report to ai_test_report.json
    
    Returns:
        JSON: Object containing:
        - stdout: Terminal output from auto_ai.py (last 4000 chars)
        - report: Parsed JSON report with metrics and suggestions
    """
    try:
        # Run auto_ai.py as subprocess with 3-minute timeout
        proc = subprocess.run(
            ["python", "auto_ai.py"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180
        )
        # Capture stdout, limit to last 4000 characters to prevent overflow
        stdout = (proc.stdout or "")[-4000:]
    except Exception as e:
        # Handle execution errors gracefully
        stdout = f"Error: {e}"
    
    # Attempt to load the generated report file
    report = {}
    if REPORT_FILE.exists():
        try:
            report = json.loads(REPORT_FILE.read_text())
        except Exception:
            report = {"error": "failed to read report"}
    
    return jsonify({"stdout": stdout, "report": report})


# Run the Flask development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
