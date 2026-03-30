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
    "label": "<Pass or Fail>",
    "reason": "<brief reason for the score>",
    "explanation": "<detailed explanation of why the response received this score>"
}

A score of 3 or above is considered "Pass", below 3 is "Fail".
"""


def build_evaluation_messages(query: str, response: str) -> list:
    """Build the messages list for the LLM evaluation call.

    :param query: The original user query.
    :param response: The response to evaluate for friendliness.
    :return: A list of message dicts for the chat completion API.
    """
    return [
        {"role": "system", "content": FRIENDLINESS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Please evaluate the friendliness of the following response.\n\n"
                f"Original query: {query}\n\n"
                f"Response to evaluate: {response}"
            ),
        },
    ]


def parse_evaluation_result(raw_result: str, threshold: int = 3) -> dict:
    """Parse the LLM's JSON response into a structured evaluation result.

    :param raw_result: The raw string output from the LLM.
    :param threshold: The minimum score to be considered "Pass".
    :return: A dict with score, label, reason, and explanation.
    """
    import json

    try:
        # Try to extract JSON from the response (handle markdown code blocks)
        text = raw_result.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]
        result = json.loads(text.strip())
        score = int(result.get("score", threshold))
        return {
            "score": max(1, min(5, score)),
            "label": result.get("label", "Pass" if score >= threshold else "Fail"),
            "reason": result.get("reason", "No reason provided"),
            "explanation": result.get("explanation", "No explanation provided"),
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        return {
            "score": threshold,
            "label": "Pass",
            "reason": "Could not parse LLM response",
            "explanation": f"Raw LLM output: {raw_result}",
        }
