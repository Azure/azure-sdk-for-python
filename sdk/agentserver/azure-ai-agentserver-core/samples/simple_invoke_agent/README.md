# simple_invoke_agent sample

This sample demonstrates a `FoundryCBAgent` that handles **only** the `/invoke` endpoint.
Stream vs non-stream mode is selected by the caller via the `Content-Type` request header:

| `Content-Type` header     | Response mode           |
|---------------------------|-------------------------|
| `application/json`        | Single JSON object      |
| `text/event-stream`       | SSE streaming response  |

The `/runs` and `/responses` endpoints are **not** used in this sample.

## Files

| File | Purpose |
|------|---------|
| `main.py` | Agent server — implements `agent_invoke` with stream/non-stream logic |
| `test_invoke_client.py` | Test client — sends both a non-streaming and a streaming request |
| `requirements.txt` | Python dependencies |

## Setup

```bash
pip install -r requirements.txt
pip install httpx  # for the test client
```

## Run

Start the server in one terminal:

```bash
python main.py
```

Run the test client in another terminal:

```bash
python test_invoke_client.py
```

Expected output:

```
============================================================
Non-streaming  (Content-Type: application/json)
============================================================
HTTP status : 200
Response    : {
  "status": "ok",
  "mode": "non-stream",
  "message": "The quick brown fox jumps over the lazy dog"
}

============================================================
Streaming  (Content-Type: text/event-stream)
============================================================
HTTP status : 200
Deltas      : The quick brown fox jumps over the lazy dog
[stream complete]
```

## Manual curl requests

Non-streaming:

```bash
curl -s -X POST http://localhost:8000/invoke \
    -H "Content-Type: application/json" \
    -d '{"message": "Hello world"}'
```

Streaming:

```bash
curl -s -X POST http://localhost:8000/invoke \
    -H "Content-Type: text/event-stream" \
    -d '{"message": "Hello world"}'
```

## Key concepts

### How streaming is detected

`agent_invoke` receives an `AgentInvokeContext` containing the raw HTTP headers and
parsed JSON payload. It checks the `Content-Type` header:

```python
async def agent_invoke(self, context: AgentInvokeContext):
    content_type = context.headers.get("content-type", "")
    is_stream = "text/event-stream" in content_type
    ...
```

### Non-streaming response

Return a `JSONResponse`:

```python
return JSONResponse({"status": "ok", "message": message})
```

### Streaming response

Return a `StreamingResponse` backed by an **async generator** that yields
`data: ...\n\n` SSE lines:

```python
async def _sse_stream(message: str):
    for token in message.split(" "):
        yield f"data: {json.dumps({'delta': token})}\n\n"
    yield "data: [DONE]\n\n"

return StreamingResponse(_sse_stream(message), media_type="text/event-stream")
```

### Why `agent_run` is implemented minimally

`agent_run` is abstract in `FoundryCBAgent` and must be overridden. In this sample it
just raises `NotImplementedError` to make the intent explicit — `/runs` and
`/responses` are out of scope here.
