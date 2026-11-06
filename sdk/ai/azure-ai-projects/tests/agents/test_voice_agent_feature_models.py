# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline wire contracts for native handoff, collection, and post-call configuration."""

from collections.abc import Mapping
from datetime import timedelta
import json

import pytest

from azure.ai.projects import models

# Reserved fictional number; used only as inert JSON, never to send or receive an SMS.
_SMS_SENDER = "+12025550123"

_SYSTEM_TOOLS = [
    pytest.param(models.VoiceAgentCollectDtmfSystemTool, "collect_dtmf", id="collect-dtmf"),
    pytest.param(models.VoiceAgentCollectSmsSystemTool, "collect_sms", id="collect-sms"),
    pytest.param(models.VoiceAgentSendDtmfSystemTool, "send_dtmf", id="send-dtmf"),
    pytest.param(models.VoiceAgentSendSmsSystemTool, "send_sms", id="send-sms"),
]

_DTMF_COMPLETION_MODES = [
    pytest.param(
        models.VoiceAgentDtmfFixedLengthCompletionMode,
        {"length": 6, "inter_digit_timeout_seconds": 2},
        {"type": "fixed_length", "length": 6, "inter_digit_timeout_seconds": 2},
        id="fixed-length",
    ),
    pytest.param(
        models.VoiceAgentDtmfTerminatorCompletionMode,
        {"terminator": models.VoiceAgentDtmfTerminator.NUMBER_SIGN, "inter_digit_timeout_seconds": 2},
        {"type": "terminator", "terminator": "#", "inter_digit_timeout_seconds": 2},
        id="number-sign",
    ),
    pytest.param(
        models.VoiceAgentDtmfTerminatorCompletionMode,
        {"terminator": models.VoiceAgentDtmfTerminator.ASTERISK, "inter_digit_timeout_seconds": 2},
        {"type": "terminator", "terminator": "*", "inter_digit_timeout_seconds": 2},
        id="asterisk",
    ),
    pytest.param(
        models.VoiceAgentDtmfInterDigitSilenceCompletionMode,
        {"inter_digit_timeout_seconds": 2},
        {"type": "inter_digit_silence", "inter_digit_timeout_seconds": 2},
        id="inter-digit-silence",
    ),
]


def _inline_graph():
    return models.VoiceAgentInlineSubagentConfig(
        subagents=[
            models.InlineVoiceSubagent(
                id="$entrypoint",
                display_description="Route the caller to a specialist.",
                model="gpt-4.1",
                instructions="Route support requests to support.",
                parallel_tool_calls=False,
                handoff_conditions=[
                    models.VoiceAgentHandoffCondition(
                        id="route-support",
                        target="support",
                        condition="The caller needs support.",
                        cancel_on_interruption=False,
                        delay_ms=timedelta(0),
                        target_response=models.VoiceAgentHandoffTargetResponse.NONE,
                    )
                ],
            ),
            models.InlineVoiceSubagent(
                id="support",
                display_description="Answer support questions.",
                model="gpt-4.1",
                instructions="Answer the support question briefly.",
                inherit_base_instructions=False,
                tools=[],
                tool_choice="none",
                temperature=0.0,
                max_response_output_tokens=128,
                voice_adaptation=models.VoiceAgentHandoffVoiceAdaptation(),
                parallel_tool_calls=False,
                handoff_conditions=[
                    models.VoiceAgentHandoffCondition(
                        id="return-to-entrypoint",
                        target="$entrypoint",
                        condition="The support question is resolved.",
                        cancel_on_interruption=True,
                        delay_ms=timedelta(milliseconds=1500),
                        target_response=models.VoiceAgentHandoffTargetResponse.AUTO,
                    )
                ],
            ),
        ],
        handoff_policy=models.VoiceAgentHandoffPolicy(max_transfers=2, max_attempts=3),
    )


