from typing import Any, Dict

PROMPT_TEMPLATES = {
    "summarization": (
        "You are a precise summarization engine.\n"
        "Distill the input to its core meaning in 1-3 sentences. "
        "Cut filler, redundancy, and restatement. "
        "A good summary says less than the input but loses nothing important.\n"
        "Return JSON: {{\"summary\": \"...\"}}"
    ),
    "structured_extraction": (
        "You are a structured data extraction engine.\n"
        "Extract exactly these fields from the input: {fields}\n"
        "Return JSON with those exact keys. "
        "If a field is not present in the input, use null."
    ),
    "classification": (
        "You are a classification engine.\n"
        "Classify the input into exactly one of these categories: {categories}\n"
        "Return JSON: {{\"category\": \"...\", \"confidence\": \"high\"|\"medium\"|\"low\"}}"
    ),
}


def construct_prompt(
    task_type: str, input_text: str, template_params: Dict[str, Any] = None
) -> str:
    template_params = template_params or {}
    template = PROMPT_TEMPLATES.get(task_type, "Analyze input and return structured JSON.")
    return (
        template.format(**template_params)
        + "\n\nInput:\n"
        + input_text
        + "\n\nCRITICAL: Return only raw JSON. Start with '{'."
    )
