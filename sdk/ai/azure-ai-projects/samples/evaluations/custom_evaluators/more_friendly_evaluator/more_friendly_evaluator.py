"""Custom evaluator that uses Azure OpenAI to assess the friendliness of a response."""

from openai import AzureOpenAI
from common_util.util import build_evaluation_instructions, build_evaluation_input, parse_evaluation_result


class MoreFriendlyEvaluator:
    """Evaluates how friendly and approachable a response is using an Azure OpenAI LLM judge.

    This evaluator receives a ``model_config`` dict that is automatically injected
    by the evaluation service when ``deployment_name`` is passed in the run's
    initialization parameters.  The dict contains Azure OpenAI connection details
    needed to construct an AzureOpenAI client.

    :param model_config: dict with azure_endpoint, api_key, api_version, azure_deployment.
    :param threshold: The minimum score (1-5) to be considered "Pass" (default: 3).
    """

    def __init__(self, *, model_config: dict, threshold: int = 3, **kwargs):
        self.client = AzureOpenAI(
            azure_endpoint=model_config["azure_endpoint"],
            api_key=model_config["api_key"],
            api_version=model_config.get("api_version"),
        )
        self.model_name = model_config.get("azure_deployment", model_config.get("model", ""))
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
