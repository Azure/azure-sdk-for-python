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
pip install -r requirements.txt
python sample_01_getting_started.py
```

## Samples index

| # | Sample | Pattern | Description |
|---|--------|---------|-------------|
| 01 | [Getting Started](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_01_getting_started.py) | `TextResponse` | Echo handler — simplest async handler that echoes user input |
| 02 | [Streaming Text Deltas](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_02_streaming_text_deltas.py) | `TextResponse` + `text=iterable` | Token-by-token streaming via async iterable, with `configure` callback |
| 03 | [Full Control](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_03_full_control.py) | `ResponseEventStream` | Convenience, streaming, and builder — three ways to emit the same output |
| 04 | [Function Calling](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_04_function_calling.py) | `ResponseEventStream` | Two-turn function calling with convenience and builder variants |
| 05 | [Conversation History](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_05_conversation_history.py) | `TextResponse` + `text=callable` | Study tutor with `context.get_history()` and `ResponsesServerOptions` |
| 06 | [Multi-Output](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_06_multi_output.py) | `ResponseEventStream` | Math solver: reasoning + message, convenience and builder variants |
| 07 | [Customization](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_07_customization.py) | `TextResponse` | Custom `ResponsesServerOptions`, default model, debug logging |
| 08 | [Mixin Composition](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_08_mixin_composition.py) | `TextResponse` | Multi-protocol server via cooperative mixin inheritance |
| 09 | [Self-Hosting](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_09_self_hosting.py) | `TextResponse` | Mount responses into an existing Starlette app under `/api` |
| 10 | [Streaming Upstream](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_10_streaming_upstream.py) | Raw events | Forward to upstream streaming LLM via `openai` SDK, relay SSE events |
| 11 | [Non-Streaming Upstream](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_11_non_streaming_upstream.py) | `ResponseEventStream` | Forward to upstream non-streaming LLM via `openai` SDK, emit items |
| 12 | [Image Generation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_12_image_generation.py) | `ResponseEventStream` | Image gen convenience, streaming partials, and full-control builder |
| 13 | [Image Input](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_13_image_input.py) | `ResponseContext` | Receive images via URL, base64 data URL, or file ID |
| 14 | [File Inputs](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_14_file_inputs.py) | `ResponseContext` | Receive files via base64 data URL, URL, or file ID |
| 15 | [Annotations](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_15_annotations.py) | `ResponseEventStream` | Attach file_path, file_citation, and url_citation annotations to messages |
| 16 | [Structured Outputs](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_16_structured_outputs.py) | `ResponseEventStream` | Return structured JSON as a `structured_outputs` item |
| 19 | [Resilient Streaming](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_19_resilient_streaming.py) | Resilient | Canonical **framework-checkpoint** handler with `resilient_background=True` — one output item per phase + `stream.checkpoint()`; on recovery seeds from `context.persisted_response` and resumes past the checkpointed phases (re-emitting the same items with their original ids) |
| 20 | [Resilient Steering](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_20_resilient_steering.py) | Resilient + steerable | Demonstrates `context.is_steered_turn` / `context.pending_input_count` with `resilient_background=True, steerable_conversations=True`; **naive re-run** recovery (no recovery-specific code — the turn re-runs) |
| 21 | [Resilient LangGraph](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_21_resilient_langgraph.py) | Resilient + steerable | **Real-time streaming** LangGraph agent (token-by-token deltas) **composing an external durable engine**: `AsyncSqliteSaver` (graph resume) **+** framework `stream.checkpoint()` / `context.persisted_response` (client items + ids). Checkpoints 1:1 with the graph, storing the graph checkpoint id in `internal_metadata`, so recovery rewinds to the point matching the persisted items — one reply, original ids, no divergence window |
| 22 | [Resilient Multiturn](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-responses/samples/sample_22_resilient_multiturn.py) | Resilient | Multi-turn conversation with `resilient_background=True, steerable_conversations=False` — `context.conversation_chain_metadata` tracks per-turn counters |

### When to use which

- **`TextResponse`** — Use for text-only responses (samples 1, 2, 5, 7–9). Handles the full SSE lifecycle automatically.
- **`ResponseEventStream`** — Use when you need function calls, reasoning items, multiple output types, image generation, structured outputs, annotations, upstream proxying, or fine-grained event control (samples 3, 4, 6, 10–12, 15, 16).
- **`ResponseContext`** — Use `get_input_items()` to inspect incoming images and files (samples 13, 14). Use `context.is_recovery`, `context.is_steered_turn`, `context.pending_input_count`, and `context.conversation_chain_metadata` for resilient / steerable handlers (samples 19–22).

### Enabling resilience and steering

Resilient + steerable behaviour is **opt-in** via `ResponsesServerOptions` —
the defaults are both `False`. The resilient samples (19–22) each show the
exact options shape they require; in short:

```python
from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions

app = ResponsesAgentServerHost(
    options=ResponsesServerOptions(
        resilient_background=True,             # opt-in to crash recovery
        steerable_conversations=True,        # opt-in to mid-turn steering
    ),
)
```

Without `resilient_background=True`, a crash mid-handler leaves the
response in the "crash-failed" state (the next process lifetime marks
it `failed` instead of re-invoking the handler). Without
`steerable_conversations=True`, concurrent multi-turn requests for the
same conversation return `409 conversation_locked` instead of queueing.