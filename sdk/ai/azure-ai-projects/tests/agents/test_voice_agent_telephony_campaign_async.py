# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
import pytest
from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects.models import (
    AgentVersionDetails,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceOutputModality,
)


class TestVoiceAgentTelephonyCampaignAsync(TestBase):
    """
    Recorded tests covering the outbound telephony call-job/campaign REST API surface exposed
    through the top-level `project_client.agent_telephony.*` operation group (added in the
    "batch 2" Voice Agents TypeSpec, distinct from the existing `project_client.agents.*`
    telephony binding/call methods).

    NOTE: All tests in this file are currently marked `skip`:
      - Probing this environment's live Voice Agents test resource with
        `agent_telephony.get_telephony_operation` (api-version "v1", the SDK's only known
        version) returns `400 UnsupportedApiVersion` with a message identifying the resolved
        route (".../agents/{agent_name}/telephony/operations/{operation_id}") but rejecting
        "v1" for it - unlike the routing-layer empty-body 404s seen for the batch-1
        `agents.*` telephony bindings/calls routes (see `test_voice_agent_telephony_async.py`),
        this route *is* registered, but the call-job/campaign feature isn't yet enabled for the
        API version this SDK targets. Un-skip once the live test service accepts "v1" for these
        routes.

    Further NOTE: the following are intentionally NOT covered here at all since they require real
    infrastructure this test environment does not have:
      - `create_telephony_call_job`/`create_telephony_campaign` need a real, working
        `telephony_binding_id` from a provisioned Teams Phone/Twilio telephony binding (same
        real-provider limitation documented for `create_telephony_binding` in
        `test_voice_agent_telephony_async.py`).
      - `begin_import_telephony_campaign_recipients`/`begin_publish_telephony_campaign`/
        `begin_validate_telephony_campaign` are long-running operations on a real campaign with
        actual recipients, which in turn requires the real telephony binding above.
    Once these are fixed/deployed service-side and real provider credentials are available,
    tests can be added/enabled for them.
    """

    def _make_definition(self, model: str) -> VoiceAgentDefinition:
        return VoiceAgentDefinition(
            model_type="managed",
            model=model,
            instructions="You are a helpful voice assistant.",
            audio=VoiceAgentAudioConfig(
                output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type="azure-standard")
            ),
            output_modalities=[VoiceOutputModality.AUDIO],
        )

    # To run only this test:
    # pytest tests\agents\test_voice_agent_telephony_campaign_async.py::TestVoiceAgentTelephonyCampaignAsync::test_telephony_call_job_not_found -s
    @pytest.mark.skip(
        reason="agent_telephony routes are registered but return 400 UnsupportedApiVersion for "
        "api-version 'v1' on the live test service. Un-skip once the service supports 'v1' for "
        "this operation group."
    )
    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_telephony_call_job_not_found(self, **kwargs):
        """
        Test outbound telephony call jobs: get/cancel against a nonexistent call job, which
        return 404.

        Routes used in this test:

        Action REST API Route                                                  Client Method
        ------+-------------------------------------------------------------+-----------------------------------------------
        POST   /agents/{agent_name}/versions                                  project_client.agents.create_version()
        GET    /agents/{agent_name}/telephony/call_jobs/{call_job_id}         project_client.agent_telephony.get_telephony_call_job()
        POST   /agents/{agent_name}/telephony/call_jobs/{call_job_id}:cancel  project_client.agent_telephony.cancel_telephony_call_job()
        DELETE /agents/{agent_name}                                          project_client.agents.delete()
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        # Voice-agent operations require the preview opt-in.
        project_client = self.create_async_client(allow_preview=True, **kwargs)
        agent_name = "VoiceAgentTelephonyCallJobTest"

        # Delete any existing agent from previous test runs (ignore failures)
        try:
            await project_client.agents.delete(agent_name=agent_name)
        except Exception:  # pylint: disable=broad-except
            pass

        agent_version: AgentVersionDetails = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=self._make_definition(model),
        )
        self._validate_agent_version(agent_version, expected_name=agent_name)

        fake_call_job_id = "nonexistent-call-job-id"
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.get_telephony_call_job(
                agent_name=agent_name, call_job_id=fake_call_job_id
            )
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.cancel_telephony_call_job(
                agent_name=agent_name,
                call_job_id=fake_call_job_id,
                etag=None,
                match_condition=MatchConditions.Unconditionally,
            )

        # Delete the voice agent.
        result = await project_client.agents.delete(agent_name=agent_name)
        assert result.deleted

    # To run only this test:
    # pytest tests\agents\test_voice_agent_telephony_campaign_async.py::TestVoiceAgentTelephonyCampaignAsync::test_telephony_campaign_not_found -s
    @pytest.mark.skip(
        reason="agent_telephony routes are registered but return 400 UnsupportedApiVersion for "
        "api-version 'v1' on the live test service. Un-skip once the service supports 'v1' for "
        "this operation group."
    )
    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_telephony_campaign_not_found(self, **kwargs):
        """
        Test outbound telephony campaigns: get/cancel/pause/resume against a nonexistent
        campaign, and get against a nonexistent recipient import, all of which return 404.

        Routes used in this test:

        Action REST API Route                                                          Client Method
        ------+-------------------------------------------------------------------+-----------------------------------------------
        POST   /agents/{agent_name}/versions                                          project_client.agents.create_version()
        GET    /agents/{agent_name}/telephony/campaigns/{campaign_id}                  project_client.agent_telephony.get_telephony_campaign()
        POST   /agents/{agent_name}/telephony/campaigns/{campaign_id}:cancel           project_client.agent_telephony.cancel_telephony_campaign()
        POST   /agents/{agent_name}/telephony/campaigns/{campaign_id}:pause           project_client.agent_telephony.pause_telephony_campaign()
        POST   /agents/{agent_name}/telephony/campaigns/{campaign_id}:resume          project_client.agent_telephony.resume_telephony_campaign()
        GET    /agents/{agent_name}/telephony/campaigns/{campaign_id}/recipient_imports/{import_id}
                                                                                       project_client.agent_telephony.get_telephony_campaign_recipient_import()
        DELETE /agents/{agent_name}                                                   project_client.agents.delete()
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        # Voice-agent operations require the preview opt-in.
        project_client = self.create_async_client(allow_preview=True, **kwargs)
        agent_name = "VoiceAgentTelephonyCampaignTest"

        # Delete any existing agent from previous test runs (ignore failures)
        try:
            await project_client.agents.delete(agent_name=agent_name)
        except Exception:  # pylint: disable=broad-except
            pass

        agent_version: AgentVersionDetails = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=self._make_definition(model),
        )
        self._validate_agent_version(agent_version, expected_name=agent_name)

        fake_campaign_id = "nonexistent-campaign-id"
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.get_telephony_campaign(
                agent_name=agent_name, campaign_id=fake_campaign_id
            )
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.cancel_telephony_campaign(
                agent_name=agent_name, campaign_id=fake_campaign_id
            )
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.pause_telephony_campaign(
                agent_name=agent_name, campaign_id=fake_campaign_id
            )
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.resume_telephony_campaign(
                agent_name=agent_name, campaign_id=fake_campaign_id
            )

        fake_import_id = "nonexistent-import-id"
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.get_telephony_campaign_recipient_import(
                agent_name=agent_name,
                campaign_id=fake_campaign_id,
                import_id=fake_import_id,
            )

        # Delete the voice agent.
        result = await project_client.agents.delete(agent_name=agent_name)
        assert result.deleted

    # To run only this test:
    # pytest tests\agents\test_voice_agent_telephony_campaign_async.py::TestVoiceAgentTelephonyCampaignAsync::test_telephony_operation_not_found -s
    @pytest.mark.skip(
        reason="agent_telephony routes are registered but return 400 UnsupportedApiVersion for "
        "api-version 'v1' on the live test service. Un-skip once the service supports 'v1' for "
        "this operation group."
    )
    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_telephony_operation_not_found(self, **kwargs):
        """
        Test the generic long-running-operation status endpoint used to poll
        `begin_import_telephony_campaign_recipients`/`begin_publish_telephony_campaign`/
        `begin_validate_telephony_campaign`, against a nonexistent operation id, which returns
        404.

        Routes used in this test:

        Action REST API Route                                              Client Method
        ------+-------------------------------------------------------------+-----------------------------------------------
        POST   /agents/{agent_name}/versions                                project_client.agents.create_version()
        GET    /agents/{agent_name}/telephony/operations/{operation_id}     project_client.agent_telephony.get_telephony_operation()
        DELETE /agents/{agent_name}                                        project_client.agents.delete()
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        # Voice-agent operations require the preview opt-in.
        project_client = self.create_async_client(allow_preview=True, **kwargs)
        agent_name = "VoiceAgentTelephonyOperationTest"

        # Delete any existing agent from previous test runs (ignore failures)
        try:
            await project_client.agents.delete(agent_name=agent_name)
        except Exception:  # pylint: disable=broad-except
            pass

        agent_version: AgentVersionDetails = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=self._make_definition(model),
        )
        self._validate_agent_version(agent_version, expected_name=agent_name)

        fake_operation_id = "nonexistent-operation-id"
        with pytest.raises(ResourceNotFoundError):
            await project_client.agent_telephony.get_telephony_operation(
                agent_name=agent_name, operation_id=fake_operation_id
            )

        # Delete the voice agent.
        result = await project_client.agents.delete(agent_name=agent_name)
        assert result.deleted
