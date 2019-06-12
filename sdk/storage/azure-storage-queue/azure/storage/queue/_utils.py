# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type,
    TYPE_CHECKING
)

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from .authentication import SharedKeyCredentials
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy,
    CustomHookPolicy
)

from ._policies import (
    StorageBlobSettings,
    StorageHeadersPolicy,
    StorageContentValidation,
    StorageSecondaryAccount)
from ._generated import AzureQueueStorage

if TYPE_CHECKING:
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy


_LOGGER = logging.getLogger(__name__)


def create_client(url, pipeline):
    # type: (str, Pipeline) -> AzureQueueStorage
    return AzureQueueStorage(url, pipeline=pipeline)

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
    config.queue_settings = StorageQueueSettings(**kwargs)
    return config

#TODO: duplicate from blob
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

def parse_connection_str(conn_str, credentials=None):
    conn_settings = dict([s.split('=', 1) for s in conn_str.split(';')])
    try:
        account_url = "{}://{}.queue.{}".format(
            conn_settings['DefaultEndpointsProtocol'],
            conn_settings['AccountName'],
            conn_settings['EndpointSuffix']
        )
        creds = credentials or SharedKeyCredentials(
            conn_settings['AccountName'], conn_settings['AccountKey'])
        return account_url, creds
    except KeyError as error:
        raise ValueError("Connection string missing setting: '{}'".format(error.args[0]))

# TODO: duplicate from blob
def is_credential_sastoken(credential):
    if credential or not isinstance(credential, six.string_types):
        return False

    parsed_query = parse_qs(credential)
    if parsed_query and all([k in sas_values for k in parsed_query.keys()]):
        return True
    return False

# TODO: duplicate from blob
def parse_query(query):
    sas_values = _QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = ["{}={}".format(k, v) for k, v in parsed_query.items() if k in sas_values]
    sas_token = None
    if sas_params:
        sas_token = '&'.join(sas_params)
    return parsed_query.get('snapshot'), sas_token

# TODO: duplicate from blob
def process_storage_error(error):
    error.error_code = error.response.headers.get('x-ms-error-code')
    if error.error_code:
        error.message += "\nErrorCode: {}".format(error.error_code)
    raise error

# TODO: duplicate from blob
def basic_error_map():
        # type: () -> Dict[int, Type]
    return {
        404: ResourceNotFoundError
    }

def _sign_string(key, string_to_sign, key_is_base64=True):
    if key_is_base64:
        key = _decode_base64_to_bytes(key)
    else:
        if isinstance(key, six.text_type):
            key = key.encode('utf-8')
    if isinstance(string_to_sign, six.text_type):
        string_to_sign = string_to_sign.encode('utf-8')
    signed_hmac_sha256 = hmac.HMAC(key, string_to_sign, hashlib.sha256)
    digest = signed_hmac_sha256.digest()
    encoded_digest = encode_base64(digest)
    return encoded_diges


class _QueryStringConstants(object):
    SIGNED_SIGNATURE = 'sig'
    SIGNED_PERMISSION = 'sp'
    SIGNED_START = 'st'
    SIGNED_EXPIRY = 'se'
    SIGNED_RESOURCE = 'sr'
    SIGNED_IDENTIFIER = 'si'
    SIGNED_IP = 'sip'
    SIGNED_PROTOCOL = 'spr'
    SIGNED_VERSION = 'sv'
    SIGNED_CACHE_CONTROL = 'rscc'
    SIGNED_CONTENT_DISPOSITION = 'rscd'
    SIGNED_CONTENT_ENCODING = 'rsce'
    SIGNED_CONTENT_LANGUAGE = 'rscl'
    SIGNED_CONTENT_TYPE = 'rsct'
    START_PK = 'spk'
    START_RK = 'srk'
    END_PK = 'epk'
    END_RK = 'erk'
    SIGNED_RESOURCE_TYPES = 'srt'
    SIGNED_SERVICES = 'ss'

    @staticmethod
    def to_list():
        return [
            _QueryStringConstants.SIGNED_SIGNATURE,
            _QueryStringConstants.SIGNED_PERMISSION,
            _QueryStringConstants.SIGNED_START,
            _QueryStringConstants.SIGNED_EXPIRY,
            _QueryStringConstants.SIGNED_RESOURCE,
            _QueryStringConstants.SIGNED_IDENTIFIER,
            _QueryStringConstants.SIGNED_IP,
            _QueryStringConstants.SIGNED_PROTOCOL,
            _QueryStringConstants.SIGNED_VERSION,
            _QueryStringConstants.SIGNED_CACHE_CONTROL,
            _QueryStringConstants.SIGNED_CONTENT_DISPOSITION,
            _QueryStringConstants.SIGNED_CONTENT_ENCODING,
            _QueryStringConstants.SIGNED_CONTENT_LANGUAGE,
            _QueryStringConstants.SIGNED_CONTENT_TYPE,
            _QueryStringConstants.START_PK,
            _QueryStringConstants.START_RK,
            _QueryStringConstants.END_PK,
            _QueryStringConstants.END_RK,
            _QueryStringConstants.SIGNED_RESOURCE_TYPES,
            _QueryStringConstants.SIGNED_SERVICES,
        ]