def _inline_graph_wire():
    return {
        "subagent_type": "inline",
        "subagents": [
            {
                "id": "$entrypoint",
                "source": "inline",
                "interface": "voice",
                "description": "Route the caller to a specialist.",
                "model": "gpt-4.1",
                "instructions": "Route support requests to support.",
                "parallel_tool_calls": False,
                "handoff_conditions": [
                    {
                        "id": "route-support",
                        "target": "support",
                        "condition": "The caller needs support.",
                        "cancel_on_interruption": False,
                        "delay_ms": 0,
                        "target_response": "none",
                    }
                ],
            },
            {
                "id": "support",
                "source": "inline",
                "interface": "voice",
                "description": "Answer support questions.",
                "model": "gpt-4.1",
                "instructions": "Answer the support question briefly.",
                "inherit_base_instructions": False,
                "tools": [],
                "tool_choice": "none",
                "temperature": 0.0,
                "max_response_output_tokens": 128,
                "voice_adaptation": {"type": "auto"},
                "parallel_tool_calls": False,
                "handoff_conditions": [
                    {
                        "id": "return-to-entrypoint",
                        "target": "$entrypoint",
                        "condition": "The support question is resolved.",
                        "cancel_on_interruption": True,
                        "delay_ms": 1500,
                        "target_response": "auto",
                    }
                ],
            },
        ],
        "handoff_policy": {"max_transfers": 2, "max_attempts": 3},
    }


def _assert_inline_graph(config):
    assert isinstance(config, models.VoiceAgentInlineSubagentConfig)
    assert config.subagent_type == "inline"
    assert isinstance(config.handoff_policy, models.VoiceAgentHandoffPolicy)
    assert config.handoff_policy.max_transfers == 2
    assert config.handoff_policy.max_attempts == 3
    entrypoint, support = config.subagents
    assert all(isinstance(node, models.InlineVoiceSubagent) for node in config.subagents)
    assert [node.id for node in config.subagents] == ["$entrypoint", "support"]
    assert entrypoint.source == support.source == "inline"
    assert entrypoint.interface == support.interface == "voice"
    assert entrypoint.display_description == "Route the caller to a specialist."
    assert support.display_description == "Answer support questions."
    assert support.inherit_base_instructions is False
    assert entrypoint.parallel_tool_calls is support.parallel_tool_calls is False
    assert support.temperature == 0.0
    assert support.tools == []
    assert support.tool_choice == "none"
    assert support.max_response_output_tokens == 128
    assert isinstance(support.voice_adaptation, models.VoiceAgentHandoffVoiceAdaptation)
    assert support.voice_adaptation.type == "auto"
    outgoing, returning = entrypoint.handoff_conditions[0], support.handoff_conditions[0]
    assert isinstance(outgoing, models.VoiceAgentHandoffCondition)
    assert isinstance(returning, models.VoiceAgentHandoffCondition)
    assert outgoing.target == support.id
    assert returning.target == entrypoint.id
    assert outgoing.cancel_on_interruption is False
    assert returning.cancel_on_interruption is True
    assert outgoing.delay_ms == timedelta(0)
    assert returning.delay_ms == timedelta(milliseconds=1500)
    assert outgoing.target_response == "none"
    assert returning.target_response == "auto"


def test_inline_handoff_graph_writable_json_roundtrip():
    config = _inline_graph()
    expected = _inline_graph_wire()

    assert json.loads(json.dumps(config.as_dict(exclude_readonly=True))) == expected

    restored = models.VoiceAgentInlineSubagentConfig(json.loads(json.dumps(expected)))
    _assert_inline_graph(restored)
    assert restored.as_dict(exclude_readonly=True) == expected
    assert "display_description" not in restored.subagents[0].as_dict()


@pytest.mark.parametrize(
    "kwargs,expected",
    [
        pytest.param({}, {}, id="service-defaults-omitted"),
        pytest.param({"max_transfers": 1}, {"max_transfers": 1}, id="attempts-default-omitted"),
        pytest.param({"max_transfers": 1, "max_attempts": 1}, {"max_transfers": 1, "max_attempts": 1}, id="minimum"),
        pytest.param(
            {"max_transfers": 100, "max_attempts": 100},
            {"max_transfers": 100, "max_attempts": 100},
            id="maximum",
        ),
    ],
)
def test_handoff_policy_writable_json_roundtrip(kwargs, expected):
    policy = models.VoiceAgentHandoffPolicy(**kwargs)
    assert json.loads(json.dumps(policy.as_dict(exclude_readonly=True))) == expected

    restored = models.VoiceAgentHandoffPolicy(json.loads(json.dumps(expected)))
    assert restored.max_transfers == expected.get("max_transfers")
    assert restored.max_attempts == expected.get("max_attempts")
    assert restored.as_dict(exclude_readonly=True) == expected


