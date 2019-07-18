# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List, Type, Tuple,
    TYPE_CHECKING
)
import base64
import hashlib
import hmac
import logging
from os import fstat
from io import (SEEK_END, SEEK_SET, UnsupportedOperation)

try:
    from urllib.parse import quote, unquote, parse_qs
except ImportError:
    from urlparse import parse_qs  # type: ignore
    from urllib2 import quote, unquote  # type: ignore

import six
import isodate

from azure.core import Configuration
from azure.core.exceptions import raise_with_traceback
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    RedirectPolicy,
    ContentDecodePolicy,
    BearerTokenCredentialPolicy,
    ProxyPolicy)
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceModifiedError,
    ResourceExistsError,
    ClientAuthenticationError,
    DecodeError)

from .constants import STORAGE_OAUTH_SCOPE, SERVICE_HOST_BASE, DEFAULT_SOCKET_TIMEOUT
from .models import LocationMode, StorageErrorCode
from .authentication import SharedKeyCredentialPolicy
from .policies import (
    StorageBlobSettings,
    StorageHeadersPolicy,
    StorageUserAgentPolicy,
    StorageContentValidation,
    StorageRequestHook,
    StorageResponseHook,
    StorageLoggingPolicy,
    StorageHosts,
    QueueMessagePolicy,
    ExponentialRetry)


if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from azure.core.exceptions import AzureError


_LOGGER = logging.getLogger(__name__)


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


class StorageAccountHostsMixin(object):

    def __init__(
            self, parsed_url,  # type: Any
            service, # type: str
            credential=None,  # type: Optional[Any]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        self._location_mode = kwargs.get('_location_mode', LocationMode.PRIMARY)
        self._hosts = kwargs.get('_hosts')
        self.scheme = parsed_url.scheme

        if service not in ['blob', 'queue', 'file']:
            raise ValueError("Invalid service: {}".format(service))
        account = parsed_url.netloc.split(".{}.core.".format(service))
        secondary_hostname = None
        self.credential = format_shared_key_credential(account, credential)
        if self.scheme.lower() != 'https' and hasattr(self.credential, 'get_token'):
            raise ValueError("Token credential is only supported with HTTPS.")
        if hasattr(self.credential, 'account_name'):
            secondary_hostname = "{}-secondary.{}.{}".format(
                self.credential.account_name, service, SERVICE_HOST_BASE)

        if not self._hosts:
            if len(account) > 1:
                secondary_hostname = parsed_url.netloc.replace(
                    account[0],
                    account[0] + '-secondary')
            if kwargs.get('secondary_hostname'):
                secondary_hostname = kwargs['secondary_hostname']
            self._hosts = {
                LocationMode.PRIMARY: parsed_url.netloc,
                LocationMode.SECONDARY: secondary_hostname}

        self.require_encryption = kwargs.get('require_encryption', False)
        self.key_encryption_key = kwargs.get('key_encryption_key')
        self.key_resolver_function = kwargs.get('key_resolver_function')

        self._config, self._pipeline = create_pipeline(self.credential, hosts=self._hosts, **kwargs)

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)

    @property
    def url(self):
        return self._format_url(self._hosts[self._location_mode])

    @property
    def primary_endpoint(self):
        return self._format_url(self._hosts[LocationMode.PRIMARY])

    @property
    def primary_hostname(self):
        return self._hosts[LocationMode.PRIMARY]

    @property
    def secondary_endpoint(self):
        if not self._hosts[LocationMode.SECONDARY]:
            raise ValueError("No secondary host configured.")
        return self._format_url(self._hosts[LocationMode.SECONDARY])

    @property
    def secondary_hostname(self):
        return self._hosts[LocationMode.SECONDARY]

    @property
    def location_mode(self):
        return self._location_mode

    @location_mode.setter
    def location_mode(self, value):
        if self._hosts.get(value):
            self._location_mode = value
            self._client._config.url = self.url  # pylint: disable=protected-access
        else:
            raise ValueError("No host URL for location mode: {}".format(value))

    def _format_query_string(self, sas_token, credential, snapshot=None):
        query_str = "?"
        if snapshot:
            query_str += 'snapshot={}&'.format(self.snapshot)
        if sas_token and not credential:
            query_str += sas_token
        elif is_credential_sastoken(credential):
            query_str += credential.lstrip('?')
            credential = None
        return query_str.rstrip('?&'), credential


