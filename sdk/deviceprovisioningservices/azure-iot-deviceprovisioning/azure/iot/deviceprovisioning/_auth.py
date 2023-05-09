# coding=utf-8
# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


from base64 import b64decode, b64encode
from hashlib import sha256
from hmac import HMAC
from time import time
from urllib.parse import quote_plus, urlencode

from azure.core.credentials import AzureSasCredential
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy


def generate_sas_token(audience: str, policy: str, key: str, expiry: int = 3600) -> str:
    """
    Generate a sas token according to the given audience, policy, key and expiry
    :param str audience: The audience / endpoint to create the SAS token for
    :param str policy: The policy this token represents
    :param str key: The key used to sign this token
    :param int expiry: Token expiry time in milliseconds
    :returns: SAS token as a string literal
    :rtype: str
    """

    encoded_uri = quote_plus(audience)

    ttl = int(time() + expiry)
    sign_key = f"{encoded_uri}\n{ttl}"
    signature = b64encode(
        HMAC(b64decode(key), sign_key.encode("utf-8"), sha256).digest()
    )
    result = {"sr": audience, "sig": signature, "se": str(ttl)}
    if policy:
        result["skn"] = policy
    return "SharedAccessSignature " + urlencode(result)


class SharedKeyCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, endpoint: str, policy_name: str, key: str) -> None:
        self.endpoint = endpoint
        self.policy_name = policy_name
        self.key = key
        super(SharedKeyCredentialPolicy, self).__init__()

    def _add_authorization_header(self, request: PipelineRequest) -> None:
        try:
            auth_string = generate_sas_token(
                audience=self.endpoint, policy=self.policy_name, key=self.key
            )
            request.http_request.headers["Authorization"] = auth_string
        except Exception as ex:
            # TODO - Wrap error as a signing error?
            raise ex

    def on_request(self, request: PipelineRequest) -> None:
        self._add_authorization_header(request=request)


class SasCredentialPolicy(SansIOHTTPPolicy):
    """Adds an authorization header for the provided credential.
    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureSasCredential
    """

    def __init__(
        self, credential: AzureSasCredential, **kwargs
    ):  # pylint: disable=unused-argument
        super(SasCredentialPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Authorization"] = self._credential.signature
