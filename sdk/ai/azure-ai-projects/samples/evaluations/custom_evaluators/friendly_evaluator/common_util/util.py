"""Utility functions for custom evaluators."""

FRIENDLINESS_SYSTEM_PROMPT = """You are an expert evaluator that assesses how friendly, warm, and approachable
a response is. You evaluate responses on a scale of 1 to 5 based on the following criteria:

Score 1 (Very Unfriendly): The response is cold, dismissive, rude, or hostile.
Score 2 (Unfriendly): The response is curt, impersonal, or lacks warmth.
Score 3 (Neutral): The response is acceptable but neither particularly friendly nor unfriendly.
Score 4 (Friendly): The response is warm, polite, and shows genuine interest in helping.
Score 5 (Very Friendly): The response is exceptionally warm, encouraging, empathetic, and makes the user feel valued.

You MUST respond in the following JSON format only:
{
    "score": <integer 1-5>,
    "reason": "<brief reason for the score>",
    "explanation": "<detailed explanation of why the response received this score>",
    "tone": "<the overall tone detected, e.g. warm, neutral, dismissive>",
    "confidence": "<high, medium, or low confidence in the assessment>"
}
"""


def build_evaluation_instructions() -> str:
    """Return the system instructions for the LLM evaluation call.

    :return: The system prompt string for the Responses API.
    """
    return FRIENDLINESS_SYSTEM_PROMPT


def build_evaluation_input(query: str, response: str) -> str:
    """Build the user input for the LLM evaluation call.

    :param query: The original user query.
    :param response: The response to evaluate for friendliness.
    :return: A string prompt for the Responses API.
    """
    return (
        f"Please evaluate the friendliness of the following response.\n\n"
        f"Original query: {query}\n\n"
        f"Response to evaluate: {response}"
    )


def parse_evaluation_result(raw_result: str, threshold: int = 3) -> dict:
    """Parse the LLM's JSON response into a structured evaluation result.

    The return dict has the standard top-level keys (score, label, reason,
    threshold, passed) and a ``properties`` dict for any extra output fields
    the evaluator wants to surface.

    :param raw_result: The raw string output from the LLM.
    :param threshold: The minimum score to be considered "Pass".
    :return: A dict with score, label, reason, threshold, passed, and properties.
    """
    import json

    # Keys that are promoted to the top level of the result
    top_level_keys = {"score", "label", "reason"}

    try:
        # Try to extract JSON from the response (handle markdown code blocks)
        text = raw_result.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text.strip())
        score = max(1, min(5, int(result.get("score", threshold))))
        passed = score >= threshold

        # Collect any extra fields returned by the LLM into properties
        properties = {k: v for k, v in result.items() if k not in top_level_keys}

        return {
            # --- Required fields (must be present for the evaluation service) ---
            "score": score,
            "label": "Pass" if passed else "Fail",
            "reason": result.get("reason", "No reason provided"),
            # --- Optional fields ---
            "threshold": threshold,
            "passed": passed,
            "properties": properties,  # extra metadata surfaced in the evaluation results
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        return {
            "score": threshold,
            "label": "Fail",
            "reason": "Could not parse LLM response",
            "threshold": threshold,
            "passed": False,
        }
