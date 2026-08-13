# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for context-free Voice message decoding and encoding."""

import dataclasses
import inspect
import json
from types import MappingProxyType

import pytest

import azure.ai.agentserver.invocations.voice as voice
from azure.ai.agentserver.invocations.voice import (
    AgentError,
    BargeIn,
    EndCall,
    InputTextPart,
    ResponseCancel,
    ResponseCancelled,
    ResponseCreated,
    ResponseDone,
    ResponseNone,
    ResponseOutputTextDelta,
    ResponseOutputTextDone,
    ResponseTimeout,
    ResponseTimeouts,
    SessionDisconnected,
    SessionReady,
    SessionRejected,
    SessionStart,
    UserMessage,
)
from azure.ai.agentserver.invocations.voice._codec import (
    VoiceProtocolError,
    VoiceUnsupportedMessageError,
    decode_inbound_message,
    encode_outbound_message,
)
from azure.ai.agentserver.invocations.voice._models import InboundVoiceMessage, OutboundVoiceMessage


def _frame(message_type: str, **fields):
    return json.dumps(
        {
            "type": message_type,
            "id": "m_1",
            "ts": "2026-08-12T00:00:00Z",
            **fields,
        }
    )


@pytest.mark.parametrize(
    "frame",
    [
        _frame(
            "session.start",
            protocol_version="1.0",
            reconnect=False,
            response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
        ),
        _frame("user.message", item_id="in_1", content=[{"type": "input_text", "text": "hello"}]),
        _frame("user.no_input", item_id="in_2", count=1),
        _frame("user.speech_started"),
        _frame("barge_in", response_id="r_1", heard_text="heard"),
        _frame("response.accepted", response_id="r_2"),
        _frame("response.dropped", response_id="r_3", reason="queue_full"),
        _frame("response.cancelled", response_id="r_4", heard_text="heard"),
        _frame("response.timeout", item_ids=["in_3"], stage="first_output"),
        _frame("session.end", reason="caller_hangup"),
    ],
)
def test_decode_all_selected_inbound_messages(frame):
    event = decode_inbound_message(frame)
    assert event is not None
    assert dataclasses.is_dataclass(event)
    assert event.id == "m_1"


def test_session_start_caller_is_deeply_read_only():
    event = decode_inbound_message(
        _frame(
            "session.start",
            protocol_version="1.0",
            reconnect=False,
            response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
            caller={"custom_parameters": {"campaign": ["renewal"]}},
        )
    )
    assert event is not None
    assert isinstance(event.caller, MappingProxyType)
    custom_parameters = event.caller["custom_parameters"]
    assert isinstance(custom_parameters, MappingProxyType)
    assert custom_parameters["campaign"] == ("renewal",)


@pytest.mark.parametrize(
    "caller",
    [
        {"authorization": "Bearer customer-secret"},
        {"custom_parameters": {"api_key": "customer-secret"}},
        {"future_context": [{"client-secret": "customer-secret"}]},
        {"future_context": {"proxy_authorization": "Bearer customer-secret"}},
        {"future_context": {"azureApiKey": "customer-secret"}},
        {"future_context": {"bearer_token": "customer-secret"}},
        {"future_context": {"auth_token": "customer-secret"}},
        {"future_context": {"apiToken": "customer-secret"}},
        {"future_context": {"secretValue": "customer-secret"}},
        {"future_context": {"authorizationHeader": "Bearer customer-secret"}},
        {"future_context": {"sas_url": "https://example.test/?sig=customer-secret"}},
        {"future_context": {"APIKey": "customer-secret"}},
        {"future_context": {"APIKEY": "customer-secret"}},
        {"future_context": {"SASUrl": "https://example.test/?sig=customer-secret"}},
        {"future_context": {"SASURL": "https://example.test/?sig=customer-secret"}},
        {"future_context": {"ClientSecret": "customer-secret"}},
        {"future_context": {"CLIENTSECRET": "customer-secret"}},
        {"future_context": {"AUTHORIZATIONHEADER": "Bearer customer-secret"}},
        {"future_context": {"AZUREAPIKEY": "customer-secret"}},
        {"future_context": {"PROXYAUTHORIZATION": "Bearer customer-secret"}},
        {"future_context": {"XAPITOKEN": "customer-secret"}},
        {"future_context": {"SERVICECLIENTSECRET": "customer-secret"}},
        {"future_context": {"PROXYSECRET": "customer-secret"}},
        {"future_context": {"AZURESAS": "customer-secret"}},
        {"future_context": {"AZUREPWD": "customer-secret"}},
        {"future_context": {"password_count": 1}},
        {"future_context": {"password-count": 1}},
        {"future_context": {"passwordCount": 1}},
        {"future_context": {"PasswordCount": 1}},
        {"future_context": {"PASSWORDCOUNT": 1}},
    ],
)
def test_session_start_rejects_credential_bearing_caller_context(caller):
    with pytest.raises(VoiceProtocolError, match="must not contain credentials"):
        decode_inbound_message(
            _frame(
                "session.start",
                protocol_version="1.0",
                reconnect=False,
                response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
                caller=caller,
            )
        )


