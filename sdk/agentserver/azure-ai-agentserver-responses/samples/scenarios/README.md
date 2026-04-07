# Azure AI Agent Server — Responses Samples

End-to-end scenario samples for `azure-ai-agentserver-responses`.

## Quick start

```bash
pip install -r requirements.txt
python sample_01_getting_started.py
```

## Samples index

### Starter samples (in `samples/`)

| Sample | Description |
|--------|-------------|
| [GetStarted/app.py](../GetStarted/app.py) | Minimal "Hello World" — sync handler, single message output. |
| [FunctionCalling/app.py](../FunctionCalling/app.py) | Two-turn function-calling pattern with `get_weather`. |
| [ConversationHistory/app.py](../ConversationHistory/app.py) | Multi-turn conversation with `context.get_history()`. |
| [MultiOutput/app.py](../MultiOutput/app.py) | Reasoning item followed by a text message. |
| [MultiProtocol/app.py](../MultiProtocol/app.py) | Invocations + Responses protocols on a single host. |

### Scenario samples (in `samples/scenarios/`)

| # | Sample | Description |
|---|--------|-------------|
| 01 | [sample_01_getting_started.py](sample_01_getting_started.py) | Echo handler — simplest sync handler that echoes user input. |
| 02 | [sample_02_streaming_text_deltas.py](sample_02_streaming_text_deltas.py) | Token-by-token streaming via `aoutput_item_message` with an async iterable. |
| 03 | [sample_03_full_control.py](sample_03_full_control.py) | Low-level builder API — explicit `add_text_content()`, `emit_delta()`, `emit_done()`. |
| 04 | [sample_04_function_calling.py](sample_04_function_calling.py) | Two-turn function calling: emit `function_call`, consume `function_call_output`. |
| 05 | [sample_05_conversation_history.py](sample_05_conversation_history.py) | Multi-turn with `context.get_history()` and `ResponsesServerOptions`. |
| 06 | [sample_06_multi_output.py](sample_06_multi_output.py) | Reasoning item + text message in a single response. |
