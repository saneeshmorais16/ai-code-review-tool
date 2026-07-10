from __future__ import annotations

import ast
import re
from collections import defaultdict


def _issue(issue_type: str, category: str, severity: str, file_path: str, line_number: int | None, explanation: str, suggested_fix: str) -> dict:
    return {
        "issue_type": issue_type,
        "category": category,
        "severity": severity,
        "file_path": file_path,
        "line_number": line_number,
        "explanation": explanation,
        "suggested_fix": suggested_fix,
    }


def _check_todos(lines: list[str], file_path: str) -> list[dict]:
    issues = []
    for index, line in enumerate(lines, start=1):
        if "TODO" in line or "FIXME" in line:
            issues.append(
                _issue(
                    "todo_or_fixme",
                    "maintainability",
                    "low",
                    file_path,
                    index,
                    "TODO/FIXME marker found.",
                    "Convert this marker into a tracked task or resolve it before release.",
                )
            )
    return issues


def _check_risky_calls(code: str, lines: list[str], language: str, file_path: str) -> list[dict]:
    issues = []
    patterns = [r"\beval\s*\(", r"\bexec\s*\("] if language == "python" else [r"\beval\s*\(", r"new\s+Function\s*\("]
    for index, line in enumerate(lines, start=1):
        if any(re.search(pattern, line) for pattern in patterns):
            issues.append(
                _issue(
                    "risky_dynamic_execution",
                    "security",
                    "high",
                    file_path,
                    index,
                    "Dynamic code execution can allow code injection or unexpected behavior.",
                    "Replace dynamic execution with explicit parsing or a restricted command map.",
                )
            )
    return issues


def _check_python_ast(code: str, file_path: str) -> list[dict]:
    issues = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [
            _issue(
                "syntax_error",
                "bug risk",
                "high",
                file_path,
                exc.lineno,
                "Python parser reported a syntax error.",
                "Fix the syntax error before review or execution.",
            )
        ]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
            if length > 40:
                issues.append(
                    _issue(
                        "long_function",
                        "maintainability",
                        "medium",
                        file_path,
                        node.lineno,
                        f"Function `{node.name}` is {length} lines long.",
                        "Split the function into smaller units with single responsibilities.",
                    )
                )
            has_try = any(isinstance(child, ast.Try) for child in ast.walk(node))
            risky_names = {"open", "requests", "urlopen", "connect"}
            calls = [child for child in ast.walk(node) if isinstance(child, ast.Call)]
            has_risky_call = any(
                isinstance(call.func, ast.Name) and call.func.id in risky_names
                for call in calls
            )
            if has_risky_call and not has_try:
                issues.append(
                    _issue(
                        "missing_error_handling",
                        "bug risk",
                        "medium",
                        file_path,
                        node.lineno,
                        f"Function `{node.name}` performs IO-like work without local error handling.",
                        "Add focused exception handling or return explicit errors to callers.",
                    )
                )
    return issues


def _check_js_function_lengths(lines: list[str], file_path: str) -> list[dict]:
    issues = []
    function_start = None
    brace_depth = 0
    for index, line in enumerate(lines, start=1):
        if function_start is None and re.search(r"\b(function|=>)\b", line):
            function_start = index
            brace_depth = line.count("{") - line.count("}")
        elif function_start is not None:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                length = index - function_start + 1
                if length > 45:
                    issues.append(
                        _issue(
                            "long_function",
                            "maintainability",
                            "medium",
                            file_path,
                            function_start,
                            f"JavaScript/TypeScript function is {length} lines long.",
                            "Extract smaller functions and isolate branching logic.",
                        )
                    )
                function_start = None
    return issues


def _check_missing_js_error_handling(lines: list[str], file_path: str) -> list[dict]:
    issues = []
    code = "\n".join(lines)
    risky = "fetch(" in code or "JSON.parse(" in code
    if risky and "try" not in code and ".catch(" not in code:
        line_number = next((i for i, line in enumerate(lines, start=1) if "fetch(" in line or "JSON.parse(" in line), 1)
        issues.append(
            _issue(
                "missing_error_handling",
                "bug risk",
                "medium",
                file_path,
                line_number,
                "Network or parsing code appears without error handling.",
                "Add try/catch or promise rejection handling with user-safe failure behavior.",
            )
        )
    return issues


def _check_duplicate_lines(lines: list[str], file_path: str) -> list[dict]:
    normalized_locations: dict[str, list[int]] = defaultdict(list)
    for index, line in enumerate(lines, start=1):
        normalized = line.strip()
        if len(normalized) >= 24 and not normalized.startswith(("#", "//", "/*", "*")):
            normalized_locations[normalized].append(index)

    issues = []
    for normalized, locations in normalized_locations.items():
        if len(locations) >= 3:
            issues.append(
                _issue(
                    "duplicate_code_hint",
                    "maintainability",
                    "low",
                    file_path,
                    locations[0],
                    "Similar code appears multiple times.",
                    "Consider extracting a helper or shared constant.",
                )
            )
    return issues


def _check_testing_gap(code: str, file_path: str) -> list[dict]:
    if "assert " in code or "test(" in code or "describe(" in code or "pytest" in code:
        return []
    return [
        _issue(
            "testing_gap",
            "testing gaps",
            "info",
            file_path,
            None,
            "No obvious test assertions were found in this snippet.",
            "Add focused tests for expected behavior and edge cases.",
        )
    ]


def run_static_checks(code: str, language: str, file_path: str) -> list[dict]:
    lines = code.splitlines()
    issues = []
    issues.extend(_check_todos(lines, file_path))
    issues.extend(_check_risky_calls(code, lines, language, file_path))
    issues.extend(_check_duplicate_lines(lines, file_path))
    issues.extend(_check_testing_gap(code, file_path))

    if language == "python":
        issues.extend(_check_python_ast(code, file_path))
    if language in {"javascript", "typescript"}:
        issues.extend(_check_js_function_lengths(lines, file_path))
        issues.extend(_check_missing_js_error_handling(lines, file_path))

    return issues
