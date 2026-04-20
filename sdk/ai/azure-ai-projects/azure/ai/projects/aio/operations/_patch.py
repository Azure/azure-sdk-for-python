# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List
from ._patch_agents_async import AgentsOperations
from ._patch_datasets_async import DatasetsOperations
from ._patch_evaluation_rules_async import EvaluationRulesOperations
from ._patch_telemetry_async import TelemetryOperations
from ._patch_connections_async import ConnectionsOperations
from ._patch_memories_async import BetaMemoryStoresOperations
from ._patch_sessions_async import BetaAgentsOperations
from ...operations._patch import _BETA_OPERATION_FEATURE_HEADERS, _OperationMethodHeaderProxy
from ._operations import (
    BetaEvaluationTaxonomiesOperations,
    BetaEvaluatorsOperations,
    BetaInsightsOperations,
    BetaOperations as GeneratedBetaOperations,
    BetaRedTeamsOperations,
    BetaSchedulesOperations,
    BetaSkillsOperations,
    BetaToolboxesOperations,
)


class BetaOperations(GeneratedBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    agents: BetaAgentsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaAgentsOperations` operations"""
    evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaEvaluationTaxonomiesOperations` operations"""
    evaluators: BetaEvaluatorsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaEvaluatorsOperations` operations"""
    insights: BetaInsightsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaInsightsOperations` operations"""
    memory_stores: BetaMemoryStoresOperations
    """:class:`~azure.ai.projects.aio.operations.BetaMemoryStoresOperations` operations"""
    red_teams: BetaRedTeamsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaRedTeamsOperations` operations"""
    schedules: BetaSchedulesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaSchedulesOperations` operations"""
    toolboxes: BetaToolboxesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaToolboxesOperations` operations"""
    skills: BetaSkillsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaSkillsOperations` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Replace with patched class that includes upload()
        self.evaluators = BetaEvaluatorsOperations(self._client, self._config, self._serialize, self._deserialize)
        # Replace with patched class that adds file-path overload to upload_session_file
        self.agents = BetaAgentsOperations(self._client, self._config, self._serialize, self._deserialize)
        # Replace with patched class that includes begin_update_memories
        self.memory_stores = BetaMemoryStoresOperations(self._client, self._config, self._serialize, self._deserialize)

        for property_name, foundry_features_value in _BETA_OPERATION_FEATURE_HEADERS.items():
            setattr(
                self,
                property_name,
                _OperationMethodHeaderProxy(getattr(self, property_name), foundry_features_value),
            )


__all__: List[str] = [
    "AgentsOperations",
    "BetaAgentsOperations",
    "BetaEvaluationTaxonomiesOperations",
    "BetaEvaluatorsOperations",
    "BetaInsightsOperations",
    "BetaMemoryStoresOperations",
    "BetaOperations",
    "BetaRedTeamsOperations",
    "BetaSchedulesOperations",
    "BetaSkillsOperations",
    "BetaToolboxesOperations",
    "ConnectionsOperations",
    "DatasetsOperations",
    "EvaluationRulesOperations",
    "TelemetryOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
