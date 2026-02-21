Bilingual Weekend Planner (Custom Container + Telemetry)

- Container-hosted multi-agent weekend planner with full GenAI telemetry capture and a standalone tracing demo that exercises `opentelemetry-instrumentation-openai-agents-v2`.

Prereqs
- Optional: Activate repo venv `source .venv/bin/activate`
- Install deps `pip install -U -r samples/python/custom/bilingual_weekend_planner/requirements.txt`

Env Vars
Choose the API host via `API_HOST`:

- `github`: GitHub Models hosted on Azure AI Inference  
  - `GITHUB_TOKEN`  
  - Optional: `GITHUB_OPENAI_BASE_URL` (default `https://models.inference.ai.azure.com`)  
  - Optional: `GITHUB_MODEL` (default `gpt-4o`)
- `azure`: Azure OpenAI  
  - `AZURE_OPENAI_ENDPOINT` (e.g. `https://<resource>.openai.azure.com/`)  
  - `AZURE_OPENAI_VERSION` (e.g. `2025-01-01-preview`)  
  - `AZURE_OPENAI_CHAT_DEPLOYMENT` (deployment name)

Modes
- Container (default): runs the bilingual triage agent via `FoundryCBAgent`.  
- `API_HOST=github GITHUB_TOKEN=... ./run.sh`
- `API_HOST=azure AZURE_OPENAI_ENDPOINT=... AZURE_OPENAI_VERSION=2025-01-01-preview AZURE_OPENAI_CHAT_DEPLOYMENT=... ./run.sh`
  - Test (non-stream):  
    `curl -s http://localhost:8088/responses -H 'Content-Type: application/json' -d '{"input":"What should I do this weekend in Seattle?"}'`
  - Test (stream):  
    `curl -s http://localhost:8088/responses -H 'Content-Type: application/json' -d '{"input":"Plan my weekend in Barcelona","stream":true}'`
- Telemetry demo: set `WEEKEND_PLANNER_MODE=demo` to run the content-capture simulation (no model calls).  
  `WEEKEND_PLANNER_MODE=demo python main.py`

Telemetry
- Console exporter is enabled by default; set `OTEL_EXPORTER_OTLP_ENDPOINT` (HTTP) or `OTEL_EXPORTER_OTLP_GRPC_ENDPOINT` to export spans elsewhere.
- Set `APPLICATION_INSIGHTS_CONNECTION_STRING` to export spans to Azure Monitor.
- GenAI capture flags are pre-configured (content, system instructions, tool metadata).
- `opentelemetry-instrumentation-openai-agents-v2` enables span-and-event message capture for requests, responses, and tool payloads.
- The tracing demo uses the `agents.tracing` helpers to emit spans without invoking external APIs.

Notes
- Uses `FoundryCBAgent` to host the bilingual weekend planner triage agent on `http://localhost:8088`.
- Tools: `get_weather`, `get_activities`, `get_current_date`.
- Rich logger output highlights tool invocations; bilingual agents route traveler requests to the right language specialist.
