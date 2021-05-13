import asyncio
import functools
from contextlib import contextmanager

from ..proxy_testcase import (
    get_test_id,
    start_record_or_playback,
    transform_request,
    stop_record_or_playback,
)

from azure.core.pipeline.transport import AsyncioRequestsTransport

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function


@contextmanager
def patch_requests_func_async(request_transform):
    original_func = AsyncioRequestsTransport.send

    async def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = request_transform(*args, **kwargs)
        return await original_func(*adjusted_args, **adjusted_kwargs)

    AsyncioRequestsTransport.send = combined_call
    yield None

    AsyncioRequestsTransport.send = original_func


def run_in_loop(func, *args, **kwargs):
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(
        func(*args, **kwargs)
    )


def RecordedByProxyAsync(func):
    @functools.wraps(func)
    def record_wrap(*args, **kwargs):
        test_id = get_test_id()
        recording_id = start_record_or_playback(test_id)

        def transform_args(*args, **kwargs):
            copied_positional_args = list(args)
            request = copied_positional_args[1]

            # TODO, get the test-proxy server a real SSL certificate. The issue here is that SSL Certificates are
            # normally associated with a domain name. Need to talk to the //SSLAdmin folks (or someone else) and get
            # a recommendation for how to get a valid SSL Cert for localhost
            kwargs["connection_verify"] = False

            transform_request(request, recording_id)

            return tuple(copied_positional_args), kwargs

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        # this ensures that within this scope, we've monkeypatched the send functionality
        with patch_requests_func_async(transform_args):
            # call the modified function.
            try:
                # value = await func(*args, **trimmed_kwargs)
                run_in_loop(func, *args, **kwargs)
            finally:
                stop_record_or_playback(test_id, recording_id)

        return value

    return record_wrap
