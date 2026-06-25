# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Sample 18 invocation-pattern e2e suite (Spec 014 Phase 9).

This suite is the user-facing complement to the framework-side conformance
suite at ``tests/e2e/resilience_contract/``. The conformance suite proves
that the framework honours every (row × cancellation-path) cell in the
resilience contract with a minimal test handler. THIS suite proves that
sample 18 — the realistic copilot handler the documentation points users
at — behaves correctly under every developer-invocation pattern the
matrix admits.

All tests are marked ``@pytest.mark.live`` because sample 18 imports the
real GitHub Copilot SDK at module top-level. Running this suite requires:

- ``github-copilot-sdk`` installed.
- ``gh copilot`` authenticated.
- ``COPILOT_MODEL`` env var (defaults to ``gpt-5-mini``).

Invoke explicitly: ``pytest -m live tests/e2e/sample_18_invocation_patterns/``.
"""
