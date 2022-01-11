# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import logging

from azure.core.exceptions import ClientAuthenticationError

from ..._internal import within_credential_chain

_LOGGER = logging.getLogger(__name__)


def log_get_token_async(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            token = await fn(*args, **kwargs)
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.INFO, "%s succeeded", fn.__qualname__
            )
            return token
        except Exception as ex:
            _LOGGER.log(
                logging.DEBUG if within_credential_chain.get() else logging.WARNING,
                "%s failed: %s",
                fn.__qualname__,
                ex,
                exc_info=_LOGGER.isEnabledFor(logging.DEBUG),
            )
            raise

    return wrapper


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
