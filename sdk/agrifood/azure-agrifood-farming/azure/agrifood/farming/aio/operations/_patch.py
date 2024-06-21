# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import sys
import os
from typing import List, Any
from ._operations import AttachmentsOperations as AttachmentsOperationsGenerated
from ._operations import InsightAttachmentsOperations as InsightAttachmentsOperationsGenerated

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
import datetime
import sys
from typing import Any, Callable, Dict, IO, Iterable, Iterator, List, Optional, TypeVar, Union, cast, overload
import urllib.parse

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.polling.base_polling import LROBasePolling
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict

from ..._serialization import Serializer
from ..._vendor import _format_url_section, raise_if_not_implemented

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

__all__: List[str] = [
    "AttachmentsOperations",
    "InsightAttachmentsOperations",
]  # Add all objects you want publicly available to users at this package level


class AttachmentsOperations(AttachmentsOperationsGenerated):
    @distributed_trace
    async def create_or_update(
        self, party_id: str, attachment_id: str, attachment: JSON, file: IO, **kwargs: Any
    ) -> JSON:
        """Creates or updates a party resource.

        :param party_id: Id of the party resource. Required.
        :type party_id: str
        :param attachment_id: Id of the attachment resource. Required.
        :type attachment_id: str
        :param attachment: Attachment resource payload to create or update. Is a model type. Required.
        :type attachment: JSON
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                attachment = {
                    "resourceId": "str", # Required. Id of the resource the attachment is associated with.
                    "resourceType": "str", # Required. Type of the resource the attachment is associated with,
                      allowed values: Party, Farm, Field, SeasonalField, Boundary, ApplicationData, HarvestData, TillageData, PlantingData, PlantTissueAnalysis
                    "description": "str",  # Optional. Textual description of the resource.
                    "eTag": "str",  # Optional. The ETag value to implement optimistic
                      concurrency.
                    "id": "str",  # Optional. Unique resource ID.
                    "name": "str",  # Optional. Name to identify resource.
                    "source": "str",  # Optional. Source of the resource.
                    "status": "str"  # Optional. Status of the resource.
                }

                # response body for status code(s): 200, 201
                response == {
                    "resourceId": "str", # Required. Id of the resource the attachment is associated with.
                    "resourceType": "str", # Required. Type of the resource the attachment is associated with.
                    "createdDateTime": "2020-02-20 00:00:00",  # Optional. Date-time when
                      resource was created, sample format: yyyy-MM-ddTHH:mm:ssZ.
                    "description": "str",  # Optional. Textual description of the resource.
                    "eTag": "str",  # Optional. The ETag value to implement optimistic
                      concurrency.
                    "id": "str",  # Optional. Unique resource ID.
                    "modifiedDateTime": "2020-02-20 00:00:00",  # Optional. Date-time when
                      resource was last modified, sample format: yyyy-MM-ddTHH:mm:ssZ.
                    "name": "str",  # Optional. Name to identify resource.
                    "source": "str",  # Optional. Source of the resource.
                    "status": "str"  # Optional. Status of the resource.
                }
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = kwargs.pop("content_type", _headers.pop("Content-Type", None))  # type: Optional[str]
        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]

        content_type = content_type or "application/merge-patch+json"

        api_version = (self._config.api_version,)

        content_type = kwargs.pop("content_type", _headers.pop("Content-Type", None))  # type: Optional[str]
        api_version = kwargs.pop("api_version", _params.pop("api-version", "2022-11-01-preview"))  # type: str
        accept = _headers.pop("Accept", "application/json")

        # Construct URL
        _url = "/parties/{partyId}/attachments/{attachmentId}"
        path_format_arguments = {
            "partyId": _SERIALIZER.url("party_id", party_id, "tr"),
            "attachmentId": _SERIALIZER.url("attachment_id", attachment_id, "str"),
        }

        _url = _format_url_section(_url, **path_format_arguments)

        # Construct parameters
        _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

        _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

        request = HttpRequest(
            method="PATCH", url=_url, params=_params, headers=_headers, files={"file": file, **attachment}
        )

        request.url = self._client.format_url(request.url)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if response.status_code == 200:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None
        if response.status_code == 201:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None
        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})
        return cast(JSON, deserialized)


class InsightAttachmentsOperations(InsightAttachmentsOperationsGenerated):
    @distributed_trace
    async def create_or_update(
        self,
        party_id: str,
        model_id: str,
        resource_type: str,
        resource_id: str,
        insight_attachment_id: str,
        insight_attachment: JSON,
        file: IO,
        **kwargs: Any
    ) -> JSON:
        """Creates or updates a party resource.

        :param party_id: Id of the party resource. Required.
        :type party_id: str
        :param model_id: Id of the model. Required.
        :type model_id: str
        :param resource_type: Type of the resource the attachment is associated with,
          allowed values: Party, Farm, Field, SeasonalField, Boundary, ApplicationData, HarvestData, TillageData, PlantingData, PlantTissueAnalysis. Required.
        :type resource_type: str
        :param resource_id: Id of the resource insight attachment is associated with. Required.
        :type resource_id: str
        :param insight_attachment_id: Id of the attachment resource. Required.
        :type insight_attachment_id: str
        :param insight_attachment: Attachment resource payload to create or update. Is a model type. Required.
        :type insight_attachment: JSON
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                insight_attachment = {
                    "insightId": "str", # Required. Id of insight resource.
                    "description": "str",  # Optional. Textual description of the resource.
                    "eTag": "str",  # Optional. The ETag value to implement optimistic
                      concurrency.
                    "name": "str",  # Optional. Name to identify resource.
                    "source": "str",  # Optional. Source of the resource.
                    "status": "str"  # Optional. Status of the resource.
                    "originalFileName": "str", # Optional. File name of the attachment.
                }

                # response body for status code(s): 200, 201
                response == {
                    "insightId": "str", # Required. Id of the insight resource.
                    "modelId": "str", # Required. Id of the model.
                    "resouceType": "str", # Required. Type of the resource the attachment is associated with.
                    "resourceId": "str", # Required. Id of the resource insight attachment is associated with.
                    "partyId": "str", # Required. Id of the party resource.
                    "originalFileName": "str", # Optional. File name of the attachment.
                    "createdDateTime": "2020-02-20 00:00:00",  # Optional. Date-time when
                      resource was created, sample format: yyyy-MM-ddTHH:mm:ssZ.
                    "description": "str",  # Optional. Textual description of the resource.
                    "eTag": "str",  # Optional. The ETag value to implement optimistic
                      concurrency.
                    "id": "str",  # Optional. Unique resource ID.
                    "modifiedDateTime": "2020-02-20 00:00:00",  # Optional. Date-time when
                      resource was last modified, sample format: yyyy-MM-ddTHH:mm:ssZ.
                    "name": "str",  # Optional. Name to identify resource.
                    "source": "str",  # Optional. Source of the resource.
                    "status": "str"  # Optional. Status of the resource.
                }
        """
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type = kwargs.pop("content_type", _headers.pop("Content-Type", None))  # type: Optional[str]
        cls = kwargs.pop("cls", None)  # type: ClsType[JSON]

        content_type = content_type or "application/merge-patch+json"

        api_version = (self._config.api_version,)

        content_type = kwargs.pop("content_type", _headers.pop("Content-Type", None))  # type: Optional[str]
        api_version = kwargs.pop("api_version", _params.pop("api-version", "2022-11-01-preview"))  # type: str
        accept = _headers.pop("Accept", "application/json")

        # Construct URL
        _url = "/parties/{partyId}/models/{modelId}/resource-types/{resourceType}/resources/{resourceId}/insight-attachments/{insightAttachmentId}"
        path_format_arguments = {
            "partyId": _SERIALIZER.url("party_id", party_id, "str"),
            "modelId": _SERIALIZER.url("model_id", model_id, "str"),
            "resourceType": _SERIALIZER.url("resource_type", resource_type, "str"),
            "resourceId": _SERIALIZER.url("resource_id", resource_id, "str"),
            "insightAttachmentId": _SERIALIZER.url("insight_attachment_id", insight_attachment_id, "str"),
        }

        _url = _format_url_section(_url, **path_format_arguments)

        # Construct parameters
        _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

        _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

        request = HttpRequest(
            method="PATCH", url=_url, params=_params, headers=_headers, files={"file": file, **insight_attachment}
        )

        request.url = self._client.format_url(request.url)  # type: ignore

        pipeline_response = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            request, stream=False, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200, 201]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        if response.status_code == 200:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None
        if response.status_code == 201:
            if response.content:
                deserialized = response.json()
            else:
                deserialized = None
        if cls:
            return cls(pipeline_response, cast(JSON, deserialized), {})
        return cast(JSON, deserialized)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
