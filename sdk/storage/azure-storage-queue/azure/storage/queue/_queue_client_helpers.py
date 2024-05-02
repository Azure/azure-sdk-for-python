# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING, Union
from urllib.parse import quote, unquote, urlparse
from ._shared.base_client import parse_query

if TYPE_CHECKING:
    from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
    from azure.core.credentials_async import AsyncTokenCredential
    from urllib.parse import ParseResult


def _parse_url(
    account_url: str,
    queue_name: str,
    credential: Optional[Union[str, Dict[str, str], "AzureNamedKeyCredential", "AzureSasCredential", "AsyncTokenCredential", "TokenCredential"]]  # pylint: disable=line-too-long
) -> Tuple["ParseResult", Any]:
    """Performs initial input validation and returns the parsed URL and SAS token.

    :param str account_url: The URL to the storage account.
    :param str queue_name: The name of the queue.
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
    if not queue_name:
        raise ValueError("Please specify a queue name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {parsed_url}")

    _, sas_token = parse_query(parsed_url.query)
    if not sas_token and not credential:
        raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")

    return parsed_url, sas_token

def _format_url(queue_name: Union[bytes, str], hostname: str, scheme: str, query_str: str) -> str:
    """Format the endpoint URL according to the current location mode hostname.

    :param Union[bytes, str] queue_name: The name of the queue.
    :param str hostname: The current location mode hostname.
    :param str scheme: The scheme for the current location mode hostname.
    :param str query_str: The query string of the endpoint URL being formatted.
    :returns: The formatted endpoint URL according to the specified location mode hostname.
    :rtype: str
    """
    if isinstance(queue_name, str):
        queue_name = queue_name.encode('UTF-8')
    else:
        pass
    return (
        f"{scheme}://{hostname}"
        f"/{quote(queue_name)}{query_str}")

def _from_queue_url(queue_url: str) -> Tuple[str, str]:
    """A client to interact with a specific Queue.

    :param str queue_url: The full URI to the queue, including SAS token if used.
    :returns: The parsed out account_url and queue name.
    :rtype: Tuple[str, str]
    """
    try:
        if not queue_url.lower().startswith('http'):
            queue_url = "https://" + queue_url
    except AttributeError as exc:
        raise ValueError("Queue URL must be a string.") from exc
    parsed_url = urlparse(queue_url.rstrip('/'))

    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {queue_url}")

    queue_path = parsed_url.path.lstrip('/').split('/')
    account_path = ""
    if len(queue_path) > 1:
        account_path = "/" + "/".join(queue_path[:-1])
    account_url = (
        f"{parsed_url.scheme}://{parsed_url.netloc.rstrip('/')}"
        f"{account_path}?{parsed_url.query}")
    queue_name = unquote(queue_path[-1])
    if not queue_name:
        raise ValueError("Invalid URL. Please provide a URL with a valid queue name")
    return(account_url, queue_name)
