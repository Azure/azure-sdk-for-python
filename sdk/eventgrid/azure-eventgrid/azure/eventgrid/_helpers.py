import hashlib
import hmac
import base64
try:
    from urllib.parse import quote
except ImportError:
    from urllib2 import quote # type: ignore
import datetime

from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from ._shared_access_signature_credential import EventGridSharedAccessSignatureCredential
from ._signature_credential_policy import EventGridSharedAccessSignatureCredentialPolicy
from . import _constants as constants

def generate_shared_access_signature(topic_hostname, shared_access_key, expiration_date_utc, **kwargs):
    # type: (str, str, datetime.Datetime, Any) -> str
    """ Helper method to generate shared access signature given hostname, key, and expiration date.
        :param str topic_hostname: The topic endpoint to send the events to.
            Similar to <YOUR-TOPIC-NAME>.<YOUR-REGION-NAME>-1.eventgrid.azure.net
        :param str shared_access_key: The shared access key to be used for generating the token
        :param datetime.datetime expiration_date_utc: The expiration datetime in UTC for the signature.
        :param str api_version: The API Version to include in the signature. If not provided, the default API version will be used.
        :rtype: str
    """

    full_topic_hostname = _get_full_topic_hostname(topic_hostname)

    full_topic_hostname = "{}?apiVersion={}".format(full_topic_hostname, kwargs.get('api_version', None) or constants.DEFAULT_API_VERSION)
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
        authentication_policy = EventGridSharedAccessSignatureCredentialPolicy(credential=credential, name=constants.EVENTGRID_TOKEN_HEADER)
    return authentication_policy
