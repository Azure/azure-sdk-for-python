# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async parity for the GA telephony and preview campaign REST tests."""

import asyncio
from contextlib import AsyncExitStack

import pytest

from azure.ai.projects import models
from azure.ai.projects.aio.operations import BetaVoiceAgentsTelephonyOperations, VoiceAgentsTelephonyOperations
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError, ResourceNotFoundError
from devtools_testutils import add_body_key_sanitizer
from devtools_testutils.aio import recorded_by_proxy_async
from test_base import TestBase
from voice_telephony_test_base import (
    MISSING_CALL_ID,
    POLL_TIMEOUT,
    TERMINAL_CALL_JOB_STATES,
    TERMINAL_CAMPAIGN_STATES,
    owned_agent_name,
    preserve_telephony_etags,
    request_id,
    sanitize_telephony_value,
    schedule_window,
    voice_definition,
    voiceBindingServicePreparer,
    voiceOutboundServicePreparer,
    voiceTelephonyServicePreparer,
)


class TestVoiceAgentTelephonyRestAsync(TestBase):
    @voiceBindingServicePreparer()
    @recorded_by_proxy_async()
    async def test_binding_lifecycle_async(self, **kwargs):
        preserve_telephony_etags()
        agent_name = owned_agent_name("binding", live=self.is_live)
        phone_number = kwargs["foundry_voice_test_source_phone_number"]
        connection_name = kwargs["foundry_voice_test_connection_name"]
        if self.is_live:
            sanitize_telephony_value(phone_number, "+12025550100")
            add_body_key_sanitizer(
                json_path="$..incoming_call_url", value="https://example.invalid/incoming", function_scoped=True
            )

        async with self.create_async_client(**kwargs) as client, AsyncExitStack() as cleanup:
            await client.agents.create_version(
                agent_name, definition=voice_definition(kwargs["foundry_voice_model_name"])
            )
            cleanup.push_async_callback(client.agents.delete, agent_name)
            telephony = client.voice_agents.telephony
            binding = await telephony.create_binding(
                agent_name,
                models.TwilioTelephonyBinding(
                    connection_name=connection_name, phone_number=phone_number, label="Before"
                ),
            )
            binding_id = binding.id
            assert binding_id
            try:
                if self.is_live and phone_number not in binding_id:
                    sanitize_telephony_value(binding_id, "sanitized-binding-id")
                assert isinstance(binding, models.TwilioTelephonyBinding)
                assert binding.phone_number == phone_number and binding.connection_name == connection_name
                assert binding.incoming_call_url.startswith("https://")
                (listed,) = [item async for item in telephony.list_bindings(agent_name, provider="twilio", limit=1)]
                assert isinstance(listed, models.TwilioTelephonyBindingListItem)
                assert listed.id == binding_id and listed.etag
                assert (await telephony.get_binding(agent_name, binding_id)).label == "Before"
                updated = await telephony.update_binding(
                    agent_name,
                    binding_id,
                    models.UpdateTelephonyBindingRequest(label="After"),
                    etag=listed.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
                assert updated.id == binding_id and updated.label == "After"
                assert (await telephony.get_binding(agent_name, binding_id)).label == "After"
            finally:
                etag = await telephony.get_binding(agent_name, binding_id, cls=lambda _, __, headers: headers["ETag"])
                assert etag
                await telephony.delete_binding(
                    agent_name, binding_id, etag=etag, match_condition=MatchConditions.IfNotModified
                )
            with pytest.raises(ResourceNotFoundError):
                await telephony.get_binding(agent_name, binding_id)

    @voiceTelephonyServicePreparer()
    @recorded_by_proxy_async()
    async def test_transfer_target_lifecycle_async(self, **kwargs):
        agent_name = owned_agent_name("transfer-targets", live=self.is_live)
        target = models.TelephonyTransferTarget(
            name="test_target",
            description="A transfer target for configuration readback only.",
            destination=models.PhoneNumber(value="+12025550102"),
        )
        async with self.create_async_client(**kwargs) as client, AsyncExitStack() as cleanup:
            await client.agents.create_version(
                agent_name, definition=voice_definition(kwargs["foundry_voice_model_name"])
            )
            cleanup.push_async_callback(client.agents.delete, agent_name)
            telephony = client.voice_agents.telephony
            current, etag = await telephony.get_transfer_targets(
                agent_name, cls=lambda _, targets, headers: (targets, headers["ETag"])
            )
            assert current.transfer_targets == [] and etag
            replaced = await telephony.replace_transfer_targets(
                agent_name, transfer_targets=[target], etag=etag, match_condition=MatchConditions.IfNotModified
            )
            assert replaced.transfer_targets == [target]
            assert (await telephony.get_transfer_targets(agent_name)).transfer_targets == [target]

    @voiceTelephonyServicePreparer()
    @recorded_by_proxy_async()
    async def test_missing_call_returns_service_not_found_async(self, **kwargs):
        agent_name = owned_agent_name("calls", live=self.is_live)
        async with self.create_async_client(**kwargs) as client, AsyncExitStack() as cleanup:
            await client.agents.create_version(
                agent_name, definition=voice_definition(kwargs["foundry_voice_model_name"])
            )
            cleanup.push_async_callback(client.agents.delete, agent_name)
            telephony = client.voice_agents.telephony
            assert [item async for item in telephony.list_calls(agent_name, limit=1)] == []
            for operation, options in (
                (telephony.get_call, {}),
                (telephony.transfer_call, {"target": "missing_target"}),
                (telephony.end_call, {}),
            ):
                with pytest.raises(ResourceNotFoundError) as error:
                    await operation(agent_name, MISSING_CALL_ID, **options)
                assert error.value.status_code == 404 and error.value.error and error.value.error.code

    @voiceOutboundServicePreparer()
    @recorded_by_proxy_async()
    async def test_scheduled_call_job_lifecycle_async(self, variables=None, **kwargs):
        agent_name = owned_agent_name("call-job", live=self.is_live)
        scheduled_at, expires_at = schedule_window(live=self.is_live, variables=variables)
        job = models.TelephonyCallJobCreate(
            connection_name=kwargs["foundry_voice_test_connection_name"],
            source=models.PhoneNumber(value=kwargs["foundry_voice_test_source_phone_number"]),
            destination=models.PhoneNumber(value=kwargs["foundry_voice_test_destination_phone_number"]),
            schedule=models.TelephonyCallJobSchedule(not_before=scheduled_at, expires_at=expires_at),
        )
        key = request_id(1, live=self.is_live)
        if self.is_live:
            add_body_key_sanitizer(json_path="$..requested_by", value="sanitized-principal", function_scoped=True)

        async with self.create_async_client(**kwargs) as client, AsyncExitStack() as cleanup:
            await client.agents.create_version(
                agent_name, definition=voice_definition(kwargs["foundry_voice_model_name"])
            )
            cleanup.push_async_callback(client.agents.delete, agent_name)
            telephony = client.voice_agents.telephony
            created = await telephony.create_call_job(agent_name, job, idempotency_key=key)
            job_id = created.id
            assert job_id
            try:
                if self.is_live:
                    sanitize_telephony_value(job_id, "sanitized-call-job")
                assert created.agent_name == agent_name and created.attempt_count == 0
                assert created.schedule is not None and created.schedule.not_before == scheduled_at
                assert (await telephony.create_call_job(agent_name, job, idempotency_key=key)).id == job_id
                assert (await telephony.get_call_job(agent_name, job_id)).id == job_id
                assert [item.id async for item in telephony.list_call_jobs(agent_name, limit=1)] == [job_id]
            finally:
                terminal = await self._cancel_call_job(telephony, agent_name, job_id)
                await telephony.delete_call_job(agent_name, job_id)
            assert terminal.status == "cancelled" and terminal.attempt_count == 0
            with pytest.raises(ResourceNotFoundError):
                await telephony.get_call_job(agent_name, job_id)
            assert [item async for item in telephony.list_call_jobs(agent_name, limit=1)] == []
        return {"scheduled_at": scheduled_at.isoformat()}

    async def _cancel_call_job(
        self, telephony: VoiceAgentsTelephonyOperations, agent_name: str, job_id: str
    ) -> models.TelephonyCallJob:
        cancel_requested = False
        for _ in range(POLL_TIMEOUT):
            current = await telephony.get_call_job(agent_name, job_id)
            if current.status in TERMINAL_CALL_JOB_STATES:
                return current
            if not cancel_requested and current.status != "cancellation_requested":
                try:
                    current = await telephony.cancel_call_job(
                        agent_name, job_id, etag=str(current.revision), match_condition=MatchConditions.IfNotModified
                    )
                except ResourceModifiedError:
                    continue
                cancel_requested = True
                if current.status in TERMINAL_CALL_JOB_STATES:
                    return current
            if self.is_live:
                await asyncio.sleep(1)
        raise AssertionError("Call-job cancellation did not settle.")

    @voiceOutboundServicePreparer()
    @recorded_by_proxy_async()
    async def test_scheduled_campaign_lifecycle_async(self, variables=None, **kwargs):
        preserve_telephony_etags()
        agent_name = owned_agent_name("campaign", live=self.is_live)
        campaign_name = "scheduled-rest-test"
        scheduled_at, expires_at = schedule_window(live=self.is_live, variables=variables)
        campaign = models.TelephonyCampaign(
            connection_name=kwargs["foundry_voice_test_connection_name"],
            source=models.PhoneNumber(value=kwargs["foundry_voice_test_source_phone_number"]),
            recipients=[
                models.TelephonyRecipient(
                    destination=models.PhoneNumber(value=kwargs["foundry_voice_test_destination_phone_number"])
                )
            ],
            schedule=models.AtTimeSchedule(scheduled_at=scheduled_at, expires_at=expires_at),
        )
        async with self.create_async_client(allow_preview=True, **kwargs) as client, AsyncExitStack() as cleanup:
            await client.agents.create_version(
                agent_name, definition=voice_definition(kwargs["foundry_voice_model_name"])
            )
            cleanup.push_async_callback(client.agents.delete, agent_name)
            campaigns = client.beta.voice_agents.telephony
            try:
                create = await campaigns.begin_create(
                    agent_name, campaign_name, campaign, operation_id=request_id(2, live=self.is_live)
                )
                prepared = await asyncio.wait_for(create.result(), timeout=POLL_TIMEOUT)
                assert create.done() and prepared.name == campaign_name
                assert prepared.status == "running" and prepared.progress.total_recipients == 1
                assert prepared.progress.active == 0
                assert isinstance(prepared.schedule, models.AtTimeSchedule)
                assert prepared.schedule.scheduled_at == scheduled_at
                monitor = await campaigns.get_operation(agent_name, campaign_name, prepared.operation_id)
                assert monitor.id == prepared.operation_id and monitor.kind == "validation"
                assert monitor.status == "succeeded"
                assert (await campaigns.get(agent_name, campaign_name)).operation_id == prepared.operation_id
                assert [item.name async for item in campaigns.list(agent_name, limit=1)] == [campaign_name]
                assert [
                    item async for item in campaigns.list_validation_errors(agent_name, campaign_name, limit=1)
                ] == []
            finally:
                terminal = await self._cancel_and_delete_campaign(campaigns, agent_name, campaign_name)
            assert terminal is not None and terminal.status == "cancelled"
            with pytest.raises(ResourceNotFoundError):
                await campaigns.get(agent_name, campaign_name)
            assert [item async for item in campaigns.list(agent_name, limit=1)] == []
        return {"scheduled_at": scheduled_at.isoformat()}

    async def _cancel_and_delete_campaign(
        self, campaigns: BetaVoiceAgentsTelephonyOperations, agent_name: str, campaign_name: str
    ) -> models.TelephonyCampaign | None:
        try:
            current = await campaigns.get(agent_name, campaign_name)
        except ResourceNotFoundError:
            return None
        if current.status in {"validating", "running"}:
            cancel = await campaigns.begin_cancel(
                agent_name,
                campaign_name,
                etag=current.etag,
                match_condition=MatchConditions.IfNotModified,
                operation_id=request_id(3, live=self.is_live),
            )
            current = await asyncio.wait_for(cancel.result(), timeout=POLL_TIMEOUT)
        assert current.status in TERMINAL_CAMPAIGN_STATES
        delete = await campaigns.begin_delete(
            agent_name,
            campaign_name,
            etag=current.etag,
            match_condition=MatchConditions.IfNotModified,
            operation_id=request_id(4, live=self.is_live),
        )
        result = await asyncio.wait_for(delete.result(), timeout=POLL_TIMEOUT)
        assert result is None
        return current
