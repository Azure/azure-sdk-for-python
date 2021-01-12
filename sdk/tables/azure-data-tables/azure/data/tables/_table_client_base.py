# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse  # type: ignore

from ._error import _validate_table_name
from ._base_client import parse_query
from ._base_client import StorageAccountHostsMixin


class TableClientBase(StorageAccountHostsMixin):
    """Create TableClientBase from a Credential.

    :param account_url:
        A url to an Azure Storage account.
    :type account_url: str
    :param table_name: The table name.
    :type table_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token, or the connection string already has shared
        access key values. The value can be a SAS token string, an account shared access
        key.
    :type credential: str

    :returns: None
    """

    def __init__(
        self,
        account_url,  # type: str
        table_name,  # type: str
        credential=None,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        _validate_table_name(table_name)

        try:
            if not account_url.lower().startswith("http"):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip("/"))
        if not table_name:
            raise ValueError("Please specify a table name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(parsed_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError(
                "You need to provide either a SAS token or an account shared key to authenticate."
            )

        self.table_name = table_name
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableClientBase, self).__init__(
            parsed_url, service="table", credential=credential, **kwargs
        )

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def _validate_signed_identifiers(cls, signed_identifiers):
        # type: (...) -> None
        """Validate the number of signed identifiers is less than five

        :param signed_identifiers:
        :type signed_identifiers: dict[str,AccessPolicy]
        """
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
