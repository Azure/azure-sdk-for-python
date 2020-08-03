import hashlib
import hmac
import base64
from urllib.parse import quote
from . import _constants as constants
import datetime

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
    full_topic_hostname = "https://{}/api/events?apiVersion={}".format(topic_hostname, kwargs.get('api_version', None) or constants.DEFAULT_API_VERSION)
    encoded_resource = quote(full_topic_hostname, safe=constants.SAFE_ENCODE)
    encoded_expiration_utc = quote(str(expiration_date_utc), safe=constants.SAFE_ENCODE)

    unsignedSas = "r={}&e={}".format(encoded_resource, encoded_expiration_utc)
    signature = quote(_hmac(shared_access_key, unsignedSas), safe=constants.SAFE_ENCODE)
    signedSas = "{}&s={}".format(unsignedSas, signature)
    return signedSas

def _hmac(key, message):
    decoded_key = base64.b64decode(key)
    bytes_message = bytes(message, 'ascii')
    hmac_new = hmac.new(decoded_key, bytes_message, hashlib.sha256).digest()

    return base64.b64encode(hmac_new)