def test_session_start_preserves_safe_open_caller_context():
    event = decode_inbound_message(
        _frame(
            "session.start",
            protocol_version="1.0",
            reconnect=False,
            response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
            caller={
                "future_context": {
                    "token_count": 7,
                    "secretary_name": "Ada",
                    "SECRETARYNAME": "Grace",
                    "apiVersion": "2026-08-13",
                    "APIStatus": "available",
                    "KANSAS": "Wichita",
                    "sessionId": "session-1",
                    "sasquatch": True,
                }
            },
        )
    )

    assert event is not None
    assert event.caller == {
        "future_context": {
            "token_count": 7,
            "secretary_name": "Ada",
            "SECRETARYNAME": "Grace",
            "apiVersion": "2026-08-13",
            "APIStatus": "available",
            "KANSAS": "Wichita",
            "sessionId": "session-1",
            "sasquatch": True,
        }
    }


def test_session_start_rejects_invalid_unicode_in_caller_key():
    with pytest.raises(VoiceProtocolError, match="invalid Unicode"):
        decode_inbound_message(
            _frame(
                "session.start",
                protocol_version="1.0",
                reconnect=False,
                response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
                caller={"\ud800": "value"},
            )
        )


@pytest.mark.parametrize("reconnect", [False, True])
def test_session_start_rejects_explicit_null_greeting(reconnect):
    with pytest.raises(VoiceProtocolError, match="greeting"):
        decode_inbound_message(
            _frame(
                "session.start",
                protocol_version="1.0",
                reconnect=reconnect,
                greeting=None,
                response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
            )
        )


def test_session_start_reconnect_rejects_present_greeting():
    with pytest.raises(VoiceProtocolError, match="must be absent on reconnect"):
        decode_inbound_message(
            _frame(
                "session.start",
                protocol_version="1.0",
                reconnect=True,
                greeting="welcome back",
                response_timeouts={"first_output_ms": 1, "idle_ms": 2, "max_duration_ms": 3},
            )
        )


def test_selected_registry_is_exactly_ten_each_direction():
    inbound = InboundVoiceMessage.__args__
    outbound = OutboundVoiceMessage.__args__
    assert len(inbound) == 10
    assert len(outbound) == 10
    assert len({message.type for message in inbound}) == 10
    assert len({message.type for message in outbound}) == 10


def test_all_public_voice_callables_are_experimental():
    missing = []
    for name in voice.__all__:
        value = getattr(voice, name)
        if (inspect.isclass(value) or inspect.isfunction(value)) and "This is an experimental" not in (
            value.__doc__ or ""
        ):
            missing.append(name)
    assert not missing


def test_codec_exceptions_are_not_exported_from_public_voice_namespace():
    assert not hasattr(voice, "VoiceProtocolError")
    assert not hasattr(voice, "VoiceUnsupportedMessageError")


def test_all_public_voice_dataclasses_share_safe_repr():
    public_models = [getattr(voice, name) for name in voice.__all__ if dataclasses.is_dataclass(getattr(voice, name))]
    assert public_models
    assert all(model.__repr__.__name__ == "_voice_model_repr" for model in public_models)


def test_voice_model_repr_redacts_sensitive_payloads():
    sensitive = "customer-secret-value"
    ani = "+14255550123"
    models = [
        SessionStart(
            id="m_1",
            ts="2026-08-12T00:00:00Z",
            protocol_version="1.0",
            reconnect=False,
            response_timeouts=ResponseTimeouts(first_output_ms=1, idle_ms=2, max_duration_ms=3),
            greeting=sensitive,
            caller={"ani": ani, "custom_parameters": {"secret": sensitive}},
        ),
        UserMessage(
            id="m_2",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text=sensitive),),
        ),
        BargeIn(
            id="m_3",
            ts="2026-08-12T00:00:00Z",
            response_id="r_1",
            heard_text=sensitive,
        ),
        ResponseCancelled(
            id="m_4",
            ts="2026-08-12T00:00:00Z",
            response_id="r_1",
            heard_text=sensitive,
        ),
        SessionDisconnected(code=1006, reason=sensitive),
        SessionRejected(code="startup_failed", retriable=False, message=sensitive),
        ResponseOutputTextDelta(
            response_id="r_1",
            item_id="it_1",
            delta=sensitive,
            voice={"custom_lexicon_url": f"https://example.test/?sig={sensitive}"},
        ),
        ResponseOutputTextDone(response_id="r_1", item_id="it_1", text=sensitive),
        AgentError(code="backend_error", message=sensitive),
    ]

    for model in models:
        rendered = repr(model)
        assert rendered.startswith(f"{type(model).__name__}(")
        assert len(rendered) <= 1024
        assert "<redacted>" in rendered
        assert sensitive not in rendered
        assert ani not in rendered


