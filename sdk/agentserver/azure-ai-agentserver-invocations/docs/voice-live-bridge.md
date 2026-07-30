# Voice Live Bridge submodule for Python

The `azure.ai.agentserver.invocations.voice` submodule adds a typed Voice Live
Bridge Protocol `1.0` host to the `azure-ai-agentserver-invocations` library. It
reuses `/invocations_ws` and owns WebSocket framing, protocol identifiers,
ordering, terminal arbitration, callback coordination, observability, and
connection cleanup.

## Getting started

### Prerequisites

- Python 3.10 or later.
- An Azure AI Hosted Agent deployment configured for Voice Live Bridge Protocol
  `1.0`.
- A Voice Live bridge and platform deployment that supports the capabilities
  used by the application.

### Install the package

```bash
pip install azure-ai-agentserver-invocations
```

This installs `azure-ai-agentserver-core` as a dependency. Authentication and
bridge route authorization are owned by the Hosted Agent platform; application
code does not accept caller credentials through this library.

## Key concepts

### `VoiceAgentServerHost`

`VoiceAgentServerHost` derives from `InvocationAgentServerHost` and owns the
`/invocations_ws` route for exact Bridge Protocol `1.0`. Register typed async
callbacks before calling `run()`.

`on_user_message` is required. Optional callbacks cover no-input turns,
speech-start signals, DTMF, handoff recovery, history mutation, barge-in,
response timeout, and session end.

### Sessions, responses, and items

- `VoiceSession` exposes immutable startup context and session-scoped controls.
- `VoiceResponse` represents one SDK-owned `r_` response and opens lazily on its
  first response-scoped operation.
- `VoiceTextItem` represents one ordered SDK-owned `it_` output item.
- Inbound bridge turns use bridge-owned `in_` identifiers.
- `VoiceCancellationToken` lets model/tool work cooperatively stop after a
  timeout, barge-in, session end, or disconnect.

Normal callback return emits `response.done` only after all output items are
complete. Use `decline()` for an explicit no-reply outcome, `fail()` for a
response-scoped error, or `handoff()` for a terminal agent transfer.

### Connection and privacy boundary

Every WebSocket connection creates a fresh runtime. The SDK does not reconnect,
retain helper state across connections, or replay callbacks and output. Caller
metadata, transcript text, DTMF digits, image references, and generated text are
excluded from SDK-owned telemetry by default.

## Examples

### Basic agent

```python
from azure.ai.agentserver.invocations.voice import (
    UserMessageEvent,
    VoiceAgentServerHost,
    VoiceResponse,
    VoiceSession,
)

app = VoiceAgentServerHost()


@app.on_user_message
async def answer(
    session: VoiceSession,
    event: UserMessageEvent,
    response: VoiceResponse,
) -> None:
    del session
    await response.send_text(f"You said: {event.text}")


app.run()
```

The bridge supplies an `in_` input item. The SDK allocates the `r_` response and
`it_` output item and emits `response.created`, output, and `response.done` in
protocol order.

### Stream a response

```python
@app.on_user_message
async def stream_answer(
    session: VoiceSession,
    event: UserMessageEvent,
    response: VoiceResponse,
) -> None:
    del session
    async for token in stream_model_reply(event.text):
        await response.send_text_delta(token)
    await response.send_text_done()
```

### Explicitly decline a turn

```python
@app.on_user_message
async def maybe_answer(
    session: VoiceSession,
    event: UserMessageEvent,
    response: VoiceResponse,
) -> None:
    del session
    if not event.text.strip():
        await response.decline(reason="no_reply_needed")
        return
    await response.send_text("How can I help?")
```

### Collect DTMF input

```python
from azure.ai.agentserver.invocations.voice import DtmfCollectedEvent


@app.on_user_message
async def present_menu(session, event, response):
    del session, event
    await response.send_text("Enter your four-digit PIN, followed by pound.")
    await response.collect_dtmf(
        max_digits=4,
        terminator="#",
        initial_timeout_ms=10_000,
        inter_digit_timeout_ms=5_000,
    )


@app.on_dtmf_collected
async def handle_digits(
    session: VoiceSession,
    event: DtmfCollectedEvent,
    response: VoiceResponse,
) -> None:
    del session
    await response.send_text(f"Received {len(event.digits)} digits.")
```

DTMF digits are sensitive caller content. Avoid recording them in logs, span
attributes, or exception messages.

### Hand off to another hosted agent

```python
@app.on_user_message
async def route_to_billing(session, event, response):
    del session, event
    await response.handoff(
        target="billing-agent",
        message="Connecting you to billing.",
    )
```

If target activation fails, the bridge sends a new `handoff.failed` recovery
turn to the `on_handoff_failed` callback.

## Troubleshooting

### Activation returns `session.rejected`

Register `on_user_message` before the first connection. The typed host accepts
only exact Bridge Protocol `1.0`; malformed `session.start` payloads or another
application frame before readiness reject activation.

### A response helper raises `VoiceBridgeConnectionClosedError`

The response or connection already reached a terminal boundary. Stop local
generation and use `response.cancellation` to coordinate cooperative model or
tool cancellation. Do not retry writes on the same helper.

### A proactive response is dropped

`start_proactive_response()` completes only after `response.accepted`. Handle
`VoiceProactiveResponseDroppedError` and create a new proactive response if the
application still needs to speak; never reuse a dropped response identifier.

## Next steps

- Run the [basic Voice agent sample](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-invocations/samples/basic_voice_agent).
- Review the [Voice submodule design](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-invocations/docs/voice-live-bridge-sdk-design.md).
- Review the parent Invocations README for the underlying raw WebSocket host.

End-to-end feature availability still depends on the corresponding Voice Live
bridge and Hosted Agent platform capabilities.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution. For
details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information, see the
[Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com).