def format_shared_key_credential(account, credential):
    if isinstance(credential, six.string_types):
        if len(account) < 2:
            raise ValueError("Unable to determine account name for shared key credential.")
        credential = {
            'account_name': account[0],
            'account_key': credential
        }
    if isinstance(credential, dict):
        if 'account_name' not in credential:
            raise ValueError("Shared key credential missing 'account_name")
        if 'account_key' not in credential:
            raise ValueError("Shared key credential missing 'account_key")
        return SharedKeyCredentialPolicy(**credential)
    return credential


service_connection_params = {
    'blob': {'primary': 'BlobEndpoint', 'secondary': 'BlobSecondaryEndpoint'},
    'queue': {'primary': 'QueueEndpoint', 'secondary': 'QueueSecondaryEndpoint'},
    'file': {'primary': 'FileEndpoint', 'secondary': 'FileSecondaryEndpoint'},
}


def parse_connection_str(conn_str, credential, service):
    conn_str = conn_str.rstrip(';')
    conn_settings = dict([s.split('=', 1) for s in conn_str.split(';')])  # pylint: disable=consider-using-dict-comprehension
    endpoints = service_connection_params[service]
    primary = None
    secondary = None
    if not credential:
        try:
            credential = {
                'account_name': conn_settings['AccountName'],
                'account_key': conn_settings['AccountKey']
            }
        except KeyError:
            credential = conn_settings.get('SharedAccessSignature')
    if endpoints['primary'] in conn_settings:
        primary = conn_settings[endpoints['primary']]
        if endpoints['secondary'] in conn_settings:
            secondary = conn_settings[endpoints['secondary']]
    else:
        if endpoints['secondary'] in conn_settings:
            raise ValueError("Connection string specifies only secondary endpoint.")
        try:
            primary = "{}://{}.{}.{}".format(
                conn_settings['DefaultEndpointsProtocol'],
                conn_settings['AccountName'],
                service,
                conn_settings['EndpointSuffix']
            )
            secondary = "{}-secondary.{}.{}".format(
                conn_settings['AccountName'],
                service,
                conn_settings['EndpointSuffix']
            )
        except KeyError:
            pass

    if not primary:
        try:
            primary = "https://{}.{}.{}".format(
                conn_settings['AccountName'],
                service,
                conn_settings.get('EndpointSuffix', SERVICE_HOST_BASE)
            )
        except KeyError:
            raise ValueError("Connection string missing required connection details.")
    return primary, secondary, credential


def url_quote(url):
    return quote(url)


def url_unquote(url):
    return unquote(url)