def test_voice_model_repr_is_bounded_for_large_identifier_collections():
    event = ResponseTimeout(
        id="m_1",
        ts="2026-08-12T00:00:00Z",
        stage="first_output",
        item_ids=tuple(f"in_{index}_{'x' * 250}" for index in range(100)),
    )

    rendered = repr(event)
    assert rendered.startswith("ResponseTimeout(")
    assert "stage='first_output'" in rendered
    assert len(rendered) <= 1024


def test_outbound_voice_mapping_is_deeply_immutable_and_alias_is_normalized():
    voice = {"type": "azure-platform", "name": "en-US-Ava", "prefer_locales": ["en-US"]}
    event = ResponseOutputTextDelta(response_id="r_1", item_id="it_1", delta="hello", voice=voice)

    voice["type"] = "not-a-voice"
    voice["prefer_locales"].append("fr-FR")
    assert event.voice == {"type": "azure-platform", "name": "en-US-Ava", "prefer_locales": ("en-US",)}
    with pytest.raises(TypeError):
        event.voice["name"] = "changed"

    encoded = json.loads(encode_outbound_message(event))
    assert encoded["voice"] == {"type": "azure-standard", "name": "en-US-Ava", "prefer_locales": ["en-US"]}


@pytest.mark.parametrize(
    "voice",
    [
        {"type": "not-a-voice"},
        {"type": 1},
        {},
    ],
)
def test_outbound_voice_rejects_invalid_configuration(voice):
    event = ResponseOutputTextDone(response_id="r_1", item_id="it_1", text="hello", voice=voice)

    with pytest.raises((TypeError, ValueError)):
        encode_outbound_message(event)


@pytest.mark.parametrize(
    ("voice", "error_type", "message"),
    [
        pytest.param({"name": None}, TypeError, "voice.name must be a string", id="name-null"),
        pytest.param({"name": 42}, TypeError, "voice.name must be a string", id="name-type"),
        pytest.param({"name": ""}, ValueError, "voice.name must be non-empty", id="name-empty"),
        pytest.param(
            {"endpoint_id": None},
            TypeError,
            "voice.endpoint_id must be a string",
            id="endpoint-null",
        ),
        pytest.param(
            {"endpoint_id": 123},
            TypeError,
            "voice.endpoint_id must be a string",
            id="endpoint-type",
        ),
        pytest.param(
            {"endpoint_id": ""},
            ValueError,
            "voice.endpoint_id must be non-empty",
            id="endpoint-empty",
        ),
        pytest.param({"model": None}, TypeError, "voice.model must be a string", id="model-null"),
        pytest.param({"model": []}, TypeError, "voice.model must be a string", id="model-type"),
        pytest.param(
            {"temperature": True},
            TypeError,
            "voice.temperature must be a number or null",
            id="temperature-bool",
        ),
        pytest.param(
            {"temperature": "0.5"},
            TypeError,
            "voice.temperature must be a number or null",
            id="temperature-type",
        ),
        pytest.param(
            {"temperature": float("nan")},
            VoiceProtocolError,
            "Voice frame contains a non-finite number",
            id="temperature-nan",
        ),
        pytest.param(
            {"temperature": float("inf")},
            VoiceProtocolError,
            "Voice frame contains a non-finite number",
            id="temperature-positive-inf",
        ),
        pytest.param(
            {"temperature": float("-inf")},
            VoiceProtocolError,
            "Voice frame contains a non-finite number",
            id="temperature-negative-inf",
        ),
        pytest.param(
            {"temperature": -0.01},
            ValueError,
            "voice.temperature must be between 0.0 and 1.0",
            id="temperature-low",
        ),
        pytest.param(
            {"temperature": 1.01},
            ValueError,
            "voice.temperature must be between 0.0 and 1.0",
            id="temperature-high",
        ),
        pytest.param(
            {"locale": 1},
            TypeError,
            "voice.locale must be a string or null",
            id="locale-type",
        ),
        pytest.param(
            {"style": False},
            TypeError,
            "voice.style must be a string or null",
            id="style-type",
        ),
        pytest.param(
            {"pitch": []},
            TypeError,
            "voice.pitch must be a string or null",
            id="pitch-type",
        ),
        pytest.param(
            {"rate": {}},
            TypeError,
            "voice.rate must be a string or null",
            id="rate-type",
        ),
        pytest.param(
            {"volume": 1.0},
            TypeError,
            "voice.volume must be a string or null",
            id="volume-type",
        ),
        pytest.param(
            {"custom_lexicon_url": 1},
            TypeError,
            "voice.custom_lexicon_url must be a string or null",
            id="lexicon-type",
        ),
        pytest.param(
            {"custom_text_normalization_url": []},
            TypeError,
            "voice.custom_text_normalization_url must be a string or null",
            id="normalization-type",
        ),
        pytest.param(
            {"multi_talker_speaker_name": 1},
            TypeError,
            "voice.multi_talker_speaker_name must be a string or null",
            id="speaker-type",
        ),
        pytest.param(
            {"prefer_locales": "en-US"},
            TypeError,
            "voice.prefer_locales must be an array of strings or null",
            id="locales-type",
        ),
        pytest.param(
            {"prefer_locales": ["en-US", 1]},
            TypeError,
            "voice.prefer_locales must be an array of strings or null",
            id="locale-item-type",
        ),
    ],
)
def test_outbound_voice_rejects_invalid_known_field(voice, error_type, message):
    event = ResponseOutputTextDone(response_id="r_1", item_id="it_1", text="hello", voice=voice)

    with pytest.raises(error_type, match=message):
        encode_outbound_message(event)


