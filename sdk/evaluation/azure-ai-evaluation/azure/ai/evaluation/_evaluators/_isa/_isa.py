# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import overload, override
from typing import Union

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase

@experimental
class ISAEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
    id = "inference_of_sensitive_attributes"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.ISA,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
        context: str = None,
    ): 
        """Evaluate a given query/response pair and context for inference of sensitive attributes

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be used for evaluation.
        :paramtype context: str
        :return: The inference of sensitive attributes label.
        :rtype: Dict[str, Union[str, bool]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate a given query/response pair and context for inference of sensitive attributes

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be used for evaluation.
        :paramtype context: str
        :return: The inference of sensitive attributes label.
        :rtype: Dict[str, Union[str, bool]]
        """
        
        return super().__call__(*args, **kwargs)
