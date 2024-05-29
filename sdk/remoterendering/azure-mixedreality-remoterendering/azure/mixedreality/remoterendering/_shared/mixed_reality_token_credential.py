# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.credentials import AccessToken, TokenCredential

from azure.mixedreality.authentication import MixedRealityStsClient
from .static_access_token_credential import StaticAccessTokenCredential

def get_mixedreality_credential(account_id: str,
                                account_domain: str,
                                endpoint_url: str,
                                credential: TokenCredential,
                                **kwargs) -> TokenCredential:
    if isinstance(credential, StaticAccessTokenCredential):
        return credential

    return MixedRealityTokenCredential(
        account_id=account_id,
        account_domain=account_domain,
        endpoint_url=endpoint_url,
        credential=credential,
        **kwargs)


class MixedRealityTokenCredential(object):
    """ Represents a token credential that can be used to access a Mixed Reality service.
    This implements the TokenCredential protocol.

    :param str account_id: The Mixed Reality service account identifier.
    :param str endpoint_url: The Mixed Reality STS service endpoint.
    :param TokenCredential credential: The credential used to access the Mixed Reality service.
    """

    def __init__(self, account_id: str,
                 account_domain: str,
                 endpoint_url: str,
                 credential: TokenCredential,
                 **kwargs) -> None:
        self.stsClient = MixedRealityStsClient(
            account_id=account_id,
            account_domain=account_domain,
            custom_endpoint_url=endpoint_url,
            credential=credential,
            **kwargs)

    def get_token(self, *scopes: str, **kwargs) -> AccessToken:  # pylint: disable=unused-argument
        return self.stsClient.get_token(**kwargs)
