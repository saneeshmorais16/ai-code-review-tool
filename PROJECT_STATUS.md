# Project Status

## Current Build Status

Starter implementation is complete locally. GitHub Actions is configured to run the test suite on pushes and pull requests.

## Completed Features

- Paste-code review endpoint.
- Multi-file upload review endpoint.
- Language detection for Python, JavaScript, TypeScript, HTML, and CSS.
- Static checks for long functions, hardcoded secret patterns, missing error handling, risky dynamic execution, TODO/FIXME comments, duplicate code hints, and testing gaps.
- Optional LLM wrapper that does not break when no API key is configured.
- Structured JSON output with issue type, severity, file path, line number, explanation, and suggested fix.
- SQLite-backed review history.
- Simple frontend for paste/upload review and severity-grouped results.
- Tests for secret scanning, risky code checks, output schema, health endpoint, and code review endpoint.

## Remaining Improvements

- Add repository ZIP ingestion with path filtering and size limits.
- Add richer AST checks for more languages.
- Add authenticated users and per-user review history.
- Add real provider adapters after privacy and data handling controls are defined.
- Add rate limiting and file size limits for hosted deployments.

## Testing Status

Latest local check:

- `pytest`: 6 passed

Run locally with:

```bash
pytest
```

## What Must Be Checked Before Making Public

- Confirm no `.env` files, credentials, logs, generated outputs, databases, local repositories, or uploads are tracked.
- Confirm examples do not contain real secrets or private source code.
- Confirm README does not claim production or commercial usage.
- Confirm optional LLM behavior is clearly documented as a starter wrapper.

## Files That Must Never Be Committed

- `.env`
- `.env.*`
- API keys, tokens, credentials, passwords, or private configuration
- `*.db`, `*.sqlite`, `*.sqlite3`
- Logs
- Generated PDFs
- `application_packets/`
- `generated_outputs/`
- `secrets/`
- `credentials/`
- `local_repos/`
- `uploads/`