@pytest.mark.parametrize("delay_ms", [0, 1500, 10000])
def test_handoff_condition_uses_integer_milliseconds_and_preserves_false(delay_ms):
    condition = models.VoiceAgentHandoffCondition(
        id="route-support",
        target="support",
        condition="The caller needs support.",
        cancel_on_interruption=False,
        delay_ms=timedelta(milliseconds=delay_ms),
        target_response=models.VoiceAgentHandoffTargetResponse.NONE,
    )
    expected = {
        "id": "route-support",
        "target": "support",
        "condition": "The caller needs support.",
        "cancel_on_interruption": False,
        "delay_ms": delay_ms,
        "target_response": "none",
    }
    writable = json.loads(json.dumps(condition.as_dict(exclude_readonly=True)))
    assert writable == expected
    assert type(writable["delay_ms"]) is int
    assert writable["cancel_on_interruption"] is False

    restored = models.VoiceAgentHandoffCondition(json.loads(json.dumps(expected)))
    assert restored.delay_ms == timedelta(milliseconds=delay_ms)
    assert restored.cancel_on_interruption is False
    assert restored.target == "support"
    assert restored.target_response == "none"
    assert restored.transfer_message is None


@pytest.mark.parametrize("mode_type,mode_kwargs,mode_wire", _DTMF_COMPLETION_MODES)
def test_dtmf_completion_mode_concrete_writable_json_roundtrip(mode_type, mode_kwargs, mode_wire):
    mode = mode_type(**mode_kwargs)
    assert json.loads(json.dumps(mode.as_dict(exclude_readonly=True))) == mode_wire

    restored = mode_type(json.loads(json.dumps(mode_wire)))
    assert restored.type == mode_wire["type"]
    assert restored.inter_digit_timeout_seconds == 2
    if mode_wire["type"] == "fixed_length":
        assert restored.length == 6
    elif mode_wire["type"] == "terminator":
        assert restored.terminator == mode_wire["terminator"]
    assert restored.as_dict(exclude_readonly=True) == mode_wire


@pytest.mark.parametrize("mode_type,mode_kwargs,mode_wire", _DTMF_COMPLETION_MODES)
@pytest.mark.parametrize("secret", [False, True], ids=["public-value", "private-reference"])
def test_dtmf_collection_arguments_writable_json_roundtrip(mode_type, mode_kwargs, mode_wire, secret):
    kwargs = {
        "secret": secret,
        "completion_mode": mode_type(**mode_kwargs),
        "timeout_seconds": 60,
        "first_digit_timeout_seconds": 5,
    }
    expected = {
        "secret": secret,
        "completion_mode": mode_wire,
        "timeout_seconds": 60,
        "first_digit_timeout_seconds": 5,
    }
    if secret:
        kwargs["output_variable_name"] = "verification_code"
        expected["output_variable_name"] = "verification_code"
    arguments = models.VoiceAgentCollectDtmfStartArguments(**kwargs)
    assert json.loads(json.dumps(arguments.as_dict(exclude_readonly=True))) == expected
    assert isinstance(arguments.completion_mode, mode_type)

    restored = models.VoiceAgentCollectDtmfStartArguments(json.loads(json.dumps(expected)))
    assert restored.secret is secret
    assert restored.timeout_seconds == 60
    assert restored.first_digit_timeout_seconds == 5
    assert restored.output_variable_name == ("verification_code" if secret else None)
    mode_data = restored.completion_mode
    assert isinstance(mode_data, Mapping)
    assert mode_data == mode_wire
    # This union has no discriminator base; reconstruct its public member explicitly.
    completion_mode = mode_type(dict(mode_data))
    assert completion_mode.type == mode_data["type"] == mode_wire["type"]
    assert completion_mode.inter_digit_timeout_seconds == 2
    if mode_wire["type"] == "fixed_length":
        assert completion_mode.length == 6
    elif mode_wire["type"] == "terminator":
        assert completion_mode.terminator == mode_wire["terminator"]
    assert completion_mode.as_dict(exclude_readonly=True) == mode_wire
    assert restored.as_dict(exclude_readonly=True) == expected


