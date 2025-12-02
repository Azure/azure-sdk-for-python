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
    RecordedTransport,
    _transform_args,
    _transform_httpx_args,
    get_test_id,
    start_record_or_playback,
    restore_httpx_response_url,
    stop_record_or_playback,
)


def recorded_by_proxy_async(*transports):
    """
    Decorator for recording and playing back test proxy sessions in async tests.

    Args:
        *transports: Which transport(s) to record. Pass one or more comma separated RecordedTransport enum values.
            - No args (default): Record AioHttpTransport.send calls (azure.core).
            - RecordedTransport.AZURE_CORE: Record AioHttpTransport.send calls. Same as the default above.
            - RecordedTransport.HTTPX: Record AsyncHTTPXTransport.handle_async_request calls.
            - RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX: Record both transports.

    Usages:

      from devtools_testutils.aio import recorded_by_proxy_async
      from devtools_testutils import RecordedTransport

      # If your test uses azure.core only network calls (default)
      @recorded_by_proxy_async
      async def test(...): ...

      # Explicitly enable azure.core recordings only (equivalent to the above)
      @recorded_by_proxy_async(RecordedTransport.AZURE_CORE)
      async def test(...): ...

      # If your test uses httpx only for network calls
      @recorded_by_proxy_async(RecordedTransport.HTTPX)
      async def test(...): ...

      # If your test uses both azure.core and httpx for network calls
      @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
      async def test(...): ...
    """

    # Bare decorator usage: @recorded_by_proxy_async
    if len(transports) == 1 and callable(transports[0]):
        test_func = transports[0]
        transport_list = [(AioHttpTransport, "send")]
        return _make_proxy_decorator_async(transport_list)(test_func)

    # Parameterized decorator usage: @recorded_by_proxy_async(...)
    # Determine which transports to use
    transport_list = []

    # If no transports specified, default to azure.core
    transport_set = set(transports) if transports else {RecordedTransport.AZURE_CORE}

    # Add transports based on what's in the set
    for transport in transport_set:
        if transport == RecordedTransport.AZURE_CORE or (
            isinstance(transport, str) and transport == RecordedTransport.AZURE_CORE.value
        ):
            transport_list.append((AioHttpTransport, "send"))
        elif transport == RecordedTransport.HTTPX or (
            isinstance(transport, str) and transport == RecordedTransport.HTTPX.value
        ):
            if AsyncHTTPXTransport is not None:
                transport_list.append((AsyncHTTPXTransport, "handle_async_request"))

    # If still no transports, fall back to azure.core
    if not transport_list:
        transport_list = [(AioHttpTransport, "send")]

    # Return a decorator function that will be applied to the test function
    return lambda test_func: _make_proxy_decorator_async(transport_list)(test_func)


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

            # Build a wrapper factory so each patched method closes over its own original
            def make_combined_call(original_transport_func, is_httpx=False):
                async def combined_call(*call_args, **call_kwargs):
                    if is_httpx:
                        adjusted_args, adjusted_kwargs = _transform_httpx_args(recording_id, *call_args, **call_kwargs)
                        result = await original_transport_func(*adjusted_args, **adjusted_kwargs)
                        restore_httpx_response_url(result)
                    else:
                        adjusted_args, adjusted_kwargs = _transform_args(recording_id, *call_args, **call_kwargs)
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
                    is_httpx_transport = (AsyncHTTPXTransport is not None and owner is AsyncHTTPXTransport) or (
                        httpx is not None and owner.__module__.startswith("httpx")
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
