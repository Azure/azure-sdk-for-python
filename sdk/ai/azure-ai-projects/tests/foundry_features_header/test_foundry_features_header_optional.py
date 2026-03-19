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

from typing import Any, ClassVar, Iterator, List, Tuple

import pytest
from azure.core.pipeline.transport import HttpTransport
from azure.ai.projects import AIProjectClient

from foundry_features_header_test_base import (
    FAKE_ENDPOINT,
    FakeCredential,
    FoundryFeaturesHeaderTestBase,
    _NON_BETA_OPTIONAL_TEST_CASES,
    _RequestCaptured,
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
    present_report = TestFoundryFeaturesHeaderOptional._report
    if present_report:
        max_len = TestFoundryFeaturesHeaderOptional._report_max_label_len
        print("\n\nFoundry-Features optional header report (sync) — test_optional_header_present_when_preview_enabled:")
        for label, header_value in sorted(present_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')

    absent_report = TestFoundryFeaturesHeaderOptional._report_absent
    if absent_report:
        max_len = TestFoundryFeaturesHeaderOptional._report_absent_max_label_len
        print(
            "\n\nFoundry-Features optional header report (sync) — test_optional_header_absent_when_preview_not_enabled:"
        )
        for label, header_value in sorted(absent_report):
            print(f'{label:<{max_len}}  |  "{header_value}"')


class TestFoundryFeaturesHeaderOptional(FoundryFeaturesHeaderTestBase):
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
    def test_optional_header_present_when_preview_enabled(
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
    def test_optional_header_absent_when_preview_not_enabled(
        self,
        client_preview_disabled: AIProjectClient,
        method_name: str,
        _expected_header_value: str,
    ) -> None:
        subclient_name, method_attr = method_name.split(".")
        sc = getattr(client_preview_disabled, subclient_name)
        method = getattr(sc, method_attr)
        self._assert_header_absent(method_name, self._make_fake_call(method))
