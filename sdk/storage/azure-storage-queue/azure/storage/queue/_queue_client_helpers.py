# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from datetime import datetime, timezone
from ._generated import AzureQueueStorage
from urllib.parse import urlparse, quote, unquote
from ._shared.base_client import StorageAccountHostsMixin, parse_connection_str, parse_query
from ._message_encoding import NoEncodePolicy, NoDecodePolicy
from ._serialize import get_api_version

def _initialize_client(self, account_url, queue_name, credential, **kwargs):
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

    self.queue_name = queue_name
    self._query_str, credential = self._format_query_string(sas_token, credential)
    loop = kwargs.pop('loop', None)
    StorageAccountHostsMixin.__init__(self, parsed_url, service='queue', credential=credential, loop=loop, **kwargs)

    self.message_encode_policy = kwargs.get('message_encode_policy', None) or NoEncodePolicy()
    self.message_decode_policy = kwargs.get('message_decode_policy', None) or NoDecodePolicy()
    self._client = AzureQueueStorage(self.url, base_url=self.url, pipeline=self._pipeline, loop=loop)
    self._client._config.version = get_api_version(kwargs)  # pylint: disable=protected-access
    self._configure_encryption(kwargs)

def _rfc_1123_to_datetime(rfc_1123: str) -> datetime:
    """Converts an RFC 1123 date string to a UTC datetime.
    """
    if not rfc_1123:
        return None

    return datetime.strptime(rfc_1123, "%a, %d %b %Y %H:%M:%S %Z")

def _filetime_to_datetime(filetime: str) -> datetime:
    """Converts an MS filetime string to a UTC datetime. "0" indicates None.
    If parsing MS Filetime fails, tries RFC 1123 as backup.
    """
    if not filetime:
        return None

    # Try to convert to MS Filetime
    try:
        filetime = int(filetime)
        if filetime == 0:
            return None

        return datetime.fromtimestamp((filetime - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS, tz=timezone.utc)
    except ValueError:
        pass

    # Try RFC 1123 as backup
    return _rfc_1123_to_datetime(filetime)
