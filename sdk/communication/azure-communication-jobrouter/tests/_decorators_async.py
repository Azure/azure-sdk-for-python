# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio
import functools
from typing import Callable, Any

from azure.core.exceptions import HttpResponseError

from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from devtools_testutils import is_live, is_live_and_not_recording
from azure.communication.jobrouter._shared.utils import parse_connection_str


class RouterPreparersAsync(object):

    @staticmethod
    def before_test_execute_async(
            method_name,  # type: str
            **kwargs  # type: Any
    ):
        def __decorator__(func):
            @functools.wraps(func)
            async def wrapper(self, *args, **kwargs):
                trim_kwargs_from_test_function(func, kwargs)
                first_method = getattr(self, method_name)
                await first_method()
                return await func(self, *args, **kwargs)

            return wrapper

        return __decorator__

    @staticmethod
    def after_test_execute_async(
            method_name,  # type: str
            **kwargs  # type: Any
    ):
        def __decorator__(func):
            @functools.wraps(func)
            async def wrapper(self, *args, **kwargs):
                trim_kwargs_from_test_function(func, kwargs)
                first_method = getattr(self, method_name)
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    raise e
                finally:
                    try:
                        await first_method()
                    except:
                        print("") # Consume exceptions

            return wrapper

        return __decorator__

    @staticmethod
    def router_test_decorator_async(func: Callable[[], object], **kwargs: Any):
        async def wrapper(self, *args, **kwargs):
            if is_live() or is_live_and_not_recording():
                self.connection_string = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
                endpoint, _ = parse_connection_str(self.connection_string)
                self.resource_name = endpoint.split(".")[0]
            else:
                self.connection_string = "endpoint=https://sanitized.communication.azure.net/;accesskey=fake==="
                self.resource_name = "sanitized"

            EXPONENTIAL_BACKOFF = 1.5
            RETRY_COUNT = 0
            MAX_RETRY = 10

            try:
                return await func(self, *args, **kwargs)
            except HttpResponseError as exc:
                if exc.status_code != 429:
                    raise
                print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
                while RETRY_COUNT < MAX_RETRY:
                    if is_live():
                        await asyncio.sleep(EXPONENTIAL_BACKOFF)
                    try:
                        return await func(self, *args, **kwargs)
                    except HttpResponseError as exc:
                        print("Retrying: {} {}".format(RETRY_COUNT, EXPONENTIAL_BACKOFF))
                        EXPONENTIAL_BACKOFF **= 2
                        RETRY_COUNT += 1
                        if exc.status_code != 429 or RETRY_COUNT >= MAX_RETRY:
                            raise

        return wrapper
