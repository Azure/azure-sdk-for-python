# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools


class RouterPreparers(object):

    @staticmethod
    def before_test_execute(
            method_name,  # type: str
            **kwargs  # type: Any
    ):
        def __decorator__(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                first_method = getattr(self, method_name)
                first_method()
                return func(self, *args, **kwargs)

            return wrapper

        return __decorator__
