# azure-ai-agentserver-optimization

Optimization config loader for Azure AI Hosted Agents.

Provides a single `load_config()` call that resolves optimization parameters (instructions, model, temperature, skills, tool definitions) from multiple sources with graceful fallback — your agent works unchanged when not running under optimization.

## Installation

```bash
pip install azure-ai-agentserver-optimization
```

## Quick Start

```python
from azure.ai.agentserver.optimization import load_config

config = load_config(default_instructions="You are a helpful assistant.")

# Use config in your agent
print(config.instructions)       # optimized or default
print(config.model)              # optimized or default
print(config.temperature)        # optimized or default
print(config.skills)             # learned skills (empty list if none)
print(config.tool_descriptions)  # optimized tool descriptions (empty dict if none)
print(config.source)             # "api:candidate:abc", "env:OPTIMIZATION_CONFIG", "local:...", or "defaults"
```

## Resolution Order

`load_config()` resolves from four sources in order — first match wins:

| Priority | Source | Env vars required | Description |
|----------|--------|-------------------|-------------|
| 1 | **Inline JSON** | `OPTIMIZATION_CONFIG` | Full config as a JSON string. Used by temporary agent versions during evaluation. |
| 2 | **Resolver API** | `OPTIMIZATION_CANDIDATE_ID`, `OPTIMIZATION_JOB_ID`, `OPTIMIZATION_RESOLVE_ENDPOINT` | Fetches the candidate config from the remote optimization service and persists it to the local directory. |
| 3 | **Local directory** | `OPTIMIZATION_LOCAL_DIR` (optional, defaults to `.agent_configs/`) | Reads from `<local_dir>/<candidate_id>/` or `baseline/` as fallback. |
| 4 | **Defaults** | *(none)* | Returns the caller-supplied defaults unchanged — the agent works normally. |

Any unexpected error is caught and logged — `load_config()` always returns a valid `OptimizationConfig`.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPTIMIZATION_CONFIG` | Inline JSON config (Priority 1). |
| `OPTIMIZATION_CANDIDATE_ID` | Candidate ID for resolver API or local folder lookup. |
| `OPTIMIZATION_JOB_ID` | Job ID for the resolver API. |
| `OPTIMIZATION_RESOLVE_ENDPOINT` | Base URL of the optimization service. |
| `OPTIMIZATION_LOCAL_DIR` | Path to the local config directory (default: `.agent_configs/`). |
| `MODEL_DEPLOYMENT_NAME` | Fallback model name when no model is resolved or specified. |

## Local Directory Layout

When using the local directory (Priority 3) or after the resolver API persists a candidate (Priority 2), the directory uses the following structure:

```
.agent_configs/
├── baseline/                     # fallback candidate
│   ├── metadata.yaml             # model, temperature, file pointers
│   ├── instructions.md           # system prompt
│   ├── tools.json                # tool descriptions (dict or OpenAI list format)
│   └── skills/                   # learned skills
│       └── <skill_name>/
│           └── SKILL.md
└── <candidate_id>/               # same layout as baseline/
    ├── metadata.yaml
    ├── instructions.md
    ├── tools.json
    └── skills/
        └── <skill_name>/
            └── SKILL.md
```

## Tool Description Formats

`tools.json` and the inline JSON config support three formats:

**Dict format** (`tool_descriptions`):
```json
{
  "lookup_policy": {
    "description": "Look up the company travel policy.",
    "parameters": {"dept": "Department name"}
  }
}
```

**Legacy camelCase** (`toolDescriptions`) — same structure, different key. `tool_descriptions` takes priority when both are present.

**OpenAI function-calling list** (`tools`):
```json
[
  {
    "type": "function",
    "function": {
      "name": "lookup_policy",
      "description": "Look up the company travel policy.",
      "parameters": {
        "type": "object",
        "properties": {
          "dept": {"type": "string", "description": "Department name"}
        }
      }
    }
  }
]
```

## OptimizationConfig Properties

| Property | Type | Description |
|----------|------|-------------|
| `instructions` | `str` | System prompt (optimized or default). |
| `model` | `str \| None` | Model deployment name. |
| `temperature` | `float \| None` | Sampling temperature. |
| `skills` | `list[Skill]` | Learned skills. |
| `skills_dir` | `str \| None` | Path to skills directory. |
| `tool_descriptions` | `dict[str, ToolDescription]` | Optimized tool descriptions. |
| `source` | `str` | Where the config was loaded from. |
| `candidate_id` | `str \| None` | Candidate ID (when resolved via API). |
| `job_id` | `str \| None` | Job ID (when resolved via API). |
| `has_skills` | `bool` | Whether skills are available. |
| `has_tool_descriptions` | `bool` | Whether tool descriptions are available. |

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md) for details.
