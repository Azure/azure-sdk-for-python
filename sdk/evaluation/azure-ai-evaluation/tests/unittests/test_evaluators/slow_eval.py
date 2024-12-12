# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import time
from typing import Dict
from typing_extensions import overload, override


from azure.ai.evaluation._evaluators._common import EvaluatorBase


class SlowEvaluator(EvaluatorBase[str]):
    """Test evaluator that just returns the input after a slight delay. Used for testing performance."""

    def __call__(
        self,
        *,
        query: str,
    ) -> Dict[str, str]:
        """Evaluate a collection of content safety metrics for the given query/response pair

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The content safety scores.
        :rtype: Dict[str, Union[str, float]]
        """
        return super().__call__(query=query)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, str]:
        time.sleep(0.5)
        return {"result": "done"}
