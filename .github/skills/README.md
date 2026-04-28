# Azure SDK Shared Copilot Skills

Copilot skills that guide AI agents through the Azure SDK development and TypeSpec-to-SDK release workflow.
These skills are consumed by GitHub Copilot (CLI, VS Code, and Coding Agent) when users work
with TypeSpec API specifications and Azure SDK generation.

Shared skills (those distributed to other Azure SDK repositories) are identified by
`distribution: shared` in their SKILL.md frontmatter metadata block and use the
`azsdk-common-` directory prefix. This prefix enables the `sync-.github.yml` pipeline
to match and distribute them to all subscribed language SDK repos.

---

## Available Skills

### Workflow & Utility Skills

| Skill | Triggers | Description |
| ----- | -------- | ----------- |
| [azsdk-common-generate-sdk-locally](azsdk-common-generate-sdk-locally/SKILL.md) | "generate SDK locally", "build SDK", "run SDK tests" | Generate, build, and test Azure SDKs locally from TypeSpec |
| [azsdk-common-prepare-release-plan](azsdk-common-prepare-release-plan/SKILL.md) | "create release plan", "link SDK PR to plan" | Create and manage release plan work items |
| [azsdk-common-apiview-feedback-resolution](azsdk-common-apiview-feedback-resolution/SKILL.md) | "APIView comments", "resolve API review feedback" | Retrieve and resolve APIView review feedback |
| [azsdk-common-pipeline-troubleshooting](azsdk-common-pipeline-troubleshooting/SKILL.md) | "pipeline failed", "build failure", "CI check failing" | Diagnose and resolve SDK CI and generation pipeline failures |
| [azsdk-common-sdk-release](azsdk-common-sdk-release/SKILL.md) | "release SDK", "trigger release pipeline" | Check release readiness and trigger SDK releases |

### Development & Meta Skills

These skills help with skill development itself:

| Skill | Triggers | Description |
| ----- | -------- | ----------- |
| [sensei](sensei/SKILL.md) | "run sensei", "improve skill", "fix frontmatter" | Iteratively improve skill frontmatter compliance using the Ralph loop |
| [skill-authoring](skill-authoring/SKILL.md) | "create a skill", "new skill", "skill template" | Guidelines for writing Agent Skills per agentskills.io spec |
| [markdown-token-optimizer](markdown-token-optimizer/SKILL.md) | "optimize markdown", "reduce tokens", "token count" | Analyze markdown files for token efficiency |

### Skill Anatomy

Each skill lives in `<name>/` and contains:

```
<name>/
├── SKILL.md           # Skill definition: YAML frontmatter + steps + related skills
├── references/        # Detailed reference docs (offloaded to keep SKILL.md under 500 tokens)
│   └── *.md
├── eval.yaml          # Evaluation config (graders, timeouts, model)
├── tasks/             # Eval task definitions (4-5 per skill)
│   └── *.yaml
└── fixtures/          # Domain-specific test fixtures
    └── <files>
```


---

## Tooling

| Tool | Purpose | Install |
| ---- | ------- | ------- |
| [**waza**](https://microsoft.github.io/waza/getting-started/) | Scaffold skills, run evals, check compliance | `go install github.com/microsoft/waza/cmd/waza@latest` |

### Testing Skills

```bash
cd .github/skills

# Check all skills
waza check

# Run evals
waza run --discover
```

---

## Project Configuration

- **`.waza.yaml`** — Default engine (`copilot-sdk`) and model (`claude-sonnet-4.6`) for evals
- **`.gitignore`** — Excludes waza output directories and temp files

## Further Reading

- [agentskills.io spec](https://agentskills.io) — Skill frontmatter specification
- [waza docs](https://microsoft.github.io/waza/getting-started/) — Scaffold, check, and eval skills
