# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, List, Optional
from typing_extensions import override
from abc import abstractmethod
import re
import numpy as np

from azure.ai.evaluation._evaluators._common import EvaluatorBase


class RegexEvaluatorBase(EvaluatorBase):
    """Base class for all evaluators that are regex-based and use pattern matching to extract answers.

    This class provides a framework for evaluators that need to extract structured answers from text
    using regular expressions. It handles the common pattern of:
    1. Using regex patterns to extract answers from predictions
    2. Comparing extracted answers against expected answers
    3. Computing accuracy and instruction-following metrics

    Child classes must implement the abstract methods:
        - extract_expected_answer: Extract the expected answer from the label
        - extract_regex: Extract a match object from the prediction using regex patterns
        - compute_match: Compare actual and extracted answers to determine correctness

    :param regex_patterns: A list of regex patterns to use for extracting answers from predictions.
        Each pattern should have a single capture group to extract the answer. If None, the child class
        must implement get_regex_patterns method.
    :type regex_patterns: Optional[List[str]]
    """

    def __init__(self, *, regex_patterns: Optional[list[str]] = None, threshold=0.5) -> None:
        super().__init__(threshold=threshold, _higher_is_better=True)
        self.regex_patterns = regex_patterns
        self.is_missing_regex_patterns = regex_patterns is None
        self.follow_instructions = []
        self.scores = []
        self.chain_of_thought_lengths = []

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Any]:
        """Produce a score evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        response = eval_input["response"]
        ground_truth = eval_input["ground_truth"]

        result = self.update(
                prediction=response,
                label=ground_truth,
                json_data={}
            )

        return result

    def update(self, prediction: str, label: str, json_data: dict) -> Dict[str, Any]:
        if self.is_missing_regex_patterns:
            self.regex_patterns = self.get_regex_patterns(prediction, label, json_data)
        expected_answer = self.extract_expected_answer(label, json_data)
        regex_match = self.extract_regex(prediction, label, json_data)

        if regex_match:
            extracted_answer = regex_match.group(1).strip()
            follow_instruction = 1
            chain_of_thought_length = self._get_chain_of_thought_length(
                prediction, regex_match.start()
            )
            self.chain_of_thought_lengths.append(chain_of_thought_length)
        else:
            extracted_answer = ""
            follow_instruction = 0
            chain_of_thought_length = -1

        score = self.compute_match(expected_answer, extracted_answer, label, json_data)
        self.scores.append(score)
        self.follow_instructions.append(follow_instruction)

        return {
            "score": score,
            "follow_instruction": follow_instruction,
            "extracted_answer": extracted_answer,
            "chain_of_thought_length": chain_of_thought_length,
        }

    def __aggregate__(self, line_results: List[str]) -> Dict[str, float]:
        """
        Base aggregation method for the RegexEvaluatorBase.
        This method aggregates the results of the metric across multiple lines of input data.
        Throws an exception if the input list or chain lengths is empty.
        """
        if not line_results:
            raise ValueError("line_results is empty passed to __aggregate__")

        # collect individual metric values
        scores = [r["score"] for r in line_results]
        follow_flags = [r["follow_instruction"] for r in line_results]

        # only include chain lengths where instruction was followed (non-negative)
        chain_lengths = [
            r.get("chain_of_thought_length", -1)
            for r in line_results
            if r.get("chain_of_thought_length", -1) >= 0
        ]

        # compute aggregate metrics
        accuracy = np.mean(scores)
        follow_instruction_rate = np.mean(follow_flags)
        chain_of_thought_length = np.mean(chain_lengths) if chain_lengths else -1

        return {
            "accuracy": accuracy,
            "follow_instruction_rate": follow_instruction_rate,
            "chain_of_thought_length": chain_of_thought_length,
        }

    def get_regex_patterns(
        self, prediction: str, label: str, json_data: dict
    ) -> List[str]:
        """
        Implement this method to get the regex patterns if you do not set them in the constructor.
        Regex patterns must have a single group to extract the answer.
        """
        raise NotImplementedError(
            "Regex pattern should be set in the constructor or implemented in this method."
        )

    @abstractmethod
    def extract_expected_answer(self, label: str, json_data: dict) -> str:
        """
        Abstract method to extract the expected answer from the label.

        Returns:
            str: The expected answer.
        """
        pass

    @abstractmethod
    def extract_regex(
        self, prediction: str, label: str, json_data: Dict
    ) -> Optional[re.Match]:
        """
        Abstract method to extract a match object from the prediction string based on the provided regex patterns.

        Returns:
            Optional[re.Match]: The extracted match object or None.
        """
        pass

    @abstractmethod
    def compute_match(
        self, actual_answer: str, extracted_answer: str, label: str, json_data: Dict
    ) -> int:
        """
        Abstract method to compare the actual answer to the extracted answer.

        Returns:
            int: 1 if the answers match, 0 otherwise.
        """
        pass

    def _extract_regex(
        self, prediction: str, label: str, json_data: Dict
    ) -> Optional[re.Match]:
        if self.regex_patterns:
            for regex_pattern in self.regex_patterns:
                match = re.search(regex_pattern, prediction)
                if match:
                    return match
        return None

    def _compute_match(
        self, actual_answer: str, extracted_answer: str, label: str, json_data: Dict
    ) -> int:
        return 1 if actual_answer == extracted_answer else 0

    def _get_chain_of_thought_length(self, prediction: str, match_index: int) -> int:
        return len(prediction[:match_index])