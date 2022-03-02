# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import functools
from aiohttp import client

from azure.keyvault.secrets import ApiVersion
from azure.keyvault.secrets._shared import HttpChallengeCache
from azure.keyvault.secrets._shared.client_base import DEFAULT_VERSION
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, is_live
import pytest
from azure.core.pipeline.transport import HttpResponse, HttpTransport, HttpRequest
from windows.http import Response, Request, Session
from typing import ContextManager, Iterator, Optional



def get_decorator(**kwargs):
    """returns a test decorator for test parameterization"""
    return [(api_version) for api_version in ApiVersion]


class SecretsTestCaseClientPrepaper(AzureRecordedTestCase):
    def __init__(self, **kwargs) -> None:
        self.azure_keyvault_url = os.getenv("AZURE_KEYVAULT_URL", "https://vaultname.vault.azure.net")
        self.is_async = kwargs.pop("is_async", False)
        self.is_logging_enabled = kwargs.pop("logging_enable", True)

    def __call__(self, fn):
        def _preparer(test_class, api_version, **kwargs):
            self._skip_if_not_configured(api_version)
            if not self.is_logging_enabled:
                kwargs.update({'logging_enable':False})
            client = self.create_client(self.azure_keyvault_url, **kwargs, api_version=api_version)
            with client:
                fn(test_class, client)
        return _preparer

    def create_client(self, vault_uri, **kwargs):
        from azure.keyvault.secrets import SecretClient
        credential = self.get_credential(SecretClient)
        return self.create_client_from_credential(
            SecretClient, credential=credential, vault_url=vault_uri, transport = WindowsHttpTransport(), **kwargs
        )

    def _skip_if_not_configured(self, api_version, **kwargs):
        if is_live() and api_version != DEFAULT_VERSION:
            pytest.skip("This test only uses the default API version for live tests")






class WindowsHttpTransportResponse(HttpResponse):
    def __init__(self, request: HttpRequest, windows_http_response: Response, stream_contextmanager: Optional[ContextManager] = None):
        super().__init__(request, windows_http_response)
        self.status_code = windows_http_response.status_code
        self.headers = windows_http_response.headers
        self.reason = windows_http_response.reason
        self.content_type = windows_http_response.headers.get('content-type')
        self.stream_contextmanager = stream_contextmanager

    def body(self):
        return self.internal_response.content

    def stream_download(self, _) -> Iterator[bytes]:
        return WindowsHttpStreamDownloadGenerator(_, self)
        


class WindowsHttpStreamDownloadGenerator():
    def __init__(self, _, response):
        self.response = response
        self.iter_func = response.internal_response.iter_content()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.iter_func)
        except StopIteration:
            self.response.stream_contextmanager.close()
            raise


class WindowsHttpTransport(HttpTransport):
    def __init__(self):
        self.client = None

    def open(self):
        self.client = Session()

    def close(self):
        self.client = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()

    def send(self, request: HttpRequest, **kwargs) -> HttpResponse:
        print(f"sending a {request.method} to {request.url}")

        stream_response = kwargs.pop("stream", False)

        request.headers['Content-Type'] = 'application/json'

        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request.data,
            "files": request.files,
            **kwargs
        }

        stream_ctx = None

        if stream_response:
            stream_ctx = self.client.request(**parameters, stream = True)
            response = stream_ctx.__enter__()

        else:
            response = self.client.request(**parameters)

        return WindowsHttpTransportResponse(request, response, stream_contextmanager=stream_ctx)
