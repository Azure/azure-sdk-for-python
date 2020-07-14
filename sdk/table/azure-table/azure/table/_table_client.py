# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import Optional, Any

from azure.table import QueryOptions

try:
    from urllib.parse import urlparse, unquote
except ImportError:
    from urlparse import urlparse  # type: ignore
    from urllib2 import unquote  # type: ignore

from azure.core.paging import ItemPaged
from azure.table._deserialize import _convert_to_entity
from azure.table._entity import Entity
from azure.table._generated import AzureTable
from azure.table._generated.models import AccessPolicy, SignedIdentifier, TableProperties
from azure.table._serialize import _get_match_headers, _add_entity_properties
from azure.table._shared.base_client import StorageAccountHostsMixin, parse_query, parse_connection_str

from azure.table._shared.request_handlers import serialize_iso
from azure.table._shared.response_handlers import process_storage_error
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.table._version import VERSION
from azure.core.tracing.decorator import distributed_trace

from ._models import TableEntityPropertiesPaged, UpdateMode

from ._shared.response_handlers import return_headers_and_deserialized


class TableClient(StorageAccountHostsMixin):
    def __init__(
            self, account_url,  # type: str
            table_name,  # type: str
            credential=None,  # type: Union[str,TokenCredential]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Create TableClient from a Credential.

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

        try:
            if not account_url.lower().startswith('http'):
                account_url = "https://" + account_url
        except AttributeError:
            raise ValueError("Account URL must be a string.")
        parsed_url = urlparse(account_url.rstrip('/'))
        if not table_name:
            raise ValueError("Please specify a table name.")
        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(parsed_url))

        _, sas_token = parse_query(parsed_url.query)
        if not sas_token and not credential:
            raise ValueError("You need to provide either a SAS token or an account shared key to authenticate.")

        self.table_name = table_name
        self._query_str, credential = self._format_query_string(sas_token, credential)
        super(TableClient, self).__init__(parsed_url, service='table', credential=credential, **kwargs)

        self._client = AzureTable(self.url, pipeline=self._pipeline)
        self._client._config.version = kwargs.get('api_version', VERSION)  # pylint: disable=protected-access

    def _format_url(self, hostname):
        """Format the endpoint URL according to the current location
        mode hostname.
        """
        return "{}://{}{}".format(self.scheme, hostname, self._query_str)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            table_name,  # type: str
            credential=None,  # type: Union[str,TokenCredential]
            **kwargs  # type: Any
    ):
        # type: (...) -> TableClient
        """Create TableClient from a Connection String.

        :param conn_str:
            A connection string to an Azure Storage account.
        :type conn_str: str
        :param table_name: The table name.
        :type table_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
        :type credential: Union[str,TokenCredential]
        :returns: A table client.
        :rtype: ~azure.table.TableClient
        """
        account_url, secondary, credential = parse_connection_str(
            conn_str, credential, 'table')
        if 'secondary_hostname' not in kwargs:
            kwargs['secondary_hostname'] = secondary
        return cls(account_url, table_name=table_name, credential=credential, **kwargs)  # type: ignore

    @classmethod
    def from_table_url(cls, table_url, credential=None, **kwargs):
        # type: (str, Optional[Any], Any) -> TableClient
        """A client to interact with a specific Table.

        :param table_url: The full URI to the table, including SAS token if used.
        :type table_url: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token. The value can be a SAS token string, an account
            shared access key, or an instance of a TokenCredentials class from azure.identity.
        :type credential: Union[str,TokenCredential]
        :returns: A table client.
        :rtype: ~azure.table.TableClient
        """
        try:
            if not table_url.lower().startswith('http'):
                table_url = "https://" + table_url
        except AttributeError:
            raise ValueError("Table URL must be a string.")
        parsed_url = urlparse(table_url.rstrip('/'))

        if not parsed_url.netloc:
            raise ValueError("Invalid URL: {}".format(table_url))

        table_path = parsed_url.path.lstrip('/').split('/')
        account_path = ""
        if len(table_path) > 1:
            account_path = "/" + "/".join(table_path[:-1])
        account_url = "{}://{}{}?{}".format(
            parsed_url.scheme,
            parsed_url.netloc.rstrip('/'),
            account_path,
            parsed_url.query)
        table_name = unquote(table_path[-1])
        if not table_name:
            raise ValueError("Invalid URL. Please provide a URL with a valid table name")
        return cls(account_url, table_name=table_name, credential=credential, **kwargs)

    @distributed_trace
    def get_table_access_policy(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> dict[str,AccessPolicy]
        """Retrieves details about any stored access policies specified on the table that may be
        used with Shared Access Signatures.

        :return: Dictionary of SignedIdentifiers
        :rtype: dict[str,AccessPolicy]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timeout = kwargs.pop('timeout', None)
        try:
            _, identifiers = self._client.table.get_access_policy(
                table=self.table_name,
                timeout=timeout,
                cls=return_headers_and_deserialized,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)
        return {s.id: s.access_policy or AccessPolicy() for s in identifiers}

    @distributed_trace
    def set_table_access_policy(
            self,
            signed_identifiers,  # type: dict[str,AccessPolicy]
            **kwargs):
        # type: (...) -> None
        """Sets stored access policies for the table that may be used with Shared Access Signatures.

        :param signed_identifiers:
        :type signed_identifiers: dict[str,AccessPolicy]
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if len(signed_identifiers) > 5:
            raise ValueError(
                'Too many access policies provided. The server does not support setting '
                'more than 5 access policies on a single resource.')
        identifiers = []
        for key, value in signed_identifiers.items():
            if value:
                value.start = serialize_iso(value.start)
                value.expiry = serialize_iso(value.expiry)
            identifiers.append(SignedIdentifier(id=key, access_policy=value))
        signed_identifiers = identifiers  # type: ignore
        try:
            self._client.table.set_access_policy(
                table=self.table_name,
                table_acl=signed_identifiers or None,
                **kwargs)
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def get_table_properties(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> TableServiceProperties
        """Gets the properties of an account's Table service,
        including properties for Analytics and CORS (Cross-Origin Resource Sharing) rules.

        :return: TableServiceProperties
        :rtype: TableServiceProperties
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        timeout = kwargs.pop('timeout', None)
        request_id_parameter = kwargs.pop('request_id_parameter', None)
        try:
            response = self._client.service.get_properties(
                timeout=timeout,
                request_id_parameter=request_id_parameter,
                **kwargs)
            return response
        except HttpResponseError as error:
            process_storage_error(error)

    @distributed_trace
    def create_table(
            self,
            **kwargs  # type: Any
    ):
        # type: (...) -> str
        """Creates a new table under the given account.

        :return: Table created
        :rtype: str
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        table_properties = TableProperties(table_name=self.table_name, **kwargs)
        table = self._client.table.create(table_properties)
        return table.table_name

    @distributed_trace
    def delete_table(
            self,
            request_id_parameter=None,  # type: Optional[str]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Creates a new table under the given account.

        :param request_id_parameter: Request Id parameter
        :type request_id_parameter: str
        :return: None
        :rtype: None
        """
        self._client.table.delete(table=self.table_name, request_id_parameter=request_id_parameter, **kwargs)

    @distributed_trace
    def delete_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            etag=None,  # type: Optional[object]
            match_condition=None,  # type: Optional[MatchCondition]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param etag: Etag of the entity
        :type etag: str
        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        self._client.table.delete_entity(
            table=self.table_name,
            partition_key=partition_key,
            row_key=row_key,
            if_match=if_match or if_not_match or '*',
            **kwargs)

    @distributed_trace
    def create_entity(
            self,
            table_entity_properties,  # type: dict[str,str]
            **kwargs  # type: Any
    ):
        # type: (...) -> Entity
        """Insert entity in a table.

        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :return: Entity mapping str to azure.table.EntityProperty
        :rtype: ~azure.table.Entity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if table_entity_properties:

            if "PartitionKey" in table_entity_properties and "RowKey" in table_entity_properties:
                table_entity_properties = _add_entity_properties(table_entity_properties)
            else:
                raise ValueError
        try:
            # TODO: table name?
            inserted_entity = self._client.table.insert_entity(
                table=self.table_name,
                table_entity_properties=table_entity_properties,
                **kwargs
            )
            properties = _convert_to_entity(inserted_entity)
            return Entity(properties)
        except ValueError as error:
            process_storage_error(error)

    @distributed_trace
    def update_entity(  # pylint:disable=R1710
            self,
            mode,  # type: Any
            table_entity_properties,  # type: dict[str,str]
            partition_key=None,  # type: Optional[str]
            row_key=None,  # type: Optional[str]
            etag=None,  # type: Optional[object]
            match_condition=None,  # type: Optional[MatchCondition]
            **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Update entity in a table.

        :param mode: Merge or Replace entity
        :type mode: ~azure.table.UpdateMode
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param etag: Etag of the entity
        :type etag: str
        :param match_condition: MatchCondition
        :type match_condition: ~azure.core.MatchConditions
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if_match, if_not_match = _get_match_headers(kwargs=dict(kwargs, etag=etag, match_condition=match_condition),
                                                    etag_param='etag', match_param='match_condition')

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        if mode is UpdateMode.replace:
            self._client.table.update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=table_entity_properties,
                if_match=if_match or if_not_match or "*",
                **kwargs)
        if mode is UpdateMode.merge:
            self._client.table.merge_entity(table=self.table_name, partition_key=partition_key,
                                            row_key=row_key, if_match=if_match or if_not_match or "*",
                                            table_entity_properties=table_entity_properties, **kwargs)

    @distributed_trace
    def query_entities(
            self,
            results_per_page=None,
            select=None,
            filter=None,    # pylint: disable=W0622
            **kwargs  # type: Any
    ):
        # type: (...) -> ItemPaged[Entity]
        """Queries entities in a table.

        :param results_per_page: Number of entities per page in return ItemPaged
        :type results_per_page: int
        :param select: Specify desired properties of an entity to return certain entities
        :type select: str
        :param filter: Specify a filter to return certain entities
        :type filter: str
        :return: Query of table entities
        :rtype: ItemPaged[Entity]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        query_options = QueryOptions(top=results_per_page, select=select, filter=filter)

        command = functools.partial(
            self._client.table.query_entities,
            **kwargs)
        return ItemPaged(
            command, results_per_page=query_options, table=self.table_name,
            page_iterator_class=TableEntityPropertiesPaged
        )

    @distributed_trace
    def get_entity(
            self,
            partition_key,  # type: str
            row_key,  # type: str
            results_per_page=None,
            select=None,
            filter=None,     # pylint: disable=W0622
            **kwargs  # type: Any
    ):
        # type: (...) -> Entity
        """Queries entities in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param results_per_page: Number of entities per page in return ItemPaged
        :type results_per_page: int
        :param select: Specify desired properties of an entity to return certain entities
        :type select: str
        :param filter: Specify a filter to return certain entities
        :type filter: str
        :return: Entity mapping str to azure.table.EntityProperty
        :rtype: ~azure.table.Entity
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        query_options = QueryOptions(top=results_per_page, select=select, filter=filter)
        entity = self._client.table.query_entities_with_partition_and_row_key(table=self.table_name,
                                                                              partition_key=partition_key,
                                                                              row_key=row_key,
                                                                              query_options=query_options,
                                                                              **kwargs)
        properties = _convert_to_entity(entity.additional_properties)
        return Entity(properties)

    @distributed_trace
    def upsert_entity(  # pylint:disable=R1710
            self,
            mode,  # type: Any
            table_entity_properties,  # type: dict[str,str]
            partition_key=None,  # type: Optional[str]
            row_key=None,  # type: Optional[str]
            **kwargs  # type: Any
    ):
        # type: (...) -> Entity or None
        # TODO: Return type will need to change
        """Update/Merge or Insert entity into table.

        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.table.UpdateMode
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, str]
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :return: Entity mapping str to azure.table.EntityProperty or None
        :rtype: ~azure.table.Entity or None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        if table_entity_properties:
            partition_key = table_entity_properties['PartitionKey']
            row_key = table_entity_properties['RowKey']
            table_entity_properties = _add_entity_properties(table_entity_properties)

        if mode is UpdateMode.merge:
            try:
                merged_entity = self._client.table.merge_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
                return merged_entity
            except ResourceNotFoundError:
                insert_entity = self.create_entity(
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
                properties = _convert_to_entity(insert_entity)
                return Entity(properties)
        if mode is UpdateMode.replace:
            try:
                update_entity = self._client.table.update_entity(
                    table=self.table_name,
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs)
                return update_entity
            except ResourceNotFoundError:
                insert_entity = self.create_entity(
                    partition_key=partition_key,
                    row_key=row_key,
                    table_entity_properties=table_entity_properties,
                    **kwargs
                )
                properties = _convert_to_entity(insert_entity)
                return Entity(properties)
