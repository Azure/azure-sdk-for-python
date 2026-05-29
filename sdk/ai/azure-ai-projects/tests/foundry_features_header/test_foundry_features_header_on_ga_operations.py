# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests optional Foundry-Features header behavior on non-beta sync methods.

These tests hard-code the non-beta methods that optionally send the
Foundry-Features header and verify both modes:
  - allow_preview=True  -> header is present with expected value
  - allow_preview unset -> header is absent
"""

import inspect
from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FOUNDRY_FEATURES_HEADER,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
    _NON_BETA_OPTIONAL_TEST_CASES,
    _RequestCaptured,
    _UNSET_SENTINELS,
)


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


@pytest.fixture(scope="module")
def client_preview_enabled() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        allow_preview=True,
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="module")
def client_preview_disabled() -> Iterator[AIProjectClient]:
    with AIProjectClient(
        endpoint=FAKE_ENDPOINT,
        credential=FakeCredential(),  # type: ignore[arg-type]
        transport=CapturingTransport(),
    ) as c:
        yield c


@pytest.fixture(scope="module", autouse=True)
def _print_report_optional() -> Iterator[None]:
    """Print two Foundry-Features reports after all sync optional tests finish:
    one for the allow_preview=True test and one for the allow_preview-unset test.
    """
    yield
    present_report = TestFoundryFeaturesHeaderOnGaOperations._report
    if present_report:
        max_len = TestFoundryFeaturesHeaderOnGaOperations._report_max_label_len
        print(
            "\n\nFoundry-Features header report on GA operations (sync) — test_foundry_features_header_present_on_ga_operations_when_preview_enabled:"
        )
        for label, header_value in sorted(present_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')

    absent_report = TestFoundryFeaturesHeaderOnGaOperations._report_absent
    if absent_report:
        max_len = TestFoundryFeaturesHeaderOnGaOperations._report_absent_max_label_len
        print(
            "\n\nFoundry-Features header report on GA operations (sync) — test_foundry_features_header_absent_on_ga_operations_when_preview_not_enabled:"
        )
        for label, header_value in sorted(absent_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


class TestFoundryFeaturesHeaderOnGaOperations(FoundryFeaturesHeaderTestBase):
    """Sync tests for optional Foundry-Features header behavior on non-beta methods."""

    _report: ClassVar[List[Tuple[str, str]]] = []
    _report_max_label_len: ClassVar[int] = 0
    _report_absent: ClassVar[List[Tuple[str, str]]] = []
    _report_absent_max_label_len: ClassVar[int] = 0

    @staticmethod
    def _capture(call: Any) -> Any:
        """Call *call()* and return the captured HttpRequest."""
        try:
            result = call()
        except _RequestCaptured as exc:
            return exc.request

        try:
            next(iter(result))
        except _RequestCaptured as exc:
            return exc.request
        except StopIteration:
            raise AssertionError("Iterator exhausted without the transport being called") from None

        raise AssertionError("Transport was never called")

    @classmethod
    def _assert_header_present(cls, label: str, call: Any, expected_value: str) -> None:
        request = cls._capture(call)
        cls._record_header_assertion(label, request, expected_value)

    @classmethod
    def _assert_header_absent(cls, label: str, call: Any) -> None:
        request = cls._capture(call)
        cls._record_header_absence_assertion(label, request)

    @pytest.mark.parametrize("method_name,expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_present_on_ga_operations_when_preview_enabled(
        self,
        client_preview_enabled: AIProjectClient,
        method_name: str,
        expected_header_value: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        self._assert_header_present(method_name, self._make_fake_call(method), expected_header_value)

    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_absent_on_ga_operations_when_preview_not_enabled(
        self,
        client_preview_disabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        self._assert_header_absent(method_name, self._make_fake_call(method))


# ---------------------------------------------------------------------------
# Tests: caller-controlled header override / augmentation on GA operations
# (only applies when allow_preview=True, since that is when the header is sent)
# ---------------------------------------------------------------------------


class TestFoundryFeaturesHeaderOverrideOnGaOperations(FoundryFeaturesHeaderTestBase):
    """Verify caller-supplied headers are correctly handled on GA (non-beta) operations.

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
    def _capture(call: Any) -> Any:
        """Invoke *call* and return the captured HttpRequest (sync version)."""
        try:
            result = call()
        except _RequestCaptured as exc:
            return exc.request
        try:
            next(iter(result))
        except _RequestCaptured as exc:
            return exc.request
        except StopIteration:
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

    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_override_on_ga_operations(
        self,
        client_preview_enabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue"} must reach the transport
        instead of the internally-set default value (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue"}
        request = self._capture(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"

    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_override_and_add_on_ga_operations(
        self,
        client_preview_enabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"Foundry-Features": "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        must result in both headers reaching the transport (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {FOUNDRY_FEATURES_HEADER: "CustomValue", "SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = self._capture(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get(FOUNDRY_FEATURES_HEADER) == "CustomValue"
        ), f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}: CustomValue' but got: {dict(request.headers)}"
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"

    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_additional_header_on_ga_operations(
        self,
        client_preview_enabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """Caller-supplied headers={"SomeOtherHeaderName": "SomeOtherHeaderValue"} (no Foundry-Features
        override) must result in the extra header AND the internally-set Foundry-Features header both
        reaching the transport (allow_preview=True)."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_enabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {"SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = self._capture(self._make_fake_call_with_headers(method, custom_headers))
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) is not None, (
            f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}' to be present but it was missing. "
            f"Headers: {dict(request.headers)}"
        )
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"

    @pytest.mark.parametrize("method_name,_expected_header_value", _NON_BETA_OPTIONAL_TEST_CASES)
    def test_foundry_features_header_additional_header_on_ga_operations_no_preview(
        self,
        client_preview_disabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        """When allow_preview is NOT set, a caller-supplied extra header
        (e.g. headers={"SomeOtherHeaderName": "SomeOtherHeaderValue"}) must still reach
        the transport. Foundry-Features is expected to be absent in this mode."""
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        custom_headers = {"SomeOtherHeaderName": "SomeOtherHeaderValue"}
        request = self._capture(self._make_fake_call_with_headers(method, custom_headers))
        assert (
            request.headers.get("SomeOtherHeaderName") == "SomeOtherHeaderValue"
        ), f"{method_name}: Expected 'SomeOtherHeaderName: SomeOtherHeaderValue' in headers but got: {dict(request.headers)}"
        assert request.headers.get(FOUNDRY_FEATURES_HEADER) is None, (
            f"{method_name}: Expected '{FOUNDRY_FEATURES_HEADER}' to be absent when allow_preview is not set, "
            f"but found: {request.headers.get(FOUNDRY_FEATURES_HEADER)}"
        )
