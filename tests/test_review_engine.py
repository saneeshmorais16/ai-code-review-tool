from __future__ import annotations

from app.review_engine import review_code


def test_review_output_schema_contains_required_fields():
    result = review_code("print(eval('1+1'))", file_path="sample.py")

    assert result["summary"]["files_reviewed"] == 1
    assert result["files"][0]["language"] == "python"
    assert result["issues"]
    required = {"issue_type", "category", "severity", "file_path", "line_number", "explanation", "suggested_fix"}
    assert required.issubset(result["issues"][0].keys())
