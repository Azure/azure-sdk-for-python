# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from .._shared.response_handlers import return_headers_and_deserialized
from .base_client import StorageAccountHostsMixin

class TableClientBase(StorageAccountHostsMixin):
    def __init__(
        self, 
        parsed_url, # type: str
        service, # type: str
        credential=None, # type: Union[str,TokenCredential]
        **kwargs # type: Any
    ):
        # type: (...) -> None
        # type: (...) -> None
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
            key, or an instance of a TokenCredentials class from azure.identity.
        :type credential: Union[str,TokenCredential]

        :returns: None
        """

        # _validate_table_name(table_name)

        # try:
        #     if not account_url.lower().startswith('http'):
        #         account_url = "https://" + account_url
        # except AttributeError:
        #     raise ValueError("Account URL must be a string.")
        # parsed_url = urlparse(account_url.rstrip('/'))
        # if not table_name:
        #     raise ValueError("Please specify a table name.")
        # if not parsed_url.netloc:
        #     raise ValueError("Invalid URL: {}".format(parsed_url))

        # _, sas_token = parse_query(parsed_url.query)
        # if not sas_token and not credential:
        #     raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")

        # self.table_name = table_name
        # self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableClientBase, self).__init__(parsed_url, service='table', credential=credential, **kwargs)

        # self._client = AzureTable(self.url, pipeline=self._pipeline)
        # self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)