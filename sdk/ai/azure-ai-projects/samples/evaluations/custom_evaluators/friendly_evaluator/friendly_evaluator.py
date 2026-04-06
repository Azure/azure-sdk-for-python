"""Custom evaluator that uses an LLM to assess the friendliness of a response."""

from openai import OpenAI
from common_util.util import build_evaluation_instructions, build_evaluation_input, parse_evaluation_result


class FriendlyEvaluator:
    """Evaluates how friendly and approachable a response is using an LLM judge.

    This evaluator sends the query and response to an LLM via the OpenAI Responses
    API, which returns a friendliness score (1-5), a pass/fail label, a reason,
    and a detailed explanation.

    :param api_key: The OpenAI API key.
    :param model_name: The model_name to use for evaluation (e.g. "gpt-4o").
    :param threshold: The minimum score (1-5) to be considered "Pass" (default: 3).
    """

    def __init__(self, *, api_key: str, model_name: str, threshold: int = 3, **kwargs):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.threshold = threshold

    def __call__(self, *, query: str, response: str, **kwargs) -> dict:
        """Evaluate the friendliness of a response.

        :param query: The original user query.
        :param response: The response to evaluate.
        :return: A dict with score, label, reason, threshold, and properties.
        """
        result = self.client.responses.create(
            model=self.model_name,
            instructions=build_evaluation_instructions(),
            input=build_evaluation_input(query, response),
            temperature=0.0,
            max_output_tokens=500,
        )

        raw_result = result.output_text
        if raw_result is None:
            raise ValueError("No content in response")
        return parse_evaluation_result(raw_result, self.threshold)