def encode_base64(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    encoded = base64.b64encode(data)
    return encoded.decode('utf-8')


def decode_base64(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    decoded = base64.b64decode(data)
    return decoded.decode('utf-8')


def _decode_base64_to_bytes(data):
    if isinstance(data, six.text_type):
        data = data.encode('utf-8')
    return base64.b64decode(data)


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
    return encoded_digest


def serialize_iso(attr):
    """Serialize Datetime object into ISO-8601 formatted string.

    :param Datetime attr: Object to be serialized.
    :rtype: str
    :raises: ValueError if format invalid.
    """
    if not attr:
        return None
    if isinstance(attr, str):
        attr = isodate.parse_datetime(attr)
    try:
        utc = attr.utctimetuple()
        if utc.tm_year > 9999 or utc.tm_year < 1:
            raise OverflowError("Hit max or min date")

        date = "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}".format(
            utc.tm_year, utc.tm_mon, utc.tm_mday,
            utc.tm_hour, utc.tm_min, utc.tm_sec)
        return date + 'Z'
    except (ValueError, OverflowError) as err:
        msg = "Unable to serialize datetime object."
        raise_with_traceback(ValueError, msg, err)
    except AttributeError as err:
        msg = "ISO-8601 object must be valid Datetime object."
        raise_with_traceback(TypeError, msg, err)


def get_length(data):
    length = None
    # Check if object implements the __len__ method, covers most input cases such as bytearray.
    try:
        length = len(data)
    except:  # pylint: disable=bare-except
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


def read_length(data):
    try:
        if hasattr(data, 'read'):
            read_data = b''
            for chunk in iter(lambda: data.read(4096), b""):
                read_data += chunk
            return len(read_data), read_data
        if hasattr(data, '__iter__'):
            read_data = b''
            for chunk in data:
                read_data += chunk
            return len(read_data), read_data
    except:  # pylint: disable=bare-except
        pass
    raise ValueError("Unable to calculate content length, please specify.")


def parse_length_from_content_range(content_range):
    '''
    Parses the blob length from the content range header: bytes 1-3/65537
    '''
    if content_range is None:
        return None

    # First, split in space and take the second half: '1-3/65537'
    # Next, split on slash and take the second half: '65537'
    # Finally, convert to an int: 65537
    return int(content_range.split(' ', 1)[1].split('/', 1)[1])


def validate_and_format_range_headers(
        start_range, end_range, start_range_required=True,
        end_range_required=True, check_content_md5=False, align_to_page=False):
    # If end range is provided, start range must be provided
    if (start_range_required or end_range is not None) and start_range is None:
        raise ValueError("start_range value cannot be None.")
    if end_range_required and end_range is None:
        raise ValueError("end_range value cannot be None.")

    # Page ranges must be 512 aligned
    if align_to_page:
        if start_range is not None and start_range % 512 != 0:
            raise ValueError("Invalid page blob start_range: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(start_range))
        if end_range is not None and end_range % 512 != 511:
            raise ValueError("Invalid page blob end_range: {0}. "
                             "The size must be aligned to a 512-byte boundary.".format(end_range))

    # Format based on whether end_range is present
    range_header = None
    if end_range is not None:
        range_header = 'bytes={0}-{1}'.format(start_range, end_range)
    elif start_range is not None:
        range_header = "bytes={0}-".format(start_range)

    # Content MD5 can only be provided for a complete range less than 4MB in size
    range_validation = None
    if check_content_md5:
        if start_range is None or end_range is None:
            raise ValueError("Both start and end range requied for MD5 content validation.")
        if end_range - start_range > 4 * 1024 * 1024:
            raise ValueError("Getting content MD5 for a range greater than 4MB is not supported.")
        range_validation = 'true'

    return range_header, range_validation


def normalize_headers(headers):
    normalized = {}
    for key, value in headers.items():
        if key.startswith('x-ms-'):
            key = key[5:]
        normalized[key.lower().replace('-', '_')] = value
    return normalized


def return_response_headers(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers)


def return_headers_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return normalize_headers(response_headers), deserialized


def return_context_and_deserialized(response, deserialized, response_headers):  # pylint: disable=unused-argument
    return response.location_mode, deserialized


def create_configuration(**kwargs):
    # type: (**Any) -> Configuration
    config = Configuration(**kwargs)
    config.headers_policy = StorageHeadersPolicy(**kwargs)
    config.user_agent_policy = StorageUserAgentPolicy(**kwargs)
    config.retry_policy = kwargs.get('retry_policy') or ExponentialRetry(**kwargs)
    config.redirect_policy = RedirectPolicy(**kwargs)
    config.logging_policy = StorageLoggingPolicy(**kwargs)
    config.proxy_policy = ProxyPolicy(**kwargs)
    config.blob_settings = StorageBlobSettings(**kwargs)
    return config


def create_pipeline(credential, **kwargs):
    # type: (Any, **Any) -> Tuple[Configuration, Pipeline]
    credential_policy = None
    if hasattr(credential, 'get_token'):
        credential_policy = BearerTokenCredentialPolicy(credential, STORAGE_OAUTH_SCOPE)
    elif isinstance(credential, SharedKeyCredentialPolicy):
        credential_policy = credential
    elif credential is not None:
        raise TypeError("Unsupported credential: {}".format(credential))

    config = kwargs.get('_configuration') or create_configuration(**kwargs)
    if kwargs.get('_pipeline'):
        return config, kwargs['_pipeline']
    transport = kwargs.get('transport')  # type: HttpTransport
    if 'connection_timeout' not in kwargs:
        kwargs['connection_timeout'] = DEFAULT_SOCKET_TIMEOUT
    if not transport:
        transport = RequestsTransport(**kwargs)
    policies = [
        QueueMessagePolicy(),
        config.headers_policy,
        config.user_agent_policy,
        StorageContentValidation(),
        StorageRequestHook(**kwargs),
        credential_policy,
        ContentDecodePolicy(),
        config.redirect_policy,
        StorageHosts(**kwargs),
        config.retry_policy,
        config.logging_policy,
        StorageResponseHook(**kwargs),
    ]
    return config, Pipeline(transport, policies=policies)


def parse_query(query_str):
    sas_values = _QueryStringConstants.to_list()
    parsed_query = {k: v[0] for k, v in parse_qs(query_str).items()}
    sas_params = ["{}={}".format(k, v) for k, v in parsed_query.items() if k in sas_values]
    sas_token = None
    if sas_params:
        sas_token = '&'.join(sas_params)

    return parsed_query.get('snapshot'), sas_token


def is_credential_sastoken(credential):
    if not credential or not isinstance(credential, six.string_types):
        return False

    sas_values = _QueryStringConstants.to_list()
    parsed_query = parse_qs(credential.lstrip('?'))
    if parsed_query and all([k in sas_values for k in parsed_query.keys()]):
        return True
    return False


def add_metadata_headers(metadata):
    headers = {}
    if metadata:
        for key, value in metadata.items():
            headers['x-ms-meta-{}'.format(key)] = value
    return headers


def process_storage_error(storage_error):
    raise_error = HttpResponseError
    error_code = storage_error.response.headers.get('x-ms-error-code')
    error_message = storage_error.message
    additional_data = {}
    try:
        error_body = ContentDecodePolicy.deserialize_from_http_generics(storage_error.response)
        if error_body:
            for info in error_body.iter():
                if info.tag.lower() == 'code':
                    error_code = info.text
                elif info.tag.lower() == 'message':
                    error_message = info.text
                else:
                    additional_data[info.tag] = info.text
    except DecodeError:
        pass

    try:
        if error_code:
            error_code = StorageErrorCode(error_code)
            if error_code in [StorageErrorCode.condition_not_met,
                              StorageErrorCode.blob_overwritten]:
                raise_error = ResourceModifiedError
            if error_code in [StorageErrorCode.invalid_authentication_info,
                              StorageErrorCode.authentication_failed]:
                raise_error = ClientAuthenticationError
            if error_code in [StorageErrorCode.resource_not_found,
                              StorageErrorCode.blob_not_found,
                              StorageErrorCode.queue_not_found,
                              StorageErrorCode.container_not_found]:
                raise_error = ResourceNotFoundError
            if error_code in [StorageErrorCode.account_already_exists,
                              StorageErrorCode.account_being_created,
                              StorageErrorCode.resource_already_exists,
                              StorageErrorCode.resource_type_mismatch,
                              StorageErrorCode.blob_already_exists,
                              StorageErrorCode.queue_already_exists,
                              StorageErrorCode.container_already_exists,
                              StorageErrorCode.container_being_deleted,
                              StorageErrorCode.queue_being_deleted]:
                raise_error = ResourceExistsError
    except ValueError:
        # Got an unknown error code
        pass

    try:
        error_message += "\nErrorCode:{}".format(error_code.value)
    except AttributeError:
        error_message += "\nErrorCode:{}".format(error_code)
    for name, info in additional_data.items():
        error_message += "\n{}:{}".format(name, info)

    error = raise_error(message=error_message, response=storage_error.response)
    error.error_code = error_code
    error.additional_info = additional_data
    raise error
