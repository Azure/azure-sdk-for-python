# Basic Voice Agent

This sample hosts a text-only agent for the Voice Live Bridge protocol `1.0`.
The SDK relays typed events while the application owns response generation,
task cancellation, and correlation.

## Prerequisites

- Python 3.10 or later
- A deployed hosted agent configured for the Voice Live Bridge

## Install

Create and activate a virtual environment, then install the sample dependency:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

For local SDK development, install the sibling packages or their wheels instead
of the published dependency:

```bash
python -m pip install \
  /path/to/azure_ai_agentserver_core-2.1.0b1-py3-none-any.whl \
  /path/to/azure_ai_agentserver_invocations-1.1.0b2-py3-none-any.whl
```

## Run

```bash
python basic_voice_agent.py
```

The server listens on `0.0.0.0` and uses the `PORT` environment variable when
set; otherwise it listens on port `8088`. The hosted platform connects to the
`/invocations_ws` route.

## Deploy

Use the accompanying `agent.manifest.yaml` when configuring the hosted agent.
The three declarations are required together: `invocations_ws`,
`voiceLiveCompatible: "true"`, and exact `bridgeProtocolVersion: "1.0"`.
Omitting the version selects the previously shipped non-Bridge integration.

The sample intentionally uses a simulated model stream. Replace
`generate_answer` with the application's model call while preserving the
application-owned task cleanup shown by the event callbacks.

`on_connection_terminating` synchronously cancels the sample's generation tasks
whenever the connection handler exits. The tasks remain responsible for their
own asynchronous resource cleanup, while `on_session_end` provides the graceful
path that also waits for them. The termination callback must stay non-blocking;
the SDK does not join application tasks or guarantee cleanup after process
termination.
