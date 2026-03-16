# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test that every public async method on AIProjectClient.beta sub-clients sends the
'Foundry-Features' HTTP request header.

This test does NOT make real network calls. It uses a custom async transport that
captures the outgoing HttpRequest and raises a sentinel exception, so no
actual HTTP traffic occurs.

Sub-clients and their methods are discovered dynamically at collection time via
introspection, so the test automatically covers new methods added to .beta and
stops covering methods that are removed — no manual updates needed.

Discovery strategy:
  - Non-callable public attributes of async `client.beta` are sub-clients
    (e.g. evaluation_taxonomies, memory_stores, …).
  - Public bound methods on each sub-client are the API methods to test.
    Both ``async def`` coroutine methods and regular ``def`` methods that
    return an ``AsyncItemPaged`` are discovered.
  - Fake arguments are inferred from each method's signature: required
    parameters (those with no default, or whose default is the _Unset sentinel)
    receive a type-appropriate placeholder value.

Run with:  pytest tests/foundry_features_header/test_required_header_async.py -s
The -s flag (or --capture=no) is required to see the printed report.
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from foundry_features_header_test_base import (
    EXPECTED_FOUNDRY_FEATURES,
    FAKE_ENDPOINT,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _RequestCaptured,
)


# ---------------------------------------------------------------------------
# Async-specific transport
# ---------------------------------------------------------------------------


class CapturingAsyncTransport(AsyncHttpTransport):
    """Async transport that captures the outgoing request and raises _RequestCaptured."""

    async def send(self, request: Any, **kwargs: Any) -> Any:  # type: ignore[override]
        raise _RequestCaptured(request)

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> "CapturingAsyncTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass


# ---------------------------------------------------------------------------
# Dynamic test-case discovery (runs at collection time, not at test time)
# ---------------------------------------------------------------------------


def _discover_async_test_cases() -> list[pytest.param]:
    """Introspect async AIProjectClient.beta and yield one pytest.param per public method.

    Steps:
      1. Instantiate a temporary async client (no network calls are made here;
         the constructor is synchronous).
      2. Non-callable public attributes of client.beta are sub-clients.
      3. Public bound methods on each sub-client are the API methods to test.
         Both coroutine methods (async def) and regular methods returning
         AsyncItemPaged satisfy inspect.ismethod() and are both included.
    """
    temp = AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
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

            label = f".beta.{sc_name}.{m_name}() [async]"
            expected = EXPECTED_FOUNDRY_FEATURES[sc_name]
            cases.append(pytest.param(label, sc_name, m_name, expected, id=label))

    return cases


_ASYNC_TEST_CASES = _discover_async_test_cases()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def async_client() -> Iterator[AsyncAIProjectClient]:
    """Provide a module-scoped async client backed by the capturing transport.

    The AIProjectClient constructor is synchronous, so no async fixture is
    needed.  Because the transport never performs real I/O, there is nothing
    to clean up after the tests.
    """
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
    )


@pytest.fixture(scope="module", autouse=True)
def _print_report_async() -> Iterator[None]:
    """Print the full Foundry-Features header report after all async tests finish."""
    yield
    report = TestFoundryFeaturesHeaderAsync._report
    max_len = TestFoundryFeaturesHeaderAsync._report_max_label_len
    if report:
        print("\n\nFoundry-Features header report (async):")
        for label, header_value in sorted(report):
            print(f"{label:<{max_len}}  |  \"{header_value}\"")


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeaderAsync(FoundryFeaturesHeaderTestBase):
    """Async tests: assert every public async .beta method sends the Foundry-Features header."""

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0

    # ------------------------------------------------------------------
    # Async capture
    # ------------------------------------------------------------------

    @staticmethod
    async def _capture_async(call: Any) -> Any:
        """Invoke *call()* and return the captured HttpRequest.

        Two cases are handled:
          1. ``async def`` methods: calling them returns an awaitable (coroutine).
             Awaiting it will hit the transport and raise _RequestCaptured.
          2. Regular ``def`` methods returning ``AsyncItemPaged``: calling them
             returns an async iterable.  Advancing to the first item triggers
             the transport and raises _RequestCaptured.
        """
        result = call()

        if inspect.isawaitable(result):
            # Coroutine path (async def method)
            try:
                await result
            except _RequestCaptured as exc:
                return exc.request
            raise AssertionError("Transport was never called (awaitable completed without raising)")

        # AsyncItemPaged path — advance to the first page to trigger the transport.
        ai = result.__aiter__()
        try:
            await ai.__anext__()
        except _RequestCaptured as exc:
            return exc.request
        except StopAsyncIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None

        raise AssertionError("Transport was never called")

    @classmethod
    async def _assert_header_async(cls, label: str, call: Any, expected_value: str) -> str:
        """Invoke *call*, capture the request, and assert the header is present and correct."""
        request = await cls._capture_async(call)
        return cls._record_header_assertion(label, request, expected_value)

    # ------------------------------------------------------------------
    # Parametrized test
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    @pytest.mark.parametrize("label,subclient_name,method_name,expected_header_value", _ASYNC_TEST_CASES)
    async def test_foundry_features_header_async(
        self,
        async_client: AsyncAIProjectClient,
        label: str,
        subclient_name: str,
        method_name: str,
        expected_header_value: str,
    ) -> None:
        """Assert that *method_name* on async .beta.<subclient_name> sends the expected Foundry-Features value."""
        sc = getattr(async_client.beta, subclient_name)
        method = getattr(sc, method_name)
        await self._assert_header_async(label, self._make_fake_call(method), expected_header_value)
