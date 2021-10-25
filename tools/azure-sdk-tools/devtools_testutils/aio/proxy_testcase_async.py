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
    start_record_or_playback,
    transform_request,
    stop_record_or_playback,
)


def recorded_by_proxy_async(test_func):
    async def record_wrap(*args, **kwargs):
        test_id = get_test_id()
        recording_id, variables = start_record_or_playback(test_id)

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
            test_output = await test_func(*args, **trimmed_kwargs, variables=variables)
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

    return record_wrap
