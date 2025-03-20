# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from concurrent.futures import as_completed
from typing import TypeVar, Dict, List

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor
from typing_extensions import override

from azure.ai.evaluation._evaluators._common import EvaluatorBase

T = TypeVar("T")


class MultiEvaluatorBase(EvaluatorBase[T]):
    """
    Base class for evaluators that contain and run multiple other evaluators to produce a
    suite of metrics.

    Child classes still need to implement the __call__ methods, but they shouldn't need a _do_eval.

    :param evaluators: The list of evaluators to run when this evaluator is called.
    :type evaluators: List[~azure.ai.evaluation._evaluators._common.EvaluatorBase]
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any
    :return: An evaluator that runs multiple other evaluators and combines their results.
    """

    def __init__(self, evaluators: List[EvaluatorBase[T]], **kwargs):
        self._threshold = kwargs.pop("threshold", 3)
        self._higher_is_better = kwargs.pop("_higher_is_better", False)
        super().__init__(threshold=self._threshold, _higher_is_better=self._higher_is_better)
        self._parallel = kwargs.pop("_parallel", True)
        self._evaluators = evaluators

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, T]:
        """Run each evaluator, possibly in parallel, and combine the results into
        a single large dictionary containing each evaluation. Inputs are passed
        directly to each evaluator without additional processing.


        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        results: Dict[str, T] = {}
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                # pylint: disable=no-value-for-parameter
                futures = {executor.submit(evaluator, **eval_input): evaluator for evaluator in self._evaluators}

                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(**eval_input)
                # Ignore is to avoid mypy getting upset over the amount of duck-typing
                # that's going on to shove evaluators around like this.
                results.update(result)  # type: ignore[arg-type]

        return results
