from kerf.prompts import construct_prompt


class TestConstructPrompt:
    def test_summarization(self):
        prompt = construct_prompt("summarization", "some text")
        assert "summarization engine" in prompt
        assert "some text" in prompt
        assert "Return only raw JSON" in prompt

    def test_classification_with_categories(self):
        prompt = construct_prompt(
            "classification", "bug report", {"categories": "bug, feature"}
        )
        assert "bug, feature" in prompt
        assert "bug report" in prompt

    def test_extraction_with_fields(self):
        prompt = construct_prompt(
            "structured_extraction", "contact info", {"fields": "name, email"}
        )
        assert "name, email" in prompt
        assert "contact info" in prompt

    def test_unknown_task_uses_fallback(self):
        prompt = construct_prompt("unknown_type", "data")
        assert "Analyze input" in prompt
        assert "data" in prompt

    def test_empty_params(self):
        prompt = construct_prompt("summarization", "text", {})
        assert "text" in prompt
