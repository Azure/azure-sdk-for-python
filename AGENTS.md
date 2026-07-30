# AGENTS.md

Resolver for agent-facing guidance in this repository. Each topic below points
to its canonical location. Keep detailed workflows and task-specific rules in
those locations rather than duplicating them here.

## What is this repository?

This monorepo contains the Azure SDK for Python:

- Service packages live under `sdk/<service>/<package>/`.
- Engineering tooling lives under `eng/` and `tools/`.
- Contributor and developer documentation lives under `doc/`.
- Agent workflows live in `.github/skills/`.
- Path-scoped review rules live in `.github/instructions/reviewer/`.
- Package-specific knowledge lives under
  `sdk/<service>/<package>/.github/skills/`.

Contributor onboarding and repository setup are documented in `README.md` and
`CONTRIBUTING.md`.

## Where to find guidance

| Task or topic | Canonical guidance |
| --- | --- |
| Modify any package under `sdk/` | `.github/skills/find-package-skill/SKILL.md` (consult first) |
| Generate, customize, validate, or test an SDK locally | `.github/skills/azsdk-common-generate-sdk-locally/SKILL.md` |
| Generate SDK pull requests through the pipeline | `.github/skills/azsdk-common-generate-sdk-pipeline/SKILL.md` |
| Resolve APIView feedback | `.github/skills/azsdk-common-apiview-feedback-resolution/SKILL.md` |
| Analyze a failed CI pipeline | `.github/skills/azsdk-common-pipeline-analysis/SKILL.md` |
| Fix a failed CI pipeline | `.github/skills/azsdk-common-pipeline-fixer/SKILL.md` |
| Create or update a release plan | `.github/skills/azsdk-common-prepare-release-plan/SKILL.md` |
| Check release readiness or release a package | `.github/skills/azsdk-common-sdk-release/SKILL.md` |
| Fix pylint, mypy, Black, or Sphinx failures | `.github/skills/fix-pylint/SKILL.md`, `fix-mypy/SKILL.md`, `fix-black/SKILL.md`, or `fix-sphinx/SKILL.md` |
| Create an API review PR or API markdown | `.github/skills/create-api-review-pr/SKILL.md` or `.github/skills/generate-api-markdown/SKILL.md` |
| Create package-specific agent guidance | `.github/skills/create-package-skill/SKILL.md` |
| Review a management-plane package | `.github/instructions/reviewer/mgmt-sdk.instructions.md` |
| Report package health | `.github/prompts/check-package-health.prompt.md` and `doc/repo_health_status.md` |
| Run repository checks with `azpysdk` | `doc/tool_usage_guide.md` |
| Test SDK packages | `doc/dev/tests.md` |
| Write Python docstrings | `doc/dev/docstring.md` |
| Follow Azure SDK Python API design | https://azure.github.io/azure-sdk/python_design.html |

Load task-specific guidance on demand. Do not load every skill or deep-dive
document before it is relevant.

## Hard rules

- Consult `.github/skills/find-package-skill/SKILL.md` before modifying a
  package under `sdk/`, then load any package-specific skill it discovers.
- Do not directly customize generated SDK files. Use the generation and
  customization workflow, and place hand-written changes in the supported
  customization layer for that package.
- Use `azpysdk` for repository checks. Follow `doc/tool_usage_guide.md` and the
  task-specific fix skill rather than reviving older tox-based commands.
- Treat the Azure SDK Python Design Guidelines as the authoritative API design
  reference. Link to the relevant section when answering design-guideline
  questions.
- Before using Azure SDK MCP tools from Visual Studio or VS Code, ensure
  [PowerShell is installed](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)
  and run `azure-sdk-mcp:azsdk_verify_setup`. This setup check is not required
  for GitHub-hosted coding agents or requests that do not use MCP tools.
- Keep management-plane review rules scoped to
  `sdk/*/azure-mgmt-*/`; do not apply them to data-plane packages.
- Use current Azure SDK skills and MCP tool names from those skills. Do not copy
  tool contracts into general repository guidance.

## Where new guidance belongs

- A workflow for a specific task type belongs in a skill under
  `.github/skills/`.
- Review-only behavior belongs in a path-scoped file under
  `.github/instructions/reviewer/`.
- Package-specific architecture, customization, and verification knowledge
  belongs in the package's `.github/skills/` directory.
- Contributor setup, prerequisites, and human-oriented procedures belong in
  `CONTRIBUTING.md` or `doc/`.
- A short, repository-wide rule belongs in this file only when it cannot live
  in a more specific location.

If a fact appears to belong in two places, keep it in the more specific
location and link to it from the more general one.
