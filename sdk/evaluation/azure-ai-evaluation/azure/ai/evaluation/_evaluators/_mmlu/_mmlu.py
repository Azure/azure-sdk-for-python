# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
from azure.ai.evaluation._evaluators._common import RegexEvaluatorBase
from typing_extensions import overload, override

ANSWER_PATTERNS = [r"(?i)ANSWER\s*:\s*\$?([A-J])\$?"]


class MMLUEvaluator(RegexEvaluatorBase):
    """
    Evaluates model performance on the MMLU (Massive Multitask Language Understanding) benchmark.

    MMLU is a comprehensive benchmark that tests a model's understanding across 57 academic subjects
    ranging from mathematics and physics to history and law. It measures both breadth and depth of
    knowledge through multiple-choice questions.

    The evaluator expects answers in the format "ANSWER: A" (or B, C, D, etc.) and computes accuracy
    metrics both overall and grouped by subject and category. Use this evaluator when you want to
    assess a model's general knowledge and reasoning abilities across diverse academic domains.

    The MMLU score value is either 0 or 1, with higher scores indicating better performance.
    :param threshold: The threshold for the evaluation. Default is 0.5.
    :type threshold: float
    
    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START mmlu_score_evaluator]
            :end-before: [END mmlu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an MMLUEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START mmlu_score_evaluator]
            :end-before: [END mmlu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an MMLUEvaluator using Azure AI Project URL in following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_mmlu_score_evaluator]
            :end-before: [END threshold_mmlu_score_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call an MMLUEvaluator.
    """

    def __init__(self, *, threshold=0.5):
        super().__init__(regex_patterns=ANSWER_PATTERNS, threshold=threshold)
        self.subject2scores = defaultdict(list)
        self.category2scores = defaultdict(list)

    def update(self, prediction: str, label: str, json_data: dict) -> Dict[str, Any]:
        sample_metrics = super().update(prediction, label, json_data)
        try:
            label_dict = json.loads(label)
        except json.JSONDecodeError:
            raise ValueError("The label/ground_truth must be a valid JSON string.")
        
        subject = label_dict.get("subject")
        if subject is None:
            raise ValueError("The label/ground_truth JSON must contain a 'subject' key.")
        
        category = label_dict.get("category")
        if category is None:
            raise ValueError("The label/ground_truth JSON must contain a 'category' key.")

        if label_dict.get("answer") is None:
            raise ValueError("The label/ground_truth JSON must contain an 'answer' key.")

        self.subject2scores[subject].append(sample_metrics["score"])
        self.category2scores[category].append(sample_metrics["score"])

        sample_metrics.update(
            {
                "mmlu_score": sample_metrics["score"], # Just needed for _real_call
                "accuracy": sample_metrics["score"],
                "subject": subject,
                "category": category,
            }
        )

        return sample_metrics

    def __aggregate__(self, line_results: List[str]) -> Dict[str, float]:
        """Aggregate the results from the line results."""
        base_metrics = super().__aggregate__(line_results)

        # compute macro accuracy by subject
        subject2scores: Dict[Any, List[float]] = defaultdict(list)
        for r in line_results:
            if "subject" not in r:
                raise KeyError(f"Missing key 'subject' in line result: {r}")
            subject2scores[r["subject"]].append(r["score"])
        accuracy_macro_by_subject = (
            np.mean([np.mean(v) for v in subject2scores.values()])
            if subject2scores
            else float("nan")
        )

        # compute macro accuracy by category
        category2scores: Dict[Any, List[float]] = defaultdict(list)
        for r in line_results:
            if "category" not in r:
                raise KeyError(f"Missing key 'category' in line result: {r}")
            category2scores[r["category"]].append(r["score"])
        accuracy_macro_by_category = (
            np.mean([np.mean(v) for v in category2scores.values()])
            if category2scores
            else float("nan")
        )
        base_metrics.update(
            {
                "accuracy_macro_by_subject": accuracy_macro_by_subject,
                "accuracy_macro_by_category": accuracy_macro_by_category,
            }
        )

        return base_metrics

    def extract_expected_answer(self, label: str, json_data: dict) -> str:
        return json.loads(label).get("answer")

    def extract_regex(self, prediction: str, label: str, json_data: Dict) -> Any:
        return self._extract_regex(prediction, label, json_data)

    def compute_match(
        self, actual_answer: str, extracted_answer: str, label: str, json_data: Dict
    ) -> int:
        return self._compute_match(actual_answer, extracted_answer, label, json_data)

    @overload  # type: ignore
    def __call__(self, *, response: str, ground_truth: str):
        """
        Evaluate the MMLU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        The ground truth must be in serialized JSON string format containing the following fields:
        - subject: The subject area of the question
        - category: The category classification
        - answer: The correct answer
        :keyword ground_truth: The ground truth to be compared against in serialized JSON string format.
        :paramtype ground_truth: str
        :return: The MMLU score.
        :rtype: Dict[str, Any]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate the MMLU score between the response and the ground truth.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword ground_truth: The ground truth to be compared against.
        :paramtype ground_truth: str
        :return: The MMLU score.
        :rtype: Dict[str, Any]
        """
        return super().__call__(*args, **kwargs)
