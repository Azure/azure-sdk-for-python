from typing import (  # pylint: disable=unused-import
    cast,
    Tuple,
)

from azure.core.pipeline.policies import BearerTokenCredentialPolicy
from ._hmac_credentials_policy import HMACCredentialsPolicy

def parse_connection_str(conn_str):
    # type: (str) -> Tuple[str, str]
    """Parses the connection string to separate fields.

    :param conn_str: The connection string.
    :type conn_str: str
    :returns: Endpoint address and access key.
    :rtype: Tuple[str, str]
    """
    if conn_str is None:
        raise ValueError(
            "Connection string is undefined."
        )
    endpoint = None
    shared_access_key = None
    for element in conn_str.split(";"):
        key, _, value = element.partition("=")
        if key.lower() == "endpoint":
            endpoint = value.rstrip("/")
        elif key.lower() == "accesskey":
            shared_access_key = value
    if not all([endpoint, shared_access_key]):
        raise ValueError(
            "Invalid connection string. You can get the connection string from your resource page in the Azure Portal. "
            "The format should be as follows: endpoint=https://<ResourceUrl>/;accesskey=<KeyValue>"
        )
    left_slash_pos = cast(str, endpoint).find("//")
    if left_slash_pos != -1:
        host = cast(str, endpoint)[left_slash_pos + 2:]
    else:
        host = str(endpoint)

    return host, str(shared_access_key)

def get_authentication_policy(
        endpoint, # type: str
        credential, # type: CommunicationTokenCredential or str
        is_async=False, # type: bool
):
    # type: (...) -> BearerTokenCredentialPolicy or HMACCredentialsPolicy
    """Returns the correct authentication policy based
    on which credential is being passed.

    :param endpoint: The endpoint to which we are authenticating to.
    :type endpoint: str
    :param credential: The credential we use to authenticate to the service
    :type credential: TokenCredential or str
    :param isAsync: For async clients there is a need to decode the url
    :type bool: isAsync or str
    :rtype: ~azure.core.pipeline.policies.BearerTokenCredentialPolicy
    ~HMACCredentialsPolicy
    """

    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if hasattr(credential, "get_token"):
        return BearerTokenCredentialPolicy(
            credential, "https://communication.azure.com//.default")
    if isinstance(credential, str):
        return HMACCredentialsPolicy(endpoint, credential, decode_url=is_async)

    raise TypeError("Unsupported credential: {}. Use an access token string to use HMACCredentialsPolicy"
                    "or a token credential from azure.identity".format(type(credential)))
