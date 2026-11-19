---
applyTo: "sdk/**/tests/**/*.py,sdk/**/test/**/*.py"
description: "Review Python SDK tests for meaningful coverage, isolation, and recorded/live behavior."
---

# Test Review

Use [the repository test guide](../../../doc/dev/tests.md) and the affected
package's existing fixtures as the reference for test conventions.

- Check that new or changed behavior is exercised, including failure and
  boundary paths where they matter. If a test is removed, check whether its
  coverage moved elsewhere.
- For service tests, verify recorded/playback runs do not depend on live-only
  credentials, time, or unrecorded requests; check sanitization of sensitive
  values before proposing a recording change.
- Verify assertions exercise the behavior under review and that tests do not
  leak mutable state, skip coverage unexpectedly, or assume test order.
- For management SDK packages, exclude `generated_tests/` from review as
  required by [`management.instructions.md`](./management.instructions.md).
