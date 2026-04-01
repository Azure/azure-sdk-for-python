# GettingStarted (Python)

This sample mirrors the .NET GettingStarted sample and shows how to host the Responses API with Starlette.

## Streaming event style used in this sample

The sample emits streaming events with typed builders instead of a generic output-item delta payload.

Event flow used in `samples/GetStarted/app.py`:

1. Create message item: `stream.add_output_item_message()`
2. Emit message added: `message_item.emit_added()`
3. Create text part: `message_item.add_text_content()`
4. Emit text part events: `emit_added()` -> `emit_delta()` -> `emit_done()`
5. Seal content part on message: `message_item.emit_content_done(text_content)`
6. Emit message done: `message_item.emit_done()`

Minimal excerpt:

```python
message_item = stream.add_output_item_message()
yield message_item.emit_added()

text_content = message_item.add_text_content()
yield text_content.emit_added()
yield text_content.emit_delta("Hello from the Python GettingStarted sample!")
yield text_content.emit_done()
yield message_item.emit_content_done(text_content)

yield message_item.emit_done()
```

## Start server

From the repository root:

```bash
python samples/GetStarted/app.py
```

## Run sample test script (requests)

Install dependency (if needed):

```bash
pip install requests
```

Run script:

```bash
python samples/GetStarted/test.py
```

## Health check

```bash
curl http://127.0.0.1:5100/ready
```

## Create response (JSON mode)

```bash
curl -X POST http://127.0.0.1:5100/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","input":"hello"}'
```

## Create response (stream mode)

```bash
curl -N -X POST http://127.0.0.1:5100/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","input":"hello","stream":true}'
```

## Background mode

```bash
curl -X POST http://127.0.0.1:5100/responses \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","input":"hello","background":true}'
```

Then query by id:

```bash
curl http://127.0.0.1:5100/responses/<response_id>
```
