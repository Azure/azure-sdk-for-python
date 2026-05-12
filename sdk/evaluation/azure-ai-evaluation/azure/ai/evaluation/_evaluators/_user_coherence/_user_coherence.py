# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
import math
import os
import logging
from typing import Dict, List, Optional, Union

from typing_extensions import overload, override

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._common._experimental import experimental

logger = logging.getLogger(__name__)


def _extract_text_content(content):
    """Extract text from message content, handling both string and list-of-content-items formats.

    Supports standard chat format (``{"type": "text", "text": ...}``) as well as
    Foundry trace format (``{"type": "output_text" | "input_text", "text": ...}``).

    :param content: The message content, either a string or a list of content items.
    :type content: Union[str, list]
    :return: The extracted text.
    :rtype: str
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                item_type = item.get("type", "")
                if item_type in ("text", "output_text", "input_text"):
                    texts.append(item.get("text", ""))
                elif "text" in item:
                    texts.append(item["text"])
            elif isinstance(item, str):
                texts.append(item)
        return " ".join(texts)
    return str(content) if content else ""


def normalize_trace_messages(messages: List[Dict]) -> List[Dict]:
    """Normalize messages from Foundry conversation traces to simple role/content dicts.

    Foundry trace messages contain extra fields (``created_by``, ``partition_key``,
    ``status``, etc.) and use content item types like ``output_text`` / ``input_text``.
    This function extracts the plain text and returns a list of ``{"role": ..., "content": ...}``
    dicts suitable for evaluation.

    Only messages with ``"type": "message"`` and role ``"user"`` or ``"assistant"`` are kept.

    :param messages: Raw message dicts from Foundry conversation traces.
    :type messages: List[Dict]
    :return: Simplified list of message dicts with "role" and "content" keys.
    :rtype: List[Dict]
    """
    normalized = []
    for msg in messages:
        role = msg.get("role", "")
        if role not in ("user", "assistant"):
            continue
        # Skip non-message items (e.g., tool_call, function_call)
        if msg.get("type") and msg["type"] != "message":
            continue
        text = _extract_text_content(msg.get("content", ""))
        if text:
            normalized.append({"role": role, "content": text})
    return normalized


def reformat_conversation_to_steps(messages: List[Dict]) -> str:
    """Convert a list of messages to the conversation_steps JSON format expected by the prompty.

    Pairs user and assistant messages sequentially into conversation steps. Each step contains a
    1-based conversation_step index, the user_question text, and the assistant_response text.

    :param messages: List of message dicts with 'role' and 'content' keys.
    :type messages: List[Dict]
    :return: JSON string in the conversation_steps format expected by the prompty.
    :rtype: str
    """
    user_messages = []
    assistant_messages = []

    for msg in messages:
        role = msg.get("role", "")
        content = _extract_text_content(msg.get("content", ""))

        if role == "user":
            user_messages.append(content)
        elif role == "assistant":
            assistant_messages.append(content)

    conversation_steps = []
    for i, user_msg in enumerate(user_messages):
        step = {
            "conversation_step": i + 1,
            "user_question": user_msg,
            "assistant_response": assistant_messages[i] if i < len(assistant_messages) else "",
        }
        conversation_steps.append(step)

    return json.dumps({"conversation_steps": conversation_steps}, indent=2)


@experimental
class UserCoherenceEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates user coherence (derail detection) across all turns of a multi-turn conversation.
    """

    _PROMPTY_FILE = "user_coherence.prompty"
    _RESULT_KEY = "user_coherence"

    _MIN_SCORE = 0
    _MAX_SCORE = 2

    id = "azureai://built-in/evaluators/user_coherence"
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
            _higher_is_better=True,
            **kwargs,
        )

    @overload
    def __call__(
        self,
        *,
        conversation: Dict,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate user coherence for a full multi-turn conversation.

        :keyword conversation: A conversation dict with a "messages" key containing
            a list of message dicts with "role" and "content" keys.
        :paramtype conversation: Dict
        :return: A dictionary with per-step and aggregate user coherence scores.
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        query: List[dict],
    ) -> Dict[str, Union[str, float]]:
        """Evaluate user coherence given a list of messages as the query.

        :keyword query: A list of message dicts representing the full conversation.
        :paramtype query: List[dict]
        :return: A dictionary with per-step and aggregate user coherence scores.
        :rtype: Dict[str, Union[str, float]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        return super().__call__(*args, **kwargs)

    @override
    async def _real_call(self, **kwargs):
        """Process the full conversation at once rather than per-turn.

        :keyword kwargs: The inputs to evaluate.
        :type kwargs: Dict
        :return: The evaluation result with per-step and aggregate scores.
        :rtype: Dict[str, Union[str, float]]
        """
        messages = self._extract_messages(kwargs)

        if not messages:
            raise EvaluationException(
                message="UserCoherenceEvaluator requires a conversation with messages. "
                "Provide either 'conversation' (dict with 'messages' key) or 'query' (list of message dicts).",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.EVALUATE,
            )

        # Reformat the full conversation into conversation_steps JSON
        conversation_steps_json = reformat_conversation_to_steps(messages)

        # Evaluate the whole conversation in one LLM call
        result = await self._do_eval({"conversation_steps": conversation_steps_json})
        return result

    @staticmethod
    def _extract_messages(kwargs: Dict) -> Optional[List[Dict]]:
        """Extract messages from kwargs, supporting both 'conversation' and 'query' inputs.

        :param kwargs: The keyword arguments.
        :type kwargs: Dict
        :return: List of message dicts, or None.
        :rtype: Optional[List[Dict]]
        """
        conversation = kwargs.get("conversation")
        if conversation is not None:
            if isinstance(conversation, dict) and "messages" in conversation:
                return conversation["messages"]
            if isinstance(conversation, list):
                return conversation

        query = kwargs.get("query")
        if isinstance(query, list):
            return query

        return None

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:  # type: ignore[override]
        """Call the prompty and parse the per-step derail scores.

        :param eval_input: Dict with 'conversation_steps' key containing the JSON string.
        :type eval_input: Dict
        :return: The evaluation result with per-step and aggregate scores.
        :rtype: Dict[str, Union[float, str, List]]
        """
        prompty_output_dict = await self._flow(timeout=self._LLM_CALL_TIMEOUT, **eval_input)
        llm_output = prompty_output_dict.get("llm_output", prompty_output_dict)

        if not isinstance(llm_output, dict):
            raise EvaluationException(
                message="UserCoherenceEvaluator: LLM returned invalid output (expected JSON object).",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.EVALUATE,
            )

        steps_metrics = llm_output.get("conversation_steps_metrics", [])

        # Compute aggregate score from non-null derail_scores
        valid_scores = [
            s["derail_score"]
            for s in steps_metrics
            if s.get("derail_score") is not None
        ]
        mean_score = sum(valid_scores) / len(valid_scores) if valid_scores else math.nan

        return {
            f"{self._result_key}": float(mean_score),
            f"{self._result_key}_per_step": steps_metrics,
            f"{self._result_key}_prompt_tokens": prompty_output_dict.get("input_token_count", 0),
            f"{self._result_key}_completion_tokens": prompty_output_dict.get("output_token_count", 0),
            f"{self._result_key}_total_tokens": prompty_output_dict.get("total_token_count", 0),
            f"{self._result_key}_finish_reason": prompty_output_dict.get("finish_reason", ""),
            f"{self._result_key}_model": prompty_output_dict.get("model_id", ""),
        }
