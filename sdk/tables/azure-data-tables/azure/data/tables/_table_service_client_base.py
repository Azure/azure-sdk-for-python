# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from ._base_client import parse_query, StorageAccountHostsMixin


class TableServiceClientBase(StorageAccountHostsMixin):
    """:ivar str account_name: Name of the storage account (Cosmos or Azure)
    Create TableServiceClientBase class for sync and async code.

    :param account_url:
        A account_url url to an Azure Storage account.
    :type service: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token, or the connection string already has shared
        access key values. The value can be a SAS token string or, an account shared access
        key.
    :type credential: str
    :returns: None
    """

    def __init__(
        self,
        account_url,  # type: Any
        service,  # type: str
        credential=None,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        try:
            if not account_url.lower().startswith("http"):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip("/"))
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(account_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                "You need to provide either a SAS token or an account shared key to authenticate."
            )
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableServiceClientBase, self).__init__(
            parsed_url, service=service, credential=credential, **kwargs
        )

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)
