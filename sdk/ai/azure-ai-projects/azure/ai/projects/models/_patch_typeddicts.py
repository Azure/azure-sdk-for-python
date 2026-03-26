# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Dict, Any
from typing_extensions import Literal, Required, TypedDict


class EvalGraderAzureAIEvaluator(TypedDict, total=False):
    """AzureAIEvaluatorGrader.

    :ivar type: The object type, which is always ``azure_ai_evaluator``. Required. Default value is
     "azure_ai_evaluator".
    :vartype type: str
    :ivar name: The name of the grader. Required.
    :vartype name: str
    :ivar evaluator_name: The name of the evaluator. Required.
    :vartype evaluator_name: str
    :ivar evaluator_version: The version of the evaluator. Latest version if not specified.
    :vartype evaluator_version: str
    :ivar initialization_parameters: The initialization parameters for the evaluation. Must support
     structured outputs.
    :vartype initialization_parameters: dict[str, any]
    :ivar data_mapping: The model to use for the evaluation. Must support structured outputs.
    :vartype data_mapping: dict[str, str]
    """

    type: Required[Literal["azure_ai_evaluator"]]
    """The object type, which is always ``azure_ai_evaluator``. Required. Default value is
     \"azure_ai_evaluator\"."""
    name: Required[str]
    """The name of the grader. Required."""
    evaluator_name: Required[str]
    """The name of the evaluator. Required."""
    evaluator_version: str
    """The version of the evaluator. Latest version if not specified."""
    initialization_parameters: Dict[str, Any]
    """The initialization parameters for the evaluation. Must support structured outputs."""
    data_mapping: Dict[str, str]
    """The model to use for the evaluation. Must support structured outputs."""
