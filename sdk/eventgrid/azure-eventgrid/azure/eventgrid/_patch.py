# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
import base64
import hmac
import hashlib
from urllib.parse import quote

DEFAULT_EVENTGRID_SCOPE = "https://eventgrid.azure.net/.default"
EVENTGRID_KEY_HEADER = "aeg-sas-key"
EVENTGRID_TOKEN_HEADER = "aeg-sas-token"
DEFAULT_API_VERSION = "2018-01-01"
SAFE_ENCODE = "~()*!.'"

def _generate_hmac(key, message):
    decoded_key = base64.b64decode(key)
    bytes_message = message.encode("ascii")
    hmac_new = hmac.new(decoded_key, bytes_message, hashlib.sha256).digest()

    return base64.b64encode(hmac_new)

def generate_sas(endpoint, shared_access_key, expiration_date_utc, **kwargs):
    # type: (str, str, datetime, Any) -> str
    """Helper method to generate shared access signature given hostname, key, and expiration date.
    :param str endpoint: The topic endpoint to send the events to.
        Similar to <YOUR-TOPIC-NAME>.<YOUR-REGION-NAME>-1.eventgrid.azure.net
    :param str shared_access_key: The shared access key to be used for generating the token
    :param datetime.datetime expiration_date_utc: The expiration datetime in UTC for the signature.
    :keyword str api_version: The API Version to include in the signature.
     If not provided, the default API version will be used.
    :return: A shared access signature string.
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
        endpoint, kwargs.get("api_version", DEFAULT_API_VERSION)
    )
    encoded_resource = quote(full_endpoint, safe=SAFE_ENCODE)
    encoded_expiration_utc = quote(str(expiration_date_utc), safe=SAFE_ENCODE)

    unsigned_sas = "r={}&e={}".format(encoded_resource, encoded_expiration_utc)
    signature = quote(
        _generate_hmac(shared_access_key, unsigned_sas), safe=SAFE_ENCODE
    )
    signed_sas = "{}&s={}".format(unsigned_sas, signature)
    return signed_sas

__all__: List[str] = [
    "generate_sas"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
