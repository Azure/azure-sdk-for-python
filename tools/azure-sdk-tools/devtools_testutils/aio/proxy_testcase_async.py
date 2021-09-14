# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging

from azure.core.pipeline.transport import AioHttpTransport

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from ..proxy_testcase import (
    get_test_id,
    set_bodiless_matcher,
    start_record_or_playback,
    transform_request,
    stop_record_or_playback,
)


async def run_wrapped_test(test_func, *args, **kwargs):
    test_id = get_test_id()
    recording_id, variables = start_record_or_playback(test_id)
    if kwargs.pop("bodiless", False):
        set_bodiless_matcher(recording_id)

    def transform_args(*args, **kwargs):
        copied_positional_args = list(args)
        request = copied_positional_args[1]

        transform_request(request, recording_id)

        return tuple(copied_positional_args), kwargs

    trimmed_kwargs = {k: v for k, v in kwargs.items()}
    trim_kwargs_from_test_function(test_func, trimmed_kwargs)

    original_transport_func = AioHttpTransport.send

    async def combined_call(*args, **kwargs):
        adjusted_args, adjusted_kwargs = transform_args(*args, **kwargs)
        return await original_transport_func(*adjusted_args, **adjusted_kwargs)

    AioHttpTransport.send = combined_call

    # call the modified function
    # we define test_output before invoking the test so the variable is defined in case of an exception
    test_output = None
    try:
        test_output = await test_func(*args, variables=variables, **trimmed_kwargs)
    except TypeError:
        logger = logging.getLogger()
        logger.info(
            "This test can't accept variables as input. The test method should accept `**kwargs` and/or a "
            "`variables` parameter to make use of recorded test variables."
        )
        test_output = await test_func(*args, **trimmed_kwargs)
    finally:
        AioHttpTransport.send = original_transport_func
        stop_record_or_playback(test_id, recording_id, test_output)

    return test_output


def recorded_by_proxy_async(test_func):
    """Decorator that redirects network requests to target the azure-sdk-tools test proxy. Use with recorded tests.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    async def record_wrap(*args, **kwargs):
        return await run_wrapped_test(test_func, *args, **kwargs)

    return record_wrap


def recorded_without_body_matching_async(test_func):
    """Decorator that redirects network requests to target the test proxy, and disables body matching in playback tests.

    For more details and usage examples, refer to
    https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/test_proxy_migration_guide.md
    """

    async def record_wrap(*args, **kwargs):
        return await run_wrapped_test(test_func, *args, bodiless=True, **kwargs)

    return record_wrap
