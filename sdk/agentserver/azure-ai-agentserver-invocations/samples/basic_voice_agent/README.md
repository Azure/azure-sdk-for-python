# Basic Voice Agent

This sample hosts a text-only agent for the Voice Live Bridge protocol `1.0`.
The SDK relays typed events while the application owns response generation,
task cancellation, correlation, and target-turn trace completion.

Caller interruptions arrive as `user.barge_in` and are handled by `@app.on_user_barge_in` with a `UserBargeIn` event. Voice Live senders must use the same event contract. Interruption cancellation and `heard_text` remain part of the same Bridge message contract.

## Prerequisites

- Python 3.10 or later
- A deployed hosted agent configured for the Voice Live Bridge

## Install

This sample requires `azure-ai-agentserver-invocations>=1.3.0b1,<2.0.0` for
`UserBargeIn` and `on_user_barge_in`. Version `1.2.x` cannot run this sample.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

Until a release containing these APIs and the CE route is published, you must
install a matching local SDK build. Replace the paths below with Core and
Invocations wheels built from the same SDK checkout:

```bash
python -m pip install \
  /path/to/azure_ai_agentserver_core-2.3.0b1-py3-none-any.whl \
  /path/to/azure_ai_agentserver_invocations-1.3.0b1-py3-none-any.whl
python -m pip install -r requirements.txt
```

After a matching release is available, `python -m pip install -r requirements.txt`
can install the dependency directly from the package feed. The version constraint
alone does not publish the new APIs or make them available in older SDK builds.

## Run

```bash
python basic_voice_agent.py
```

Install dependencies in the virtual environment or image, not with
`pip install --user`. For hosted deployments, set
`PYTHONNOUSERSITE` to `"1"` in the complete agent definition's environment
variables or Python Dockerfile, not the protocol-only manifest fragment.
See the [Python startup guide](../../../../ai/azure-ai-projects/samples/hosted_agents/README.md#python-startup-configuration).

The server listens on `0.0.0.0` and uses the `PORT` environment variable when
set; otherwise it listens on port `8088`. Foundry selects the container route
from the hosted agent's protocol declaration: `invocations_ws` forwards to
`/invocations_ws`, while `voice_conversation_engine` forwards to `/voice_conversation_engine`.

## Deploy

Use the accompanying `agent.manifest.yaml` when configuring the hosted agent.
For the legacy endpoint, the three declarations are required together: `invocations_ws`,
`voiceLiveCompatible: "true"`, and exact `bridgeProtocolVersion: "1.0"`.
Omitting the version selects the previously shipped non-Bridge integration.

### Standalone Conversation Engine

With an SDK build that includes standalone CE support, keep the existing
`app = VoiceAgentServerHost()` construction and declare CE in the hosted agent
definition. Use the field matching the agent's existing schema; enabling CE does
not require a schema migration.

For new-schema definitions using `container_configuration` or `code_configuration`:

```yaml
protocol_versions:
  - protocol: voice_conversation_engine
    version: "1.0.0"
```

For legacy definitions using `image`:

```yaml
container_protocol_versions:
  - protocol: voice_conversation_engine
    version: "1.0.0"
```

These are hosted agent definition fragments, not complete deployment manifests
or replacements for `agent.manifest.yaml`. If the agent must also serve legacy
Bridge calls, retain its existing `invocations_ws` declaration and Bridge metadata.

The typed host exposes both `/voice_conversation_engine` and `/invocations_ws`, but the
Foundry protocol declaration determines which public endpoint can invoke it.
For CE, no `invocations_ws` declaration,
`voiceLiveCompatible`, or `bridgeProtocolVersion` metadata is required. The existing
callbacks, IDs, cancellation and cleanup code are unchanged, and the message
handshake still uses `protocol_version="1.0"`. The SDK does not modify the
Foundry registration. Existing legacy deployments can keep their manifest and
metadata unchanged. Rebuild the container
with the new SDK before publishing a CE-declaring version. Foundry CE routing and
CE-aware Voice Live must be deployed before enabling this registration; local SDK
tests alone do not prove that the end-to-end route is ready.

The sample intentionally uses a simulated model stream. Replace
`generate_answer` with the application's model call while preserving the
application-owned task cleanup shown by the event callbacks.

Each response generation declares one target turn with
`session.start_target_turn(...)`. The generation task activates that handle
around the real model/output work and completes it only after the activation
scope exits. Cancellation callbacks store an application-owned terminal hint
before cancelling the task; the runner or done callback then completes the turn
with the first truthful outcome. The SDK does not inspect or retain the task.
For unfinished work, the sample maps clean peer closure to `abandoned`,
application/server failures to `error`, protocol or transport loss to
`transport_error`, and cancellation to `cancelled`. An explicit application
hint such as `end_call` or `timeout` remains the first winner.
The sample also caps active generations per connection and bounds retained model
output by both UTF-8 bytes and chunk count; excess input receives `response.none`.

`Session` is intentionally send-only and does not track whether a response is
open. After `response.created`, this sample sends `response.cancel` when local
model generation fails. Applications that stop a response for another local
reason must likewise coordinate `response.cancel` with task cancellation; a
bare `Task.cancel()` only stops local work. Bridge-originated barge-in, timeout,
response cancellation, session end, and connection termination already provide
the stop signal, so their callbacks only cancel the local task. If a send fails
or is cancelled after transport commitment, whether its frame was accepted is
ambiguous; the application must choose its own close or reconciliation policy.
The SDK does not infer that outcome or retry the frame.

`on_connection_terminating` synchronously cancels the sample's generation tasks
whenever the connection handler exits. The tasks remain responsible for their
own asynchronous resource cleanup, while `on_session_end` provides the graceful
path that also waits for them. The termination callback must stay non-blocking;
the SDK does not join application tasks or guarantee cleanup after process
termination.
