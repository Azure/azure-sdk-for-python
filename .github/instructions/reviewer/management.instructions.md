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
- Use the `apiVersions` service-to-version map in `_metadata.json` for
  API-version checks, not the nullable singular `apiVersion`. Missing or
  malformed maps are unverified evidence; do not fall back to `apiVersion`.
- If any value in `apiVersions` contains `preview` (case-insensitive),
  `_version.py` must contain a beta package version such as `1.0.0b1`, not a
  stable version such as `1.0.0`. This includes mixed stable/preview maps.
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
- For a confirmed first release, synchronous and asynchronous client class
  names must end with the exact suffix `MgmtClient`. A mismatch is a blocking
  finding: ask the author to customize the name in `client.tsp` and regenerate
  the SDK. Do not apply this requirement to existing releases or infer a first
  release from a missing baseline alone; report unverifiable evidence as such.
- README snippets must follow the actual client signature and usage.
