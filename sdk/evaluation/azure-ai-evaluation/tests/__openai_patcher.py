"""Implementation of an httpx.Client that forwards traffic to the Azure SDK test-proxy.

.. note::

    This module has side-effects!

    Importing this module will replace the default httpx.Client used
    by the openai package with one that can redirect it's traffic
    to the Azure SDK test-proxy on demand.

"""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, Iterator, Literal, Optional

import httpx
import openai._base_client
from typing_extensions import override


@dataclass
class TestProxyConfig:
    recording_id: str
    """The ID for the ongoing test recording."""

    recording_mode: Literal["playback", "record"]
    """The current recording mode."""

    proxy_url: str
    """The url for the Azure SDK test proxy."""


class TestProxyHttpxClientBase:
    recording_config: Optional[TestProxyConfig] = None

    @classmethod
    def is_recording(cls) -> bool:
        """Whether we are forwarding requests to the test proxy

        :return: True if forwarding, False otherwise
        :rtype: bool
        """
        return cls.recording_config is not None

    @classmethod
    @contextmanager
    def record_with_proxy(cls, config: TestProxyConfig) -> Iterable[None]:
        """Forward all requests made within the scope of context manager to test-proxy.

        :param TestProxyConfig config: The test proxy configuration
        """
        cls.recording_config = config

        yield

        cls.recording_config = None

    @contextmanager
    def _reroute_to_proxy(self, request: httpx.Request) -> Iterator[None]:
        """Temporarily re-route a request to be sent throught the test proxy.

        The request is modified in place, but is restored once the contextmanager exits

        :param httpx.Request request: The request to update
        :return: None
        :rtype: None
        """
        assert self.is_recording(), f"{self._reroute_to_proxy.__qualname__} should only be called while recording"
        config = self.recording_config
        original_url = request.url

        request_path = original_url.copy_with(scheme="", netloc=b"")
        request.url = httpx.URL(config.proxy_url).join(request_path)

        original_headers = request.headers
        request.headers = request.headers.copy()
        request.headers.setdefault(
            "x-recording-upstream-base-uri", str(httpx.URL(scheme=original_url.scheme, netloc=original_url.netloc))
        )
        request.headers["x-recording-id"] = config.recording_id
        request.headers["x-recording-mode"] = config.recording_mode

        yield

        request.url = original_url
        request.headers = original_headers


class TestProxyHttpxClient(TestProxyHttpxClientBase, openai._base_client.SyncHttpxClientWrapper):
    @override
    def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        if self.is_recording():
            with self._reroute_to_proxy(request):
                response = super().send(request, **kwargs)

            response.request.url = request.url
            return response
        else:
            return super().send(request, **kwargs)


class TestProxyAsyncHttpxClient(TestProxyHttpxClientBase, openai._base_client.AsyncHttpxClientWrapper):
    @override
    async def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        if self.is_recording():
            with self._reroute_to_proxy(request):
                response = await super().send(request, **kwargs)

            response.request.url = request.url
            return response
        else:
            return await super().send(request, **kwargs)


# openai._base_client.{Async,Sync}HttpxClientWrapper are default httpx.Clients instantiated by openai
openai._base_client.SyncHttpxClientWrapper = TestProxyHttpxClient
openai._base_client.AsyncHttpxClientWrapper = TestProxyAsyncHttpxClient
