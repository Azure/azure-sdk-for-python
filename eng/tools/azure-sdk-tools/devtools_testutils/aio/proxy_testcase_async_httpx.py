# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Async proxy decorators for httpx-based clients (e.g., OpenAI AsyncOpenAI SDK).

These decorators monkeypatch httpx async transport classes to redirect requests through the test proxy,
enabling recording and playback for async clients that use httpx instead of Azure Core's transport layer.
"""
import logging
import urllib.parse as url_parse

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

from ..helpers import is_live_and_not_recording, trim_kwargs_from_test_function
from ..proxy_testcase import (
    get_test_id,
    start_record_or_playback,
    stop_record_or_playback,
    get_proxy_netloc,
)
from ..helpers import is_live

try:
    import httpx
except ImportError:
    httpx = None


def recorded_by_proxy_async_httpx(test_func):
    """Decorator that redirects async httpx network requests to target the azure-sdk-tools test proxy.

    Use this decorator for async tests that use httpx-based clients (like OpenAI AsyncOpenAI SDK)
    instead of Azure SDK clients. It monkeypatches httpx.AsyncHTTPTransport.handle_async_request
    to route requests through the test proxy.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#write-or-run-tests
    """
    if httpx is None:
        raise ImportError("httpx is required to use recorded_by_proxy_async_httpx. Install it with: pip install httpx")

    async def record_wrap(*args, **kwargs):
        def transform_httpx_request(request: httpx.Request, recording_id: str) -> None:
            """Transform an httpx.Request to route through the test proxy."""
            parsed_result = url_parse.urlparse(str(request.url))

            # Store original upstream URI
            if "x-recording-upstream-base-uri" not in request.headers:
                request.headers["x-recording-upstream-base-uri"] = f"{parsed_result.scheme}://{parsed_result.netloc}"

            # Set recording headers
            request.headers["x-recording-id"] = recording_id
            request.headers["x-recording-mode"] = "record" if is_live() else "playback"

            # Rewrite URL to proxy
            updated_target = parsed_result._replace(**get_proxy_netloc()).geturl()
            request.url = httpx.URL(updated_target)

        def restore_httpx_response_url(response: httpx.Response) -> httpx.Response:
            """Restore the response's request URL to the original upstream target."""
            try:
                parsed_resp = url_parse.urlparse(str(response.request.url))
                upstream_uri_str = response.request.headers.get("x-recording-upstream-base-uri", "")
                if upstream_uri_str:
                    upstream_uri = url_parse.urlparse(upstream_uri_str)
                    original_target = parsed_resp._replace(
                        scheme=upstream_uri.scheme or parsed_resp.scheme,
                        netloc=upstream_uri.netloc
                    ).geturl()
                    response.request.url = httpx.URL(original_target)
            except Exception:
                # Best-effort restore; don't fail the call if something goes wrong
                pass
            return response

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(test_func, trimmed_kwargs)

        if is_live_and_not_recording():
            return await test_func(*args, **trimmed_kwargs)

        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)
        original_transport_func = httpx.AsyncHTTPTransport.handle_async_request

        async def combined_call(transport_self, request: httpx.Request) -> httpx.Response:
            transform_httpx_request(request, recording_id)
            result = await original_transport_func(transport_self, request)
            return restore_httpx_response_url(result)

        httpx.AsyncHTTPTransport.handle_async_request = combined_call

        # Call the test function
        test_variables = None
        test_run = False
        try:
            try:
                test_variables = await test_func(*args, variables=variables, **trimmed_kwargs)
                test_run = True
            except TypeError as error:
                if "unexpected keyword argument" in str(error) and "variables" in str(error):
                    logger = logging.getLogger()
                    logger.info(
                        "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
                        "`variables` parameter to make use of recorded test variables."
                    )
                else:
                    raise error
            # If the test couldn't accept `variables`, run without passing them
            if not test_run:
                test_variables = await test_func(*args, **trimmed_kwargs)

        except ResourceNotFoundError as error:
            error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
            message = error_body.get("message") or error_body.get("Message")
            error_with_message = ResourceNotFoundError(message=message, response=error.response)
            raise error_with_message from error

        finally:
            httpx.AsyncHTTPTransport.handle_async_request = original_transport_func
            stop_record_or_playback(test_id, recording_id, test_variables)

        return test_variables

    return record_wrap
