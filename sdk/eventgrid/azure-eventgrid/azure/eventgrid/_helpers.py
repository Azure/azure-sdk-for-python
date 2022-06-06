# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import TYPE_CHECKING, Any
import json
import hashlib
import hmac
import base64
import six

try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote  # type: ignore

from msrest import Serializer
from azure.core.exceptions import raise_with_traceback
from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, BearerTokenCredentialPolicy
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from ._signature_credential_policy import EventGridSasCredentialPolicy
from . import _constants as constants

from ._generated.models import (
    CloudEvent as InternalCloudEvent,
)

if TYPE_CHECKING:
    from datetime import datetime

def generate_sas(endpoint, shared_access_key, expiration_date_utc, **kwargs):
    # type: (str, str, datetime, Any) -> str
    """Helper method to generate shared access signature given hostname, key, and expiration date.
    :param str endpoint: The topic endpoint to send the events to.
        Similar to <YOUR-TOPIC-NAME>.<YOUR-REGION-NAME>-1.eventgrid.azure.net
    :param str shared_access_key: The shared access key to be used for generating the token
    :param datetime.datetime expiration_date_utc: The expiration datetime in UTC for the signature.
    :keyword str api_version: The API Version to include in the signature.
     If not provided, the default API version will be used.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/sync_samples/sample_generate_sas.py
            :start-after: [START generate_sas]
            :end-before: [END generate_sas]
            :language: python
            :dedent: 0
            :caption: Generate a shared access signature.
    """
    full_endpoint = "{}?apiVersion={}".format(
        endpoint, kwargs.get("api_version", constants.DEFAULT_API_VERSION)
    )
    encoded_resource = quote(full_endpoint, safe=constants.SAFE_ENCODE)
    encoded_expiration_utc = quote(str(expiration_date_utc), safe=constants.SAFE_ENCODE)

    unsigned_sas = "r={}&e={}".format(encoded_resource, encoded_expiration_utc)
    signature = quote(
        _generate_hmac(shared_access_key, unsigned_sas), safe=constants.SAFE_ENCODE
    )
    signed_sas = "{}&s={}".format(unsigned_sas, signature)
    return signed_sas

def _generate_hmac(key, message):
    decoded_key = base64.b64decode(key)
    bytes_message = message.encode("ascii")
    hmac_new = hmac.new(decoded_key, bytes_message, hashlib.sha256).digest()

    return base64.b64encode(hmac_new)


def _get_authentication_policy(credential, bearer_token_policy=BearerTokenCredentialPolicy):
    if credential is None:
        raise ValueError("Parameter 'self._credential' must not be None.")
    if hasattr(credential, "get_token"):
        return bearer_token_policy(
            credential,
            constants.DEFAULT_EVENTGRID_SCOPE
        )
    if isinstance(credential, AzureKeyCredential):
        return AzureKeyCredentialPolicy(
            credential=credential, name=constants.EVENTGRID_KEY_HEADER
        )
    if isinstance(credential, AzureSasCredential):
        return EventGridSasCredentialPolicy(
            credential=credential, name=constants.EVENTGRID_TOKEN_HEADER
        )
    raise ValueError(
        "The provided credential should be an instance of a TokenCredential, AzureSasCredential or AzureKeyCredential"
    )


def _is_cloud_event(event):
    # type: (Any) -> bool
    required = ("id", "source", "specversion", "type")
    try:
        return all([_ in event for _ in required]) and event["specversion"] == "1.0"
    except TypeError:
        return False

def _is_eventgrid_event(event):
    # type: (Any) -> bool
    required = ("subject", "eventType", "data", "dataVersion", "id", "eventTime")
    try:
        return all([prop in event for prop in required])
    except TypeError:
        return False


def _eventgrid_data_typecheck(event):
    try:
        data = event.get("data")
    except AttributeError:
        data = event.data

    if isinstance(data, six.binary_type):
        raise TypeError(
            "Data in EventGridEvent cannot be bytes. Please refer to"
            "https://docs.microsoft.com/en-us/azure/event-grid/event-schema"
        )

def _cloud_event_to_generated(cloud_event, **kwargs):
    if isinstance(cloud_event.data, six.binary_type):
        data_base64 = cloud_event.data
        data = None
    else:
        data = cloud_event.data
        data_base64 = None
    return InternalCloudEvent(
        id=cloud_event.id,
        source=cloud_event.source,
        type=cloud_event.type,
        specversion=cloud_event.specversion,
        data=data,
        data_base64=data_base64,
        time=cloud_event.time,
        dataschema=cloud_event.dataschema,
        datacontenttype=cloud_event.datacontenttype,
        subject=cloud_event.subject,
        additional_properties=cloud_event.extensions,
        **kwargs
    )

def _from_cncf_events(event):
    """This takes in a CNCF cloudevent and returns a dictionary.
    If cloud events library is not installed, the event is returned back.
    """
    try:
        from cloudevents.http import to_json
        return json.loads(to_json(event))
    except (AttributeError, ImportError):
        # means this is not a CNCF event
        return event
    except Exception as err: # pylint: disable=broad-except
        msg = """Failed to serialize the event. Please ensure your
        CloudEvents is correctly formatted (https://pypi.org/project/cloudevents/)"""
        raise_with_traceback(ValueError, msg, err)


def _build_request(endpoint, content_type, events):
    serialize = Serializer()
    header_parameters = {}  # type: Dict[str, Any]
    header_parameters['Content-Type'] = serialize.header("content_type", content_type, 'str')

    query_parameters = {}  # type: Dict[str, Any]
    query_parameters['api-version'] = serialize.query("api_version", "2018-01-01", 'str')

    body = serialize.body(events, '[object]')
    if body is None:
        data = None
    else:
        data = json.dumps(body)
        header_parameters['Content-Length'] = str(len(data))

    request = HttpRequest(
        method="POST",
        url=endpoint,
        headers=header_parameters,
        data=data
    )
    request.format_parameters(query_parameters)
    return request
