# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING, Union
from urllib.parse import urlparse
from ._shared.base_client import parse_query

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from urllib.parse import ParseResult


def _parse_url(
    account_url: str,
    credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential", "TokenCredential"]] # pylint: disable=line-too-long
) -> Tuple["ParseResult", Any]:
    """Performs initial input validation and returns the parsed URL and SAS token.

    :param str account_url: The URL to the storage account.
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string,
        an instance of a AzureSasCredential or AzureNamedKeyCredential from azure.core.credentials,
        an account shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the resource URI already contains a SAS token, this will be ignored in favor of an explicit credential
        - except in the case of AzureSasCredential, where the conflicting SAS tokens will raise a ValueError.
        If using an instance of AzureNamedKeyCredential, "name" should be the storage account name, and "key"
        should be the storage account key.
    :type credential:
        ~azure.core.credentials.AzureNamedKeyCredential or
        ~azure.core.credentials.AzureSasCredential or
        ~azure.core.credentials.TokenCredential or
        str or dict[str, str] or None
    :returns: The parsed URL and SAS token.
    :rtype: Tuple[ParseResult, Any]
    """
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip('/'))
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")

    _, sas_token = parse_query(parsed_url.query)
    if not sas_token and not credential:
        raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")

    return parsed_url, sas_token
