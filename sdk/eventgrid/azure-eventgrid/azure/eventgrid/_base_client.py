# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Any,
    List,
    Union,
    TYPE_CHECKING
)

from azure.core.pipeline.policies import (
    RequestIdPolicy,
    HeadersPolicy,
    RedirectPolicy,
    RetryPolicy,
    ContentDecodePolicy,
    CustomHookPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy
)
from ._helpers import _get_authentication_policy
from ._policies import CloudEventDistributedTracingPolicy

if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from ._shared_access_signature_credential import EventGridSharedAccessSignatureCredential


class PublisherClientMixin(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self, credential, **kwargs):
        # type: (Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> None
        self._policies = self._policies(credential, **kwargs)

    def _policies(self, credential, **kwargs):
        # type: (Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> List[Any]
        auth_policy = _get_authentication_policy(credential)
        policies = [
            RequestIdPolicy(**kwargs),
            HeadersPolicy(**kwargs),
            UserAgentPolicy(**kwargs),
            ProxyPolicy(**kwargs),
            ContentDecodePolicy(**kwargs),
            RedirectPolicy(**kwargs),
            RetryPolicy(**kwargs),
            auth_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            CloudEventDistributedTracingPolicy(**kwargs),
            HttpLoggingPolicy(**kwargs)
        ]
        return policies
