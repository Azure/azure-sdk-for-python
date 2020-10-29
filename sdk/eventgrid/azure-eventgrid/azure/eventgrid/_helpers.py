# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, Any
import hashlib
import hmac
import base64
import six
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote # type: ignore

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from ._shared_access_signature_credential import EventGridSharedAccessSignatureCredential
from ._signature_credential_policy import EventGridSharedAccessSignatureCredentialPolicy
from . import _constants as constants

if TYPE_CHECKING:
    from datetime import datetime

def generate_shared_access_signature(topic_hostname, shared_access_key, expiration_date_utc, **kwargs):
    # type: (str, str, datetime, Any) -> str
    """ Helper method to generate shared access signature given hostname, key, and expiration date.
        :param str topic_hostname: The topic endpoint to send the events to.
            Similar to <YOUR-TOPIC-NAME>.<YOUR-REGION-NAME>-1.eventgrid.azure.net
        :param str shared_access_key: The shared access key to be used for generating the token
        :param datetime.datetime expiration_date_utc: The expiration datetime in UTC for the signature.
        :param str api_version: The API Version to include in the signature.
         If not provided, the default API version will be used.
        :rtype: str
    """

    full_topic_hostname = _get_full_topic_hostname(topic_hostname)

    full_topic_hostname = "{}?apiVersion={}".format(
        full_topic_hostname,
        kwargs.get('api_version', None) or constants.DEFAULT_API_VERSION
    )
    encoded_resource = quote(full_topic_hostname, safe=constants.SAFE_ENCODE)
    encoded_expiration_utc = quote(str(expiration_date_utc), safe=constants.SAFE_ENCODE)

    unsigned_sas = "r={}&e={}".format(encoded_resource, encoded_expiration_utc)
    signature = quote(_generate_hmac(shared_access_key, unsigned_sas), safe=constants.SAFE_ENCODE)
    signed_sas = "{}&s={}".format(unsigned_sas, signature)
    return signed_sas

def _get_topic_hostname_only_fqdn(topic_hostname):
    if topic_hostname.startswith('http://'):
        raise ValueError("HTTP is not supported. Only HTTPS is supported.")
    if topic_hostname.startswith('https://'):
        topic_hostname = topic_hostname.replace("https://", "")
    if topic_hostname.endswith("/api/events"):
        topic_hostname = topic_hostname.replace("/api/events", "")

    return topic_hostname

def _get_full_topic_hostname(topic_hostname):
    if topic_hostname.startswith('http://'):
        raise ValueError("HTTP is not supported. Only HTTPS is supported.")
    if not topic_hostname.startswith('https://'):
        topic_hostname = "https://{}".format(topic_hostname)
    if not topic_hostname.endswith("/api/events"):
        topic_hostname = "{}/api/events".format(topic_hostname)

    return topic_hostname

def _generate_hmac(key, message):
    decoded_key = base64.b64decode(key)
    bytes_message = message.encode('ascii')
    hmac_new = hmac.new(decoded_key, bytes_message, hashlib.sha256).digest()

    return base64.b64encode(hmac_new)

def _get_authentication_policy(credential):
    if credential is None:
        raise ValueError("Parameter 'self._credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(credential=credential, name=constants.EVENTGRID_KEY_HEADER)
    if isinstance(credential, EventGridSharedAccessSignatureCredential):
        authentication_policy = EventGridSharedAccessSignatureCredentialPolicy(
            credential=credential,
            name=constants.EVENTGRID_TOKEN_HEADER
        )
    return authentication_policy

def _is_cloud_event(event):
    # type: (Any) -> bool
    required = ('id', 'source', 'specversion', 'type')
    try:
        return all([_ in event for _ in required]) and event['specversion'] == "1.0"
    except TypeError:
        return False

def _eventgrid_data_typecheck(event):
    try:
        data = event.get('data')
    except AttributeError:
        data = event.data

    if isinstance(data, six.binary_type):
        raise TypeError("Data in EventGridEvent cannot be bytes. Please refer to"\
            "https://docs.microsoft.com/en-us/azure/event-grid/event-schema")
