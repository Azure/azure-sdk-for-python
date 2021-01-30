# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse # type: ignore

# pylint: disable=unused-import,ungrouped-imports
from typing import Any, Union

from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline.policies import BearerTokenCredentialPolicy

from .._generated.aio import MixedRealityStsRestClient
from .._generated.models import TokenRequestOptions
from .._version import SDK_MONIKER
from ..shared._authentication_endpoint import construct_endpoint_url
from ..shared._mixedreality_account_key_credential import MixedRealityAccountKeyCredential
from ..utils import _convert_to_access_token, _generate_cv_base

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class MixedRealityStsClient(object):
    """ A client to interact with the Mixed Reality STS service.

    :param str account_id:
        The Mixed Reality service account identifier.
    :param str account_domain:
        The Mixed Reality service account domain.
    :param Union[TokenCredential, AzureKeyCredential] credential:
        The credential used to access the Mixed Reality service.
    """

    def __init__(self,
        account_id: str,
        account_domain: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        **kwargs) -> None:
        if not account_id:
            raise ValueError("account_id can not be None")

        if not account_domain:
            raise ValueError("account_domain can not be None")

        if not credential:
            raise ValueError("credential can not be None")

        self._account_id = account_id
        self._account_domain = account_domain
        self._credential = credential

        endpoint_url = kwargs.pop('endpoint_url', construct_endpoint_url(account_domain))

        try:
            if not endpoint_url.lower().startswith('http'):
                endpoint_url = "https://" + endpoint_url
        except AttributeError:
            raise ValueError("Host URL must be a string")

        parsed_url = urlparse(endpoint_url.rstrip('/'))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(endpoint_url))

        self._endpoint_url = endpoint_url

        if isinstance(credential, AzureKeyCredential):
            credential = MixedRealityAccountKeyCredential(account_id, credential)

        authentication_policy = BearerTokenCredentialPolicy(credential, [endpoint_url + '/.default'])

        self._client = MixedRealityStsRestClient(
            base_url=endpoint_url,
            authentication_policy=authentication_policy,
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @distributed_trace_async
    async def get_token(self, **kwargs) -> AccessToken:
        """
        Retrieve a token from the STS service for the specified account identifier asynchronously.
        """
        token_request_options = TokenRequestOptions()
        token_request_options.client_request_id=_generate_cv_base()

        response = await self._client.get_token(
            self._account_id,
            api_version=None,
            token_request_options=token_request_options,
            **kwargs)
        return _convert_to_access_token(response)

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> "MixedRealityStsClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
