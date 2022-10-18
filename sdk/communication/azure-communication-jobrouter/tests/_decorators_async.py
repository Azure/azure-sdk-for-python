# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import functools
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function


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
                    await first_method()

            return wrapper

        return __decorator__