@pytest.mark.parametrize("secret", [False, True], ids=["public-value", "private-reference"])
def test_sms_collection_arguments_writable_json_roundtrip(secret):
    kwargs = {"secret": secret, "from_phone_number": _SMS_SENDER, "timeout_seconds": 60}
    expected = {"secret": secret, "from_phone_number": "+12025550123", "timeout_seconds": 60}
    if secret:
        kwargs["output_variable_name"] = "confirmation_message"
        expected["output_variable_name"] = "confirmation_message"
    arguments = models.VoiceAgentCollectSmsStartArguments(**kwargs)
    assert json.loads(json.dumps(arguments.as_dict(exclude_readonly=True))) == expected

    restored = models.VoiceAgentCollectSmsStartArguments(json.loads(json.dumps(expected)))
    assert restored.secret is secret
    assert restored.from_phone_number == "+12025550123"
    assert restored.timeout_seconds == 60
    assert restored.output_variable_name == ("confirmation_message" if secret else None)
    assert restored.as_dict(exclude_readonly=True) == expected


@pytest.mark.parametrize(
    "argument_type,kwargs,expected",
    [
        pytest.param(
            models.VoiceAgentCollectionStartArguments,
            {"secret": False},
            {"secret": False},
            id="generic",
        ),
        pytest.param(
            models.VoiceAgentCollectDtmfStartArguments,
            {"secret": False, "completion_mode": models.VoiceAgentDtmfFixedLengthCompletionMode()},
            {"secret": False, "completion_mode": {"type": "fixed_length"}},
            id="dtmf",
        ),
        pytest.param(
            models.VoiceAgentCollectSmsStartArguments,
            {"secret": False, "from_phone_number": _SMS_SENDER},
            {"secret": False, "from_phone_number": "+12025550123"},
            id="sms",
        ),
    ],
)
def test_collection_arguments_keep_false_without_inventing_service_defaults(argument_type, kwargs, expected):
    arguments = argument_type(**kwargs)
    assert json.loads(json.dumps(arguments.as_dict(exclude_readonly=True))) == expected

    restored = argument_type(json.loads(json.dumps(expected)))
    assert restored.secret is False
    assert restored.timeout_seconds is None
    assert restored.output_variable_name is None
    assert restored.as_dict(exclude_readonly=True) == expected


@pytest.mark.parametrize("tool_type,tool_name", _SYSTEM_TOOLS)
@pytest.mark.parametrize("timeout_seconds", [1, 300])
def test_system_tool_discriminators_and_timeout_roundtrip(tool_type, tool_name, timeout_seconds):
    tool = tool_type(
        description="Offline system-tool configuration.", timeout_seconds=timedelta(seconds=timeout_seconds)
    )
    expected = {
        "type": "system",
        "name": tool_name,
        "description": "Offline system-tool configuration.",
        "timeout_seconds": timeout_seconds,
    }
    writable = json.loads(json.dumps(tool.as_dict(exclude_readonly=True)))
    assert writable == expected
    assert type(writable["timeout_seconds"]) is int

    wire = {
        "kind": "voice",
        "sub_protocol": "realtime",
        "model_type": "managed",
        "model": "gpt-4.1",
        "tools": [expected],
    }
    restored = models.VoiceAgentDefinition(json.loads(json.dumps(wire)))
    assert len(restored.tools) == 1
    restored_tool = restored.tools[0]
    assert isinstance(restored_tool, tool_type)
    assert isinstance(restored_tool, models.VoiceAgentSystemTool)
    assert restored_tool.type == "system"
    assert restored_tool.name == tool_name
    assert restored_tool.description == "Offline system-tool configuration."
    assert restored_tool.timeout_seconds == timedelta(seconds=timeout_seconds)
    assert restored.as_dict(exclude_readonly=True) == wire


