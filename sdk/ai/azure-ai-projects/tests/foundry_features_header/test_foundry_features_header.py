# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test that every public method on AIProjectClient.beta sub-clients sends the
'Foundry-Features' HTTP request header.

This test does NOT make real network calls. It uses a custom transport that
captures the outgoing HttpRequest and raises a sentinel exception, so no
actual HTTP traffic occurs.

Sub-clients and their methods are discovered dynamically at collection time via
introspection, so the test automatically covers new methods added to .beta and
stops covering methods that are removed — no manual updates needed.

Discovery strategy:
  - Non-callable public attributes of `client.beta` are sub-clients
    (e.g. evaluation_taxonomies, memory_stores, …).
  - Public bound methods on each sub-client are the API methods to test.
  - Fake arguments are inferred from each method's signature: required
    parameters (those with no default, or whose default is the _Unset sentinel)
    receive a type-appropriate placeholder value.

Run with:  pytest tests/foundry_features_header/test_required_header.py -s
The -s flag (or --capture=no) is required to see the printed report.
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient

from foundry_features_header_test_base import (
    EXPECTED_FOUNDRY_FEATURES,
    FAKE_ENDPOINT,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
    _RequestCaptured,
)


# ---------------------------------------------------------------------------
# Sync-specific transport
# ---------------------------------------------------------------------------


class CapturingTransport(HttpTransport):
    """Sync transport that captures the outgoing request and raises _RequestCaptured."""

    def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self) -> "CapturingTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Dynamic test-case discovery (runs at collection time, not at test time)
# ---------------------------------------------------------------------------


def _discover_test_cases() -> list[pytest.param]:
    """Introspect AIProjectClient.beta and yield one pytest.param per public method.

    Steps:
      1. Instantiate a temporary client (no network calls are made here).
      2. Non-callable public attributes of client.beta are sub-clients.
      3. Public bound methods on each sub-client are the API methods to test.
    """
    temp = AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    )

    cases: list[pytest.param] = []
    for sc_name in sorted(dir(temp.beta)):
        if sc_name.startswith("_"):
            continue
        sc = getattr(temp.beta, sc_name)
        # Sub-clients are non-callable objects (instances of operations classes).
        # Skip anything callable (e.g. methods directly on BetaOperations itself).
        if callable(sc):
            continue

        assert sc_name in EXPECTED_FOUNDRY_FEATURES, (
            f"New .beta sub-client '{sc_name}' discovered but not found in EXPECTED_FOUNDRY_FEATURES. "
            f"Please add an entry for '.beta.{sc_name}' to the EXPECTED_FOUNDRY_FEATURES mapping in "
            f"base_test.py."
        )

        for m_name in sorted(dir(sc)):
            if m_name.startswith("_"):
                continue
            method = getattr(sc, m_name)
            if not inspect.ismethod(method):
                continue

            label = f".beta.{sc_name}.{m_name}()"
            expected = EXPECTED_FOUNDRY_FEATURES[sc_name]
            cases.append(pytest.param(label, sc_name, m_name, expected, id=label))

    return cases


_TEST_CASES = _discover_test_cases()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="session", autouse=True)
def _print_report() -> Iterator[None]:
    """Print the full Foundry-Features header report after all tests finish."""
    yield
    report = TestFoundryFeaturesHeader._report
    max_len = TestFoundryFeaturesHeader._report_max_label_len
    if report:
        print("\n\nFoundry-Features header report (sync):")
        for label, header_value in sorted(report):
            print(f"{label:<{max_len}}  |  \"{header_value}\"")


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeader(FoundryFeaturesHeaderTestBase):
    """Sync tests: assert every public .beta method sends the Foundry-Features header."""

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0

    # ------------------------------------------------------------------
    # Sync capture
    # ------------------------------------------------------------------

    @staticmethod
    def _capture(call: Any) -> Any:
        """Call *call()* and return the captured HttpRequest.

        Most methods raise _RequestCaptured immediately (transport is hit
        synchronously).  Lazy methods that return an ItemPaged only call the
        transport when the first item is fetched, so we trigger that with next().
        """
        try:
            result = call()
        except _RequestCaptured as exc:
            return exc.request

        # call() returned without raising -> lazy iterable (ItemPaged)
        try:
            next(iter(result))
        except _RequestCaptured as exc:
            return exc.request
        except StopIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None

        raise AssertionError("Transport was never called")

    @classmethod
    def _assert_header(cls, label: str, call: Any, expected_value: str) -> str:
        """Invoke *call*, capture the request, and assert the header is present and correct."""
        request = cls._capture(call)
        return cls._record_header_assertion(label, request, expected_value)

    # ------------------------------------------------------------------
    # Parametrized test
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("label,subclient_name,method_name,expected_header_value", _TEST_CASES)
    def test_foundry_features_header(
        self,
        client: AIProjectClient,
        label: str,
        subclient_name: str,
        method_name: str,
        expected_header_value: str,
    ) -> None:
        """Assert that *method_name* on .beta.<subclient_name> sends the expected Foundry-Features value."""
        sc = getattr(client.beta, subclient_name)
        method = getattr(sc, method_name)
        self._assert_header(label, self._make_fake_call(method), expected_header_value)