# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging
import urllib.parse as url_parse
from contextlib import AsyncExitStack
from functools import wraps

from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.transport import AioHttpTransport

try:
    import httpx

    AsyncHTTPXTransport = httpx.AsyncHTTPTransport
except ImportError:
    httpx = None
    AsyncHTTPXTransport = None

from ..helpers import is_live_and_not_recording, trim_kwargs_from_test_function
from ..proxy_testcase import (
    get_test_id,
    start_record_or_playback,
    transform_request,
    transform_httpx_request,
    restore_httpx_response_url,
    stop_record_or_playback,
)


# helper: turn decorator args into a normalized list of (owner, attr_name)
def _normalize_transport_specs(specs):
    norm = []
    for spec in specs:
        if isinstance(spec, tuple) and len(spec) == 2:
            owner, attr = spec
            norm.append((owner, attr))
        else:
            # If a class was provided, assume attribute name "send"
            # (Safer than accepting a bare function object like AioHttpTransport.send,
            # because assignment requires knowing the owner and attribute name.)
            norm.append((spec, "send"))
    return norm


def recorded_by_proxy_async(*maybe_specs):
    """
    Usages:
      # This is how you decorate your async test functions

      # If your test uses azure.core only network calls
      @recorded_by_proxy_async
      async def test(...): ...

      # If your test uses httpx only for network calls
      from httpx import AsyncHTTPTransport as AsyncHTTPXTransport
      @recorded_by_proxy_async((AsyncHTTPXTransport, "handle_async_request"))
      async def test(...): ...

      # If your test uses both azure.core and httpx for network calls
      from azure.core.pipeline.transport import AioHttpTransport
      from httpx import AsyncHTTPTransport as AsyncHTTPXTransport
      @recorded_by_proxy_async((AioHttpTransport, "send"), (AsyncHTTPXTransport, "handle_async_request"))
      async def test(...): ...
    """

    # Bare decorator usage: @recorded_by_proxy_async
    if len(maybe_specs) == 1 and callable(maybe_specs[0]):
        test_func = maybe_specs[0]
        transports = _normalize_transport_specs([(AioHttpTransport, "send")])
        return _make_proxy_decorator_async(transports)(test_func)

    # Parameterized decorator usage: @recorded_by_proxy_async(...)
    transports = _normalize_transport_specs(maybe_specs or [(AioHttpTransport, "send")])
    return _make_proxy_decorator_async(transports)


def _make_proxy_decorator_async(transports):
    def _decorator(test_func):
        @wraps(test_func)
        async def record_wrap(*args, **kwargs):
            # ---- your existing trimming/early-exit logic ----
            trimmed_kwargs = {k: v for k, v in kwargs.items()}
            trim_kwargs_from_test_function(test_func, trimmed_kwargs)

            if is_live_and_not_recording():
                return await test_func(*args, **trimmed_kwargs)

            test_id = get_test_id()
            recording_id, variables = start_record_or_playback(test_id)

            def transform_args_inner(*call_args, **call_kwargs):
                copied_positional_args = list(call_args)
                request = copied_positional_args[1]
                transform_request(request, recording_id)
                return tuple(copied_positional_args), call_kwargs

            def transform_httpx_args_inner(*call_args, **call_kwargs):
                copied_positional_args = list(call_args)
                request = copied_positional_args[1]
                transform_httpx_request(request, recording_id)
                return tuple(copied_positional_args), call_kwargs

            # Build a wrapper factory so each patched method closes over its own original
            def make_combined_call(original_transport_func, is_httpx=False):
                async def combined_call(*call_args, **call_kwargs):
                    if is_httpx:
                        adjusted_args, adjusted_kwargs = transform_httpx_args_inner(*call_args, **call_kwargs)
                        result = await original_transport_func(*adjusted_args, **adjusted_kwargs)
                        restore_httpx_response_url(result)
                    else:
                        adjusted_args, adjusted_kwargs = transform_args_inner(*call_args, **call_kwargs)
                        result = await original_transport_func(*adjusted_args, **adjusted_kwargs)
                        # rewrite request.url to the original upstream for LROs, etc.
                        parsed_result = url_parse.urlparse(result.request.url)
                        upstream_uri = url_parse.urlparse(result.request.headers["x-recording-upstream-base-uri"])
                        upstream_uri_dict = {"scheme": upstream_uri.scheme, "netloc": upstream_uri.netloc}
                        original_target = parsed_result._replace(**upstream_uri_dict).geturl()
                        result.request.url = original_target
                    return result

                return combined_call

            # Patch multiple transports and ensure restoration
            test_variables = None
            test_run = False
            async with AsyncExitStack() as stack:
                originals = []
                # monkeypatch all requested transports
                for owner, name in transports:
                    original = getattr(owner, name)
                    # Check if this is an httpx transport by comparing with httpx transport classes
                    is_httpx_transport = (
                        (AsyncHTTPXTransport is not None and owner is AsyncHTTPXTransport)
                        or (httpx is not None and owner.__module__.startswith("httpx"))
                    )
                    setattr(owner, name, make_combined_call(original, is_httpx=is_httpx_transport))
                    originals.append((owner, name, original))

                try:
                    try:
                        test_variables = await test_func(*args, variables=variables, **trimmed_kwargs)
                        test_run = True
                    except TypeError as error:
                        if "unexpected keyword argument" in str(error) and "variables" in str(error):
                            logger = logging.getLogger()
                            logger.info(
                                "This test can't accept variables as input. "
                                "Accept `**kwargs` and/or a `variables` parameter to use recorded variables."
                            )
                        else:
                            raise

                    if not test_run:
                        test_variables = await test_func(*args, **trimmed_kwargs)

                except ResourceNotFoundError as error:
                    error_body = ContentDecodePolicy.deserialize_from_http_generics(error.response)
                    troubleshoot = "Playback failure -- for help resolving, see https://aka.ms/azsdk/python/test-proxy/troubleshoot."
                    message = error_body.get("message") or error_body.get("Message")
                    error_with_message = ResourceNotFoundError(
                        message=f"{troubleshoot} Error details:\n{message}",
                        response=error.response,
                    )
                    raise error_with_message from error

                finally:
                    # restore in reverse order
                    for owner, name, original in reversed(originals):
                        setattr(owner, name, original)
                    stop_record_or_playback(test_id, recording_id, test_variables)

            return test_variables

        return record_wrap

    return _decorator
