# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# A collection of very simple evaluators designed to test column mappings.
# (aka proper data file -> _call__ input mapping)

from typing import Dict, Union
from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import EvaluatorBase


class NonOptionalEval:
    def __init__(self):
        pass

    def __call__(self, query, response):
        return {"non_score": 0}


class HalfOptionalEval:
    def __init__(self):
        pass

    def __call__(self, query, *, response="default"):
        return {"half_score": 0 if response == "default" else 1}


class OptionalEval:
    def __init__(self):
        pass

    def __call__(self, *, query="default", response="default"):
        return {"opt_score": (0 if query == "default" else 1) + (0 if response == "default" else 2)}


class NoInputEval:
    def __init__(self):
        pass

    def __call__(self):
        return {"no_score": 0}


class EchoEval:
    def __init__(self):
        pass

    def __call__(self, *, query="default", response="default"):
        return {"echo_query": query, "echo_response": response}


class CountingEval(EvaluatorBase):
    """Returns an incrementing number, which can be reset as needed"""

    def __init__(self, **kwargs):
        self._count = 0
        super().__init__(**kwargs)

    def reset(self):
        self._count = 0

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, int]:
        self._count += 1
        return {"response": self._count}

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """"""

    @overload
    def __call__(self, *, conversation):
        """"""

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        return super().__call__(*args, **kwargs)
