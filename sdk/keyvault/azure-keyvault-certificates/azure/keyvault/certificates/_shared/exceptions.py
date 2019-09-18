# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
from typing import TYPE_CHECKING

from azure.core.exceptions import DecodeError, ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline.policies import ContentDecodePolicy

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Type
    from azure.core.exceptions import AzureError
    from azure.core.pipeline.transport import HttpResponse


def get_exception_for_key_vault_error(cls, response):
    # type: (Type[AzureError], HttpResponse) -> AzureError
    try:
        body = ContentDecodePolicy.deserialize_from_http_generics(response)
        message = "({}) {}".format(body["error"]["code"], body["error"]["message"])
    except (DecodeError, KeyError):
        # Key Vault error response bodies have the expected shape and should be deserializable.
        # If we somehow land here, we'll take HttpResponse's default message.
        message = None

    return cls(message=message, response=response)


_code_to_core_error = {404: ResourceNotFoundError, 409: ResourceExistsError}

# map status codes to callables returning appropriate azure-core errors
error_map = {
    status_code: functools.partial(get_exception_for_key_vault_error, cls)
    for status_code, cls in _code_to_core_error.items()
}
