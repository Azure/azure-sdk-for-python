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

| # | Sample | Pattern | Description |
|---|--------|---------|-------------|
| 01 | [sample_01_getting_started.py](sample_01_getting_started.py) | `TextResponse` | Echo handler — simplest sync handler that echoes user input. |
| 02 | [sample_02_streaming_text_deltas.py](sample_02_streaming_text_deltas.py) | `TextResponse` + `create_text_stream` | Token-by-token streaming via async iterable. |
| 03 | [sample_03_full_control.py](sample_03_full_control.py) | `ResponseEventStream` builders | Low-level builder API — explicit `add_text_content()`, `emit_delta()`, `emit_done()`. |
| 04 | [sample_04_function_calling.py](sample_04_function_calling.py) | `ResponseEventStream` | Two-turn function calling: emit `function_call`, consume `function_call_output`. |
| 05 | [sample_05_conversation_history.py](sample_05_conversation_history.py) | `TextResponse` + async `create_text` | Multi-turn with `context.get_history()` and `ResponsesServerOptions`. |
| 06 | [sample_06_multi_output.py](sample_06_multi_output.py) | `ResponseEventStream` | Reasoning item + text message in a single response. |
| 07 | [sample_07_customization.py](sample_07_customization.py) | `TextResponse` | Custom `ResponsesServerOptions`, default model, debug logging. |
| 08 | [sample_08_mixin_composition.py](sample_08_mixin_composition.py) | `TextResponse` | Multi-protocol server via cooperative mixin inheritance. |
| 09 | [sample_09_self_hosting.py](sample_09_self_hosting.py) | `TextResponse` | Mount responses into an existing Starlette app under `/api`. |
| 10 | [sample_10_streaming_upstream.py](sample_10_streaming_upstream.py) | Raw events | Forward to upstream streaming LLM via `openai` SDK, relay SSE events. |
| 11 | [sample_11_non_streaming_upstream.py](sample_11_non_streaming_upstream.py) | `ResponseEventStream` | Forward to upstream non-streaming LLM via `openai` SDK, emit items. |
