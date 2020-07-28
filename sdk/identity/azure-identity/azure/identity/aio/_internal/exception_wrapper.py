# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from azure.core.exceptions import ClientAuthenticationError


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
