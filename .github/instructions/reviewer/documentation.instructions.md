---
applyTo: "sdk/**/README.md,sdk/**/CHANGELOG.md,sdk/**/samples/**/*.py,sdk/**/samples-dev/**/*.py"
description: "Review Python SDK README, changelog, and sample changes against the actual client API."
---

# SDK Documentation Review

Check changed prose and examples against the actual public client, especially
constructor arguments, method names, async usage, and return types. For
docstrings in changed Python source, use [the repository docstring guide](../../../doc/dev/docstring.md).

- Verify user-visible changes are described accurately in the package
  changelog, following [the changelog guide](../../../doc/dev/changelog_updates.md).
  Do not demand a new entry for changes that do not affect users.
- Check README and sample snippets for runnable API usage, not only syntax.
  Generated examples may be illustrative; avoid flagging placeholder values
  unless they cause a real error.
- For management SDK packages, skip `generated_samples/` and apply the
  changelog, version, client-name, and README rules in
  `management.instructions.md`.
