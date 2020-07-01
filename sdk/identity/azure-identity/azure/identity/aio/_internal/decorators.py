# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging


def log_get_token(logger):
    """Adds logging around get_token calls.

    :param logging.RootLogger logger: logger instance which will receive messages
    """

    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                token = await fn(*args, **kwargs)
                logger.info("%s succeeded", fn.__qualname__)
                return token
            except Exception as ex:
                logger.warning("%s failed: %s", fn.__qualname__, ex, exc_info=logger.isEnabledFor(logging.DEBUG))
                raise

        return wrapper

    return decorator
