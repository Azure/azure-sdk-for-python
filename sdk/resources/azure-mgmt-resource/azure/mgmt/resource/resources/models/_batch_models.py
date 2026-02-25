# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
from azure.core import CaseInsensitiveEnumMeta
from .._utils import serialization as _serialization

if TYPE_CHECKING:
    from .. import models as _models


class BatchRequest(_serialization.Model):
    """Batch request definition.

    :ivar http_method: The HTTP method for the request. Required.
    :vartype http_method: str
    :ivar relative_url: The relative URL for the request. Required.
    :vartype relative_url: str
    :ivar name: Optional name to identify this request within the batch. Optional.
    :vartype name: str
    :ivar body: The request body (for PUT/PATCH/POST operations). Optional.
    :vartype body: any
    :ivar headers: Request headers. Optional.
    :vartype headers: dict[str, str]
    :ivar depends_on: List of request names that this request depends on. Optional.
    :vartype depends_on: list[str]
    """

    _attribute_map = {
        "http_method": {"key": "httpMethod", "type": "str"},
        "relative_url": {"key": "relativeUrl", "type": "str"},
        "name": {"key": "name", "type": "str"},
        "body": {"key": "body", "type": "object"},
        "headers": {"key": "headers", "type": "{str}"},
        "depends_on": {"key": "dependsOn", "type": "[str]"},
    }

    def __init__(
        self,
        *,
        http_method: str,
        relative_url: str,
        name: Optional[str] = None,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        depends_on: Optional[List[str]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword http_method: The HTTP method for the request. Required.
        :paramtype http_method: str
        :keyword relative_url: The relative URL for the request. Required.
        :paramtype relative_url: str
        :keyword name: Optional name to identify this request within the batch. Optional.
        :paramtype name: str
        :keyword body: The request body (for PUT/PATCH/POST operations). Optional.
        :paramtype body: any
        :keyword headers: Request headers. Optional.
        :paramtype headers: dict[str, str]
        :keyword depends_on: List of request names that this request depends on. Optional.
        :paramtype depends_on: list[str]
        """
        super().__init__(**kwargs)
        self.http_method = http_method
        self.relative_url = relative_url
        self.name = name
        self.body = body
        self.headers = headers
        self.depends_on = depends_on


class BatchRequests(_serialization.Model):
    """Collection of batch requests.

    :ivar requests: The batch requests to execute. Required.
    :vartype requests: list[~azure.mgmt.resource.models.BatchRequest]
    """

    _attribute_map = {
        "requests": {"key": "requests", "type": "[BatchRequest]"},
    }

    def __init__(self, *, requests: List["_models.BatchRequest"], **kwargs: Any) -> None:
        """
        :keyword requests: The batch requests to execute. Required.
        :paramtype requests: list[~azure.mgmt.resource.models.BatchRequest]
        """
        super().__init__(**kwargs)
        self.requests = requests


class BatchResponseItem(_serialization.Model):
    """Individual response within a batch response.

    :ivar name: The name of the request (if provided in the batch request). Optional.
    :vartype name: str
    :ivar status_code: The HTTP status code of the response. Required.
    :vartype status_code: int
    :ivar status: The status of the batch response item. Required.
    :vartype status: str or ~azure.mgmt.resource.models.BatchResponseStatus
    :ivar body: The response body. Optional.
    :vartype body: any
    :ivar headers: Response headers. Optional.
    :vartype headers: dict[str, str]
    """

    _attribute_map = {
        "name": {"key": "name", "type": "str"},
        "status_code": {"key": "statusCode", "type": "int"},
        "status": {"key": "status", "type": "str"},
        "body": {"key": "body", "type": "object"},
        "headers": {"key": "headers", "type": "{str}"},
    }

    def __init__(
        self,
        *,
        status_code: int,
        status: Union[str, "BatchResponseStatus"],
        name: Optional[str] = None,
        body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
    ) -> None:
        """
        :keyword status_code: The HTTP status code of the response. Required.
        :paramtype status_code: int
        :keyword status: The status of the batch response item. Required.
        :paramtype status: str or ~azure.mgmt.resource.models.BatchResponseStatus
        :keyword name: The name of the request (if provided in the batch request). Optional.
        :paramtype name: str
        :keyword body: The response body. Optional.
        :paramtype body: any
        :keyword headers: Response headers. Optional.
        :paramtype headers: dict[str, str]
        """
        super().__init__(**kwargs)
        self.name = name
        self.status_code = status_code
        self.status = status
        self.body = body
        self.headers = headers


class BatchResponse(_serialization.Model):
    """Batch operation response.

    :ivar responses: Individual responses within the batch. Required.
    :vartype responses: list[~azure.mgmt.resource.models.BatchResponseItem]
    """

    _attribute_map = {
        "responses": {"key": "responses", "type": "[BatchResponseItem]"},
    }

    def __init__(self, *, responses: List["_models.BatchResponseItem"], **kwargs: Any) -> None:
        """
        :keyword responses: Individual responses within the batch. Required.
        :paramtype responses: list[~azure.mgmt.resource.models.BatchResponseItem]
        """
        super().__init__(**kwargs)
        self.responses = responses


class BatchResponseStatus(str, metaclass=CaseInsensitiveEnumMeta):
    """Batch response status enumeration.

    :cvar SUCCEEDED: The request succeeded.
    :vartype SUCCEEDED: str
    :cvar FAILED: The request failed.
    :vartype FAILED: str
    :cvar VALIDATION_FAILED: The request was processed but failed validation.
    :vartype VALIDATION_FAILED: str
    :cvar SKIPPED: The request was skipped due to dependency failure.
    :vartype SKIPPED: str
    """

    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    VALIDATION_FAILED = "ValidationFailed"
    SKIPPED = "Skipped"