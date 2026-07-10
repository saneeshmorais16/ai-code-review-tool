from __future__ import annotations

from pathlib import Path

from app.config import SUPPORTED_EXTENSIONS


def detect_language(file_path: str | None = None, code: str = "") -> str:
    if file_path:
        suffix = Path(file_path).suffix.lower()
        if suffix in SUPPORTED_EXTENSIONS:
            return SUPPORTED_EXTENSIONS[suffix]

    sample = code.lstrip().lower()
    if sample.startswith("<!doctype html") or sample.startswith("<html"):
        return "html"
    if "def " in code or "import " in code or "__name__" in code:
        return "python"
    if "interface " in code or ": string" in code or ": number" in code:
        return "typescript"
    if "function " in code or "const " in code or "let " in code:
        return "javascript"
    if "{" in code and "}" in code and ";" in code:
        return "css"
    return "unknown"
