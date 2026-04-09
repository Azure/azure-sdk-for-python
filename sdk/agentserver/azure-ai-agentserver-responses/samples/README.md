---
page_type: sample
languages:
- python
products:
- azure
name: azure-ai-agentserver-responses samples for Python
description: Samples for the azure-ai-agentserver-responses client library.
---

# azure-ai-agentserver-responses Samples

## Quick start

```bash
pip install -r scenarios/requirements.txt
python scenarios/sample_01_getting_started.py
```

## Samples index

| # | Sample | Pattern | Description |
|---|--------|---------|-------------|
| 01 | [Getting Started](scenarios/sample_01_getting_started.py) | `TextResponse` | Echo handler — simplest sync handler that echoes user input |
| 02 | [Streaming Text Deltas](scenarios/sample_02_streaming_text_deltas.py) | `TextResponse` + `create_text_stream` | Token-by-token streaming via async iterable |
| 03 | [Full Control](scenarios/sample_03_full_control.py) | `ResponseEventStream` builders | Low-level builder API — explicit `add_text_content()`, `emit_delta()`, `emit_done()` |
| 04 | [Function Calling](scenarios/sample_04_function_calling.py) | `ResponseEventStream` | Two-turn function calling: emit `function_call`, consume `function_call_output` |
| 05 | [Conversation History](scenarios/sample_05_conversation_history.py) | `TextResponse` + async `create_text` | Multi-turn with `context.get_history()` and `ResponsesServerOptions` |
| 06 | [Multi-Output](scenarios/sample_06_multi_output.py) | `ResponseEventStream` | Reasoning item + text message in a single response |
| 07 | [Customization](scenarios/sample_07_customization.py) | `TextResponse` | Custom `ResponsesServerOptions`, default model, debug logging |
| 08 | [Mixin Composition](scenarios/sample_08_mixin_composition.py) | `TextResponse` | Multi-protocol server via cooperative mixin inheritance |
| 09 | [Self-Hosting](scenarios/sample_09_self_hosting.py) | `TextResponse` | Mount responses into an existing Starlette app under `/api` |
| 10 | [Streaming Upstream](scenarios/sample_10_streaming_upstream.py) | Raw events | Forward to upstream streaming LLM via `openai` SDK, relay SSE events |
| 11 | [Non-Streaming Upstream](scenarios/sample_11_non_streaming_upstream.py) | `ResponseEventStream` | Forward to upstream non-streaming LLM via `openai` SDK, emit items |

### When to use which

- **`TextResponse`** — Use for text-only responses (samples 1, 2, 5, 7–9). Handles the full SSE lifecycle automatically.
- **`ResponseEventStream`** — Use when you need function calls, reasoning items, multiple output types, upstream proxying, or fine-grained event control (samples 3, 4, 6, 10, 11).