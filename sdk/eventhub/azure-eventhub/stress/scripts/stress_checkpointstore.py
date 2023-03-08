# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import random

from azure.core.pipeline.transport import RequestsTransport
from azure.core.exceptions import (
    ServiceRequestTimeoutError,
    ServiceResponseTimeoutError,
    HttpResponseError,

)
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore


def _request_timeout_patch(*args, **kwargs):
    raise ServiceRequestTimeoutError("Stress checkpoint store request error.")


def _response_timeout_patch(*args, **kwargs):
    raise ServiceResponseTimeoutError("Stress checkpoint store response error.")


def _response_error_patch(*args, **kwargs):
    raise HttpResponseError("Stress checkpoint store HTTP status error.")


class StressTestTransport(RequestsTransport):

    def __init__(self, **kwargs) -> None:
        self.request_latency = kwargs.pop('request_latency', 0)
        request_patch = kwargs.pop('request_patch', None)
        if request_patch == 'request_timeout':
            self.request_patch = _request_timeout_patch
        elif request_patch == 'response_timeout':
            self.request_patch = _response_timeout_patch
        elif request_patch == 'response_error':
            self.request_patch = _response_error_patch
        else:
            self.request_patch = request_patch
        self.patch_frequency = kwargs.pop('patch_frequency', 0.2)
        super().__init__(**kwargs)

    def send(self, request, **kwargs):
        time.sleep(self.request_latency)
        if self.request_patch and random.random() <= self.patch_frequency:
            return self.request_patch(request, **kwargs)
        return super().send(request, **kwargs)


class StressTestCheckpointStore(BlobCheckpointStore):
    """This checkpoint store is intended to be a wrapper around the BlobCheckpointStore to allow injecting
    request latency and network errors.

    :param str account_url:
        The URI to the storage account.
    :param container_name:
        The name of the container for the blob.
    :type container_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :keyword int request_latency: The number of seconds to sleep before sending the outgoing request. The
        default value is 0 (i.e. no delay)
    :keyword request_patch: Replace the service request with injected behaviour. This can be one of a number of
        supported strings for typical errors or a Callable that accepts the request object and kwargs 
        and returns an HttpResponse object. This patch will be applied at random to approx 20% of requests.
        Supported string values are 'request_timeout', 'response_timeout' and 'response_error'.
    :keyword str api_version:
            The Storage API version to use for requests. Default value is '2019-07-07'.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.

    """

    def __init__(
            self,
            blob_account_url: str,
            container_name: str,
            credential=None,
            *,
            request_latency = 0,
            request_patch = None,
            **kwargs) -> None:
        transport = StressTestTransport(
            request_latency=request_latency,
            request_patch=request_patch,
            **kwargs
        )
        super().__init__(
            blob_account_url,
            container_name,
            credential=credential,
            transport=transport,
            **kwargs
        )
