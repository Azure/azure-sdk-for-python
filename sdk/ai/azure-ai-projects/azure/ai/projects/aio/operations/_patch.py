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
from ._patch_agent_insights_async import AgentInsightMonitorsOperations
from ._patch_datasets_async import DatasetsOperations
from ._patch_evaluators_async import EvaluatorsOperations
from ._patch_evaluation_rules_async import EvaluationRulesOperations
from ._patch_telemetry_async import TelemetryOperations
from ._patch_connections_async import ConnectionsOperations
from ._patch_memories_async import BetaMemoryStoresOperations
from ._patch_models_async import BetaModelsOperations
from ...operations._patch import (
    _BETA_OPERATION_FEATURE_HEADERS,
    _OperationMethodHeaderProxy,
    _VOICE_AGENT_CONDITIONAL_TELEPHONY_METHODS,
)
from .._realtime import (
    AsyncRealtime,
    AsyncRealtimeConnection,
    AsyncRealtimeConnectionManager,
    ClientEvent,
    ConversationItem,
    ServerEvent,
)
from .._live import (
    AsyncBetaLive,
    AsyncBetaLiveConnection,
    AsyncBetaLiveConnectionManager,
    LiveClientEvent,
    LiveServerEvent,
)

# Nested operation groups are re-exported here rather than in the generated package exports.
from ._patch_campaigns_async import BetaVoiceAgentsTelephonyOperations
from ._operations import (
    BetaEvaluationTaxonomiesOperations,
    BetaInsightsOperations,
    BetaOperations as GeneratedBetaOperations,
    BetaRedTeamsOperations,
    BetaRoutinesOperations,
    BetaSchedulesOperations,
    BetaSkillsOperations,
    BetaVoiceAgentsLiveConversationsOperations,
    BetaVoiceAgentsOperations as GeneratedBetaVoiceAgentsOperations,
    VoiceAgentsConversationsOperations,
    VoiceAgentsOperations as GeneratedVoiceAgentsOperations,
    VoiceAgentsTelephonyOperations,
)


class VoiceAgentsOperations(GeneratedVoiceAgentsOperations):
    """Generally available voice-agent operations.

    Access these operations through :class:`~azure.ai.projects.aio.AIProjectClient`'s
    ``voice_agents`` attribute.
    """

    conversations: VoiceAgentsConversationsOperations
    """:class:`~azure.ai.projects.aio.operations.VoiceAgentsConversationsOperations` operations"""
    telephony: VoiceAgentsTelephonyOperations
    """:class:`~azure.ai.projects.aio.operations.VoiceAgentsTelephonyOperations` operations"""
    realtime: AsyncRealtime
    """:class:`~azure.ai.projects.aio.operations.AsyncRealtime` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # WebSocket connections cannot be kept alive by the generated HTTP pipeline.
        self.realtime = AsyncRealtime(self)
        if self._config.allow_preview:
            setattr(
                self,
                "telephony",
                _OperationMethodHeaderProxy(
                    self.telephony,
                    _BETA_OPERATION_FEATURE_HEADERS["voice_agents"],
                    method_names=_VOICE_AGENT_CONDITIONAL_TELEPHONY_METHODS,
                ),
            )


class BetaVoiceAgentsOperations(GeneratedBetaVoiceAgentsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s :attr:`beta` attribute's
        :attr:`~azure.ai.projects.aio.operations.BetaOperations.voice_agents` attribute.
    """

    telephony: BetaVoiceAgentsTelephonyOperations
    """:class:`~azure.ai.projects.aio.operations.BetaVoiceAgentsTelephonyOperations` operations"""
    live_conversations: BetaVoiceAgentsLiveConversationsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaVoiceAgentsLiveConversationsOperations` operations"""
    live: AsyncBetaLive
    """:class:`~azure.ai.projects.aio.operations.AsyncBetaLive` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.telephony = BetaVoiceAgentsTelephonyOperations(
            self._client, self._config, self._serialize, self._deserialize
        )
        self.live = AsyncBetaLive(self)


class BetaOperations(GeneratedBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    evaluation_taxonomies: BetaEvaluationTaxonomiesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaEvaluationTaxonomiesOperations` operations"""
    insights: BetaInsightsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaInsightsOperations` operations"""
    memory_stores: BetaMemoryStoresOperations
    """:class:`~azure.ai.projects.aio.operations.BetaMemoryStoresOperations` operations"""
    models: BetaModelsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaModelsOperations` operations"""
    red_teams: BetaRedTeamsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaRedTeamsOperations` operations"""
    routines: BetaRoutinesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaRoutinesOperations` operations"""
    schedules: BetaSchedulesOperations
    """:class:`~azure.ai.projects.aio.operations.BetaSchedulesOperations` operations"""
    skills: BetaSkillsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaSkillsOperations` operations"""
    voice_agents: BetaVoiceAgentsOperations
    """:class:`~azure.ai.projects.aio.operations.BetaVoiceAgentsOperations` operations"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Replace with patched class that includes begin_update_memories
        self.memory_stores = BetaMemoryStoresOperations(self._client, self._config, self._serialize, self._deserialize)
        # Replace with patched class that includes create (3-step upload helper)
        self.models = BetaModelsOperations(self._client, self._config, self._serialize, self._deserialize)
        # Replace with patched class that wires up the hand-written realtime client
        self.voice_agents = BetaVoiceAgentsOperations(self._client, self._config, self._serialize, self._deserialize)

        for property_name, foundry_features_value in _BETA_OPERATION_FEATURE_HEADERS.items():
            setattr(
                self,
                property_name,
                _OperationMethodHeaderProxy(getattr(self, property_name), foundry_features_value),
            )


__all__: List[str] = [
    "AgentsOperations",
    "AsyncRealtime",
    "AsyncRealtimeConnection",
    "AsyncRealtimeConnectionManager",
    "AsyncBetaLive",
    "AsyncBetaLiveConnection",
    "AsyncBetaLiveConnectionManager",
    "LiveClientEvent",
    "LiveServerEvent",
    "AgentInsightMonitorsOperations",
    "BetaEvaluationTaxonomiesOperations",
    "BetaInsightsOperations",
    "BetaMemoryStoresOperations",
    "BetaModelsOperations",
    "BetaOperations",
    "BetaRedTeamsOperations",
    "BetaRoutinesOperations",
    "BetaSchedulesOperations",
    "BetaSkillsOperations",
    "BetaVoiceAgentsTelephonyOperations",
    "BetaVoiceAgentsLiveConversationsOperations",
    "BetaVoiceAgentsOperations",
    "VoiceAgentsConversationsOperations",
    "VoiceAgentsOperations",
    "VoiceAgentsTelephonyOperations",
    "ClientEvent",
    "ConnectionsOperations",
    "ConversationItem",
    "DatasetsOperations",
    "EvaluatorsOperations",
    "EvaluationRulesOperations",
    "ServerEvent",
    "TelemetryOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
