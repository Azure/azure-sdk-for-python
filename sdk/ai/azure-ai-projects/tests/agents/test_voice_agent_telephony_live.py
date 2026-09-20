"""Live Twilio tests that place real PSTN calls and may incur provider charges.

Run serially with AZURE_TEST_RUN_LIVE=true and DefaultAzureCredential configured:
    pytest tests/agents/test_voice_agent_telephony_live.py -n 0 -s

Required environment variables: FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_VOICE_MODEL_NAME,
FOUNDRY_TELEPHONY_CONNECTION_1, and FOUNDRY_TELEPHONY_NUMBER_1. The outbound test
also requires FOUNDRY_TELEPHONY_CONNECTION_2 and FOUNDRY_TELEPHONY_NUMBER_2.
Use two distinct, dedicated Twilio test numbers in E.164 format. Number 1 receives
the outbound call from number 2; the test then transfers that call to number 2.
Do not run concurrently with other tests using the same provider numbers.
"""

import logging
import os
import re
import time
from contextlib import ExitStack
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Iterator, List
from uuid import uuid4

import pytest
from devtools_testutils import is_live
from azure.core import MatchConditions
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CreateTelephonyCallJobRequest,
    CreateTwilioTelephonyBindingRequest,
    PSTNTelephonyTransferDestination,
    TelephonyBindingListItem,
    TelephonyBindingStatus,
    TelephonyCallJobSchedule,
    TelephonyCallSummary,
    TelephonyOutboundDestination,
    TelephonyOutboundDestinationType,
    TelephonyProvider,
    TelephonyTransferTarget,
    UpdateTelephonyBindingRequest,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
)
from azure.ai.projects.operations import BetaVoiceAgentsTelephonyOperations

_LOGGER = logging.getLogger(__name__)
_CALL_TIMEOUT = 120
_POLL_INTERVAL = 2

pytestmark = [
    pytest.mark.live_test_only,
    pytest.mark.skipif(not is_live(), reason="Live-only: uses Twilio resources and places real PSTN calls."),
]


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        pytest.skip(f"{name} is required for live telephony testing")
    return value


def _phone_number(name: str) -> str:
    value = _required_env(name)
    assert re.fullmatch(r"\+[1-9][0-9]{7,14}", value), f"{name} must be an E.164 phone number"
    return value


@pytest.fixture
def telephony_project_client(request: pytest.FixtureRequest) -> Iterator[AIProjectClient]:
    if hasattr(request.config, "workerinput"):
        pytest.skip("Live telephony tests share provider numbers; run with -n 0")
    endpoint = _required_env("FOUNDRY_PROJECT_ENDPOINT")
    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
            yield client


def _definition(model: str, instructions: str) -> VoiceAgentDefinition:
    return VoiceAgentDefinition(
        model_type=VoiceModelType.MANAGED,
        model=model,
        instructions=instructions,
        output_modalities=[VoiceOutputModality.AUDIO],
        audio=VoiceAgentAudioConfig(
            output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type="azure-standard")
        ),
    )


def _cleanup(action: Callable[..., Any], **kwargs: Any) -> None:
    try:
        action(**kwargs)
    except Exception:
        _LOGGER.warning("Live telephony cleanup failed: %s", action.__name__, exc_info=True)


def _find_binding(
    telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str, binding_id: str
) -> TelephonyBindingListItem:
    binding = next((item for item in telephony.list_bindings(agent_name) if item.id == binding_id), None)
    assert binding is not None, "Created telephony binding was not listed"
    assert binding.etag, "Listed telephony binding has no ETag"
    return binding


def _delete_binding(telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str, binding_id: str) -> None:
    for binding in telephony.list_bindings(agent_name):
        if binding.id == binding_id:
            assert binding.etag, "Listed telephony binding has no ETag"
            telephony.delete_binding(
                agent_name, binding_id, etag=binding.etag, match_condition=MatchConditions.IfNotModified
            )
            return


