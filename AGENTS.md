# Azure SDK for Python agent guidance

This repository contains the Azure SDK for Python, including data-plane and
management-plane client libraries, shared core libraries, tests, samples, and
engineering-system tooling.

## Instruction hierarchy

Use the smallest relevant set of instructions:

1. Follow this file for repository-wide conventions.
2. Follow the nearest nested `AGENTS.md`, when present.
3. Apply matching path-specific instructions from `.github/instructions/`.
4. Load a matching skill from `.github/skills/` for specialized workflows.
5. Consult the linked developer documentation for details that are not needed
   in every agent context.

`.github/copilot-instructions.md` is a thin Copilot adapter to this file. Do
not duplicate repository guidance there.

## Repository layout

- `sdk/`: service-specific packages, generally under
  `sdk/<service>/<package>/`
- `eng/`: build, test, generation, release, and CI infrastructure
- `doc/`: contributor and SDK development documentation
- `scripts/` and `tools/`: repository automation
- `.github/instructions/`: file- and task-scoped guidance
- `.github/skills/`: specialized, progressively loaded workflows

The default branch is `main`. Work in the current workspace unless the user
provides another repository or worktree.

## Engineering principles

- Make focused changes that address the requested behavior without modifying
  unrelated code or reverting existing user changes.
- Inspect enough surrounding code, callers, tests, and package metadata to
  preserve existing behavior and sync/async consistency.
- Reuse repository helpers and neighboring package patterns before introducing
  new abstractions or dependencies.
- Treat generated output as generated: identify whether a change belongs in
  TypeSpec, a customization, generator tooling, or handwritten code before
  editing it.
- Keep type safety and public API compatibility. Verify released API history
  before reporting or introducing a breaking change.
- Never place credentials, tokens, customer data, or unsanitized secrets in
  source, tests, recordings, logs, or documentation.

Use the
[Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
as the authority for SDK design and public API questions. Apply them to the
changed SDK surface, not unrelated pre-existing code.

## Tools and specialized workflows

Load the matching skill instead of reproducing its procedure in general
instructions. Available skills cover TypeSpec generation, APIView feedback,
pipeline analysis and repair, pylint, mypy, formatting, Sphinx, package
release, SDK health reporting, and code review.

Run `azsdk_verify_setup` immediately before the first workflow operation that
depends on the Azure SDK MCP tools. It is not a prerequisite for reading,
searching, reviewing, editing, or running ordinary repository commands. If an
MCP workflow reports that PowerShell or another prerequisite is unavailable,
surface the error and follow that workflow's setup guidance.

For TypeSpec generation and package lifecycle work, use
`.github/skills/azsdk-common-generate-sdk-locally/SKILL.md`. For releases, use
`.github/skills/azsdk-common-sdk-release/SKILL.md`. Do not publish, merge, or
trigger a release unless the user explicitly requests it and the relevant
workflow confirms readiness.

## Validation

- Use Python 3.10-compatible code unless a package declares a newer minimum.
- Run the smallest existing check that covers the change, from the affected
  package directory.
- Use `azpysdk <check> .` for package checks; for example:
  `azpysdk pylint .` and `azpysdk mypy .`.
- Run focused tests first. Expand to package-level checks when the change or a
  focused failure warrants it.
- Do not install new tooling unless a dependency change requires it or an
  existing validation command fails because a required dependency is missing.
- Do not claim that a check passed unless it was run successfully. Report
  unverified validation and blockers explicitly.

Relevant references:

- [Contributing guide](CONTRIBUTING.md)
- [Tool usage guide](doc/tool_usage_guide.md)
- [Testing guide](doc/dev/tests.md)
- [Pylint guide](doc/dev/pylint_checking.md)
- [Static type-checking guide](doc/dev/static_type_checking_cheat_sheet.md)
- [Packaging guide](doc/dev/packaging.md)
- [Changelog guide](doc/dev/changelog_updates.md)

## Pull requests and reviews

- Create pull requests as drafts unless the user explicitly requests otherwise.
- Review changed behavior rather than imposing conventions on unrelated code.
- Report actionable, high-confidence findings with evidence and avoid
  duplicating one root cause across multiple comments.
- Use `.github/skills/code-review/SKILL.md` for broad reviews and the
  path-specific reviewer instructions it references.
