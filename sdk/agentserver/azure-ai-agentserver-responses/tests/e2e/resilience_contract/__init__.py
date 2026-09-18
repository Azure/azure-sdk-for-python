# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Resilience-contract conformance suite (Spec 014).

This package contains behavioral tests that exercise every row × applicable
termination path of the documented resilience matrix in
``sdk/agentserver/specs/resilience-contract.md`` § The matrix.

All tests in this package MUST follow the rules in Constitution Principle X:

- Use real signal mechanisms via ``_crash_harness``:
  * Path A — SIGTERM with long grace (handler completes naturally).
  * Path B — SIGTERM with deliberately-short grace (grace exhaustion).
  * Path C — SIGKILL + restart (real crash recovery).
- MUST NOT mock ``_crash_harness`` or fabricate ``ResilienceContext``.
- MUST NOT call internal failure-marker functions directly.
- MUST parametrize on ``stream=False/True`` where the matrix collapses
  ``stream``.

The ``test_contract_completeness.py`` meta-test fails CI if any documented
(row, applicable path) is missing a paired test module, OR if any module
is missing one of the parametrize ids the matrix requires.
"""
