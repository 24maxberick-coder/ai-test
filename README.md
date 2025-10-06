# openai-plus (ai-test)

A Flask-based, ChatGPT-like AI interface with multi-modal inputs, theme (black/white) toggle, and a continuous feedback-driven testing loop. The GUI mimics ChatGPT while integrating an AutoAI script to repeatedly test and improve features based on ai_features.md and live user feedback.

## Features
- ChatGPT-like web UI (Flask + HTML/CSS/JS) with dark/light ("black/white") switch
- Multi-modal inputs: text, image placeholder, audio placeholder plumbing (stubs)
- Feedback collection UI and API endpoint writing to user_feedback.jsonl
- AutoAI testing integration: run repository analysis and print JSON report in UI
- Favicon and tab: browser tab title set to `openai-plus` and favicon at `static/favicon.png`
- Roadmap driven by ai_features.md and user feedback snapshot

## Project Structure
- app.py — Flask server and API routes (/api/chat, /api/feedback, /api/run_auto_ai)
- templates/index.html — ChatGPT-like front-end
- static/style.css — Styles including dark/light theme
- static/script.js — Front-end logic, chat, feedback, AutoAI triggers
- static/favicon.png — Favicon (OpenAI logo with green plus: placeholder file)
- auto_ai.py — Automated code analysis and report generator (ai_test_report.json)
- ai_features.md — Community/prioritized features list to guide work

## Quickstart
1) Clone and install
```
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install flask
# Optional: pytest, pylint/flake8 if you plan to extend tests
```

2) Run the Flask app
```
python app.py
```
Then open http://localhost:5000 in your browser.

3) Use the UI
- Type a message and click Send
- Toggle theme between light and black (dark)
- Provide feedback in the panel and submit
- Click "Run AutoAI Tests" to execute auto_ai.py and see stdout + report

## Continuous Improvement Loop
- Feedback is stored in user_feedback.jsonl
- AutoAI outputs ai_test_report.json with metrics and suggestions
- Contributors should regularly review ai_features.md and feedback to prioritize tasks

## Contributing
- Open an issue describing desired features or bugs
- When adding features, update ai_features.md and consider new tags for feedback
- Ensure auto_ai.py covers new files in complexity/performance checks

## Deployment
- Any WSGI host works. For gunicorn:
```
export FLASK_APP=app:app
pip install gunicorn
gunicorn -b 0.0.0.0:5000 app:app
```
- Behind Nginx or on a PaaS (Railway/Render/Fly/Heroku), map port 5000

## Notes
- The favicon currently is a placeholder. Replace static/favicon.png with a 32x32 PNG of the OpenAI logo overlaid with a green plus ➕ (top-right).
- Image/Audio uploads are stubbed for privacy; the backend receives only flags has_image/has_audio. Wire to actual processing as needed.
- Keep the tab name as `openai-plus` to match requirements.
