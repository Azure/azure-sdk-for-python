# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os, logging
from typing import Dict, List, Optional, Union, Any, Tuple

from typing_extensions import overload, override
from azure.ai.evaluation._legacy.prompty import AsyncPrompty

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import ConversationValidator, ValidatorInterface
from azure.ai.evaluation._model_configurations import Conversation
from ..._common.utils import (
    ErrorBlame,
    ErrorTarget,
    EvaluationException,
    ErrorCategory,
    construct_prompty_model_config,
    validate_model_config,
    simplify_messages,
)

try:
    from ..._user_agent import UserAgentSingleton
except ImportError:

    class UserAgentSingleton:
        @property
        def value(self) -> str:
            return "None"


logger = logging.getLogger(__name__)


class GroundednessEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """Evaluates groundedness score for a given query (optional), response, and context or a multi-turn conversation,
    including reasoning.

    The groundedness measure assesses the correspondence between claims in an AI-generated answer and the source
    context, making sure that these claims are substantiated by the context. Even if the responses from LLM are
    factually correct, they'll be considered ungrounded if they can't be verified against the provided sources
    (such as your input source or your database). Use the groundedness metric when you need to verify that
    AI-generated responses align with and are validated by the provided context.

    Groundedness scores range from 1 to 5, with 1 being the least grounded and 5 being the most grounded.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param threshold: The threshold for the groundedness evaluator. Default is 3.
    :type threshold: int
    :param credential: The credential for authenticating to Azure AI service.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword is_reasoning_model: If True, the evaluator will use reasoning model configuration (o1/o3 models).
        This will adjust parameters like max_completion_tokens and remove unsupported parameters. Default is False.
    :paramtype is_reasoning_model: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START groundedness_evaluator]
            :end-before: [END groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a GroundednessEvaluator.

    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_groundedness_evaluator]
            :end-before: [END threshold_groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a GroundednessEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START groundedness_evaluator]
            :end-before: [END groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call GroundednessEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE_NO_QUERY = "groundedness_without_query.prompty"
    _PROMPTY_FILE_WITH_QUERY = "groundedness_with_query.prompty"
    _RESULT_KEY = "groundedness"
    _OPTIONAL_PARAMS = ["query"]
    _SUPPORTED_TOOLS = ["file_search"]

    _validator: ValidatorInterface
    _validator_with_query: ValidatorInterface

    id = "azureai://built-in/evaluators/groundedness"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=3, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_NO_QUERY)  # Default to no query

        # Initialize input validator
        self._validator = ConversationValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=False,
        )

        self._validator_with_query = ConversationValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=True
        )


        self._higher_is_better = True
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            credential=credential,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )
        self._model_config = model_config
        self._credential = credential
        self.threshold = threshold
        # Needs to be set because it's used in call method to re-validate prompt if `query` is provided

    @overload
    def __call__(
        self,
        *,
        response: str,
        context: str,
        query: Optional[str] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate groundedness for given input of response, context

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be evaluated.
        :paramtype context: str
        :keyword query: The query to be evaluated. Optional parameter for use with the `response`
            and `context` parameters. If provided, a different prompt template will be used for evaluation.
        :paramtype query: Optional[str]
        :return: The groundedness score.
        :rtype: Dict[str, float]
        """

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: List[dict],
        tool_definitions: List[dict],
    ) -> Dict[str, Union[str, float]]:
        """Evaluate groundedness for agent response with tool calls. Only file_search tool is supported.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response from the agent to be evaluated.
        :paramtype response: List[dict]
        :keyword tool_definitions: The tool definitions used by the agent.
        :paramtype tool_definitions: List[dict]
        :return: The groundedness score.
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate groundedness for a conversation

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The groundedness score.
        :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate groundedness. Accepts either a query, response, and context for a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated. Mutually exclusive with `conversation`. Optional parameter for use
            with the `response` and `context` parameters. If provided, a different prompt template will be used for
            evaluation.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated. Mutually exclusive with the `conversation` parameter.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated. Mutually exclusive with the `conversation` parameter.
        :paramtype context: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]]
        """

        if kwargs.get("query", None):
            self._ensure_query_prompty_loaded()

        return super().__call__(*args, **kwargs)

    def _ensure_query_prompty_loaded(self):
        """Switch to the query prompty file if not already loaded."""

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_WITH_QUERY)

        self._prompty_file = prompty_path
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(self._model_config),
            self._DEFAULT_OPEN_API_VERSION,
            UserAgentSingleton().value,
        )
        self._flow = AsyncPrompty.load(
            source=self._prompty_file,
            model=prompty_model_config,
            token_credential=self._credential,
            is_reasoning_model=self._is_reasoning_model,
        )

    def _has_context(self, eval_input: dict) -> bool:
        """
        Return True if eval_input contains a non-empty 'context' field.
        Treats None, empty strings, empty lists, and lists of empty strings as no context.
        """
        context = eval_input.get("context", None)
        if not context:
            return False
        if context == "<>":  # Special marker for no context
            return False
        if isinstance(context, list):
            return any(str(c).strip() for c in context)
        if isinstance(context, str):
            return bool(context.strip())
        return True

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        if eval_input.get("query", None) is None:
            return await super()._do_eval(eval_input)

        contains_context = self._has_context(eval_input)

        simplified_query = simplify_messages(eval_input["query"], drop_tool_calls=contains_context)
        simplified_response = simplify_messages(eval_input["response"], drop_tool_calls=False)

        # Build simplified input
        simplified_eval_input = {
            "query": simplified_query,
            "response": simplified_response,
            "context": eval_input["context"],
        }

        # Replace and call the parent method
        return await super()._do_eval(simplified_eval_input)

    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Union[DoEvalResult[T_EvalValue], AggregateResult[T_EvalValue]]
        """
        # Convert inputs into list of evaluable inputs.
        try:
            # Validate input before processing
            if kwargs.get("context") or kwargs.get("conversation"):
                self._validator.validate_eval_input(kwargs)
            else:
                self._validator_with_query.validate_eval_input(kwargs)
            return await super()._real_call(**kwargs)
        except EvaluationException as ex:
            if ex.category == ErrorCategory.NOT_APPLICABLE:
                return {
                    self._result_key: self._NOT_APPLICABLE_RESULT,
                    f"{self._result_key}_result": "pass",
                    f"{self._result_key}_threshold": self.threshold,
                    f"{self._result_key}_reason": f"Supported tools were not called. Supported tools for groundedness are {self._SUPPORTED_TOOLS}.",
                }
            else:
                raise ex

    def _convert_kwargs_to_eval_input(self, **kwargs):
        if kwargs.get("context") or kwargs.get("conversation"):
            return super()._convert_kwargs_to_eval_input(**kwargs)
        query = kwargs.get("query")
        response = kwargs.get("response")
        tool_definitions = kwargs.get("tool_definitions")

        if query and self._prompty_file != self._PROMPTY_FILE_WITH_QUERY:
            self._ensure_query_prompty_loaded()

        if (not query) or (not response):  # or not tool_definitions:
            msg = f"{type(self).__name__}: Either 'conversation' or individual inputs must be provided. For Agent groundedness 'query' and 'response' are required."
            raise EvaluationException(
                message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )
        context = self._get_context_from_agent_response(response, tool_definitions)

        filtered_response = self._filter_file_search_results(response)
        return super()._convert_kwargs_to_eval_input(response=filtered_response, context=context, query=query)

    def _filter_file_search_results(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out file_search tool results from the messages."""
        file_search_ids = self._get_file_search_tool_call_ids(messages)
        return [
            msg for msg in messages if not (msg.get("role") == "tool" and msg.get("tool_call_id") in file_search_ids)
        ]

    def _get_context_from_agent_response(self, response, tool_definitions):
        """Extract context text from file_search tool results in the agent response."""
        NO_CONTEXT = "<>"
        context = ""
        try:
            logger.debug("Extracting context from response")
            tool_calls = self._parse_tools_from_response(response=response)
            logger.debug(f"Tool Calls parsed successfully: {tool_calls}")

            if not tool_calls:
                return NO_CONTEXT

            context_lines = []
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict) or tool_call.get("type") != "tool_call":
                    continue

                tool_name = tool_call.get("name")
                if tool_name != "file_search":
                    continue

                # Extract tool results
                for result in tool_call.get("tool_result", []):
                    results = result if isinstance(result, list) else [result]
                    for r in results:
                        file_name = r.get("file_name", "Unknown file name")
                        for content in r.get("content", []):
                            text = content.get("text")
                            if text:
                                context_lines.append(f"{file_name}:\n- {text}---\n\n")

            context = "\n".join(context_lines) if len(context_lines) > 0 else None

        except Exception as ex:
            logger.debug(f"Error extracting context from agent response : {str(ex)}")
            context = None

        context = context if context else NO_CONTEXT
        return context

    def _get_file_search_tool_call_ids(self, query_or_response):
        """Return a list of tool_call_ids for file search tool calls."""
        tool_calls = self._parse_tools_from_response(query_or_response)
        return [tc.get("tool_call_id") for tc in tool_calls if tc.get("name") == "file_search"]
