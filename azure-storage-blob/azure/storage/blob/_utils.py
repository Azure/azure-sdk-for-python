# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import base64
import hashlib
import hmac
import sys
from os import fstat
from io import (BytesIO, IOBase, SEEK_CUR, SEEK_END, SEEK_SET, UnsupportedOperation)
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type,
    TYPE_CHECKING
)
try:
    from urllib.parse import urlparse, quote, unquote
except ImportError:
    from urlparse import urlparse
    from urllib2 import quote, unquote

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    CustomHookPolicy
)
from azure.core.exceptions import ResourceNotFoundError

from .authentication import SharedKeyCredentials
from ._policies import (
    StorageBlobSettings,
    StorageHeadersPolicy,
    StorageContentValidation,
    StorageSecondaryAccount)
from ._generated import AzureBlobStorage
from ._generated.models import (
    LeaseAccessConditions,
    ModifiedAccessConditions,
    SequenceNumberAccessConditions
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

def parse_connection_str(conn_str, credentials):
    conn_settings = dict([s.split('=', 1) for s in conn_str.split(';')])
    try:
        account_url = "{}://{}.blob.{}".format(
            conn_settings['DefaultEndpointsProtocol'],
            conn_settings['AccountName'],
            conn_settings['EndpointSuffix']
        )
        creds = credentials or SharedKeyCredentials(
            conn_settings['AccountName'], conn_settings['AccountKey'])
        return account_url, creds
    except KeyError as error:
        raise ValueError("Connection string missing setting: '{}'".format(error.args[0]))

def url_quote(url):
    return quote(url)


def url_unquote(url):
    return unquote(url)


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


def _decode_base64_to_bytes(data):
    if isinstance(data, _unicode_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, _unicode_type):
            key = key.encode('utf-8')
    if isinstance(string_to_sign, _unicode_type):
        string_to_sign = string_to_sign.encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = encode_base64(digest)
    return encoded_digest


def get_length(data):
    length = None
    # Check if object implements the __len__ method, covers most input cases such as bytearray.
    try:
        length = len(data)
    except:
        pass

    if not length:
        # Check if the stream is a file-like stream object.
        # If so, calculate the size using the file descriptor.
        try:
            fileno = data.fileno()
        except (AttributeError, UnsupportedOperation):
            pass
        else:
            return fstat(fileno).st_size

        # If the stream is seekable and tell() is implemented, calculate the stream size.
        try:
            current_position = data.tell()
            data.seek(0, SEEK_END)
            length = data.tell() - current_position
            data.seek(current_position, SEEK_SET)
        except (AttributeError, UnsupportedOperation):
            pass

    return length


def return_response_headers(response, deserialized, response_headers):
    return response_headers


def create_client(url, pipeline):
    # type: (str, Pipeline) -> AzureBlobStorage
    return AzureBlobStorage(url, pipeline=pipeline)


def create_configuration(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration(**kwargs)
    config.headers_policy = StorageHeadersPolicy(**kwargs)
    config.user_agent_policy = UserAgentPolicy(**kwargs)
    config.retry_policy = RetryPolicy(**kwargs)
    config.redirect_policy = RedirectPolicy(**kwargs)
    config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.custom_hook_policy = CustomHookPolicy(**kwargs)
    config.blob_settings = StorageBlobSettings(**kwargs)
    return config


def create_pipeline(configuration, credentials, **kwargs):
    # type: (Configuration, Optional[HTTPPolicy], **Any) -> Tuple[Configuration, Pipeline]
    config = configuration or create_configuration(**kwargs)
    if kwargs.get('_pipeline'):
        return config, kwargs['_pipeline']
    transport = kwargs.get('transport')  # type: HttpTransport
    if not transport:
        transport = RequestsTransport(config)
    policies = [
        StorageSecondaryAccount(),
        config.user_agent_policy,
        config.headers_policy,
        StorageContentValidation(),
        credentials,
        ContentDecodePolicy(),
        config.redirect_policy,
        config.retry_policy,
        config.logging_policy,
        config.custom_hook_policy,
    ]
    return config, Pipeline(transport, policies=policies)


def basic_error_map():
    # type: () -> Dict[int, Type]
    return {
        404: ResourceNotFoundError
    }


def process_storage_error(error):
    error.error_code = error.response.headers.get('x-ms-error-code')
    if error.error_code:
        error.message += "\nErrorCode: {}".format(error.error_code)
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


def get_sequence_conditions(
        if_sequence_number_lte=None, # type: Optional[int]
        if_sequence_number_lt=None, # type: Optional[int]
        if_sequence_number_eq=None, # type: Optional[int]
    ):
    # type: (...) -> Union[SequenceNumberAccessConditions, None]
    if any([if_sequence_number_lte, if_sequence_number_lt, if_sequence_number_eq]):
        return SequenceNumberAccessConditions(
            if_sequence_number_less_than_or_equal_to=if_sequence_number_lte,
            if_sequence_number_less_than=if_sequence_number_lt,
            if_sequence_number_equal_to=if_sequence_number_eq
        )
    return None


def get_modification_conditions(
        if_modified_since=None,  # type: Optional[datetime]
        if_unmodified_since=None,  # type: Optional[datetime]
        if_match=None,  # type: Optional[str]
        if_none_match=None  # type: Optional[str]
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
