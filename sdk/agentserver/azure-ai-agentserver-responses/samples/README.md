# Samples (Python)

Runnable Starlette servers demonstrating the `azure-ai-agentserver-responses` package.

Each sample includes:
- `app.py` to start the sample server
- `test.py` as a requests-based client that exercises the scenario

## Prerequisites

- Python 3.10+
- Dependencies from this package installed
- `requests` installed for test clients

Install requests if needed:

```bash
pip install requests
```

## Samples

### GettingStarted

A minimal echo handler showing default JSON mode, streaming SSE mode, and background mode.

```bash
python samples/GetStarted/app.py
python samples/GetStarted/test.py
```

### FunctionCalling

A two-turn function-calling flow:
- Turn 1 returns a `get_weather` function call output item.
- Turn 2 sends a `function_call_output` input item and receives a text reply.

```bash
python samples/FunctionCalling/app.py
python samples/FunctionCalling/test.py
```

### MultiOutput

A response containing multiple output items in one run:
- reasoning item with summary text
- final text message item

```bash
python samples/MultiOutput/app.py
python samples/MultiOutput/test.py
```

### ConversationHistory

A multi-turn conversational flow using `previous_response_id` and `context.get_history_async()`.

```bash
python samples/ConversationHistory/app.py
python samples/ConversationHistory/test.py
```

## Notes

- Each sample binds to a unique local port:
  - GettingStarted: `5100`
  - FunctionCalling: `5101`
  - MultiOutput: `5102`
  - ConversationHistory: `5103`
- Start one sample app before running its corresponding `test.py`.