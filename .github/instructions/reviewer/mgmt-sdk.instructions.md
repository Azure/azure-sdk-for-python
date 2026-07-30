---
applyTo: "sdk/*/azure-mgmt-*/**"
description: "Azure management-plane SDK review rules for generated source, versions, metadata, and client documentation."
---

# Management SDK review rules

Apply these rules only to management-plane packages under
`sdk/*/azure-mgmt-*/`. Only report issues introduced by the change under
review.

## Review scope

- Skip `generated_samples/` and `generated_tests/`.
- Skip generated source under `azure/mgmt/**/` except `_client.py`.
- Review package metadata, `CHANGELOG.md`, `README.md`, and the public client
  signature where relevant.

## Version consistency

- The version in `_version.py` must match the latest version in `CHANGELOG.md`.
- If `_metadata.json` has an `apiVersion` containing `preview`, `_version.py`
  must contain a preview version such as `1.0.0b1`, not a stable version such
  as `1.0.0`.
- If the latest `CHANGELOG.md` release date is more than three weeks in the
  future, ask the author to verify the date.

## Package stability metadata

For a stable version, whose version string does not contain `b`:

- `pyproject.toml` must set `is_stable = true`.
- Classifiers must include
  `"Development Status :: 5 - Production/Stable"`.

For a preview version, whose version string contains `b`:

- `pyproject.toml` must set `is_stable = false`.
- Classifiers must include `"Development Status :: 4 - Beta"`.

## Client consistency

- The client `__init__` signature in `_client.py` must contain `credential`,
  `subscription_id`, and `base_url` in that order. Default values are not part
  of this check.
- If `subscription_id` is absent, `pyproject.toml` must contain
  `no_sub = true`. Otherwise, recommend adding it and regenerating the SDK.
- The client class name in `_client.py`, the client name used in `README.md`,
  and the `title` in `pyproject.toml` must match.
- README code snippets must follow the actual client signature and usage
  pattern.
