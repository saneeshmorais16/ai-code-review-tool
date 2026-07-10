from __future__ import annotations

from collections import Counter

from app.language_detection import detect_language
from app.llm_reviewer import optional_llm_review
from app.secret_scanner import scan_for_secrets
from app.static_checks import run_static_checks


def _summary(issues: list[dict], files_reviewed: int) -> dict:
    by_severity = Counter(issue["severity"] for issue in issues)
    by_category = Counter(issue["category"] for issue in issues)
    return {
        "files_reviewed": files_reviewed,
        "issue_count": len(issues),
        "by_severity": dict(by_severity),
        "by_category": dict(by_category),
    }


def review_code(code: str, file_path: str = "pasted_code.txt", language: str | None = None) -> dict:
    detected_language = language or detect_language(file_path=file_path, code=code)
    issues = []
    issues.extend(scan_for_secrets(code, file_path))
    issues.extend(run_static_checks(code, detected_language, file_path))
    issues.extend(optional_llm_review(code, detected_language, file_path))

    return {
        "id": None,
        "summary": _summary(issues, 1),
        "files": [{"file_path": file_path, "language": detected_language}],
        "issues": issues,
    }


def review_files(files: list[dict]) -> dict:
    all_issues = []
    reviewed_files = []
    for item in files:
        file_path = item.get("file_path", "uploaded_file.txt")
        code = item.get("code", "")
        language = detect_language(file_path=file_path, code=code)
        reviewed_files.append({"file_path": file_path, "language": language})
        all_issues.extend(scan_for_secrets(code, file_path))
        all_issues.extend(run_static_checks(code, language, file_path))
        all_issues.extend(optional_llm_review(code, language, file_path))

    return {
        "id": None,
        "summary": _summary(all_issues, len(files)),
        "files": reviewed_files,
        "issues": all_issues,
    }
