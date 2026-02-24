# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, List, Optional
from azure.core import CaseInsensitiveEnumMeta


class BatchRequest:
    """The specification for one request that will be part of a larger batch.

    All required parameters must be populated in order to send to Azure.

    :ivar content: The content of the HTTP request. Required.
    :vartype content: any
    :ivar dependent_on: Other requests in the batch that this request depends on. Optional.
    :vartype dependent_on: list[str]
    :ivar headers: The HTTP headers for the request. Optional.
    :vartype headers: dict[str, str]
    :ivar http_method: The HTTP method of the request, such as GET, PUT, POST, or DELETE.
     Required.
    :vartype http_method: str
    :ivar name: A unique name for the request, which can be used to reference it from other
     requests in the batch. Required.
    :vartype name: str
    :ivar uri: The URI of the request (without the hostname). This is often the path portion of
     the URI. Required.
    :vartype uri: str
    """

    def __init__(
        self,
        *,
        content: Any,
        http_method: str,
        name: str,
        uri: str,
        dependent_on: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        self.content = content
        self.dependent_on = dependent_on
        self.headers = headers
        self.http_method = http_method
        self.name = name
        self.uri = uri


class BatchRequests:
    """The batch API entity definition.

    All required parameters must be populated in order to send to Azure.

    :ivar requests: Specifications for all of the requests that will be invoked as part of the
     batch. Required.
    :vartype requests: list[~azure.mgmt.resource.models.BatchRequest]
    """

    def __init__(self, *, requests: List["BatchRequest"], **kwargs):
        self.requests = requests


class BatchResponse:
    """An individual response from a request that was invoked as part of a batch.

    :ivar content: The content of the HTTP response.
    :vartype content: any
    :ivar headers: The HTTP response headers.
    :vartype headers: dict[str, str]
    :ivar http_status_code: The HTTP status code returned for the individual request.
    :vartype http_status_code: int
    :ivar name: The name of the request.
    :vartype name: str
    """

    def __init__(
        self,
        *,
        content: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        http_status_code: Optional[int] = None,
        name: Optional[str] = None,
        **kwargs
    ):
        self.content = content
        self.headers = headers
        self.http_status_code = http_status_code
        self.name = name


class BatchResponseStatus:
    """Batch API operation response.

    :ivar completed_requests_count: The number of requests that have been completed.
    :vartype completed_requests_count: int
    :ivar failed_requests_count: The number of requests that have failed.
    :vartype failed_requests_count: int
    :ivar provisioning_state: The provisioning state of the batch operation.
    :vartype provisioning_state: str or ~azure.mgmt.resource.models.ProvisioningState
    :ivar responses: The individual responses for each request in the batch.
    :vartype responses: list[~azure.mgmt.resource.models.BatchResponse]
    :ivar total_requests_count: The total number of requests submitted in the batch.
    :vartype total_requests_count: int
    """

    def __init__(
        self,
        *,
        completed_requests_count: Optional[int] = None,
        failed_requests_count: Optional[int] = None,
        provisioning_state: Optional[str] = None,
        responses: Optional[List["BatchResponse"]] = None,
        total_requests_count: Optional[int] = None,
        **kwargs
    ):
        self.completed_requests_count = completed_requests_count
        self.failed_requests_count = failed_requests_count
        self.provisioning_state = provisioning_state
        self.responses = responses
        self.total_requests_count = total_requests_count


class BatchProvisioningState(str, metaclass=CaseInsensitiveEnumMeta):
    """The provisioning state for batch operations.

    :cvar ACCEPTED: Batch request has been accepted.
    :vartype ACCEPTED: str
    :cvar CANCELED: Batch processing was canceled.
    :vartype CANCELED: str
    :cvar FAILED: Batch processing failed.
    :vartype FAILED: str
    :cvar RUNNING: Batch processing is ongoing.
    :vartype RUNNING: str
    :cvar SUCCEEDED: Batch processing succeeded.
    :vartype SUCCEEDED: str
    """

    ACCEPTED = "Accepted"
    CANCELED = "Canceled"
    FAILED = "Failed"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"