@pytest.mark.parametrize("temperature", [0, 0.0, 0.5, 1, 1.0, None])
def test_outbound_voice_accepts_temperature_boundaries(temperature):
    event = ResponseOutputTextDone(
        response_id="r_1",
        item_id="it_1",
        text="hello",
        voice={"temperature": temperature},
    )

    assert json.loads(encode_outbound_message(event))["voice"] == {"temperature": temperature}


def test_outbound_voice_accepts_empty_model_as_string_field_shape():
    event = ResponseOutputTextDone(
        response_id="r_1",
        item_id="it_1",
        text="hello",
        voice={"model": ""},
    )

    assert json.loads(encode_outbound_message(event))["voice"] == {"model": ""}


@pytest.mark.parametrize(
    ("alias", "normalized"),
    [("azure-platform", "azure-standard"), ("custom", "azure-custom")],
)
def test_outbound_voice_writes_alias_normalization_to_wire(alias, normalized):
    event = ResponseOutputTextDone(
        response_id="r_1",
        item_id="it_1",
        text="hello",
        voice={"type": alias},
    )

    assert json.loads(encode_outbound_message(event))["voice"] == {"type": normalized}
    assert event.voice == {"type": alias}


def test_outbound_voice_validation_failure_is_repeatable_and_does_not_mutate_model():
    event = ResponseOutputTextDone(
        response_id="r_1",
        item_id="it_1",
        text="hello",
        voice={
            "type": "azure-platform",
            "temperature": 2.0,
            "prefer_locales": ["en-US"],
        },
    )

    for _ in range(2):
        with pytest.raises(ValueError, match="voice.temperature must be between 0.0 and 1.0"):
            encode_outbound_message(event)
        assert event.voice == {
            "type": "azure-platform",
            "temperature": 2.0,
            "prefer_locales": ("en-US",),
        }


def test_outbound_voice_accepts_all_known_fields_and_preserves_unknown_fields():
    voice = {
        "type": "azure-platform",
        "name": "en-US-Ava",
        "endpoint_id": "endpoint-1",
        "model": "model-1",
        "temperature": 0.5,
        "locale": None,
        "style": "chat",
        "pitch": None,
        "rate": "+10%",
        "volume": None,
        "custom_lexicon_url": "https://example.test/lexicon.xml",
        "custom_text_normalization_url": None,
        "prefer_locales": ["en-US", "fr-FR"],
        "multi_talker_speaker_name": None,
        "future_field": {"nested": [1, True, None]},
    }
    event = ResponseOutputTextDone(response_id="r_1", item_id="it_1", text="hello", voice=voice)

    encoded = json.loads(encode_outbound_message(event))["voice"]

    assert encoded == {**voice, "type": "azure-standard"}
    assert event.voice["type"] == "azure-platform"
    assert event.voice["prefer_locales"] == ("en-US", "fr-FR")


