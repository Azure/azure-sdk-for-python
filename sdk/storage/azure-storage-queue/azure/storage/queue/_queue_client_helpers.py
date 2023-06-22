# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from datetime import datetime, timezone
from ._generated import AzureQueueStorage
from ._generated.aio import AzureQueueStorage as AsyncAzureQueueStorage
from urllib.parse import urlparse, quote, unquote
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._message_encoding import NoEncodePolicy, NoDecodePolicy
from ._serialize import get_api_version

def _initialize_client(account_url, queue_name, credential):
    try:
        if not account_url.lower().startswith('http'):
            account_url = "https://" + account_url
    except AttributeError:
        raise ValueError("Account URL must be a string.")
    parsed_url = urlparse(account_url.rstrip('/'))
    if not queue_name:
        raise ValueError("Please specify a queue name.")
    if not parsed_url.netloc:
        raise ValueError(f"Invalid URL: {parsed_url}")

    _, sas_token = parse_query(parsed_url.query)
    if not sas_token and not credential:
        raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")
    
    return parsed_url, sas_token
