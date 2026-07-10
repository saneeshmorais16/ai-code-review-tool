from __future__ import annotations

from app.config import ANTHROPIC_API_KEY, LLM_PROVIDER, OPENAI_API_KEY


def llm_available() -> bool:
    if LLM_PROVIDER == "openai":
        return bool(OPENAI_API_KEY)
    if LLM_PROVIDER == "anthropic":
        return bool(ANTHROPIC_API_KEY)
    return False


def optional_llm_review(code: str, language: str, file_path: str) -> list[dict]:
    """Placeholder wrapper for future LLM providers.

    The first portfolio version intentionally avoids making network calls. This
    keeps local reviews deterministic and prevents missing API keys from
    breaking the application.
    """
    if not llm_available():
        return []

    return [
        {
            "issue_type": "llm_review",
            "category": "maintainability",
            "severity": "info",
            "file_path": file_path,
            "line_number": None,
            "explanation": "LLM provider is configured, but this starter wrapper does not send code externally.",
            "suggested_fix": "Implement a provider adapter after adding data handling and privacy controls.",
        }
    ]