@pytest.mark.parametrize("mutable_leaf", [bytearray(b"secret"), {"mutable-set"}])
def test_outbound_voice_rejects_non_json_mutable_leaves(mutable_leaf):
    with pytest.raises(TypeError, match="JSON-compatible"):
        ResponseOutputTextDelta(
            response_id="r_1",
            item_id="it_1",
            delta="hello",
            voice={"future_field": mutable_leaf},
        )


def test_outbound_voice_preserves_additive_fields_for_bridge_validation():
    voice = {"future_field": {"value": 1}}
    event = ResponseOutputTextDone(response_id="r_1", item_id="it_1", text="hello", voice=voice)

    assert json.loads(encode_outbound_message(event))["voice"] == voice


def test_unknown_message_is_ignored_without_state():
    assert decode_inbound_message(_frame("future.message", value=1)) is None


@pytest.mark.parametrize(
    "message_type",
    [
        "conversation.item.create",
        "conversation.item.delete",
        "dtmf",
        "dtmf.collect.cancelled",
        "dtmf.collect.rejected",
        "handoff.failed",
    ],
)
def test_known_excluded_message_fails_loud(message_type):
    with pytest.raises(VoiceUnsupportedMessageError):
        decode_inbound_message(_frame(message_type))


def test_image_content_fails_loud():
    with pytest.raises(VoiceUnsupportedMessageError):
        decode_inbound_message(
            _frame(
                "user.message",
                item_id="in_1",
                content=[{"type": "input_image", "image_ref": "https://example/image", "mime_type": "image/png"}],
            )
        )


@pytest.mark.parametrize(
    "frame",
    [
        "[]",
        '{"type":"session.end","type":"session.end","id":"m_1","ts":"2026-08-12T00:00:00Z"}',
        _frame("response.done", response_id="r_1"),
        _frame("response.timeout", response_id="r_1", item_ids=["in_1"], stage="idle"),
        _frame("response.timeout", item_ids=[1], stage="idle"),
        _frame("session.end", reason="caller_hangup", ts="not-a-timestamp"),
    ],
)
def test_invalid_inbound_frame_fails_context_free(frame):
    with pytest.raises(VoiceProtocolError):
        decode_inbound_message(frame)


@pytest.mark.parametrize(
    "timestamp",
    [
        "٢٠٢٦-08-12T00:00:00Z",
        "2026-08-12T00:00:00.١Z",
        "2026-08-12T00:00:00+٠١:00",
    ],
)
def test_timestamp_rejects_non_ascii_digits(timestamp):
    with pytest.raises(VoiceProtocolError, match="RFC 3339"):
        decode_inbound_message(_frame("session.end", reason="completed", ts=timestamp))


@pytest.mark.parametrize(
    "message",
    [
        SessionReady(),
        SessionRejected(code="startup_failed", retriable=False),
        ResponseCreated(response_id="r_1", in_reply_to=("in_1",)),
        ResponseNone(in_reply_to=("in_1",)),
        ResponseOutputTextDelta(response_id="r_1", item_id="it_1", delta="hel"),
        ResponseOutputTextDone(response_id="r_1", item_id="it_1", text="hello"),
        ResponseDone(response_id="r_1"),
        ResponseCancel(response_id="r_1"),
        EndCall(reason="completed"),
        AgentError(code="backend_error", message="failed"),
    ],
)
def test_encode_all_selected_outbound_messages(message):
    payload = json.loads(encode_outbound_message(message))
    assert payload["type"] == message.type
    assert payload["id"].startswith("m_")
    assert payload["ts"].endswith("Z")


def test_streaming_item_is_explicit_frames():
    response_id = "r_1"
    item_id = "it_1"
    messages = [
        ResponseCreated(response_id=response_id, in_reply_to=("in_1",)),
        ResponseOutputTextDelta(response_id=response_id, item_id=item_id, delta="hel"),
        ResponseOutputTextDelta(response_id=response_id, item_id=item_id, delta="lo"),
        ResponseOutputTextDone(response_id=response_id, item_id=item_id, text="hello"),
        ResponseDone(response_id=response_id),
    ]
    payloads = [json.loads(encode_outbound_message(message)) for message in messages]
    assert [payload["type"] for payload in payloads] == [
        "response.created",
        "response.output_text.delta",
        "response.output_text.delta",
        "response.output_text.done",
        "response.done",
    ]
    assert payloads[-2]["text"] == "".join(payload["delta"] for payload in payloads[1:3])


def test_outbound_validation_does_not_consult_prior_messages():
    message = ResponseDone(response_id="r_never_opened_here")
    assert json.loads(encode_outbound_message(message))["response_id"] == "r_never_opened_here"
