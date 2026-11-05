# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline execution of the async GPT Live text and function-tool samples."""

import asyncio
import json

import pytest

from azure.ai.projects import models
from test_live_samples import (
    _closed,
    _load_module,
    _response,
    _started,
    _text_response,
    sample_environment,
)


pytestmark = pytest.mark.asyncio
_SCENARIOS = ("text_conversation", "function_tool")


def _load_sample(monkeypatch, scenario):
    return _load_module(monkeypatch, f"sample_voice_agent_live_{scenario}_async.py")


def _tool_call(**fields):
    return {
        "id": "function-item-test",
        "type": "function_call",
        "name": "get_weather",
        "call_id": "canonical-call-test",
        "arguments": '{"city":"Seattle"}',
        "status": "completed",
        **fields,
    }


def _tool_cycle(call):
    return [
        _response("response.output_item.done", item=call),
        _response("response.completed", response={"status": "completed", "output": []}),
    ]


def _assert_owned_cleanup(sample, environment):
    client, connection = environment.async_client, environment.async_connection
    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    assert agent_name.startswith("live-offline-")
    client.beta.voice_agents.live.connect.assert_called_once_with(
        agent_name=agent_name, agent_version="owned-version", store=False
    )
    client.agents.delete_version.assert_awaited_once_with(agent_name=agent_name, agent_version="owned-version")
    client.agents.delete.assert_not_called()
    connection.session.close.assert_awaited_once_with()
    connection.session.start.assert_not_called()
    connection.response.cancel.assert_not_called()
    client.beta.voice_agents.realtime.connect.assert_not_called()
    client.beta.voice_agents.live.connect.return_value.__aexit__.assert_awaited_once()
    client.__aexit__.assert_awaited_once()
    credential = sample.DefaultAzureCredential.return_value
    credential.__aenter__.assert_awaited_once()
    credential.__aexit__.assert_awaited_once()
    sample.AIProjectClient.assert_called_once_with(
        endpoint="https://example.invalid/api/projects/offline",
        credential=credential.__aenter__.return_value,
        allow_preview=True,
    )


async def test_async_text_reuses_one_session_and_waits_for_each_completed_turn(monkeypatch, sample_environment, capsys):
    sample = _load_sample(monkeypatch, "text_conversation")
    connection = sample_environment.async_connection
    prompts = ["My name is Ada.", "What is my name?"]
    monkeypatch.setattr(sample, "TEXT_PROMPTS", prompts)
    events = iter(
        [
            {"type": "future.event"},
            _started(),
            *_text_response("Hello, Ada."),
            *_text_response("Your name is Ada."),
            _closed(),
        ]
    )
    completed = 0
    submitted = []

    async def receive():
        nonlocal completed
        event = next(events)
        if event.get("type") == "response.event" and event["event"]["type"] == "response.completed":
            completed += 1
        if event.get("type") == "session.closed":
            connection.session.close.assert_awaited_once()
        return event

    async def submit(*, item):
        assert completed == len(submitted)
        submitted.append(item["content"][0]["text"])

    async def respond():
        assert connection.response.create.await_count == completed + 1

    connection.recv.side_effect = receive
    connection.response.item.create.side_effect = submit
    connection.response.create.side_effect = respond

    await sample.main()

    assert submitted == prompts
    assert completed == 2
    assert connection.response.create.await_count == 2
    sample_environment.async_client.agents.create_version.assert_awaited_once()
    _assert_owned_cleanup(sample, sample_environment)
    output = capsys.readouterr().out
    assert output.count("Responses backend: Hello, Ada.\n") == 1
    assert output.count("Responses backend: Your name is Ada.\n") == 1
    assert "Session closed: close_requested" in output


async def test_async_function_uses_canonical_call_id_after_each_completed_cycle(
    monkeypatch, sample_environment, capsys
):
    sample = _load_sample(monkeypatch, "function_tool")
    connection = sample_environment.async_connection
    call = _tool_call()
    events = iter(
        [
            _started(),
            _response("response.output_item.added", item={**call, "arguments": "", "status": "in_progress"}),
            _response("response.function_call_arguments.delta", item_id=call["id"], delta='{"city":'),
            _response("response.function_call_arguments.delta", item_id=call["id"], delta='"Seattle"}'),
            _response(
                "response.function_call_arguments.done",
                item_id=call["id"],
                name="get_weather",
                arguments=call["arguments"],
            ),
            _response("response.output_item.done", item=call),
            *_tool_cycle(call),
            *_text_response("The sample weather in Seattle is sunny, 72 F."),
            _closed(),
        ]
    )
    completed = 0
    submitted = []

    async def receive():
        nonlocal completed
        event = next(events)
        if event.get("type") == "response.event" and event["event"]["type"] == "response.completed":
            completed += 1
        if event.get("type") == "session.closed":
            connection.session.close.assert_awaited_once()
        return event

    async def submit(*, item):
        assert completed == len(submitted)
        submitted.append(item)

    async def respond():
        assert connection.response.create.await_count == completed + 1

    connection.recv.side_effect = receive
    connection.response.item.create.side_effect = submit
    connection.response.create.side_effect = respond

    await sample.main()

    assert completed == 2
    assert len(submitted) == 2
    assert submitted[0]["content"][0]["text"] == "Use get_weather for Seattle, then report the sample result."
    assert submitted[1]["type"] == "function_call_output"
    assert submitted[1]["call_id"] == call["call_id"] != call["id"]
    assert json.loads(submitted[1]["output"]) == {"city": "Seattle", "condition": "sunny", "temperature_f": 72}
    assert connection.response.create.await_count == 2
    definition = sample_environment.async_client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition, models.VoiceAgentLiveDefinition)
    assert definition.model_type == models.VoiceModelType.SELF_DEPLOYED
    assert definition.model == "live-deployment-test"
    assert definition.store is False
    assert isinstance(definition.delegation, models.VoiceAgentLiveResponsesDelegation)
    responses = definition.delegation.responses
    assert isinstance(responses, models.LiveResponsesDelegationSettingsInputParam)
    assert responses.model == "backend-deployment-test"
    assert responses.parallel_tool_calls is False
    assert len(responses.tools) == 1
    assert isinstance(responses.tools[0], models.LiveFunctionToolInputParam)
    assert responses.tools[0].name == "get_weather"
    assert responses.tools[0].strict is True
    _assert_owned_cleanup(sample, sample_environment)
    assert "Responses backend: The sample weather in Seattle is sunny, 72 F." in capsys.readouterr().out


