from __future__ import annotations

import re

SECRET_PATTERNS = [
    ("hardcoded_secret", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
    ("private_key", re.compile(r"-----BEGIN (RSA|OPENSSH|PRIVATE) KEY-----")),
    ("bearer_token", re.compile(r"(?i)bearer\s+[a-z0-9._\-]{16,}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
]


def scan_for_secrets(code: str, file_path: str) -> list[dict]:
    issues = []
    for line_number, line in enumerate(code.splitlines(), start=1):
        for issue_type, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                issues.append(
                    {
                        "issue_type": issue_type,
                        "category": "security",
                        "severity": "critical",
                        "file_path": file_path,
                        "line_number": line_number,
                        "explanation": "A secret-like value appears to be hardcoded in source code.",
                        "suggested_fix": "Move secrets to a secure secret manager or environment variable and rotate exposed values.",
                    }
                )
    return issues
