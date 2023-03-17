# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import defaultdict
import functools
from typing import Optional, Type

from azure.core.exceptions import DecodeError, HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.rest import HttpResponse


def _get_exception_for_key_vault_error(cls: Type[HttpResponseError], response: HttpResponse) -> HttpResponseError:
    """Construct cls (HttpResponseError or subclass thereof) with Key Vault's error message."""

    try:
        body = ContentDecodePolicy.deserialize_from_http_generics(response)
        message: Optional[str] = f"({body['error']['code']}) {body['error']['message']}"
    except (DecodeError, KeyError):
        # Key Vault error response bodies should have the expected shape and be de-serializable.
        # If we somehow land here, we'll take HttpResponse's default message.
        message = None

    return cls(message=message, response=response)


# errors map to HttpResponseError...
_default = functools.partial(_get_exception_for_key_vault_error, HttpResponseError)

# ...unless this mapping specifies another type
_code_to_core_error = {404: ResourceNotFoundError, 409: ResourceExistsError}


class _ErrorMap(defaultdict):
    """A dict whose 'get' method returns a default value.

    defaultdict would be preferable but defaultdict.get returns None for keys having no value
    (azure.core.exceptions.map_error calls error_map.get)
    """

    def get(self, key, value=None):  # pylint:disable=unused-argument
        return self[key]


# map status codes to callables returning appropriate azure-core errors
error_map = _ErrorMap(lambda: _default,
    {
        status_code: functools.partial(_get_exception_for_key_vault_error, cls)
        for status_code, cls in _code_to_core_error.items()
    }
)
