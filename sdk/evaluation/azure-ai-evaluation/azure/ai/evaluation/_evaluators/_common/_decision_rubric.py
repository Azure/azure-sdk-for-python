# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Decision support shared by built-in evaluators that package a Decision rubric beside their prompt."""

import json
import logging
from typing import Any, Optional, Union

from azure.ai.evaluation._exceptions import ErrorTarget
from azure.ai.evaluation._legacy.prompty._yaml_utils import load_yaml
from ._base_model_eval import ModelEvaluatorBase
from ._decision_strategy import BinaryScoring, DecisionEvaluationStrategy, LikertScoring
from ._model_runners import is_decision_model_config

LOGGER = logging.getLogger(__name__)


def rubric_strategy(
    evaluator: ModelEvaluatorBase,
    rubric_path: str,
    error_target: ErrorTarget,
    scoring: Optional[Union[BinaryScoring, LikertScoring]] = None,
) -> DecisionEvaluationStrategy:
    """Build the strategy that asks an evaluator's decision model the questions of a packaged rubric.

    The rubric's ``status`` question decides applicability and its ``result`` question is asked under the
    evaluator's result key. Unless ``scoring`` is given, binary evaluators score at the runner's probability
    threshold and the others on a 1 to 5 scale.

    :param evaluator: An evaluator configured with a decision model.
    :type evaluator: ~azure.ai.evaluation._evaluators._common.ModelEvaluatorBase
    :param rubric_path: The path of the rubric file with ``status`` and ``result`` questions.
    :type rubric_path: str
    :param error_target: The target of errors raised while interpreting answers.
    :type error_target: ~azure.ai.evaluation._exceptions.ErrorTarget
    :param scoring: Optional scoring that replaces the default.
    :type scoring: Optional[Union[BinaryScoring, LikertScoring]]
    :return: The evaluator's decision strategy.
    :rtype: DecisionEvaluationStrategy
    """
    rubric = json.loads(json.dumps(load_yaml(rubric_path)))
    runner = evaluator._decision_model_runner
    if scoring is None:
        if evaluator._binary_decision:
            scoring = BinaryScoring(runner.probability_threshold)
        else:
            scoring = LikertScoring(5, minimum=1)
    return DecisionEvaluationStrategy(
        runner,
        result_key=evaluator._result_key,
        error_target=error_target,
        questions={"status": rubric["status"], evaluator._result_key: rubric["result"]},
        scoring=scoring,
        threshold=evaluator._threshold,
        timeout=evaluator._LLM_CALL_TIMEOUT,
    )


def with_probability_threshold(model_config: Any, probability_threshold: Any, evaluator_name: str) -> Any:
    """Return the model configuration a binary evaluator passes to its base.

    A decision configuration is copied with ``probability_threshold`` overriding its own value; the decision
    runner validates it. Chat models ignore the value with a warning and keep their configuration unchanged.

    :param model_config: The caller's model configuration, which is never modified.
    :type model_config: Any
    :param probability_threshold: The caller's probability threshold, or None when not supplied.
    :type probability_threshold: Any
    :param evaluator_name: The evaluator name used in the warning.
    :type evaluator_name: str
    :return: The model configuration for the base.
    :rtype: Any
    """
    if probability_threshold is None:
        return model_config
    if is_decision_model_config(model_config):
        return {**model_config, "probability_threshold": probability_threshold}
    LOGGER.warning("%s ignores 'probability_threshold', which applies only to decision models.", evaluator_name)
    return model_config


def decode_message_list(value: Any) -> Any:
    """Decode a JSON-encoded list, such as a list of messages; any other value is returned unchanged.

    :param value: A response or query value.
    :type value: Any
    :return: The decoded list, or the original value.
    :rtype: Any
    """
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, ValueError):
            return value
        if isinstance(decoded, list):
            return decoded
    return value


def final_assistant_text(response: Any) -> Any:
    """Join the text of the assistant messages in a list of messages.

    An assistant message's text is its string content or the text items of its content list. Tool calls, tool
    results and other content are dropped so only the plain-text agent response remains. Any other value, such as
    a plain response or the content list of one conversation turn, is returned unchanged.

    :param response: A preprocessed list of messages, or another response value.
    :type response: Any
    :return: The assistant text, or the original response.
    :rtype: Any
    """
    if not isinstance(response, list) or not any(isinstance(item, dict) and "role" in item for item in response):
        return response
    text = []
    for message in response:
        if isinstance(message, dict) and message.get("role") == "assistant":
            content = message.get("content")
            if isinstance(content, str):
                text.append(content)
                continue
            for item in content or []:
                if isinstance(item, dict) and "text" in item:
                    text.append(item["text"])
    return "\n".join(text)
