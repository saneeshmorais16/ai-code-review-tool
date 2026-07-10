from __future__ import annotations

from app.secret_scanner import scan_for_secrets


def test_secret_pattern_detection():
    issues = scan_for_secrets('OPENAI_API_KEY = "1234567890abcdef"', "settings.py")

    assert len(issues) == 1
    assert issues[0]["category"] == "security"
    assert issues[0]["severity"] == "critical"
    assert issues[0]["line_number"] == 1
