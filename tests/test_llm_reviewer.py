from app.llm_reviewer import optional_llm_review


def test_offline_demo_review_is_labelled():
    issues = optional_llm_review("print('hello')", "python", "demo.py")

    assert issues
    assert issues[0]["issue_type"] == "offline_demo_ai_review"
    assert "No code was sent" in issues[0]["explanation"]
