# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Dict, List
from ._patch_agents import AgentsOperations
from ._patch_datasets import DatasetsOperations
from ._patch_evaluation_rules import EvaluationRulesOperations
from ._patch_telemetry import TelemetryOperations
from ._patch_connections import ConnectionsOperations
from ._patch_memories import BetaMemoryStoresOperations
from ._operations import (
    BetaEvaluationTaxonomiesOperations,
    BetaEvaluatorsOperations,
    BetaInsightsOperations,
    BetaRedTeamsOperations,
    BetaSchedulesOperations,
    BetaOperations as GeneratedBetaOperations,
)


_BETA_CUSTOM_HEADERS: Dict[str, str] = {"MyHeader": "MyValue"}


class _HeaderInjectingProxy:
    """A proxy that injects custom HTTP request headers into all public method calls on the wrapped object."""

    def __init__(self, wrapped: Any, headers: Dict[str, str]) -> None:
        object.__setattr__(self, "_wrapped", wrapped)
        object.__setattr__(self, "_headers", headers)

    def __getattr__(self, name: str) -> Any:
        attr = getattr(object.__getattribute__(self, "_wrapped"), name)
        if callable(attr) and not name.startswith("_"):
            inj_headers = object.__getattribute__(self, "_headers")

            def _wrapper(*args: Any, **kwargs: Any) -> Any:
                existing = kwargs.pop("headers", {}) or {}
                kwargs["headers"] = {**inj_headers, **existing}
                return attr(*args, **kwargs)

            return _wrapper
        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(object.__getattribute__(self, "_wrapped"), name, value)


class BetaOperations(GeneratedBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
    """:class:`~azure.ai.projects.operations.BetaEvaluationTaxonomiesOperations` operations"""
    evaluators: BetaEvaluatorsOperations
    """:class:`~azure.ai.projects.operations.BetaEvaluatorsOperations` operations"""
    insights: BetaInsightsOperations
    """:class:`~azure.ai.projects.operations.BetaInsightsOperations` operations"""
    memory_stores: BetaMemoryStoresOperations
    """:class:`~azure.ai.projects.operations.BetaMemoryStoresOperations` operations"""
    red_teams: BetaRedTeamsOperations
    """:class:`~azure.ai.projects.operations.BetaRedTeamsOperations` operations"""
    schedules: BetaSchedulesOperations
    """:class:`~azure.ai.projects.operations.BetaSchedulesOperations` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Wrap all public operation properties to inject custom headers on every HTTP request
        self.evaluation_taxonomies = _HeaderInjectingProxy(self.evaluation_taxonomies, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]
        self.evaluators = _HeaderInjectingProxy(self.evaluators, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]
        self.insights = _HeaderInjectingProxy(self.insights, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]
        # Replace with patched class that includes begin_update_memories, then wrap for header injection
        raw_memory_stores = BetaMemoryStoresOperations(self._client, self._config, self._serialize, self._deserialize)
        self.memory_stores = _HeaderInjectingProxy(raw_memory_stores, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]
        self.red_teams = _HeaderInjectingProxy(self.red_teams, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]
        self.schedules = _HeaderInjectingProxy(self.schedules, _BETA_CUSTOM_HEADERS)  # type: ignore[assignment]


__all__: List[str] = [
    "AgentsOperations",
    "BetaEvaluationTaxonomiesOperations",
    "EvaluationRulesOperations",
    "BetaEvaluatorsOperations",
    "BetaInsightsOperations",
    "BetaMemoryStoresOperations",
    "BetaOperations",
    "BetaRedTeamsOperations",
    "BetaSchedulesOperations",
    "ConnectionsOperations",
    "DatasetsOperations",
    "TelemetryOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
