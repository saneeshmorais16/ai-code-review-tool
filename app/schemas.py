from __future__ import annotations

from pydantic import BaseModel, Field


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1)
    file_path: str = "pasted_code.txt"
    language: str | None = None


class ReviewIssue(BaseModel):
    issue_type: str
    category: str
    severity: str
    file_path: str
    line_number: int | None = None
    explanation: str
    suggested_fix: str


class ReviewedFile(BaseModel):
    file_path: str
    language: str


class ReviewSummary(BaseModel):
    files_reviewed: int
    issue_count: int
    by_severity: dict[str, int]
    by_category: dict[str, int]


class ReviewResponse(BaseModel):
    id: int | None = None
    summary: ReviewSummary
    files: list[ReviewedFile]
    issues: list[ReviewIssue]
