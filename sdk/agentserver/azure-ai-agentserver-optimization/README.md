# Azure AI Agent Server Optimization client library for Python

The `azure-ai-agentserver-optimization` package provides a drop-in config loader for optimization-ready Azure AI Hosted Agents. A single `load_config()` call resolves optimization parameters (instructions, model, temperature, skills, tool definitions) from multiple sources with graceful fallback — your agent works unchanged when not running under optimization.

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
| 2 | **Resolver API** | `OPTIMIZATION_CANDIDATE_ID`, `OPTIMIZATION_RESOLVE_ENDPOINT` | Fetches the candidate config from the remote optimization service and persists it to the local directory. The endpoint should be the full job-scoped URL. |
| 3 | **Local directory** | `OPTIMIZATION_LOCAL_DIR` (optional, defaults to `.agent_configs/`) | Reads from `<local_dir>/<candidate_id>/` or `baseline/` as fallback. |
| 4 | **No config** | *(none)* | Returns `None`. |

When `load_config()` encounters an invalid config source (e.g. malformed JSON env var, unreadable metadata), it raises `ValueError`. Other exceptions (e.g. network errors from the resolver API) propagate to the caller.

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPTIMIZATION_CONFIG` | Inline JSON config (Priority 1). |
| `OPTIMIZATION_CANDIDATE_ID` | Candidate ID for resolver API or local folder lookup. |
| `OPTIMIZATION_RESOLVE_ENDPOINT` | Full job-scoped URL of the optimization service (e.g. `https://host/api/projects/proj/agents_optimization_job/job-1`). |
| `OPTIMIZATION_LOCAL_DIR` | Path to the local config directory (default: `.agent_configs/`). |

### Local Directory Layout

The local config directory **must** exist with at least a `baseline/` folder before the agent can start to do optimization. When running under optimization, the resolver API (Priority 2) persists candidate configs into the same layout. If a `<candidate_id>/` folder exists it takes precedence; otherwise `baseline/` is used as the fallback.

```
.agent_configs/
├── baseline/                     # required — default candidate used at startup
│   ├── metadata.yaml             # model, temperature, file pointers
│   ├── instructions.md           # system prompt
│   ├── tools.json                # tool definitions (OpenAI function-calling list format)
│   └── skills/                   # learned skills
│       └── <skill_name>/
│           └── SKILL.md
└── <candidate_id>/               # optional — created by resolver API, same layout as baseline/
    ├── metadata.yaml
    ├── instructions.md
    ├── tools.json
    └── skills/
        └── <skill_name>/
            └── SKILL.md
```

#### `metadata.yaml`

Points to the other files and sets model parameters. All fields are optional:

```yaml
model: gpt-4o
temperature: 0.7
instruction_file: instructions.md
skill_dir: skills
tool_file: tools.json
```

#### `instructions.md`

The system prompt for the agent — plain text or Markdown:

```markdown
You are a travel assistant. Help users search flights, book hotels,
and answer questions about company travel policy.
```

#### `tools.json`

Tool definitions in the OpenAI function-calling list format:

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

#### `skills/*/SKILL.md`

Each skill lives in its own subfolder with a `SKILL.md` file. An optional YAML frontmatter block provides the name and description; the rest is the skill body:

```markdown
---
name: budget-checker
description: Check whether a trip is within budget.
---

Compare the trip cost against the department's remaining travel budget
and return APPROVED or DENIED with a reason.
```

### OptimizationConfig Properties

| Property | Type | Description |
|----------|------|-------------|
| `instructions` | `str \| None` | System prompt (optimized or default). |
| `model` | `str \| None` | Model deployment name. |
| `temperature` | `float \| None` | Sampling temperature. |
| `skills` | `list[Skill]` | Learned skills (from inline config). |
| `skills_dir` | `str \| None` | Path to skills directory (for on-demand loading). |
| `tool_definitions` | `list[dict]` | Optimized tool definitions (OpenAI function-calling format). |
| `source` | `str` | Where the config was loaded from. |
| `candidate_id` | `str \| None` | Candidate ID (when resolved via API or local folder). |
| `has_skills` | `bool` | Whether skills are available (inline or via skills_dir). |

### Public API

| Export | Type | Description |
|--------|------|-------------|
| `load_config(*, config_dir)` | function | Load optimization config with 4-priority resolution. |
| `load_skills_from_dir(path)` | function | Load skills from a directory of `SKILL.md` files. |
| `OptimizationConfig` | class | Resolved config with instructions, model, temperature, skills_dir, tool_definitions. |
| `OptimizationConfig.apply_tool_descriptions(tools)` | method | Patch `__doc__`, `.description`, and parameter descriptions on tool functions. |
| `OptimizationConfig.compose_instructions()` | method | Return instructions with skill catalog appended. |
| `CandidateConfig` | class | Typed representation of the resolver API response. |
| `Skill` | class | A learned skill (name, description, body). |

## Examples

### Basic usage

```python
from azure.ai.agentserver.optimization import load_config

config = load_config()                          # uses .agent_configs/baseline/
config = load_config(config_dir="my_configs")   # custom directory

if config is None:
    print("No optimization config found")
else:
    print(config.instructions)       # optimized system prompt
    print(config.model)              # optimized model name
    print(config.temperature)        # optimized temperature
    print(config.tool_definitions)   # optimized tool definitions (list)
    print(config.source)             # "env:OPTIMIZATION_CONFIG", "api:candidate:abc", "local:...", etc.
```

### Apply optimized tool descriptions

```python
from azure.ai.agentserver.optimization import load_config

config = load_config()

# Your @tool-decorated functions
def search_flights(origin: str, destination: str):
    """Search for flights."""
    ...

def book_hotel(city: str):
    """Book a hotel room."""
    ...

# Patches __doc__ and .description on matching tools with optimized descriptions
config.apply_tool_descriptions([search_flights, book_hotel])
```

### Load skills on demand

```python
from pathlib import Path
from azure.ai.agentserver.optimization import load_config, load_skills_from_dir

config = load_config()

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
- **Config not loading from resolver API** — ensure both env vars are set: `OPTIMIZATION_CANDIDATE_ID` and `OPTIMIZATION_RESOLVE_ENDPOINT`.
- **Local directory not found** — check that `OPTIMIZATION_LOCAL_DIR` points to an existing directory, or ensure `.agent_configs/` exists relative to your main script.
- **`load_config()` returns `None`** — no config source was found; set up a baseline folder or set the appropriate env vars.

## Next steps

- [Azure SDK for Python documentation](https://learn.microsoft.com/azure/developer/python/)
- [Contributing guide](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md) for details.
