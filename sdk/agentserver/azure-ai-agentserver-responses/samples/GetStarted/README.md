# GettingStarted (Python)

This sample mirrors the .NET GettingStarted sample and shows how to host the Responses API with Starlette.

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
