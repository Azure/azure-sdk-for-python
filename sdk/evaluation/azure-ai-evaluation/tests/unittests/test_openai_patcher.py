# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any

import httpx
import pytest

from tests.__openai_patcher import (
    TestProxyConfig as _TestProxyConfig,
    TestProxyHttpxClientBase as _TestProxyHttpxClientBase,
)


class _DummyClient(_TestProxyHttpxClientBase):
    pass


def _assert_proxy_reroute(http_module: Any) -> None:
    request = http_module.Request("POST", "https://example.test/openai/path?api-version=test")
    original_url = request.url
    config = _TestProxyConfig(
        recording_id="recording",
        recording_mode="playback",
        proxy_url="http://localhost:5000",
    )

    with _TestProxyHttpxClientBase.record_with_proxy(config):
        with _DummyClient()._reroute_to_proxy(request):
            assert type(request.url) is type(original_url)
            assert str(request.url) == "http://localhost:5000/openai/path?api-version=test"
            assert request.headers["x-recording-upstream-base-uri"] == "https://example.test"

    assert request.url == original_url


@pytest.mark.unittest
def test_proxy_reroute_with_httpx() -> None:
    _assert_proxy_reroute(httpx)


@pytest.mark.unittest
def test_proxy_reroute_with_httpx2() -> None:
    httpx2 = pytest.importorskip("httpx2")
    _assert_proxy_reroute(httpx2)
