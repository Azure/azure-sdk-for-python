# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import logging
from typing import Dict, Union, List, Optional
from typing_extensions import overload, override
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common._experimental import experimental


logger = logging.getLogger(__name__)


@experimental
class ToolSuccessEvaluator(PromptyEvaluatorBase[Union[str, bool]]):
    """The Tool Success evaluator determines whether tool calls done by an AI agent includes failures or not. This evaluator focuses solely on tool call results
    and tool definitions, disregarding user's query to the agent, conversation history and agent's final response.
    Although tool definitions is optional, providing them can help the evaluator better understand the context of the tool calls made by the agent.
    Please note that this evaluator validates tool calls for potential technical failures like errors, exceptions, timeouts and empty results (only in cases where empty results could indicate a failure).
    It does not assess the correctness or the tool result itself, like mathematical errors and unrealistic field values like name="668656"
    Scoring is binary:
    - TRUE: All tool calls were successful
    - FALSE: At least one tool call failed

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    .. admonition:: Example:
        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START tool_success_evaluator]
            :end-before: [END tool_success_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ToolSuccessEvaluator with a tool definitions and response.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START tool_success_evaluator]
            :end-before: [END tool_success_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ToolSuccessEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    """

    _PROMPTY_FILE = "tool_success.prompty"
    _RESULT_KEY = "tool_success"
    _OPTIONAL_PARAMS = ["tool_definitions"]

    id = "azureai://built-in/evaluators/tool_success"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, credential=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            credential=credential,
            **kwargs,
        )

    @overload
    def __call__(
        self,
        *,
        response: Union[str, List[dict]],
        tool_definitions: Optional[Union[dict, List[dict]]] = None,
    ) -> Dict[str, Union[str, bool]]:
        """Evaluate tool call success for a given response, and optionally tool definitions

        Example with list of messages:
            evaluator = ToolSuccessEvaluator(model_config)
            response = [{'createdAt': 1700000070, 'run_id': '0', 'role': 'assistant', 'content': [{'type': 'text', 'text': '**Day 1:** Morning: Visit Louvre Museum (9 AM - 12 PM)...'}]}]

            result = evaluator(response=response, )

        :keyword response: The response being evaluated, either a string or a list of messages (full agent response potentially including tool calls)
        :paramtype response: Union[str, List[dict]]
        :keyword tool_definitions: Optional tool definitions to use for evaluation.
        :paramtype tool_definitions: Union[dict, List[dict]]
        :return: A dictionary with the tool success evaluation results.
        :rtype: Dict[str, Union[str, bool]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Invokes the instance using the overloaded __call__ signature.

        For detailed parameter types and return value documentation, see the overloaded __call__ definition.
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[bool, str]]:  # type: ignore[override]
        """Do Tool Success evaluation.
        :param eval_input: The input to the evaluator. Expected to contain whatever inputs are needed for the _flow method
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """

        if "response" not in eval_input:
            raise EvaluationException(
                message="response, is a required inputs to the Tool Success evaluator.",
                internal_message="response, is a required inputs to the Tool Success evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.TOOL_SUCCESS_EVALUATOR,
            )
        if eval_input["response"] is None or eval_input["response"] == []:
            raise EvaluationException(
                message="response cannot be None or empty for the Tool Success evaluator.",
                internal_message="response cannot be None or empty for the Tool Success evaluator.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.TOOL_SUCCESS_EVALUATOR,
            )

        eval_input["tool_calls"] = reformat_tool_calls_results(eval_input["response"], logger)

        if "tool_definitions" in eval_input:
            tool_definitions = eval_input["tool_definitions"]
            filtered_tool_definitions = filter_to_used_tools(
                tool_definitions=tool_definitions,
                msgs_list=eval_input["response"],
                logger=logger,
            )
            eval_input["tool_definitions"] = reformat_tool_definitions(filtered_tool_definitions, logger)

        llm_output = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        if isinstance(llm_output, dict):
            success = llm_output.get("success", False)
            if isinstance(success, str):
                success = success.upper() == "TRUE"

            success_result = "pass" if success == True else "fail"
            reason = llm_output.get("explanation", "")
            return {
                f"{self._result_key}": success,
                f"{self._result_key}_result": success_result,
                f"{self._result_key}_reason": reason,
                f"{self._result_key}_details": llm_output.get("details", ""),
            }
        if logger:
            logger.warning("LLM output is not a dictionary, returning False for the success.")
        return {self._result_key: False}


def filter_to_used_tools(tool_definitions, msgs_list, logger=None):
    """Filters the tool definitions to only include those that were actually used in the messages lists."""
    try:
        used_tool_names = set()
        any_tools_used = False

        for msg in msgs_list:
            if msg.get("role") == "assistant" and "content" in msg:
                for content in msg.get("content", []):
                    if content.get("type") == "tool_call":
                        any_tools_used = True
                        if "tool_call" in content and "function" in content["tool_call"]:
                            used_tool_names.add(content["tool_call"]["function"])
                        elif "name" in content:
                            used_tool_names.add(content["name"])

        filtered_tools = [tool for tool in tool_definitions if tool.get("name") in used_tool_names]
        if any_tools_used and not filtered_tools:
            if logger:
                logger.warning("No tool definitions matched the tools used in the messages. Returning original list.")
            filtered_tools = tool_definitions

        return filtered_tools
    except Exception as e:
        if logger:
            logger.warning(f"Failed to filter tool definitions, returning original list. Error: {e}")
        return tool_definitions


def _get_tool_calls_results(agent_response_msgs):
    """Extracts formatted agent tool calls and results from response."""
    agent_response_text = []
    tool_results = {}

    # First pass: collect tool results

    for msg in agent_response_msgs:
        if msg.get("role") == "tool" and "tool_call_id" in msg:
            for content in msg.get("content", []):
                if content.get("type") == "tool_result":
                    result = content.get("tool_result")
                    tool_results[msg["tool_call_id"]] = f"[TOOL_RESULT] {result}"

    # Second pass: parse assistant messages and tool calls
    for msg in agent_response_msgs:
        if "role" in msg and msg.get("role") == "assistant" and "content" in msg:

            for content in msg.get("content", []):

                if content.get("type") == "tool_call":
                    if "tool_call" in content and "function" in content.get("tool_call", {}):
                        tc = content.get("tool_call", {})
                        func_name = tc.get("function", {}).get("name", "")
                        args = tc.get("function", {}).get("arguments", {})
                        tool_call_id = tc.get("id")
                    else:
                        tool_call_id = content.get("tool_call_id")
                        func_name = content.get("name", "")
                        args = content.get("arguments", {})
                    args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
                    call_line = f"[TOOL_CALL] {func_name}({args_str})"
                    agent_response_text.append(call_line)
                    if tool_call_id in tool_results:
                        agent_response_text.append(tool_results[tool_call_id])

    return agent_response_text


def reformat_tool_calls_results(response, logger=None):
    try:
        if response is None or response == []:
            return ""
        agent_response = _get_tool_calls_results(response)
        if agent_response == []:
            # If no message could be extracted, likely the format changed, fallback to the original response in that case
            if logger:
                logger.warning(
                    f"Empty agent response extracted, likely due to input schema change. Falling back to using the original response: {response}"
                )
            return response
        return "\n".join(agent_response)
    except:
        # If the agent response cannot be parsed for whatever reason (e.g. the converter format changed), the original response is returned
        # This is a fallback to ensure that the evaluation can still proceed. See comments on reformat_conversation_history for more details.
        if logger:
            logger.warning(f"Agent response could not be parsed, falling back to original response: {response}")
        return response


def reformat_tool_definitions(tool_definitions, logger=None):
    try:
        output_lines = ["TOOL_DEFINITIONS:"]
        for tool in tool_definitions:
            name = tool.get("name", "unnamed_tool")
            desc = tool.get("description", "").strip()
            params = tool.get("parameters", {}).get("properties", {})
            param_names = ", ".join(params.keys()) if params else "no parameters"
            output_lines.append(f"- {name}: {desc} (inputs: {param_names})")
        return "\n".join(output_lines)
    except Exception as e:
        # If the tool definitions cannot be parsed for whatever reason, the original tool definitions are returned
        # This is a fallback to ensure that the evaluation can still proceed. See comments on reformat_conversation_history for more details.
        if logger:
            logger.warning(
                f"Tool definitions could not be parsed, falling back to original definitions: {tool_definitions}"
            )
        return tool_definitions
