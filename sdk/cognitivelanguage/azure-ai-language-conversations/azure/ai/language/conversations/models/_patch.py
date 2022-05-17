# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ast import Dict
from typing import List, Optional
from ._models import (
    CustomConversationTaskParameters as CustomConversationTaskParametersGenerated,
)

# class CustomConversationTaskParameters(CustomConversationTaskParametersGenerated):
#     """Input parameters necessary for a CustomConversation task.

#     All required parameters must be populated in order to send to Azure.

#     :ivar project_name: Required. The name of the project to use.
#     :vartype project_name: str
#     :ivar deployment_name: Required. The name of the deployment to use.
#     :vartype deployment_name: str
#     :ivar verbose: If true, the service will return more detailed information in the response.
#     :vartype verbose: bool
#     :ivar is_logging_enabled: If true, the service will keep the query for further review.
#     :vartype is_logging_enabled: bool
#     :ivar direct_target: The name of a target project to forward the request to.
#     :vartype direct_target: str
#     :ivar target_project_parameters: A dictionary representing the parameters for each target
#      project.
#     :vartype target_project_parameters: dict[str,
#      ~azure.ai.language.conversations.models.AnalysisParameters]
#     """

#     def __init__(
#         self,
#         *,
#         project_name: str,
#         deployment_name: str,
#         verbose: Optional[bool] = None,
#         is_logging_enabled: Optional[bool] = None,
#         direct_target: Optional[str] = None,
#         target_project_parameters: Optional[Dict[str, "_models.AnalysisParameters"]] = None,
#         **kwargs
#     ):
#         """
#         :keyword project_name: Required. The name of the project to use.
#         :paramtype project_name: str
#         :keyword deployment_name: Required. The name of the deployment to use.
#         :paramtype deployment_name: str
#         :keyword verbose: If true, the service will return more detailed information in the response.
#         :paramtype verbose: bool
#         :keyword is_logging_enabled: If true, the service will keep the query for further review.
#         :paramtype is_logging_enabled: bool
#         :keyword direct_target: The name of a target project to forward the request to.
#         :paramtype direct_target: str
#         :keyword target_project_parameters: A dictionary representing the parameters for each target
#          project.
#         :paramtype target_project_parameters: dict[str,
#          ~azure.ai.language.conversations.models.AnalysisParameters]
#         """
#         super().__init__(
#             project_name=project_name,
#             deployment_name=deployment_name,
#             verbose=verbose,
#             is_logging_enabled=is_logging_enabled,
#             direct_target=direct_target,
#             target_project_parameters=target_project_parameters,
#             **kwargs
#         )
#         self.string_index_type = "UnicodeCodePoint"
#         self._attribute_map.update({"string_index_type": {"key": "stringIndexType", "type": "str"}})


__all__: List[str] = [
    # "CustomConversationTaskParameters"
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