def _replace_targets(
    telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str, targets: List[TelephonyTransferTarget]
) -> None:
    headers = {}
    current = telephony.get_transfer_targets(
        agent_name, raw_response_hook=lambda response: headers.update(response.http_response.headers)
    )
    etag = next((value for key, value in headers.items() if key.lower() == "etag"), None)
    assert etag, "Telephony transfer targets response has no ETag"
    if targets:
        assert not current.transfer_targets, "A new agent should have no transfer targets"
    replaced = telephony.replace_transfer_targets(
        agent_name, transfer_targets=targets, etag=etag, match_condition=MatchConditions.IfNotModified
    )
    assert [target.name for target in replaced.transfer_targets] == [target.name for target in targets]


def _cancel_job(telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str, call_job_id: str) -> None:
    job = telephony.get_call_job(agent_name, call_job_id)
    if job.cancellation is None:
        telephony.cancel_call_job(
            agent_name, call_job_id, etag=str(job.revision), match_condition=MatchConditions.IfNotModified
        )


def _wait_for_inbound_call(telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str) -> TelephonyCallSummary:
    deadline = time.monotonic() + _CALL_TIMEOUT
    while time.monotonic() < deadline:
        call = next(iter(telephony.list_calls(agent_name)), None)
        if call is not None:
            return call
        time.sleep(_POLL_INTERVAL)
    pytest.fail(f"No inbound Twilio call arrived within {_CALL_TIMEOUT} seconds")


def _wait_for_dispatched_job(telephony: BetaVoiceAgentsTelephonyOperations, agent_name: str, call_job_id: str) -> None:
    deadline = time.monotonic() + _CALL_TIMEOUT
    while time.monotonic() < deadline:
        job = telephony.get_call_job(agent_name, call_job_id)
        if job.attempt_count > 0:
            return
        time.sleep(_POLL_INTERVAL)
    pytest.fail(f"Outbound call job did not create an attempt within {_CALL_TIMEOUT} seconds")


