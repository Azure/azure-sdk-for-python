**IMPORTANT!** All samples and other resources made available in this GitHub repository ("samples") are designed to assist in accelerating development of agents, solutions, and agent workflows for various scenarios. Review all provided resources and carefully test output behavior in the context of your use case. AI responses may be inaccurate and AI actions should be monitored with human oversight.

# Echo Agent — Invocations Protocol (WebSocket Streaming)

This sample demonstrates a minimal echo agent built with [azure-ai-agentserver-invocations](https://pypi.org/project/azure-ai-agentserver-invocations/) that streams responses word-by-word using WebSocket.

## How It Works

The agent receives user input via the Invocations protocol over WebSocket (`ws://localhost:8088/invocations/ws`) and echoes it back with a `🔊 Echo:` prefix. Each word is streamed as a separate `stream_chunk` message, followed by a final `stream_end` signal.

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

### Test

Using the included client:

```bash
python streaming_client.py
python streaming_client.py --message "Hello world!"
```

Or using the `websockets` library directly:

```python
import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8088/invocations/ws") as ws:
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

## Deploying to Microsoft Foundry

To deploy your agent to Microsoft Foundry, follow the deployment guide at https://github.com/microsoft/hosted-agents-vnext-private-preview/blob/main/azd-quickstart.md
