# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type,
    TYPE_CHECKING
)

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    CustomHookPolicy
)
from azure.core.exceptions import ResourceNotFoundError

from ._generated import AzureBlobStorage
from ._generated.models import (
    LeaseAccessConditions,
    ModifiedAccessConditions
)

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.exceptions import AzureError
    from .lease import Lease

try:
    _unicode_type = unicode
except NameError:
    _unicode_type = str


def encode_base64(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')

def decode_base64(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    decoded = base64.b64decode(data)
    return decoded.decode('utf-8')


def return_response_headers(response, deserialized, response_headers):
    return response_headers


def create_client(url, pipeline):
    # type: (str, Pipeline) -> AzureBlobStorage
    return AzureBlobStorage(url, pipeline=pipeline)


def create_configuration(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration(**kwargs)
    config.headers_policy = HeadersPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(**kwargs)
    config.retry_policy = RetryPolicy(**kwargs)
    config.redirect_policy = RedirectPolicy(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.custom_hook_policy = CustomHookPolicy(**kwargs)
    return config


def create_pipeline(configuration, credentials, **kwargs):
    # type: (Configuration, Optional[HTTPPolicy], **Any) -> Pipeline
    if kwargs.get('_pipeline'):
        return kwargs['_pipeline']
    config = configuration or create_configuration(**kwargs)
    transport = kwargs.get('transport')  # type: HttpTransport
    if not transport:
        transport = RequestsTransport(config)
    policies = [
        config.user_agent_policy,
        config.headers_policy,
        credentials,
        ContentDecodePolicy(),
        config.redirect_policy,
        config.retry_policy,
        config.logging_policy,
        config.custom_hook_policy,
    ]
    return Pipeline(transport, policies=policies)


def basic_error_map():
    # type: () -> Dict[int, Type]
    return {
        404: ResourceNotFoundError
    }


def process_storage_error(error):
    error_code = error.response.headers.get('x-ms-error-code')
    if error_code:
        error.error_code = error_code
        error.message += "\nErrorCode: {}".format(error_code)
    raise error


def add_metadata_headers(metadata):
    # type: (Dict[str, str]) -> Dict[str, str]
    headers = {}
    if metadata:
        for key, value in metadata.items():
            headers['x-ms-meta-{}'.format(key)] = value
    return headers


def get_access_conditions(lease):
    # type: (Optional[Union[Lease, str]]) -> Union[LeaseAccessConditions, None]
    try:
        lease_id = lease.id
    except AttributeError:
        lease_id = lease
    return LeaseAccessConditions(lease_id=lease_id) if lease_id else None


def get_modification_conditions(
        if_modified_since,  # type: Optional[datetime]
        if_unmodified_since,  # type: Optional[datetime]
        if_match,  # type: Optional[str]
        if_none_match  # type: Optional[str]
    ):
    # type: (...) -> Union[ModifiedAccessConditions, None]
    if any([if_modified_since, if_unmodified_since, if_match, if_none_match]):
        return ModifiedAccessConditions(
            if_modified_since=if_modified_since,
            if_unmodified_since=if_unmodified_since,
            if_match=if_match,
            if_none_match=if_none_match
        )
    return None
