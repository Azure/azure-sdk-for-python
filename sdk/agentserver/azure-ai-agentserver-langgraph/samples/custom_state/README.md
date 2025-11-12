# Custom LangGraph State Converter (Mini RAG) Sample

This sample demonstrates how to host a LangGraph agent **with a custom internal state** using the `azure.ai.agentserver` SDK by supplying a custom `LanggraphStateConverter` (`RAGStateConverter`). It shows the minimal pattern required to adapt OpenAI Responses-style requests to a LangGraph state and back to an OpenAI-compatible response.

## What It Shows
- Defining a custom state (`RAGState`) separate from the wire contract.
- Implementing `RAGStateConverter.request_to_state` and `state_to_response` to bridge request ↔ graph ↔ response.
- A simple multi-step graph: intent analysis → optional retrieval → answer generation.
- Lightweight retrieval (keyword scoring over an in‑memory knowledge base) with citation annotations added to the assistant message.
- Graceful local fallback answer when Azure OpenAI credentials are absent.
- Non‑streaming response path only (streaming intentionally not implemented).

## Flow Overview
```
CreateResponse request
  -> RAGStateConverter.request_to_state
    -> LangGraph executes nodes (analyze → retrieve? → answer)
      -> Final state
        -> RAGStateConverter.state_to_response
          -> OpenAI-style response object
```

## Running
```
python main.py
```
Optional environment variables for live model call:
- AZURE_OPENAI_API_KEY
- AZURE_OPENAI_ENDPOINT (e.g. https://<your-project>.cognitiveservices.azure.com/)
- AZURE_AI_MODEL_DEPLOYMENT_NAME (model deployment name)

## Extending
| Goal | Change |
|------|--------|
| Real retrieval | Replace `retrieve_docs` with embedding + vector / search backend. |
| Richer answers | Introduce prompt templates or additional graph nodes. |
| Multi‑turn memory | Persist prior messages; include truncated history in `request_to_state`. |
| Tool / function calls | Add nodes producing tool outputs and incorporate into final response. |
| Better citations | Store offsets / URLs and expand annotation objects. |
| Streaming support | (See below) |

### Adding Streaming
1. Allow `stream=True` in requests and propagate a flag into state.
2. Implement `get_stream_mode` (return appropriate mode, e.g. `events`).
3. Implement `state_to_response_stream` to yield `ResponseStreamEvent` objects (lifecycle + deltas) and finalize with a completed event.
4. Optionally collect incremental model tokens during `generate_answer`.

## Key Takeaway
A custom `LanggraphStateConverter` is the seam where you map external request contracts to an internal graph-friendly state shape and then format the final (or streamed) result back to the OpenAI Responses schema. Start simple (non‑streaming), then layer retrieval sophistication, memory, tools, and streaming as needed.

Streaming is not supported in this sample out-of-the-box.
