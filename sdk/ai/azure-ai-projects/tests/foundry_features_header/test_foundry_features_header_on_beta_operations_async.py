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

NOTE: This does not test follow up paging calls for "list" operations. It only
tests the first call.
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from foundry_features_header_test_base import (
    EXPECTED_FOUNDRY_FEATURES,
    FAKE_ENDPOINT,
    FOUNDRY_FEATURES_HEADER,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _RequestCaptured,
    _UNSET_SENTINELS,
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

        # Use the underlying operation's dir() for method discovery.
        # The proxy may not implement __dir__ in older installs, causing dir(sc) to
        # return no public methods. Methods are still fetched via getattr(sc, ...) so
        # the header-injecting proxy wrapper is exercised.
        _underlying_op = getattr(sc, "_operation", sc)
        for m_name in sorted(dir(_underlying_op)):
            if m_name.startswith("_"):
                continue
            method = getattr(sc, m_name)
            if not callable(method):
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
    report = TestFoundryFeaturesHeaderOnBetaOperationsAsync._report
    max_len = TestFoundryFeaturesHeaderOnBetaOperationsAsync._report_max_label_len
    if report:
        print("\n\nFoundry-Features header report (async):")
        for label, header_value in sorted(report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeaderOnBetaOperationsAsync(FoundryFeaturesHeaderTestBase):
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
    async def test_foundry_features_header_on_beta_operations_async(
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
        extra_kwargs: dict[str, Any] = {}
        await self._assert_header_async(
            label, self._make_fake_call(method, extra_kwargs=extra_kwargs), expected_header_value
        )


# ---------------------------------------------------------------------------
# Pick the first discovered beta method (reuses _ASYNC_TEST_CASES, no extra I/O)
# ---------------------------------------------------------------------------

_, _FIRST_SC_NAME, _FIRST_M_NAME, _ = _ASYNC_TEST_CASES[0].values


# ---------------------------------------------------------------------------
# Tests: caller-controlled header override / augmentation behaviour (async)
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeaderOverrideOnBetaOperationsAsync(FoundryFeaturesHeaderTestBase):
    """Verify callers can override or augment the internally-set Foundry-Features header (async).

    All three tests operate on the first public method enumerated on any .beta sub-client
    to avoid hard-coding a specific API surface.
    """

    @staticmethod
    async def _capture_async(call: Any) -> Any:
        """Invoke *call* and return the captured HttpRequest (async version)."""
        result = call()
        if inspect.isawaitable(result):
            try:
                await result
            except _RequestCaptured as exc:
                return exc.request
            raise AssertionError("Transport was never called (awaitable completed without raising)")
        ai = result.__aiter__()
        try:
            await ai.__anext__()
        except _RequestCaptured as exc:
            return exc.request
        except StopAsyncIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None
        raise AssertionError("Transport was never called")

    @staticmethod
    def _make_fake_call_with_headers(method: Any, headers: dict) -> Any:
        """Like _make_fake_call but also passes *headers* as a keyword argument."""
        sig = inspect.signature(method)
        args: list[Any] = []
        kwargs: dict[str, Any] = {"headers": headers}
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            is_required = param.default is inspect.Parameter.empty or param.default in _UNSET_SENTINELS
            if not is_required:
                continue
            fake = FoundryFeaturesHeaderTestBase._fake_for_param(param)
            if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY):
                args.append(fake)
            else:
                kwargs[param_name] = fake
        return lambda: method(*args, **kwargs)

    @pytest.mark.asyncio
    async def test_foundry_features_header_override_on_beta_operations_async(
        self, async_client: AsyncAIProjectClient
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue"} must reach the transport
        instead of the internally-set default value."""
        sc = getattr(async_client.beta, _FIRST_SC_NAME)
        method = getattr(sc, _FIRST_M_NAME)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"

    @pytest.mark.asyncio
    async def test_foundry_features_header_override_and_add_on_beta_operations_async(
        self, async_client: AsyncAIProjectClient
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        must result in both headers reaching the transport (custom Foundry-Features value and extra header)."""
        sc = getattr(async_client.beta, _FIRST_SC_NAME)
        method = getattr(sc, _FIRST_M_NAME)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"

    @pytest.mark.asyncio
    async def test_foundry_features_header_additional_header_on_beta_operations_async(
        self, async_client: AsyncAIProjectClient
    ) -> None:
        """Caller-supplied headers={"SomeOtherHeaderName": "SomeOtherHeaderValue"} (no Foundry-Features
        override) must result in the extra header AND the internally-set Foundry-Features header both
        reaching the transport."""
        sc = getattr(async_client.beta, _FIRST_SC_NAME)
        method = getattr(sc, _FIRST_M_NAME)
        custom_headers = {"SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) is not None, (
            f"Expected '{FOUNDRY_FEATURES_HEADER}' to be present but it was missing. "
            f"Headers: {dict(request.headers)}"
        )
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"
