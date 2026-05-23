# Azure AI Agent Server Optimization client library for Python

The `azure-ai-agentserver-optimization` package provides a drop-in config loader for optimization-ready Azure AI Hosted Agents. A single `load_config()` call resolves optimization parameters (instructions, model, temperature, skills, tool descriptions) from multiple sources with graceful fallback — your agent works unchanged when not running under optimization.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-optimization
```

### Prerequisites

- Python 3.10 or later

## Key concepts

### Resolution Order

`load_config()` resolves from four sources in order — first match wins:

| Priority | Source | Env vars required | Description |
|----------|--------|-------------------|-------------|
| 1 | **Inline JSON** | `OPTIMIZATION_CONFIG` | Full config as a JSON string. Used by temporary agent versions during evaluation. |
| 2 | **Resolver API** | `OPTIMIZATION_CANDIDATE_ID`, `OPTIMIZATION_JOB_ID`, `OPTIMIZATION_RESOLVE_ENDPOINT` | Fetches the candidate config from the remote optimization service and persists it to the local directory. |
| 3 | **Local directory** | `OPTIMIZATION_LOCAL_DIR` (optional, defaults to `.agent_configs/`) | Reads from `<local_dir>/<candidate_id>/` or `baseline/` as fallback. |
| 4 | **Defaults** | *(none)* | Returns the caller-supplied defaults unchanged — the agent works normally. |

Any unexpected error is caught and logged — `load_config()` always returns a valid `OptimizationConfig`.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPTIMIZATION_CONFIG` | Inline JSON config (Priority 1). |
| `OPTIMIZATION_CANDIDATE_ID` | Candidate ID for resolver API or local folder lookup. |
| `OPTIMIZATION_JOB_ID` | Job ID for the resolver API. |
| `OPTIMIZATION_RESOLVE_ENDPOINT` | Base URL of the optimization service. |
| `OPTIMIZATION_LOCAL_DIR` | Path to the local config directory (default: `.agent_configs/`). |
| `MODEL_DEPLOYMENT_NAME` | Fallback model name when no model is resolved or specified. |

### Local Directory Layout

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

### Tool Description Formats

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

### OptimizationConfig Properties

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

### Public API

| Export | Type | Description |
|--------|------|-------------|
| `load_config(...)` | function | Load optimization config with 4-priority resolution. |
| `load_skills_from_dir(path)` | function | Load skills from a directory of `SKILL.md` files. |
| `OptimizationConfig` | dataclass | Resolved config with instructions, model, temperature, skills_dir, tool_descriptions. |
| `OptimizationConfig.apply_tool_descriptions(tools)` | method | Patch `__doc__` on tool functions from optimized descriptions. |
| `OptimizationConfig.compose_instructions()` | method | Return instructions with skill catalog appended. |
| `CandidateConfig` | dataclass | Typed representation of the resolver API response. |
| `Skill` | dataclass | A learned skill (name, description, body). |
| `ToolDescription` | dataclass | Optimized tool description (description, parameters). |

## Examples

### Basic usage

```python
from azure.ai.agentserver.optimization import load_config

config = load_config(default_instructions="You are a helpful assistant.")

print(config.instructions)       # optimized or default
print(config.model)              # optimized or default
print(config.temperature)        # optimized or default
print(config.tool_descriptions)  # optimized tool descriptions (empty dict if none)
print(config.source)             # "env:OPTIMIZATION_CONFIG", "api:candidate:abc", "local:...", or "defaults"
```

### Apply optimized tool descriptions

```python
from azure.ai.agentserver.optimization import load_config

config = load_config(default_instructions="You are a travel agent.")

# Your @tool-decorated functions
def search_flights(origin: str, destination: str):
    """Search for flights."""
    ...

def book_hotel(city: str):
    """Book a hotel room."""
    ...

# Patches __doc__ on matching tools with optimized descriptions
config.apply_tool_descriptions([search_flights, book_hotel])
```

### Load skills on demand

```python
from pathlib import Path
from azure.ai.agentserver.optimization import load_config, load_skills_from_dir

config = load_config(default_instructions="You are a helpful assistant.")

# Skills are not loaded inline — load them when needed
if config.skills_dir:
    skills = load_skills_from_dir(Path(config.skills_dir))
    for skill in skills:
        print(f"{skill.name}: {skill.description}")
```

## Troubleshooting

Enable debug logging to see resolution details:

```python
import logging
logging.getLogger("azure.ai.agentserver.optimization").setLevel(logging.DEBUG)
```

Common issues:
- **Config not loading from resolver API** — ensure all three env vars are set: `OPTIMIZATION_CANDIDATE_ID`, `OPTIMIZATION_JOB_ID`, and `OPTIMIZATION_RESOLVE_ENDPOINT`.
- **Local directory not found** — check that `OPTIMIZATION_LOCAL_DIR` points to an existing directory, or ensure `.agent_configs/` exists relative to your main script.
- **`load_config()` returns defaults unexpectedly** — check logs for warnings about path traversal, bad JSON, or missing directories.

## Next steps

- [Azure SDK for Python documentation](https://learn.microsoft.com/azure/developer/python/)
- [Contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md) for details.
