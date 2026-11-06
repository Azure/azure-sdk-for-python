# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Custom asynchronous Voice Agent campaign operations."""

from collections.abc import MutableMapping
from typing import Any, IO, Optional, Union, overload

from azure.core import MatchConditions
from azure.core.polling import AsyncLROPoller

from ._operations import BetaVoiceAgentsCampaignsOperations as GeneratedBetaVoiceAgentsCampaignsOperations
from ... import models as _models
from ..._utils.campaign_polling import _configure_campaign_polling

JSON = MutableMapping[str, Any]


class BetaVoiceAgentsCampaignsOperations(GeneratedBetaVoiceAgentsCampaignsOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, access these operations through
        :class:`~azure.ai.projects.aio.AIProjectClient`'s ``beta.voice_agents.campaigns`` attribute.
    """

    def _configure_polling(self, kwargs: dict[str, Any]) -> None:
        _configure_campaign_polling(
            kwargs,
            self._config.polling_interval,
            {"endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True)},
            is_async=True,
        )

    @overload
    async def begin_create(
        self,
        agent_name: str,
        campaign_name: str,
        campaign: _models.TelephonyCampaign,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.TelephonyCampaign]: ...

    @overload
    async def begin_create(
        self,
        agent_name: str,
        campaign_name: str,
        campaign: JSON,
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.TelephonyCampaign]: ...

    @overload
    async def begin_create(
        self,
        agent_name: str,
        campaign_name: str,
        campaign: IO[bytes],
        *,
        operation_id: Optional[str] = None,
        content_type: str = "application/json",
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.TelephonyCampaign]: ...

    async def begin_create(
        self,
        agent_name: str,
        campaign_name: str,
        campaign: Union[_models.TelephonyCampaign, JSON, IO[bytes]],
        *,
        operation_id: Optional[str] = None,
        etag: Optional[str] = None,
        match_condition: Optional[MatchConditions] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.TelephonyCampaign]:
        """Create or replace a failed telephony campaign.

        All recipients must validate and have CallJobs before dialing. Immediate calls may
        begin before preparation finishes. The final Campaign GET is guarded by the initiating
        operation ID.

        :param agent_name: Owning Agent. Required.
        :type agent_name: str
        :param campaign_name: Campaign name. Only failed preparation permits replacement. Required.
        :type campaign_name: str
        :param campaign: Complete campaign configuration. Required.
        :type campaign: ~azure.ai.projects.models.TelephonyCampaign or MutableMapping[str, Any] or IO[bytes]
        :keyword operation_id: Optional retry key. Conflicting reuse returns an error.
        :paramtype operation_id: str
        :keyword etag: Resource ETag used with ``match_condition``.
        :paramtype etag: str
        :keyword match_condition: The match condition to use with the ETag.
        :paramtype match_condition: ~azure.core.MatchConditions
        :return: A poller returning the Campaign after preparation.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.projects.models.TelephonyCampaign]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._configure_polling(kwargs)
        return await super().begin_create(
            agent_name,
            campaign_name,
            campaign,
            operation_id=operation_id,
            etag=etag,
            match_condition=match_condition,
            **kwargs,
        )

    async def begin_cancel(
        self,
        agent_name: str,
        campaign_name: str,
        *,
        etag: str,
        match_condition: MatchConditions,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.TelephonyCampaign]:
        """Cancel a validating or running telephony campaign.

        Stops new calls and retries; connected calls finish naturally. The final Campaign GET
        is guarded by the initiating operation ID.

        :param agent_name: Owning Agent. Required.
        :type agent_name: str
        :param campaign_name: Campaign name. Required.
        :type campaign_name: str
        :keyword etag: Exact current Campaign ETag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use with the ETag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword operation_id: Optional retry key.
        :paramtype operation_id: str
        :return: A poller returning the Campaign after cancellation.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.projects.models.TelephonyCampaign]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._configure_polling(kwargs)
        return await super().begin_cancel(
            agent_name,
            campaign_name,
            etag=etag,
            match_condition=match_condition,
            operation_id=operation_id,
            **kwargs,
        )

    async def begin_delete(
        self,
        agent_name: str,
        campaign_name: str,
        *,
        etag: str,
        match_condition: MatchConditions,
        operation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncLROPoller[None]:
        """Delete a terminal telephony campaign and its recipient/task data.

        Completion does not fetch the deleted Campaign. Dataset, connections, Agent,
        independent jobs, and call history are preserved.

        :param agent_name: Owning Agent. Required.
        :type agent_name: str
        :param campaign_name: Campaign name. Required.
        :type campaign_name: str
        :keyword etag: Exact current Campaign ETag. Required.
        :paramtype etag: str
        :keyword match_condition: The match condition to use with the ETag. Required.
        :paramtype match_condition: ~azure.core.MatchConditions
        :keyword operation_id: Optional retry key.
        :paramtype operation_id: str
        :return: A poller returning None after deletion.
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        self._configure_polling(kwargs)
        return await super().begin_delete(
            agent_name,
            campaign_name,
            etag=etag,
            match_condition=match_condition,
            operation_id=operation_id,
            **kwargs,
        )
