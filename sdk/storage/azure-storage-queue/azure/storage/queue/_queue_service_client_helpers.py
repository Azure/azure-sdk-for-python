# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from urllib.parse import urlparse
from ._shared.base_client import parse_query

def _parse_url(account_url, credential):
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
