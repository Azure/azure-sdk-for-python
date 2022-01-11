# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from azure.mixedreality.authentication import MixedRealityStsClient
from .static_access_token_credential import StaticAccessTokenCredential

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any, Union
    from azure.core.credentials import AccessToken, TokenCredential


def get_mixedreality_credential(account_id, account_domain, endpoint_url, credential, **kwargs):
    # type: (str, str, str, TokenCredential, Any) -> TokenCredential
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

    def __init__(self, account_id, account_domain, endpoint_url, credential, **kwargs):
        # type: (str, str, str, TokenCredential, Any) -> None
        self.stsClient = MixedRealityStsClient(
            account_id=account_id,
            account_domain=account_domain,
            custom_endpoint_url=endpoint_url,
            credential=credential,
            **kwargs)

    def get_token(self, *scopes, **kwargs):  # pylint: disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        return self.stsClient.get_token(**kwargs)
