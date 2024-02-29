"""Implementation of an httpx.Client that forwards traffic to the Azure SDK test-proxy.

.. note::

    This module has side-effects!

    Importing this module will replace the default httpx.Client used
    by the openai package with one that can redirect it's traffic
    to the Azure SDK test-proxy on demand.

"""
from contextlib import contextmanager
from typing import Iterable, Literal, Optional

import httpx
import openai._base_client
from typing_extensions import override
from dataclasses import dataclass


@dataclass
class TestProxyConfig:
    recording_id: str
    """The ID for the ongoing test recording."""

    recording_mode: Literal["playback", "record"]
    """The current recording mode."""

    proxy_url: str
    """The url for the Azure SDK test proxy."""


class TestProxyHttpxClient(openai._base_client.SyncHttpxClientWrapper):
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

    @override
    def send(self, request: httpx.Request, **kwargs) -> httpx.Response:
        if self.is_recording():
            return self._send_to_proxy(request, **kwargs)
        else:
            return super().send(request, **kwargs)

    def _send_to_proxy(self, request: httpx.Request, **kwargs) -> httpx.Response:
        """Forwards a network request to the test proxy

        :param httpx.Request request: The request to send
        :keyword **kwargs: The kwargs accepted by httpx.Client.send
        :return: The request's response
        :rtype: httpx.Response
        """
        assert self.is_recording(), f"{self._send_to_proxy.__qualname__} should only be called while recording"
        config = self.recording_config
        original_url = request.url

        request_path = original_url.copy_with(scheme="", netloc=b"")
        request.url = httpx.URL(config.proxy_url).join(request_path)

        headers = request.headers
        if headers.get("x-recording-upstream-base-uri", None) is None:
            headers["x-recording-upstream-base-uri"] = str(
                httpx.URL(scheme=original_url.scheme, netloc=original_url.netloc)
            )
        headers["x-recording-id"] = config.recording_id
        headers["x-recording-mode"] = config.recording_mode

        response = super().send(request, **kwargs)

        response.request.url = original_url
        return response


# openai._base_client.SyncHttpxClientWrapper is default httpx.Client instantiated by openai
openai._base_client.SyncHttpxClientWrapper = TestProxyHttpxClient
