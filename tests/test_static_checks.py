from __future__ import annotations

from app.static_checks import run_static_checks


def test_risky_code_detection():
    issues = run_static_checks("def run(x):\n    return eval(x)\n", "python", "tool.py")

    issue_types = {issue["issue_type"] for issue in issues}
    assert "risky_dynamic_execution" in issue_types


def test_todo_detection():
    issues = run_static_checks("// FIXME: handle errors\nfetch('/api')", "javascript", "app.js")

    issue_types = {issue["issue_type"] for issue in issues}
    assert "todo_or_fixme" in issue_types
    assert "missing_error_handling" in issue_types
