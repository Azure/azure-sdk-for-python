---
applyTo: "sdk/**/*.py"
description: "Review Python SDK source changes for correctness, API compatibility, and sync/async consistency."
---

# SDK Source Review

Apply the [Azure SDK Python Design Guidelines](https://azure.github.io/azure-sdk/python_design.html)
to changed public APIs, not to unrelated pre-existing code. Prefer concrete
regressions to speculative style or naming concerns.

- Trace constructor and method changes through public imports, usage sites,
  type annotations, and sync/async counterparts. Check forwarded credentials,
  request options, polling, paging, and error behavior when relevant.
- Before reporting a breaking change, verify that the removed or changed API
  exists in a released stable version; account for preview-only packages and
  intentional major-version migrations.
- For generated code, determine whether a defect comes from TypeSpec,
  handwritten customization, or generation tooling. Point to an actionable
  changed source when possible rather than requesting manual edits to output.
- Check newly introduced logging, credentials, URLs, and request handling for
  concrete secret exposure or unsafe data flows; do not infer a vulnerability
  from the presence of a credential parameter alone.
- For `azure-mgmt-*` packages, follow
  [`management.instructions.md`](./management.instructions.md) instead of
  reviewing excluded generated implementation files.
