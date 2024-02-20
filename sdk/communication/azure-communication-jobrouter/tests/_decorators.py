# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
from typing import Callable, Any

from devtools_testutils import is_live, is_live_and_not_recording
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function
from azure.communication.jobrouter._shared.utils import parse_connection_str


class RouterPreparers(object):

    @staticmethod
    def before_test_execute(
            method_name,  # type: str
            **kwargs  # type: Any
    ):
        def __decorator__(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                trim_kwargs_from_test_function(func, kwargs)
                first_method = getattr(self, method_name)
                first_method()
                return func(self, *args, **kwargs)

            return wrapper

        return __decorator__

    @staticmethod
    def after_test_execute(
            method_name,  # type: str
            **kwargs  # type: Any
    ):
        def __decorator__(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                trim_kwargs_from_test_function(func, kwargs)
                first_method = getattr(self, method_name)
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    raise e
                finally:
                    try:
                        first_method()
                    except:
                        print("") # Consume exceptions

            return wrapper

        return __decorator__

    @staticmethod
    def router_test_decorator(func: Callable[[], object], **kwargs: Any):
        def wrapper(self, *args, **kwargs):
            if is_live() or is_live_and_not_recording():
                self.connection_string = os.getenv('COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING')
                endpoint, _ = parse_connection_str(self.connection_string)
                self.resource_name = endpoint.split(".")[0]
            else:
                self.connection_string = "endpoint=https://sanitized.communication.azure.net/;accesskey=fake==="
                self.resource_name = "sanitized"

            func(self, *args, **kwargs)

        return wrapper
