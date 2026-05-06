# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from functools import wraps
import inspect
from typing import Any, Callable, List
from ..models._patch import _FOUNDRY_FEATURES_HEADER_NAME, _BETA_OPERATION_FEATURE_HEADERS, _has_header_case_insensitive
from ._patch_agents import AgentsOperations
from ._patch_datasets import DatasetsOperations
from ._patch_evaluation_rules import EvaluationRulesOperations
from ._patch_telemetry import TelemetryOperations
from ._patch_connections import ConnectionsOperations
from ._patch_memories import BetaMemoryStoresOperations
from ._patch_sessions import BetaAgentsOperations
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


def _method_accepts_keyword_headers(method: Callable[..., Any]) -> bool:
    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        return False

    for parameter in signature.parameters.values():
        if parameter.name == "headers":
            return True
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            return True

    return False


class _OperationMethodHeaderProxy:
    """Proxy that injects the Foundry-Features header into public operation method calls."""

    def __init__(self, operation: Any, foundry_features_value: str):
        object.__setattr__(self, "_operation", operation)
        object.__setattr__(self, "_foundry_features_value", foundry_features_value)

    def __getattr__(self, name: str) -> Any:
        attribute = getattr(self._operation, name)

        if name.startswith("_") or not callable(attribute) or not _method_accepts_keyword_headers(attribute):
            return attribute

        @wraps(attribute)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            headers = kwargs.get("headers")
            if headers is None:
                kwargs["headers"] = {_FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features_value}
            elif not _has_header_case_insensitive(headers, _FOUNDRY_FEATURES_HEADER_NAME):
                try:
                    headers[_FOUNDRY_FEATURES_HEADER_NAME] = self._foundry_features_value
                except Exception:  # pylint: disable=broad-except
                    # Fall back to replacing invalid/immutable header containers.
                    kwargs["headers"] = {
                        _FOUNDRY_FEATURES_HEADER_NAME: self._foundry_features_value,
                    }

            return attribute(*args, **kwargs)

        return _wrapped

    def __dir__(self) -> list:
        return dir(self._operation)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._operation, name, value)


class BetaOperations(GeneratedBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    agents: BetaAgentsOperations
    """:class:`~azure.ai.projects.operations.BetaAgentsOperations` operations"""
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
    toolboxes: BetaToolboxesOperations
    """:class:`~azure.ai.projects.operations.BetaToolboxesOperations` operations"""
    skills: BetaSkillsOperations
    """:class:`~azure.ai.projects.operations.BetaSkillsOperations` operations"""

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
