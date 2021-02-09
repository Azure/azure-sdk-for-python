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
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from ._signature_credential_policy import EventGridSasCredentialPolicy
from . import _constants as constants

if TYPE_CHECKING:
    from datetime import datetime

def generate_sas(endpoint, shared_access_key, expiration_date_utc, **kwargs):
    # type: (str, str, datetime, Any) -> str
    """ Helper method to generate shared access signature given hostname, key, and expiration date.
        :param str endpoint: The topic endpoint to send the events to.
            Similar to <YOUR-TOPIC-NAME>.<YOUR-REGION-NAME>-1.eventgrid.azure.net
        :param str shared_access_key: The shared access key to be used for generating the token
        :param datetime.datetime expiration_date_utc: The expiration datetime in UTC for the signature.
        :keyword str api_version: The API Version to include in the signature.
         If not provided, the default API version will be used.
        :rtype: str
    """

    full_endpoint = _get_full_endpoint(endpoint)

    full_endpoint = "{}?apiVersion={}".format(
        full_endpoint,
        kwargs.get('api_version', None) or constants.DEFAULT_API_VERSION
    )
    encoded_resource = quote(full_endpoint, safe=constants.SAFE_ENCODE)
    encoded_expiration_utc = quote(str(expiration_date_utc), safe=constants.SAFE_ENCODE)

    unsigned_sas = "r={}&e={}".format(encoded_resource, encoded_expiration_utc)
    signature = quote(_generate_hmac(shared_access_key, unsigned_sas), safe=constants.SAFE_ENCODE)
    signed_sas = "{}&s={}".format(unsigned_sas, signature)
    return signed_sas

def _get_endpoint_only_fqdn(endpoint):
    if endpoint.startswith('http://'):
        raise ValueError("HTTP is not supported. Only HTTPS is supported.")
    if endpoint.startswith('https://'):
        endpoint = endpoint.replace("https://", "")
    if endpoint.endswith("/api/events"):
        endpoint = endpoint.replace("/api/events", "")

    return endpoint

def _get_full_endpoint(endpoint):
    if endpoint.startswith('http://'):
        raise ValueError("HTTP is not supported. Only HTTPS is supported.")
    if not endpoint.startswith('https://'):
        endpoint = "https://{}".format(endpoint)
    if not endpoint.endswith("/api/events"):
        endpoint = "{}/api/events".format(endpoint)

    return endpoint

def _generate_hmac(key, message):
    decoded_key = base64.b64decode(key)
    bytes_message = message.encode('ascii')
    hmac_new = hmac.new(decoded_key, bytes_message, hashlib.sha256).digest()

    return base64.b64encode(hmac_new)

def _get_authentication_policy(credential):
    if credential is None:
        raise ValueError("Parameter 'self._credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        return AzureKeyCredentialPolicy(credential=credential, name=constants.EVENTGRID_KEY_HEADER)
    if isinstance(credential, AzureSasCredential):
        return EventGridSasCredentialPolicy(
            credential=credential,
            name=constants.EVENTGRID_TOKEN_HEADER
        )
    raise ValueError("The provided credential should be an instance of AzureSasCredential or AzureKeyCredential")

def _is_cloud_event(event):
    # type: (Any) -> bool
    required = ('id', 'source', 'specversion', 'type')
    try:
        return all([_ in event for _ in required]) and event['specversion'] == "1.0"
    except TypeError:
        return False

def _is_eventgrid_event(event):
    # type: (Any) -> bool
    required = ('subject', 'eventType', 'data', 'dataVersion', 'id', 'eventTime')
    try:
        return all([prop in event for prop in required])
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
