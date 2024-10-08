# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from collections import Counter
from typing import List

from promptflow._utils.async_utils import async_run_allowing_running_loop

from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException


class _AsyncF1ScoreEvaluator:
    def __init__(self):
        pass

    async def __call__(self, *, response: str, ground_truth: str, **kwargs):
        """
        Evaluate F1 score.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The F1 score.
        :rtype: Dict[str, float]
        """
        # Validate inputs
        if not (response and response.strip() and response != "None") or not (
            ground_truth and ground_truth.strip() and ground_truth != "None"
        ):
            msg = "Both 'response' and 'ground_truth' must be non-empty strings."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                error_category=ErrorCategory.MISSING_FIELD,
                error_blame=ErrorBlame.USER_ERROR,
                error_target=ErrorTarget.F1_EVALUATOR,
            )

        # Run f1 score computation.
        f1_result = self._compute_f1_score(response=response, ground_truth=ground_truth)

        return {"f1_score": f1_result}

    @classmethod
    def _compute_f1_score(cls, response: str, ground_truth: str) -> float:
        import re
        import string

        class QASplitTokenizer:
            """Quality assurance tokenizer that splits text on whitespace."""

            def __call__(self, line) -> List[str]:
                """Tokenizes an input line using split() on whitespace

                :param line: The input segment to be tokenized
                :type line: str
                :return: The tokenized segment
                :rtype: List[str]
                """

                return line.split()

        def normalize_text(text: str) -> str:
            """Lower text and remove punctuation, articles and extra whitespace.

            :param text: The text to be normalized
            :type text: str
            :return: The normalized text
            :rtype: str
            """

            def remove_articles(text):
                return re.sub(r"\b(a|an|the)\b", " ", text)

            def white_space_fix(text):
                return " ".join(text.split())

            def remove_punctuation(text):
                exclude = set(string.punctuation)
                return "".join(ch for ch in text if ch not in exclude)

            def lower(text):
                return text.lower()

            return white_space_fix(remove_articles(remove_punctuation(lower(text))))

        tokenizer = QASplitTokenizer()
        prediction_tokens = tokenizer(normalize_text(response))
        reference_tokens = tokenizer(normalize_text(ground_truth))

        common_tokens = Counter(prediction_tokens) & Counter(reference_tokens)
        num_common_tokens = sum(common_tokens.values())

        if num_common_tokens == 0:
            f1 = 0.0
        else:
            precision = 1.0 * num_common_tokens / len(prediction_tokens)
            recall = 1.0 * num_common_tokens / len(reference_tokens)

            f1 = (2.0 * precision * recall) / (precision + recall)

        return f1


class F1ScoreEvaluator:
    """
    Initialize a f1 score evaluator for calculating F1 score.

    **Usage**

    .. code-block:: python

        eval_fn = F1ScoreEvaluator()
        result = eval_fn(
            response="The capital of Japan is Tokyo.",
            ground_truth="Tokyo is Japan's capital, known for its blend of traditional culture \
                and technological advancements.")

    **Output format**

    .. code-block:: python

        {
            "f1_score": 0.42
        }
    """

    def __init__(self):
        self._async_evaluator = _AsyncF1ScoreEvaluator()

    def __call__(self, *, response: str, ground_truth: str, **kwargs):
        """
        Evaluate F1 score.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be evaluated.
        :paramtype ground_truth: str
        :return: The F1 score.
        :rtype: Dict[str, float]
        """

        return async_run_allowing_running_loop(
            self._async_evaluator, response=response, ground_truth=ground_truth, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
