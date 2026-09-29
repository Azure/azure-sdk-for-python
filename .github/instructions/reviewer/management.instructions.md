---
applyTo: "sdk/*/azure-mgmt-*/**"
description: "Review Python management SDK changes using management-specific scope, version, metadata, and documentation rules."
---

# Management SDK Review

These rules apply to management-plane SDK packages under
`sdk/*/azure-mgmt-*/`.

## Review scope

- Skip `generated_samples/` and `generated_tests/` entirely.
- Under `azure/mgmt/**/`, review only `_client.py`. Read other generated files
  only when needed as evidence for an applicable metadata or documentation
  check.

## Version consistency

- The version in `_version.py` must match the latest version in `CHANGELOG.md`.
- If `_metadata.json` contains a preview `apiVersion`, `_version.py` must
  contain a beta package version such as `1.0.0b1`, not a stable version such
  as `1.0.0`.
- If the latest changelog release date is more than three weeks in the future,
  ask the author to verify it.

## Package stability metadata

- For a stable version without `b`, `pyproject.toml` must set
  `is_stable = true` and include
  `"Development Status :: 5 - Production/Stable"`.
- For a preview version containing `b`, `pyproject.toml` must set
  `is_stable = false` and include `"Development Status :: 4 - Beta"`.

## Client consistency

- The client `__init__` signature in `_client.py` must contain `credential`,
  `subscription_id`, and `base_url`, in that order. Default values are not
  checked.
- If `subscription_id` is absent, `pyproject.toml` must contain
  `no_sub = true`; otherwise, recommend adding it and regenerating the SDK.
- The client class name in `_client.py`, the client used in `README.md`, and
  the `title` in `pyproject.toml` must match.
- README snippets must follow the actual client signature and usage.
