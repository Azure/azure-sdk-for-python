# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging


def log_get_token(logger, class_name):
    """Adds logging around get_token calls.

    :param logging.RootLogger logger: logger instance which will receive messages
    :param str class_name: required for the sake of Python 2.7, which lacks an easy way to get the credential's class
        name from the decorated function
    """

    def decorator(fn):
        qualified_name = class_name + ".get_token"

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                token = fn(*args, **kwargs)
                logger.info("%s succeeded", qualified_name)
                return token
            except Exception as ex:
                logger.warning("%s failed: %s", qualified_name, ex, exc_info=logger.isEnabledFor(logging.DEBUG))
                raise

        return wrapper

    return decorator
