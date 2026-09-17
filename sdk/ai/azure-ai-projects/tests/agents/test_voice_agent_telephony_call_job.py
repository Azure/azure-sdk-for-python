# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects.models import (
    AgentVersionDetails,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceOutputModality,
)


class TestVoiceAgentTelephonyCallJob(TestBase):
    """
    Recorded tests covering the outbound telephony call-job REST API surface exposed through the
    top-level `project_client.beta.voice_agents.telephony.*` operation group (added in the
    "batch 2" Voice Agents TypeSpec, distinct from the existing `project_client.agents.*`
    telephony binding/call methods).

    NOTE: All tests in this file are currently marked `skip`:
      - Probing this environment's live Voice Agents test resource with
        `voice_agents.telephony.get_call_job` (api-version "v1", the SDK's only known
        version) returns `400 UnsupportedApiVersion` with a message identifying the resolved
        route (".../agents/{agent_name}/telephony/call_jobs/{call_job_id}") but rejecting
        "v1" for it - unlike the routing-layer empty-body 404s seen for the batch-1
        `agents.*` telephony bindings/calls routes (see `test_voice_agent_telephony.py`), this
        route *is* registered, but the call-job feature isn't yet enabled for the API
        version this SDK targets. Un-skip once the live test service accepts "v1" for these
        routes.

    Further NOTE: `create_call_job` is intentionally NOT covered here at all since it requires
    real infrastructure this test environment does not have: a real, working `connection_name`
    pointing at a provisioned Teams Phone/Twilio Foundry connection -- outbound calls originate
    directly from the connection, so no pre-existing telephony binding is required (same
    real-provider limitation documented for `create_binding` in `test_voice_agent_telephony.py`).
    Once these are fixed/deployed service-side and real provider credentials are available, tests
    can be added/enabled for it.

    The `voice_agents.telephony` campaign operation group (`create_campaign`,
    `begin_import_campaign_recipients`, `begin_validate_campaign`, `begin_publish_campaign`,
    `pause_campaign`/`resume_campaign`/`cancel_campaign`, `get_operation`, and their models) was
    removed from the TypeSpec/generated SDK surface; this file no longer covers it.
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
    # pytest tests\agents\test_voice_agent_telephony_call_job.py::TestVoiceAgentTelephonyCallJob::test_telephony_call_job_not_found -s
    @pytest.mark.skip(
        reason="voice_agents.telephony routes are registered but return 400 UnsupportedApiVersion for "
        "api-version 'v1' on the live test service. Un-skip once the service supports 'v1' for "
        "this operation group."
    )
    @servicePreparer()
    @recorded_by_proxy()
    def test_telephony_call_job_not_found(self, **kwargs):
        """
        Test outbound telephony call jobs: get/cancel against a nonexistent call job, which
        return 404.

        Routes used in this test:

        Action REST API Route                                                  Client Method
        ------+-------------------------------------------------------------+-----------------------------------------------
        POST   /agents/{agent_name}/versions                                  project_client.agents.create_version()
        GET    /agents/{agent_name}/telephony/call_jobs/{call_job_id}         project_client.beta.voice_agents.telephony.get_call_job()
        POST   /agents/{agent_name}/telephony/call_jobs/{call_job_id}:cancel  project_client.beta.voice_agents.telephony.cancel_call_job()
        DELETE /agents/{agent_name}                                          project_client.agents.delete()
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        # Voice-agent operations require the preview opt-in.
        project_client = self.create_client(allow_preview=True, **kwargs)
        agent_name = "VoiceAgentTelephonyCallJobTest"

        # Delete any existing agent from previous test runs (ignore failures)
        try:
            project_client.agents.delete(agent_name=agent_name)
        except Exception:  # pylint: disable=broad-except
            pass

        agent_version: AgentVersionDetails = project_client.agents.create_version(
            agent_name=agent_name,
            definition=self._make_definition(model),
        )
        self._validate_agent_version(agent_version, expected_name=agent_name)

        fake_call_job_id = "nonexistent-call-job-id"
        with pytest.raises(ResourceNotFoundError):
            project_client.beta.voice_agents.telephony.get_call_job(agent_name=agent_name, call_job_id=fake_call_job_id)
        with pytest.raises(ResourceNotFoundError):
            # cancel_call_job's "etag" is a numeric call-job revision, not an opaque ETag - the
            # service rejects an "If-Match: *" unconditional match for this endpoint, so a
            # well-formed (if make-believe) revision is passed here instead, using the default
            # match_condition (MatchConditions.IfNotModified).
            project_client.beta.voice_agents.telephony.cancel_call_job(
                agent_name=agent_name,
                call_job_id=fake_call_job_id,
                etag="0",
            )

        # Delete the voice agent.
        result = project_client.agents.delete(agent_name=agent_name)
        assert result.deleted
