**IMPORTANT!** All samples and other resources made available in this GitHub repository ("samples") are designed to assist in accelerating development of agents, solutions, and agent workflows for various scenarios. Review all provided resources and carefully test output behavior in the context of your use case. AI responses may be inaccurate and AI actions should be monitored with human oversight.

# Echo Agent — Conversations Protocol (WebSocket + HTTP SSE Streaming)

This sample demonstrates a minimal echo agent built with [azure-ai-agentserver-conversations](https://pypi.org/project/azure-ai-agentserver-conversations/) that streams responses word-by-word. It supports **two communication modes**:

- **WebSocket** — persistent connection at `ws://localhost:8088/conversations/ws`
- **HTTP SSE** — stateless POST at `http://localhost:8088/conversations`

## How It Works

The agent receives user input and echoes it back with a `🔊 Echo:` prefix. Each word is streamed as a separate token chunk.

- **WebSocket mode**: tokens are sent as `stream_chunk` messages, followed by a `stream_end` signal.
- **HTTP SSE mode**: tokens are sent as `data:` lines per the Server-Sent Events spec, followed by an `event: done` signal.

## Running Locally

### Prerequisites

- Python 3.10+
- Azure CLI installed and authenticated (`az login`)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the Agent

```bash
python main.py
```

The agent starts on `http://localhost:8088/`.

### Test with WebSocket

Using the `websockets` library:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/conversations/ws") as ws:
        await ws.send(json.dumps({
            "action": "invoke",
            "payload": {"message": "Hello world!"}
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg["type"] == "stream_chunk":
                print(msg["payload"]["token"], end=" ", flush=True)
            elif msg["type"] == "stream_end":
                print("\nDone!", flush=True)
                break
            elif msg["type"] == "error":
                print(f"Error: {msg['error']}")
                break

asyncio.run(main())
```

### Test with HTTP SSE

Using `curl`:

```bash
curl -N -X POST http://localhost:8088/conversations \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello world!"}'
```

### Browser Client

A browser-based client with a WebSocket/HTTP mode switcher is available under `../browser_client/`:

```bash
cd ../browser_client
python client.py
```

Then open `http://localhost:8080` and use the toggle to switch between WebSocket and HTTP (SSE) modes.

## Deploying to Microsoft Foundry

To deploy your agent to Microsoft Foundry, follow the deployment guide at https://github.com/microsoft/hosted-agents-vnext-private-preview/blob/main/azd-quickstart.md
