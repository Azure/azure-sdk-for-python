# AGENTS.md - Azure SDK for Python

Agent-facing routing guidance for this repository. Each section points to the
canonical home for a topic — a skill, a path-specific instruction, or a linked
doc — so read those on demand.

## Repository overview

Active development of the Azure SDK for Python: data-plane client libraries,
management-plane (`azure-mgmt-*`) libraries, shared core functionality, and the
engineering system. Packages live under `sdk/<service>/<package>/`. The default
branch is `main`; work in the current workspace unless told otherwise.
Contributor setup lives in [`CONTRIBUTING.md`](CONTRIBUTING.md).

Layout:
- `sdk/` — service packages (e.g. `sdk/storage/azure-storage-blob`)
- `eng/` — build, test, generation, release, and CI tooling (including `eng/tools/`)
- `doc/` — contributor and SDK developer documentation
- `.github/instructions/` — path-scoped review guidance
- `.github/skills/` — specialized, on-demand workflows
- `.github/copilot-instructions.md` — thin Copilot adapter to this file

## Instruction hierarchy

Apply the smallest relevant set, most-specific first:
1. The nearest applicable `AGENTS.md`.
2. Matching path-specific instructions under `.github/instructions/`.
3. The matching skill under `.github/skills/` for specialized work.
4. Linked developer documentation in `doc/` for detail.

## Automation boundaries

Do not publish to PyPI or trigger a release unless the user explicitly requests
it and the relevant workflow confirms readiness.

Always:
- Never merge pull requests without human review or force-push to protected
  branches.
- Never commit secrets, credentials, or customer data.
- Route security- or authentication-logic changes through security review.
- Require justification before adding dependencies, design review before
  changing public API signatures, and an explanation before disabling or
  removing tests.
- Get explicit user approval before undertaking a large-scale refactor.
- Don't hand-edit generated SDK code — customize via TypeSpec or the
  [generate-sdk](.github/skills/azsdk-common-generate-sdk-locally/SKILL.md) skill.
- Treat CI/CD workflow-definition changes as requiring explicit human prompting.

## Where to find guidance

| Task / topic | Where to look |
| --- | --- |
| Add a feature or fix a bug in a package under `sdk/` | [`.github/skills/find-package-skill/SKILL.md`](.github/skills/find-package-skill/SKILL.md) (check FIRST for package-specific skills) |
| Generate or regenerate SDK code from TypeSpec, build, and validate | [`.github/skills/azsdk-common-generate-sdk-locally/SKILL.md`](.github/skills/azsdk-common-generate-sdk-locally/SKILL.md) |
| Release / publish a package | [`.github/skills/azsdk-common-sdk-release/SKILL.md`](.github/skills/azsdk-common-sdk-release/SKILL.md) |
| Prepare a release plan | [`.github/skills/azsdk-common-prepare-release-plan/SKILL.md`](.github/skills/azsdk-common-prepare-release-plan/SKILL.md) |
| Resolve APIView feedback | [`.github/skills/azsdk-common-apiview-feedback-resolution/SKILL.md`](.github/skills/azsdk-common-apiview-feedback-resolution/SKILL.md) |
| Analyze a CI / pipeline failure | [`.github/skills/azsdk-common-pipeline-analysis/SKILL.md`](.github/skills/azsdk-common-pipeline-analysis/SKILL.md) |
| Apply fixes for a pipeline failure | [`.github/skills/azsdk-common-pipeline-fixer/SKILL.md`](.github/skills/azsdk-common-pipeline-fixer/SKILL.md) |
| Detect and mitigate SDK breaking changes | [`.github/skills/azsdk-common-sdk-breaking-change/SKILL.md`](.github/skills/azsdk-common-sdk-breaking-change/SKILL.md) |
| Fix pylint / mypy / black / sphinx issues | [`.github/skills/fix-pylint/SKILL.md`](.github/skills/fix-pylint/SKILL.md), [`fix-mypy`](.github/skills/fix-mypy/SKILL.md), [`fix-black`](.github/skills/fix-black/SKILL.md), [`fix-sphinx`](.github/skills/fix-sphinx/SKILL.md) |
| Full check inventory and `azpysdk` command reference | [`doc/tool_usage_guide.md`](doc/tool_usage_guide.md) |
| Report package / repository health | [`.github/skills/sdk-health/SKILL.md`](.github/skills/sdk-health/SKILL.md) |
| Create a new package-specific skill | [`.github/skills/create-package-skill/SKILL.md`](.github/skills/create-package-skill/SKILL.md) |
| Copilot code review (CCR) | [`.github/skills/code-review/SKILL.md`](.github/skills/code-review/SKILL.md) (routes to the reviewer instructions) |
| Review criteria (source, tests, docs, deps, mgmt) | [`.github/instructions/reviewer/`](.github/instructions/reviewer/) |
| Design / create / debug / upgrade agentic workflows | [`.github/skills/agentic-workflows/SKILL.md`](.github/skills/agentic-workflows/SKILL.md) |
| Testing, recordings, and the `azpysdk` runner | [`doc/dev/tests.md`](doc/dev/tests.md) |
| TypeSpec code generation deep dive | [`doc/dev/ai/typespec_generation.md`](doc/dev/ai/typespec_generation.md) |
| Pylint checking and type-checking references | [`doc/dev/pylint_checking.md`](doc/dev/pylint_checking.md), [`static_type_checking_cheat_sheet.md`](doc/dev/static_type_checking_cheat_sheet.md) |
| Docstring format (Sphinx / reStructuredText) | [`doc/dev/docstring.md`](doc/dev/docstring.md) |
| Packaging and changelog (Chronus) conventions | [`doc/dev/packaging.md`](doc/dev/packaging.md), [`changelog_updates.md`](doc/dev/changelog_updates.md) |
| Authoritative API design guidelines | https://azure.github.io/azure-sdk/python_design.html |
| Other deep dives | [`doc/dev/`](doc/dev/) (browse the directory) |

## Hard rules

- For SDK design or public API questions, link to the most relevant specific
  Design Guidelines page or section rather than only the guidelines homepage.
- Run `azsdk_verify_setup` before the first operation that depends on Azure SDK
  MCP tools — not before ordinary reading, searching, editing, or local validation.
- If an Azure SDK MCP workflow cannot start because PowerShell is unavailable,
  provide the [PowerShell installation instructions](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)
  and recommend restarting the IDE after installation so the MCP server starts.
- Before adding or changing handwritten patches or customizations of generated
  Python SDK code, including `_patch.py`, investigate whether the behavior comes
  from the service spec/configuration or the emitter/generator. Follow the
  [patch diagnosis checklist](doc/dev/customize_code/how-to-patch-sdk-code.md#before-you-customize)
  and document the evidence, rationale, and any investigation blockers before
  adopting a package-local workaround.
- Make focused, minimal changes: only touch files relevant to the task, and do
  not fix unrelated pre-existing issues.
- Write Python 3.10-compatible code unless the affected package declares a newer
  minimum.
- Run the smallest existing validation that covers the change, and do not claim
  a check passed unless it was actually run.
- Create pull requests as drafts; never open them ready-for-review unless the
  user explicitly asks.
- Don't duplicate guidance that lives in a skill or linked doc — link to the
  canonical source instead of copying it here.

## Reporting Issues

Report problems with AI agent interactions via
[Azure SDK for Python Issues](https://github.com/Azure/azure-sdk-for-python/issues)
using the `Agent` label. Include the agent name/version, the prompt used, and
expected vs. actual behavior.
