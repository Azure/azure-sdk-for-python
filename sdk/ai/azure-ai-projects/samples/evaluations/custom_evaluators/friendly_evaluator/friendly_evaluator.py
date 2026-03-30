"""Custom evaluator that uses an LLM to assess the friendliness of a response."""

from openai import AzureOpenAI
from common_util.util import build_evaluation_messages, parse_evaluation_result


class FriendlyEvaluator:
    """Evaluates how friendly and approachable a response is using an LLM judge.

    This evaluator sends the query and response to an LLM, which returns a
    friendliness score (1-5), a pass/fail label, a reason, and a detailed explanation.

    :param model_config: A dict containing Azure OpenAI connection info. Expected keys:
        - azure_endpoint: The Azure OpenAI endpoint URL.
        - azure_deployment: The deployment/model name.
        - api_version: The API version (default: "2024-06-01").
        - api_key: (Optional) The API key. If not provided, DefaultAzureCredential is used.
    :param threshold: The minimum score (1-5) to be considered "Pass" (default: 3).
    """

    def __init__(self, *, model_config: dict, threshold: int = 3, **kwargs):
        self.model_config = model_config
        self.threshold = threshold
        api_key = model_config.get("api_key")

        if api_key:
            self.client = AzureOpenAI(
                azure_endpoint=model_config["azure_endpoint"],
                api_key=api_key,
                api_version=model_config.get("api_version", "2024-06-01"),
            )
        else:
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider

            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self.client = AzureOpenAI(
                azure_endpoint=model_config["azure_endpoint"],
                azure_ad_token_provider=token_provider,
                api_version=model_config.get("api_version", "2024-06-01"),
            )

        self.deployment = model_config["azure_deployment"]

    def __call__(self, *, query: str, response: str, **kwargs) -> dict:
        """Evaluate the friendliness of a response.

        :param query: The original user query.
        :param response: The response to evaluate.
        :return: A dict with score, label, reason, and explanation.
        """
        messages = build_evaluation_messages(query, response)

        completion = self.client.chat.completions.create(
            model=self.deployment,
            messages=messages,
            temperature=0.0,
            max_tokens=500,
        )

        raw_result = completion.choices[0].message.content
        if raw_result is None:
            raise ValueError("No content in completion response")
        return parse_evaluation_result(raw_result, self.threshold)
