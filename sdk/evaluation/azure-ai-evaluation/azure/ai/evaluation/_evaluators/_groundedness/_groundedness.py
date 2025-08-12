# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
from inspect import signature
from typing import Dict, List, Optional, Union

from typing_extensions import overload, override
from azure.ai.evaluation._legacy._adapters._flows import AsyncPrompty

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation
from ..._common.utils import (
    ErrorBlame,
    ErrorTarget,
    EvaluationException,
    ErrorCategory,
    construct_prompty_model_config,
    validate_model_config,
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
    """
    Evaluates groundedness score for a given query (optional), response, and context or a multi-turn conversation,
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
    :keyword is_reasoning_model: (Preview) Adjusts prompty config
        for reasoning models when True.
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

    id = "azureai://built-in/evaluators/groundedness"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=3, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(
            current_dir, self._PROMPTY_FILE_NO_QUERY
        )  # Default to no query

        self._higher_is_better = True
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )
        self._model_config = model_config
        self.threshold = threshold

        # Cache whether AsyncPrompty.load supports the is_reasoning_model parameter.
        try:
            self._has_is_reasoning_model_param: bool = (
                "is_reasoning_model" in signature(AsyncPrompty.load).parameters
            )
        except Exception:  # Very defensive: if inspect fails, assume not supported
            self._has_is_reasoning_model_param = False

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
            current_dir = os.path.dirname(__file__)
            prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_WITH_QUERY)
            self._prompty_file = prompty_path
            prompty_model_config = construct_prompty_model_config(
                validate_model_config(self._model_config),
                self._DEFAULT_OPEN_API_VERSION,
                UserAgentSingleton().value,
            )

            if self._has_is_reasoning_model_param:
                self._flow = AsyncPrompty.load(
                    source=self._prompty_file,
                    model=prompty_model_config,
                    is_reasoning_model=self._is_reasoning_model,
                )
            else:
                self._flow = AsyncPrompty.load(
                    source=self._prompty_file,
                    model=prompty_model_config,
                )

        return super().__call__(*args, **kwargs)

    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result.
        :rtype: Union[DoEvalResult[T_EvalValue], AggregateResult[T_EvalValue]]
        """
        # Convert inputs into list of evaluable inputs.
        try:
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
        if "context" in kwargs or "conversation" in kwargs:
            return super()._convert_kwargs_to_eval_input(**kwargs)

        query = kwargs.get("query")
        response = kwargs.get("response")
        tool_definitions = kwargs.get("tool_definitions")

        if not query or not response or not tool_definitions:
            msg = f"{type(self).__name__}: Either 'conversation' or individual inputs must be provided. For Agent groundedness 'query', 'response' and 'tool_definitions' are required."
            raise EvaluationException(
                message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        context = self._get_context_from_agent_response(response, tool_definitions)
        if not context:
            raise EvaluationException(
                message=f"Context could not be extracted from agent response. Supported tools for groundedness are {self._SUPPORTED_TOOLS}. If supported tools are not used groundedness is not calculated.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.NOT_APPLICABLE,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        return super()._convert_kwargs_to_eval_input(
            response=response[-1], context=context, query=query
        )

    def _get_context_from_agent_response(self, response, tool_definitions):
        context = ""
        try:
            logger.debug("Extracting context from response")
            tool_calls = self._parse_tools_from_response(response=response)
            logger.debug(f"Tool Calls parsed successfully : {tool_calls}")
            if tool_calls:
                for tool_call in tool_calls:
                    if (
                        isinstance(tool_call, dict)
                        and tool_call.get("type") == "tool_call"
                    ):
                        tool_name = tool_call.get("name")
                        for tool in tool_definitions:
                            if (
                                tool.get("name") == tool_name
                                and tool.get("type") in self._SUPPORTED_TOOLS
                            ):
                                if tool_name == "file_search":
                                    tool_result = tool_call.get("tool_result")
                                    if tool_result:
                                        for result in tool_result:
                                            content_list = result.get("content")
                                            if content_list:
                                                for content in content_list:
                                                    text = content.get("text")
                                                    if text:
                                                        context = (
                                                            context + "\n" + str(text)
                                                        )
        except Exception as ex:
            logger.debug(f"Error extracting context from agent response : {str(ex)}")
            context = ""

        return context if context else