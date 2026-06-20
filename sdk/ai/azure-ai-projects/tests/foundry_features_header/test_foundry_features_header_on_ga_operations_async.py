# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests optional Foundry-Features header behavior on non-beta async methods.

These tests hard-code the non-beta async methods that optionally send the
Foundry-Features header and verify both modes:
  - allow_preview=True  -> header is present with expected value
  - allow_preview unset -> header is absent
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FOUNDRY_FEATURES_HEADER,
    AsyncFakeCredential,
    FoundryFeaturesHeaderTestBase,
    _NON_BETA_OPTIONAL_TEST_CASES,
    _RequestCaptured,
    _UNSET_SENTINELS,
)


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


@pytest.fixture(scope="module")
def async_client_preview_enabled() -> Iterator[AsyncAIProjectClient]:
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        allow_preview=True,
        transport=CapturingAsyncTransport(),
    )


@pytest.fixture(scope="module")
def async_client_preview_disabled() -> Iterator[AsyncAIProjectClient]:
    yield AsyncAIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=AsyncFakeCredential(),  # type: ignore[arg-type]
        transport=CapturingAsyncTransport(),
    )


@pytest.fixture(scope="module", autouse=True)
def _print_report_optional_async() -> Iterator[None]:
    """Print two Foundry-Features reports after all async optional tests finish:
    one for the allow_preview=True test and one for the allow_preview-unset test.
    """
    yield
    present_report = TestFoundryFeaturesHeaderOnGaOperationsAsync._report
    if present_report:
        max_len = TestFoundryFeaturesHeaderOnGaOperationsAsync._report_max_label_len
        print(
            "\n\nFoundry-Features header report on GA operations (async) — test_foundry_features_header_present_on_ga_operations_when_preview_enabled_async:"
        )
        for label, header_value in sorted(present_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')

    absent_report = TestFoundryFeaturesHeaderOnGaOperationsAsync._report_absent
    if absent_report:
        max_len = TestFoundryFeaturesHeaderOnGaOperationsAsync._report_absent_max_label_len
        print(
            "\n\nFoundry-Features header report on GA operations (async) — test_foundry_features_header_absent_on_ga_operations_when_preview_not_enabled_async:"
        )
        for label, header_value in sorted(absent_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


class TestFoundryFeaturesHeaderOnGaOperationsAsync(FoundryFeaturesHeaderTestBase):
    """Async tests for optional Foundry-Features header behavior on non-beta methods."""

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0
    _report_absent: ClassVar[List[Tuple[str, str]]] = []
    _report_absent_max_label_len: ClassVar[int] = 0

    @staticmethod
    async def _capture_async(call: Any) -> Any:
        """Invoke *call()* and return the captured HttpRequest."""
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

    @classmethod
    async def _assert_header_present_async(cls, label: str, call: Any, expected_value: str) -> None:
        request = await cls._capture_async(call)
        cls._record_header_assertion(label, request, expected_value)

    @classmethod
    async def _assert_header_absent_async(cls, label: str, call: Any) -> None:
        request = await cls._capture_async(call)
        cls._record_header_absence_assertion(label, request)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_present_on_ga_operations_when_preview_enabled_async(
        self,
        async_client_preview_enabled: AsyncAIProjectClient,
        method_name: str,
        expected_header_value: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        await self._assert_header_present_async(method_name, self._make_fake_call(method), expected_header_value)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_absent_on_ga_operations_when_preview_not_enabled_async(
        self,
        async_client_preview_disabled: AsyncAIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        await self._assert_header_absent_async(method_name, self._make_fake_call(method))


# ---------------------------------------------------------------------------
# Tests: caller-controlled header override / augmentation on GA operations (async)
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeaderOverrideOnGaOperationsAsync(FoundryFeaturesHeaderTestBase):
    """Verify caller-supplied headers are correctly handled on GA (non-beta) async operations.

    All tests are parametrized over _NON_BETA_OPTIONAL_TEST_CASES.

    Tests with allow_preview=True (header is injected internally):
      - override: caller supplies Foundry-Features → custom value wins.
      - override-and-add: caller supplies Foundry-Features + extra header → both reach transport.
      - additional-header: caller supplies only an extra header → extra header AND the
        internally-set Foundry-Features header both reach the transport.

    Tests without allow_preview (header is NOT injected internally):
      - additional-header-no-preview: caller supplies only an extra header → that header
        reaches the transport (Foundry-Features is absent, as expected).
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
    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_override_on_ga_operations_async(
        self,
        async_client_preview_enabled: AsyncAIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue"} must reach the transport
        instead of the internally-set default value (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_override_and_add_on_ga_operations_async(
        self,
        async_client_preview_enabled: AsyncAIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        must result in both headers reaching the transport (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_additional_header_on_ga_operations_async(
        self,
        async_client_preview_enabled: AsyncAIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"SomeOtherHeaderName": "SomeOtherHeaderValue"} (no Foundry-Features
        override) must result in the extra header AND the internally-set Foundry-Features header both
        reaching the transport (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {"SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) is not None, (
            f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}' to be present but it was missing. "
            f"Headers: {dict(request.headers)}"
        )
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    async def test_foundry_features_header_additional_header_on_ga_operations_no_preview_async(
        self,
        async_client_preview_disabled: AsyncAIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """When allow_preview is NOT set, a caller-supplied extra header
        (e.g. headers={"SomeOtherHeaderName": "SomeOtherHeaderValue"}) must still reach
        the transport. Foundry-Features is expected to be absent in this mode."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(async_client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {"SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = await self._capture_async(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) is None, (
            f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}' to be absent when allow_preview is not set, "
            f"but found: {request.headers.get(FOUNDRY_FEATURES_HEADER)}"
        )
