# 🧭 PLANNING.md

## 🎯 What this project is
AgentServer is a set of Python packages under `sdk/agentserver` that host agents for
Azure AI Foundry. The core package provides the runtime/server, tooling runtime, and
Responses API models, while the adapter packages wrap popular frameworks. The primary
users are SDK consumers who want to run agents locally and deploy them as Foundry-hosted
containers. Work is “done” when adapters faithfully translate framework execution into
Responses API-compatible outputs and the packages pass their expected tests and samples.

**Behavioral/policy rules live in `AGENTS.md`.** This document is architecture + repo map + doc index.

## 🎯 Goals / Non-goals
Goals:
- Keep a stable architecture snapshot and repo map for fast onboarding.
- Document key request/response flows, including streaming.
- Clarify the development workflow and testing expectations for AgentServer packages.

Non-goals:
- Detailed API documentation (belongs in package docs and docstrings).
- Per-initiative plans (belong in `TASK.md` or a dedicated plan file).
- Speculative refactors (align with KISS/YAGNI in `AGENTS.md`).

## 🧩 Architecture (snapshot)
### 🏗️ Project Structure
- **azure-ai-agentserver-core**: Core library
  - Runtime/context
  - HTTP gateway
  - Foundry integrations
  - Responses API protocol (current)
- **azure-ai-agentserver-agentframework**: adapters for Agent Framework agents/workflows,
  thread and checkpoint persistence.
- **azure-ai-agentserver-langgraph**: adapter and converters for LangGraph agents and
  Response API events.

### Current vs target
- Current: OpenAI Responses API protocol lives in `azure-ai-agentserver-core` alongside
  core runtime and HTTP gateway code; framework adapters layer on top.
- Target (planned, not fully implemented):
  - Core layer: app/runtime/context, foundry integrations (tools, checkpointing), HTTP gateway
  - Protocol layer: Responses API in its own package
  - Framework layer: adapters (agentframework, langgraph, other frameworks)

### Key flows
- Request path: `/runs` or `/responses` → `AgentRunContext` → agent execution → Responses
  API payload.
- Streaming path: generator/async generator → SSE event stream.
- Framework adapter path: framework input → converter → Response API output (streaming
  or non-streaming).
- Tools path: Foundry tool runtime invoked via core `tools/runtime` APIs.

## 🗺️ Repo map
- `azure-ai-agentserver-core`: Core library (runtime/context, HTTP gateway, Foundry integrations,
  Responses API protocol today).
- `azure-ai-agentserver-agentframework`: Agent Framework adapter.
- `azure-ai-agentserver-langgraph`: LangGraph adapter.
- Core runtime and models: `azure-ai-agentserver-core/azure/ai/agentserver/core/`
- Agent Framework adapter: `azure-ai-agentserver-agentframework/azure/ai/agentserver/agentframework/`
- LangGraph adapter: `azure-ai-agentserver-langgraph/azure/ai/agentserver/langgraph/`
- Samples: `azure-ai-agentserver-*/samples/`
- Tests: `azure-ai-agentserver-*/tests/`
- Package docs (Sphinx inputs): `azure-ai-agentserver-*/doc/`
- Repo-wide guidance: `CONTRIBUTING.md`, `doc/dev/tests.md`, `doc/eng_sys_checks.md`

## 📚 Doc index
### **Read repo-wide guidance**:
- `CONTRIBUTING.md`
- `doc/dev/tests.md`
- `doc/eng_sys_checks.md`

### **Read the package READMEs**:
  - `sdk/agentserver/azure-ai-agentserver-core/README.md`
  - `sdk/agentserver/azure-ai-agentserver-agentframework/README.md`
  - `sdk/agentserver/azure-ai-agentserver-langgraph/README.md`

### “If you need X, look at Y”
- Enable/disable checks for a package → that package `pyproject.toml` → `[tool.azure-sdk-build]`
- How to run tests / live-recorded tests → `doc/dev/tests.md`
- Engineering system checks / gates → `doc/eng_sys_checks.md`
- Adapter conversion behavior → the relevant adapter package + its tests + samples

## ✅ Testing strategy
- Unit/integration tests live in each package’s `tests/` directory.
- Samples are part of validation via the `samples` tox environment.
- For live/recorded testing patterns, follow `doc/dev/tests.md`.

## 🚀 Rollout / migrations
- Preserve public API stability and follow Azure SDK release policy.
- Do not modify generated code (see paths in `AGENTS.md`).
- CI checks are controlled per package in `pyproject.toml` under
  `[tool.azure-sdk-build]`.

## ⚠️ Risks / edge cases
- Streaming event ordering and keep-alive behavior.
- Credential handling (async credentials and adapters).
- Response API schema compatibility across adapters.
- Tool invocation failures and error surfacing.

## 📌 Progress
See `TASK.md` for active work items; no checklists here.
