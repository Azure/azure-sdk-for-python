# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging

from azure.core.exceptions import ClientAuthenticationError


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


def wrap_exceptions(fn):
    """Prevents leaking exceptions defined outside azure-core by raising ClientAuthenticationError from them."""

    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            result = await fn(*args, **kwargs)
            return result
        except ClientAuthenticationError:
            raise
        except Exception as ex:  # pylint:disable=broad-except
            auth_error = ClientAuthenticationError(message="Authentication failed: {}".format(ex))
            raise auth_error from ex

    return wrapper
