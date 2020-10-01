# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Any,
    Union,
    List,
    TYPE_CHECKING
)

from azure.core.pipeline.policies import (
    RequestIdPolicy,
    HeadersPolicy,
    AsyncRedirectPolicy,
    AsyncRetryPolicy,
    ContentDecodePolicy,
    CustomHookPolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
    UserAgentPolicy
)
from ._policies import CloudEventDistributedTracingPolicy
from ._helpers import _get_authentication_policy
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from ._shared_access_signature_credential import EventGridSharedAccessSignatureCredential


class AsyncPublisherClientMixin(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self, credential, **kwargs):
        # type: (Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> None
        self.policies = AsyncPublisherClientMixin._policies(credential, **kwargs)

    @staticmethod
    def _policies(credential, **kwargs):
        # type: (Union[AzureKeyCredential, EventGridSharedAccessSignatureCredential], Any) -> List[Any]
        auth_policy = _get_authentication_policy(credential)
        policies = [
            RequestIdPolicy(**kwargs),
            HeadersPolicy(**kwargs),
            UserAgentPolicy(**kwargs),
            ProxyPolicy(**kwargs),
            ContentDecodePolicy(**kwargs),
            AsyncRedirectPolicy(**kwargs),
            AsyncRetryPolicy(**kwargs),
            auth_policy,
            CustomHookPolicy(**kwargs),
            NetworkTraceLoggingPolicy(**kwargs),
            DistributedTracingPolicy(**kwargs),
            CloudEventDistributedTracingPolicy(),
            HttpLoggingPolicy(**kwargs)
        ]
        return policies
