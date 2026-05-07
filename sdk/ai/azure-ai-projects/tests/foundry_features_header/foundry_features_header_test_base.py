# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Shared base class and helpers for Foundry-Features HTTP header tests (sync and async).

The following are shared by both test_required_header.py (sync) and
test_required_header_async.py (async):

  - Constants: FAKE_ENDPOINT, FOUNDRY_FEATURES_HEADER, EXPECTED_FOUNDRY_FEATURES
  - _RequestCaptured exception sentinel
  - FakeCredential / AsyncFakeCredential stubs
  - FoundryFeaturesHeaderTestBase with utility/assertion class methods
"""

from __future__ import annotations  # To make `dict[str, Any] | None` work on Python 3.9
import inspect
import pytest
import tempfile
from typing import Any, ClassVar, List, Tuple, Union, get_origin

from azure.core.credentials import AccessToken

# Both sentinel values used to mark "required but unset" parameters.
# The sync and async generated _operations modules define _Unset independently.
from azure.ai.projects.operations._operations import _Unset as _SyncUnset
from azure.ai.projects.aio.operations._operations import _Unset as _AsyncUnset

FAKE_ENDPOINT = "https://fake-account.services.ai.azure.com/api/projects/fake-project"
FOUNDRY_FEATURES_HEADER = "Foundry-Features"

# Expected Foundry-Features header value for each .beta sub-client.
# If a new sub-client is added to .beta and is missing from this mapping, the test will
# fail at collection time with a message asking you to add it here.
EXPECTED_FOUNDRY_FEATURES: dict[str, str] = {
    "evaluation_taxonomies": "Evaluations=V1Preview",
    "evaluators": "Evaluations=V1Preview",
    "insights": "Insights=V1Preview",
    "memory_stores": "MemoryStores=V1Preview",
    "red_teams": "RedTeams=V1Preview",
    "schedules": "Schedules=V1Preview",
    "toolboxes": "Toolboxes=V1Preview",
    "skills": "Skills=V1Preview",
    "datasets": "DataGenerationJobs=V1Preview",
    "agents": "HostedAgents=V1Preview,AgentEndpoints=V1Preview,CodeAgents=V1Preview",
}

# Shared test cases for non-beta methods that optionally send the Foundry-Features header.
# Used by both test_foundry_features_header_optional.py (sync) and
# test_foundry_features_header_optional_async.py (async).
_NON_BETA_OPTIONAL_TEST_CASES = [
    # Each pytest.param entry has the following positional arguments:
    #   1. method_name           (str) – "<subclient>.<method>" on AIProjectClient, e.g. "agents.create_version"
    #      The subclient and method names are parsed automatically from this string.
    #   2. expected_header_value (str) – Expected value of the Foundry-Features header when allow_preview=True.
    #      Use a comma-separated list of feature=version pairs, e.g. "FeatureA=V1Preview,FeatureB=V1Preview".
    #   The test id is derived automatically from method_name.
    pytest.param(
        "agents.create_version",
        "HostedAgents=V1Preview,WorkflowAgents=V1Preview,AgentEndpoints=V1Preview",
    ),
    pytest.param(
        "evaluation_rules.create_or_update",
        "Evaluations=V1Preview",
    ),
]

# Both sentinel values – used by _make_fake_call to detect required parameters
# whose defaults are the internal _Unset object (rather than inspect.Parameter.empty).
_UNSET_SENTINELS: frozenset = frozenset({_SyncUnset, _AsyncUnset})

# ---------------------------------------------------------------------------
# Sentinel exception raised by capturing transports
# ---------------------------------------------------------------------------


class _RequestCaptured(Exception):
    """Raised by CapturingTransport / CapturingAsyncTransport to abort I/O early."""

    def __init__(self, request: Any) -> None:
        self.request = request
        super().__init__("request captured")


# ---------------------------------------------------------------------------
# Stub credentials
# ---------------------------------------------------------------------------


class FakeCredential:
    """Sync stub credential that returns a never-expiring token."""

    def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class AsyncFakeCredential:
    """Async stub credential that returns a never-expiring token."""

    async def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


# ---------------------------------------------------------------------------
# Base test class
# ---------------------------------------------------------------------------


class FoundryFeaturesHeaderTestBase:
    """Base class with utilities shared by sync and async Foundry-Features header tests.

    Subclasses must define their own *class-level* ``_report``, ``_report_absent``,
    ``_report_max_label_len``, and ``_report_absent_max_label_len`` so that each test
    module accumulates its own reports and they do not bleed into one another.
    """

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0
    _report_absent: ClassVar[List[Tuple[str, str]]] = []
    _report_absent_max_label_len: ClassVar[int] = 0

    # ------------------------------------------------------------------
    # Fake-argument builder
    # ------------------------------------------------------------------

    @staticmethod
    def _fake_for_param(param: inspect.Parameter) -> Any:
        """Return a plausible fake value for a single required parameter.

        Resolution order:
          - Union types (e.g. Union[Model, JSON, IO[bytes]])  -> {} (JSON body)
          - list / List[...]                                  -> []
          - str                                               -> "fake-value" (special case: for "folder" param we return the OS temp dir, since we need the folder to exist.)
          - int                                               -> 0
          - bool                                              -> False
          - anything else (model classes, etc.)               -> {}
        """
        if param.name == "folder" and param.annotation is str:
            return tempfile.gettempdir()

        ann = param.annotation
        if ann is inspect.Parameter.empty:
            return "fake-value"

        origin = get_origin(ann)
        if origin is Union:
            return {}
        if origin is list:
            return []
        if ann is str:
            return "fake-value"
        if ann is int:
            return 0
        if ann is bool:
            return False
        return {}

    @classmethod
    def _make_fake_call(cls, method: Any, extra_kwargs: dict[str, Any] | None = None) -> Any:
        """Return a zero-argument callable that invokes *method* with fake args.

        Only required parameters (no default, or default is the _Unset sentinel
        from either the sync or async generated operations module) are populated.
        Optional ones are omitted so as not to trigger extra validation paths.

        *extra_kwargs*, when provided, are merged into the keyword arguments
        passed to *method* (useful for parameters that are optional in the
        signature but required at runtime).
        """
        sig = inspect.signature(method)
        args: list[Any] = []
        kwargs: dict[str, Any] = dict(extra_kwargs) if extra_kwargs else {}

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue

            is_required = param.default is inspect.Parameter.empty or param.default in _UNSET_SENTINELS
            if not is_required:
                continue

            fake = cls._fake_for_param(param)
            if param.kind in (param.POSITIONAL_OR_KEYWORD, param.POSITIONAL_ONLY):
                args.append(fake)
            else:  # KEYWORD_ONLY
                kwargs[param_name] = fake

        return lambda: method(*args, **kwargs)

    # ------------------------------------------------------------------
    # Assertion + report recording (shared logic, transport-agnostic)
    # ------------------------------------------------------------------

    @classmethod
    def _record_header_assertion(cls, label: str, request: Any, expected_value: str) -> str:
        """Assert the Foundry-Features header on *request* equals *expected_value*,
        then record the result in *cls._report* for the end-of-session summary.
        """
        header_value: str | None = request.headers.get(FOUNDRY_FEATURES_HEADER)
        assert header_value, (
            f"{label}: REST call was made but '{FOUNDRY_FEATURES_HEADER}' header is "
            f"missing or empty.\nActual headers: {dict(request.headers)}"
        )
        assert header_value == expected_value, (
            f"{label}: expected '{FOUNDRY_FEATURES_HEADER}: {expected_value}' " f"but got '{header_value}'"
        )
        cls._report_max_label_len = max(cls._report_max_label_len, len(label))
        cls._report.append((label, header_value))
        return header_value

    @classmethod
    def _record_header_absence_assertion(cls, label: str, request: Any) -> None:
        """Assert the Foundry-Features header is absent on *request*,
        then record the result in *cls._report_absent* for the end-of-module summary.
        """
        assert FOUNDRY_FEATURES_HEADER not in request.headers, (
            f"{label}: expected '{FOUNDRY_FEATURES_HEADER}' header to be absent.\n"
            f"Actual headers: {dict(request.headers)}"
        )
        absence_note = f"'{FOUNDRY_FEATURES_HEADER}' header not present (as expected)"
        cls._report_absent_max_label_len = max(cls._report_absent_max_label_len, len(label))
        cls._report_absent.append((label, absence_note))
