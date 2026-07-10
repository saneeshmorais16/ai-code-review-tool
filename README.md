# AI Code Review Tool

AI Code Review Tool is a portfolio-ready starter app that reviews pasted code or uploaded files and returns structured feedback about bugs, security concerns, complexity, maintainability, readability, testing gaps, and improvement suggestions.

The first version works locally without any LLM API key. It uses deterministic static rules by default, with an optional LLM-compatible wrapper left in place for future provider integration.

## Problem Statement

Small teams and individual developers often want quick feedback before opening a pull request, but many tools either require external services or are too heavy for early-stage projects. This project provides a lightweight, local-first review workflow with structured JSON output and review history.

## Why It Matters

The app demonstrates practical software engineering around AI-adjacent tooling: API design, static analysis, optional provider boundaries, frontend interaction, persistence, automated tests, and safe repository hygiene.

## Tech Stack

- Python
- FastAPI
- SQLite
- Pydantic
- JavaScript, HTML, and CSS
- pytest
- GitHub Actions

## Core Features

- Paste-code review.
- File upload review.
- Language detection for Python, JavaScript, TypeScript, HTML, and CSS.
- Static checks for long functions, secret-like values, missing error handling, risky `eval`/`exec`, TODO/FIXME markers, duplicate code hints, and testing gaps.
- Optional LLM review wrapper that stays disabled unless configured.
- Structured review output.
- SQLite review history.
- Simple browser frontend.

## Architecture Overview

```text
Frontend
  -> FastAPI endpoints
  -> language detection
  -> secret scanner
  -> static checks
  -> optional LLM wrapper
  -> structured JSON response
  -> SQLite review history
```

## Example Code Review Output

```json
{
  "id": 1,
  "summary": {
    "files_reviewed": 1,
    "issue_count": 2,
    "by_severity": {
      "critical": 1,
      "high": 1
    },
    "by_category": {
      "security": 2
    }
  },
  "files": [
    {
      "file_path": "demo.py",
      "language": "python"
    }
  ],
  "issues": [
    {
      "issue_type": "hardcoded_secret",
      "category": "security",
      "severity": "critical",
      "file_path": "demo.py",
      "line_number": 1,
      "explanation": "A secret-like value appears to be hardcoded in source code.",
      "suggested_fix": "Move secrets to a secure secret manager or environment variable and rotate exposed values."
    }
  ]
}
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

## Run the API

```bash
python run.py
```

Or:

```bash
uvicorn app.main:app --reload
```

Open the frontend:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET http://127.0.0.1:8000/health
```

Review code:

```bash
curl -X POST "http://127.0.0.1:8000/review/code" \
  -H "Content-Type: application/json" \
  -d '{"file_path":"demo.py","code":"print(eval(\"1+1\"))"}'
```

## Run Tests

```bash
pytest
```

GitHub Actions runs the same test command on pushes and pull requests.

## Responsible AI and Limitations

- This starter version uses local static rules by default.
- Optional LLM review is a placeholder wrapper and does not send code to external providers.
- Static checks can produce false positives and false negatives.
- Do not use this project to review private repositories or sensitive code without explicit data handling controls.
- This project does not claim production readiness or commercial use.

## Future Improvements

- Add repository ZIP upload with allowlisted file types and size limits.
- Add deeper Python AST checks and JavaScript parser-based analysis.
- Add configurable rule severities.
- Add SARIF export.
- Add real LLM provider adapters with privacy controls and redaction.
- Add authentication and per-user histories for hosted use.

## No-Secrets Note

Do not commit API keys, `.env` files, tokens, credentials, passwords, private repositories, private code, logs, generated PDFs, temporary application packets, SQLite databases, uploads, or generated outputs. Use `.env.example` only for placeholder names.
