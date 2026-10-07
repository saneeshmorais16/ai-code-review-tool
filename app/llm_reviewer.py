from __future__ import annotations

import json
import urllib.error
import urllib.request

from app.config import (
    AI_REVIEW_MODE,
    AI_REVIEW_TIMEOUT_SECONDS,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

SYSTEM_PROMPT = (
    "You are a cautious code review assistant. Do not execute code. "
    "Return concise JSON issues with issue_type, category, severity, explanation, and suggested_fix. "
    "Mention that human review is required before relying on findings."
)


def llm_available() -> bool:
    if AI_REVIEW_MODE != "live":
        return False
    if LLM_PROVIDER == "openai":
        return bool(OPENAI_API_KEY)
    if LLM_PROVIDER == "anthropic":
        return bool(ANTHROPIC_API_KEY)
    return False


def _offline_demo_issue(file_path: str) -> dict:
    return {
        "issue_type": "offline_demo_ai_review",
        "category": "maintainability",
        "severity": "info",
        "file_path": file_path,
        "line_number": None,
        "explanation": "Offline demo mode is active. No code was sent to an external AI provider.",
        "suggested_fix": "Set AI_REVIEW_MODE=live and configure a provider API key only after reviewing privacy and data-handling requirements. Human review is still required.",
    }


def _parse_json_issues(payload: str, file_path: str) -> list[dict]:
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        return [
            {
                "issue_type": "ai_review_unstructured_response",
                "category": "maintainability",
                "severity": "info",
                "file_path": file_path,
                "line_number": None,
                "explanation": "The AI provider returned non-JSON feedback, so it was not trusted as structured review output.",
                "suggested_fix": "Read provider output manually and keep human review in the loop.",
            }
        ]
    if isinstance(parsed, dict):
        parsed = parsed.get("issues", [])
    if not isinstance(parsed, list):
        return []
    issues: list[dict] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        issues.append(
            {
                "issue_type": str(item.get("issue_type", "ai_review")),
                "category": str(item.get("category", "maintainability")),
                "severity": str(item.get("severity", "info")),
                "file_path": file_path,
                "line_number": item.get("line_number"),
                "explanation": str(item.get("explanation", "AI provider returned a review note.")),
                "suggested_fix": str(item.get("suggested_fix", "Validate this suggestion with human review before applying.")),
            }
        )
    return issues


def _post_json(url: str, headers: dict[str, str], body: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=AI_REVIEW_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _openai_review(code: str, language: str, file_path: str) -> list[dict]:
    response = _post_json(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {OPENAI_API_KEY}"},
        {
            "model": OPENAI_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this {language} file named {file_path}. Return JSON only.\n\n{code[:12000]}"},
            ],
        },
    )
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "[]")
    return _parse_json_issues(content, file_path)


def _anthropic_review(code: str, language: str, file_path: str) -> list[dict]:
    response = _post_json(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        {
            "model": ANTHROPIC_MODEL,
            "max_tokens": 1200,
            "temperature": 0,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": f"Review this {language} file named {file_path}. Return JSON only.\n\n{code[:12000]}"}],
        },
    )
    parts = response.get("content", [])
    content = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    return _parse_json_issues(content, file_path)


def optional_llm_review(code: str, language: str, file_path: str) -> list[dict]:
    """Run optional AI review without executing submitted code.

    Default offline demo mode returns a labelled informational finding and
    never sends code externally. Live mode requires explicit environment
    configuration and provider keys.
    """
    if not llm_available():
        return [_offline_demo_issue(file_path)] if AI_REVIEW_MODE == "offline_demo" else []

    try:
        if LLM_PROVIDER == "openai":
            return _openai_review(code, language, file_path)
        if LLM_PROVIDER == "anthropic":
            return _anthropic_review(code, language, file_path)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [
            {
                "issue_type": "ai_review_provider_error",
                "category": "maintainability",
                "severity": "info",
                "file_path": file_path,
                "line_number": None,
                "explanation": f"AI provider review failed safely: {exc.__class__.__name__}. Static review results are still available.",
                "suggested_fix": "Check provider configuration and keep human review in the loop before acting on AI feedback.",
            }
        ]
    return []