@pytest.mark.parametrize("include", [None, []], ids=["omitted", "transcript-only"])
def test_post_call_destinations_writable_json_roundtrip(include):
    config = models.VoiceAgentPostCallConfig(
        destinations=[
            models.VoiceAgentEventGridPostCallDestination(connection_name="offline-events"),
            models.VoiceAgentRoutinePostCallDestination(name="offline-summary"),
        ],
        include=include,
    )
    expected = {
        "destinations": [
            {"type": "event_grid", "connection_name": "offline-events"},
            {"type": "routine", "name": "offline-summary"},
        ]
    }
    if include is not None:
        expected["include"] = []
    assert json.loads(json.dumps(config.as_dict(exclude_readonly=True))) == expected

    restored = models.VoiceAgentPostCallConfig(json.loads(json.dumps(expected)))
    event_grid, routine = restored.destinations
    assert isinstance(event_grid, models.VoiceAgentEventGridPostCallDestination)
    assert isinstance(routine, models.VoiceAgentRoutinePostCallDestination)
    assert event_grid.type == "event_grid"
    assert event_grid.connection_name == "offline-events"
    assert routine.type == "routine"
    assert routine.name == "offline-summary"
    assert restored.include == include
    assert restored.as_dict(exclude_readonly=True) == expected


def test_native_voice_definition_preserves_advanced_feature_models_on_version_readback():
    definition = models.VoiceAgentDefinition(
        model_type=models.VoiceModelType.MANAGED,
        model="gpt-4.1",
        instructions="Help the caller and route support questions.",
        store=False,
        parallel_tool_calls=False,
        subagent_config=_inline_graph(),
        tools=[
            models.VoiceAgentCollectDtmfSystemTool(),
            models.VoiceAgentCollectSmsSystemTool(),
            models.VoiceAgentSendDtmfSystemTool(),
            models.VoiceAgentSendSmsSystemTool(),
        ],
        post_call=models.VoiceAgentPostCallConfig(
            destinations=[
                models.VoiceAgentEventGridPostCallDestination(connection_name="offline-events"),
                models.VoiceAgentRoutinePostCallDestination(name="offline-summary"),
            ],
            include=[],
        ),
    )
    expected = {
        "kind": "voice",
        "sub_protocol": "realtime",
        "model_type": "managed",
        "model": "gpt-4.1",
        "instructions": "Help the caller and route support questions.",
        "store": False,
        "parallel_tool_calls": False,
        "subagent_config": _inline_graph_wire(),
        "tools": [
            {"type": "system", "name": "collect_dtmf"},
            {"type": "system", "name": "collect_sms"},
            {"type": "system", "name": "send_dtmf"},
            {"type": "system", "name": "send_sms"},
        ],
        "post_call": {
            "destinations": [
                {"type": "event_grid", "connection_name": "offline-events"},
                {"type": "routine", "name": "offline-summary"},
            ],
            "include": [],
        },
    }
    assert json.loads(json.dumps(definition.as_dict(exclude_readonly=True))) == expected

    wire = {
        "object": "agent.version",
        "id": "offline-voice:1",
        "name": "offline-voice",
        "version": "1",
        "created_at": 1700000000,
        "metadata": {},
        "definition": expected,
    }
    version = models.AgentVersionDetails(json.loads(json.dumps(wire)))
    restored = version.definition
    assert isinstance(restored, models.VoiceAgentDefinition)
    assert restored.kind == "voice"
    assert restored.sub_protocol == "realtime"
    assert restored.model_type == "managed"
    assert restored.model == "gpt-4.1"
    assert restored.store is False
    assert restored.parallel_tool_calls is False
    _assert_inline_graph(restored.subagent_config)
    assert len(restored.tools) == 4
    assert isinstance(restored.tools[0], models.VoiceAgentCollectDtmfSystemTool)
    assert isinstance(restored.tools[1], models.VoiceAgentCollectSmsSystemTool)
    assert isinstance(restored.tools[2], models.VoiceAgentSendDtmfSystemTool)
    assert isinstance(restored.tools[3], models.VoiceAgentSendSmsSystemTool)
    assert [tool.name for tool in restored.tools] == ["collect_dtmf", "collect_sms", "send_dtmf", "send_sms"]
    assert isinstance(restored.post_call, models.VoiceAgentPostCallConfig)
    event_grid, routine = restored.post_call.destinations
    assert isinstance(event_grid, models.VoiceAgentEventGridPostCallDestination)
    assert isinstance(routine, models.VoiceAgentRoutinePostCallDestination)
    assert event_grid.connection_name == "offline-events"
    assert routine.name == "offline-summary"
    assert restored.post_call.include == []
    assert restored.as_dict(exclude_readonly=True) == expected
    assert version.as_dict() == wire
