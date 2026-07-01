---
name: code-review
description: "Guidelines for reviewing pull requests to the App Configuration packages in this repository (azure-appconfiguration and azure-appconfiguration-provider). USE FOR: reviewing a PR, what to check in a code review, repository rules to enforce during review, giving review feedback, responding to review comments, PR best practices. DO NOT USE FOR: automated code analysis, running linters, creating PRs."
---

# Code Review

How to review a pull request against the App Configuration code in this repository: what to check in the diff, the repository rules to enforce, and how to handle the review conversation. The reviewing guidance is primary; the authoring and feedback sections support both sides of the review.

**Scope:** the data-plane client library `sdk/appconfiguration/azure-appconfiguration/` and the provider library `sdk/appconfiguration/azure-appconfiguration-provider/`. The management library `azure-mgmt-appconfiguration` follows the separate MGMT review rules.

## Reviewing a PR

Work through this when reviewing a diff:

- **Repository rules are honored** — check the change against every rule in [Repository rules to enforce](#repository-rules-to-enforce) below.
- **Behavior changes are covered by tests** — including the negative/disabled code path, in both sync and async forms.
- **Public API changes are intentional** — new or modified public surface must be reflected in `api.md` and reviewed for breaking changes.
- **Logging isn't noisy** — flag warnings emitted per-call/per-request; prefer `info`/`debug` for non-actionable conditions.
- **Scope is focused** — the PR addresses a single concern; flag unrelated changes for a separate PR.
- **Treat every comment as worth addressing** — nothing is a nit.

## Repository rules to enforce

Hard constraints for the App Configuration packages. A change that violates any of these should not pass review.

- **CHANGELOG is required** — every user-facing change must add an entry under the top `## <version> (Unreleased)` section of the package's `CHANGELOG.md` (Features Added / Breaking Changes / Bugs Fixed / Other Changes). The version in `_version.py` must match the latest version in `CHANGELOG.md`. This is a release-blocking check.
- **Don't hand-edit generated code** — `azure/appconfiguration/_generated/` is produced from TypeSpec (see `tsp-location.yaml`). Changes belong in the TypeSpec source or the hand-written customization layer (the non-`_generated` modules), then regenerate. Flag direct edits to `_generated/`. See the `find-package-skill` and `azsdk-common-generate-sdk-locally` skills.
- **No new dependencies** — minimize them; if one is truly required it must be justified and, where possible, an *optional* dependency. New runtime dependencies require design review.
- **No breaking changes to public API** outside a major version — and even within a major version, minimize them. The breaking-changes check runs in CI; a flagged break needs explicit justification and design review.
- **Prefer public APIs over private modules** — avoid importing from underscore-prefixed/private paths when a public API exists.
- **Sync/async parity** — changes under `azure/appconfiguration/` (or `azure/appconfiguration/provider/`) that have an `aio/` counterpart must be updated in both the sync and async code paths, with matching tests.
- **New features ship with samples and tests** — user-facing features require a `samples/` example and sync + async unit tests under `tests/`.
- **Validation must pass** — run via `azpysdk` from the package directory: black → pylint → mypy → pyright → sphinx → pytest. MyPy, Pylint, Sphinx, and Tests-CI are release-blocking. See the `fix-black`, `fix-pylint`, `fix-mypy`, and `fix-sphinx` skills.
- **New source files** — must include the MIT copyright header and a module docstring.

## Authoring a PR (so it reviews well)

- **One issue, one PR** — keep each pull request focused on a single concern; don't mix fixes for multiple issues.
- **Descriptive title** — meaningful in source-control history without extra context.
- **Self-explanatory description** — explain what changed and *why*, link the issue the PR closes, and call out any CHANGELOG entry.
- **Test before requesting review** — run `azpysdk` validation locally and verify your changes work first.
- **Follow existing code style** — consistency matters more than personal preference.
- **Self-review sizable changes** — catch obvious issues before reviewers do.
