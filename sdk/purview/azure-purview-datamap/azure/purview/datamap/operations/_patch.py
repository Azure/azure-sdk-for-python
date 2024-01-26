# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ._operations import EntityOperations as EntityOperationsGenerated
import sys
from typing import Any, Dict, List, Optional

from msrest import Serializer

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.rest import HttpRequest

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


def build_entity_import_business_metadata_request(
    files: Optional[Dict[str, Any]] = None, content: Any = None, **kwargs: Any
) -> HttpRequest:
    content_type: Optional[str] = kwargs.pop("content_type", None)

    accept = "application/json"
    # Construct URL
    _url = "/atlas/v2/entity/businessmetadata/import"

    # Construct headers
    _header_parameters: Dict[str, Any] = kwargs.pop("headers", {})
    if content_type is not None:
        _header_parameters["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _header_parameters["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, headers=_header_parameters, files=files, content=content, **kwargs)



class EntityOperations(EntityOperationsGenerated):
    def import_business_metadata(self, *args, **kwargs) -> JSON:
        _headers = kwargs.pop("headers", {}) or {}
        _params = kwargs.pop("params", {}) or {}

        request = build_entity_import_business_metadata_request(
            headers=_headers,
            params=_params,
        )
        path_format_arguments = {
            "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, "str", skip_quote=True),
        }
        request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

        pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=True, **kwargs
        )
        response = pipeline_response.http_response

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }

        if response.status_code not in [200]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        deserialized = response
        return deserialized


__all__: List[str] = [
    "EntityOperations",
]  # Add all objects you want publicly available to users at this package level