async def test_async_function_rejects_a_repeated_call_in_a_later_cycle(monkeypatch, sample_environment):
    sample = _load_sample(monkeypatch, "function_tool")
    connection = sample_environment.async_connection
    connection.recv.side_effect = [_started(), *_tool_cycle(_tool_call()), *_tool_cycle(_tool_call())]

    with pytest.raises(RuntimeError, match="missing or repeated function call ID"):
        await sample.main()

    assert connection.response.item.create.await_count == 2
    assert connection.response.create.await_count == 2
    _assert_owned_cleanup(sample, sample_environment)


async def test_async_function_bounds_the_number_of_response_cycles(monkeypatch, sample_environment):
    sample = _load_sample(monkeypatch, "function_tool")
    connection = sample_environment.async_connection
    events = [_started()]
    for index in range(6):
        events.extend(_tool_cycle(_tool_call(call_id=f"call-{index}")))
    connection.recv.side_effect = events

    with pytest.raises(RuntimeError, match="six-response tool-call limit"):
        await sample.main()

    assert connection.response.item.create.await_count == 7
    assert connection.response.create.await_count == 7
    _assert_owned_cleanup(sample, sample_environment)


@pytest.mark.parametrize("scenario", _SCENARIOS)
@pytest.mark.parametrize(
    "event,match",
    [
        ({"type": "error", "error": {"code": "invalid_command", "message": "rejected"}}, "invalid_command: rejected"),
        (_response("response.failed", response={"status": "failed"}), "Responses backend response.failed"),
    ],
)
async def test_async_samples_propagate_service_failures(monkeypatch, sample_environment, scenario, event, match):
    sample = _load_sample(monkeypatch, scenario)
    sample_environment.async_connection.recv.side_effect = [_started(), event]

    with pytest.raises(RuntimeError, match=match):
        await sample.main()

    _assert_owned_cleanup(sample, sample_environment)


@pytest.mark.parametrize("scenario", _SCENARIOS)
@pytest.mark.parametrize("failure", [RuntimeError("create failed")])
async def test_async_samples_do_not_delete_versions_when_creation_fails(
    monkeypatch, sample_environment, scenario, failure
):
    sample = _load_sample(monkeypatch, scenario)
    client = sample_environment.async_client
    client.agents.create_version.side_effect = failure

    with pytest.raises(type(failure)):
        await sample.main()

    client.agents.delete_version.assert_not_awaited()
    client.agents.delete.assert_not_called()
    client.beta.voice_agents.live.connect.assert_not_called()
    client.__aexit__.assert_awaited_once()
    sample.DefaultAzureCredential.return_value.__aexit__.assert_awaited_once()


@pytest.mark.parametrize("scenario", _SCENARIOS)
async def test_async_samples_delete_owned_version_if_connect_fails(monkeypatch, sample_environment, scenario):
    sample = _load_sample(monkeypatch, scenario)
    client = sample_environment.async_client
    client.beta.voice_agents.live.connect.return_value.__aenter__.side_effect = ConnectionError("connect failed")

    with pytest.raises(ConnectionError, match="connect failed"):
        await sample.main()

    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    client.agents.delete_version.assert_awaited_once_with(agent_name=agent_name, agent_version="owned-version")
    client.agents.delete.assert_not_called()
    sample_environment.async_connection.session.close.assert_not_awaited()
    client.__aexit__.assert_awaited_once()
    sample.DefaultAzureCredential.return_value.__aexit__.assert_awaited_once()


@pytest.mark.parametrize("scenario", _SCENARIOS)
@pytest.mark.parametrize("phase", ["response"])
async def test_async_samples_preserve_cancellation_and_clean_up(monkeypatch, sample_environment, scenario, phase):
    sample = _load_sample(monkeypatch, scenario)
    connection = sample_environment.async_connection
    receiving = asyncio.Event()

    async def receive():
        if phase == "response" and connection.recv.await_count == 1:
            return _started()
        receiving.set()
        await asyncio.Future()

    connection.recv.side_effect = receive
    connection.session.close.side_effect = ConnectionError("cleanup failed")
    task = asyncio.create_task(sample.main())
    try:
        await asyncio.wait_for(receiving.wait(), timeout=1)
    finally:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    _assert_owned_cleanup(sample, sample_environment)
    assert connection.response.create.await_count == (1 if phase == "response" else 0)
