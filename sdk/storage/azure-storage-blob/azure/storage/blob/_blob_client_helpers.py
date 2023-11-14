# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Tuple, TYPE_CHECKING
from urllib.parse import urlparse
from ._shared.base_client import parse_query

if TYPE_CHECKING:
    from urllib.parse import ParseResult

def _parse_url(
    account_url: str,
    container_name: str,
    blob_name: str
) -> Tuple["ParseResult", Any]:
    """Performs initial input validation and returns the parsed URL, SAS token, and path snapshot.

    :param str account_url: The URL to the storage account.
    :param str container_name: The name of the container.
    :param str blob_name: The name of the blob.
    :returns: The parsed URL, SAS token, and path snapshot.
    :rtype: Tuple[ParseResult, Any]
    """
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError as exc:
        raise ValueError("Account URL must be a string.") from exc
    parsed_url = urlparse(account_url.rstrip('/'))

    if not (container_name and blob_name):
        raise ValueError("Please specify a container name and blob name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {account_url}")

    path_snapshot, sas_token = parse_query(parsed_url.query)

    return parsed_url, sas_token, path_snapshot