class TestVoiceAgentTelephonyLive:
    def test_binding_lifecycle(self, telephony_project_client: AIProjectClient) -> None:
        model = _required_env("FOUNDRY_VOICE_MODEL_NAME")
        connection = _required_env("FOUNDRY_TELEPHONY_CONNECTION_1")
        number = _phone_number("FOUNDRY_TELEPHONY_NUMBER_1")
        client = telephony_project_client
        telephony = client.beta.voice_agents.telephony
        agent_name = f"tel-bind-{uuid4().hex[:8]}"

        with ExitStack() as cleanup:
            client.agents.create_version(
                agent_name=agent_name,
                definition=_definition(model, "Greet the caller briefly, then say goodbye."),
            )
            cleanup.callback(_cleanup, client.agents.delete, agent_name=agent_name)
            binding = telephony.create_binding(
                agent_name,
                CreateTwilioTelephonyBindingRequest(
                    connection_name=connection, phone_number=number, label="Python SDK live test"
                ),
            )
            cleanup.callback(
                _cleanup, _delete_binding, telephony=telephony, agent_name=agent_name, binding_id=binding.id
            )
            assert binding.id
            listed = _find_binding(telephony, agent_name, binding.id)
            retrieved = telephony.get_binding(agent_name, binding.id)
            assert retrieved.id == binding.id
            updated = telephony.update_binding(
                agent_name,
                binding.id,
                UpdateTelephonyBindingRequest(label="Updated Python SDK live test"),
                etag=listed.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.label == "Updated Python SDK live test"
            _delete_binding(telephony, agent_name, binding.id)
            assert all(item.id != binding.id for item in telephony.list_bindings(agent_name))

    def test_twilio_binding_and_outbound_call(self, telephony_project_client: AIProjectClient) -> None:
        model = _required_env("FOUNDRY_VOICE_MODEL_NAME")
        connection1 = _required_env("FOUNDRY_TELEPHONY_CONNECTION_1")
        connection2 = _required_env("FOUNDRY_TELEPHONY_CONNECTION_2")
        number1 = _phone_number("FOUNDRY_TELEPHONY_NUMBER_1")
        number2 = _phone_number("FOUNDRY_TELEPHONY_NUMBER_2")
        assert number1 != number2, "Use two distinct, dedicated Twilio test numbers"
        client = telephony_project_client
        telephony = client.beta.voice_agents.telephony
        suffix = uuid4().hex[:8]
        inbound_agent = f"tel-in-{suffix}"
        outbound_agent = f"tel-out-{suffix}"

        with ExitStack() as cleanup:
            for agent_name, instructions in (
                (inbound_agent, "Greet the caller briefly, then say goodbye."),
                (outbound_agent, "Say hello, wait for one reply, then say goodbye."),
            ):
                client.agents.create_version(agent_name=agent_name, definition=_definition(model, instructions))
                cleanup.callback(_cleanup, client.agents.delete, agent_name=agent_name)

            binding = telephony.create_binding(
                inbound_agent,
                CreateTwilioTelephonyBindingRequest(
                    connection_name=connection1, phone_number=number1, label="Python SDK live test"
                ),
            )
            cleanup.callback(
                _cleanup, _delete_binding, telephony=telephony, agent_name=inbound_agent, binding_id=binding.id
            )
            assert binding.id
            assert binding.provider == TelephonyProvider.TWILIO
            assert binding.status == TelephonyBindingStatus.ACTIVE
            assert binding.incoming_call_url

            cleanup.callback(_cleanup, _replace_targets, telephony=telephony, agent_name=inbound_agent, targets=[])
            _replace_targets(
                telephony,
                inbound_agent,
                [
                    TelephonyTransferTarget(
                        name="test_number_2",
                        description="Python SDK live test target",
                        destination=PSTNTelephonyTransferDestination(value=number2),
                    )
                ],
            )

            job = telephony.create_call_job(
                outbound_agent,
                CreateTelephonyCallJobRequest(
                    destination=TelephonyOutboundDestination(
                        type=TelephonyOutboundDestinationType.PHONE_NUMBER, value=number1
                    ),
                    connection_name=connection2,
                    source=number2,
                    purpose="Python SDK live telephony validation",
                ),
                idempotency_key=str(uuid4()),
            )
            cleanup.callback(_cleanup, _cancel_job, telephony=telephony, agent_name=outbound_agent, call_job_id=job.id)
            assert job.id
            assert job.agent_name == outbound_agent
            assert job.connection_name == connection2
            assert job.source == number2

            inbound_call = _wait_for_inbound_call(telephony, inbound_agent)
            cleanup.callback(_cleanup, telephony.end_call, agent_name=inbound_agent, call_id=inbound_call.id)
            assert inbound_call.id
            assert inbound_call.provider == TelephonyProvider.TWILIO
            assert inbound_call.caller_number == number2
            assert inbound_call.provider_number == number1
            record = telephony.get_call(inbound_agent, inbound_call.id)
            assert record.id == inbound_call.id
            transferred = telephony.transfer_call(inbound_agent, inbound_call.id, target="test_number_2")
            assert transferred.id == inbound_call.id
            _wait_for_dispatched_job(telephony, outbound_agent, job.id)

            not_before = datetime.now(timezone.utc) + timedelta(minutes=10)
            scheduled = telephony.create_call_job(
                outbound_agent,
                CreateTelephonyCallJobRequest(
                    destination=TelephonyOutboundDestination(
                        type=TelephonyOutboundDestinationType.PHONE_NUMBER, value=number1
                    ),
                    connection_name=connection2,
                    source=number2,
                    purpose="Python SDK live cancellation validation",
                    schedule=TelephonyCallJobSchedule(
                        not_before=not_before, expires_at=not_before + timedelta(minutes=10)
                    ),
                ),
                idempotency_key=str(uuid4()),
            )
            cleanup.callback(
                _cleanup, _cancel_job, telephony=telephony, agent_name=outbound_agent, call_job_id=scheduled.id
            )
            cancelled = telephony.cancel_call_job(
                outbound_agent,
                scheduled.id,
                etag=str(scheduled.revision),
                match_condition=MatchConditions.IfNotModified,
            )
            assert cancelled.cancellation is not None
            _replace_targets(telephony, inbound_agent, [])
