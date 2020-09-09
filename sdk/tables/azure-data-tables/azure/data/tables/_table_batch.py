# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
import warnings

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpRequest, HttpResponse

from ._deserialize import _return_headers_and_deserialized
from ._models import PartialBatchErrorException, UpdateMode
from ._serialize import _get_match_headers, _add_entity_properties

class TableBatchOperations(object):
    '''
    This is the class that is used for batch operations for the data tables
    service.

    The Tables service supports batch transactions on entities that are in the
    same table and belong to the same partition group. Multiple operations are
    supported within a single transaction. The batch can include at most 100
    entities, and its total payload may be no more than 4 MB in size.

    TODO: confirm # of entities, payload size, partition group
    '''

    def __init__(self, client, serializer, deserializer, config, table_name):
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config
        self.table_name = table_name

        self._partition_key = None
        self._requests = []


    def commit(
        self, table_name, # type: str
        **kwargs
    ):
        """
        Commits a :class:`~azure.storage.table.TableBatchOperations` request.
        :param str table_name:
            The name of the table to commit the batch to.
        :param TableBatch batch:
            The batch to commit.
        :param int timeout:
            The server timeout, expressed in seconds.
        :return:
            A list of the batch responses corresponding to the requests in the batch.
            The items could either be an etag, in case of success, or an error object in case of failure.
        :rtype: list(:class:`~azure.data.tables.models.AzureBatchOperationError`, str)
        """
        # TODO: add this if necessary
        # self._validate_not_none('table_name', table_name)
        self._client._client._batch_send(self._requests, **kwargs)


    def _verify_partition_key(
        self, entity # type: Union[Entity, dict]
    ):
        # (...) -> None
        if self._partition_key is None:
            self._partition_key = entity['PartitionKey']
        elif 'PartitionKey' in entity:
            if entity['PartitionKey'] != self._partition_key:
                raise PartialBatchErrorException("Partition Keys must all be the same", None, None)


    def create_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Insert entity in a table.

        :param entity: The properties for the table entity.
        :type entity: Union[TableEntity, dict[str,str]]
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: dict[str,str]
        :raises: ~azure.core.exceptions.HttpResponseError
        # TODO: update the example here
        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START create_entity]
                :end-before: [END create_entity]
                :language: python
                :dedent: 8
                :caption: Creating and adding an entity to a Table
        """
        if "PartitionKey" in entity and "RowKey" in entity:
            entity = _add_entity_properties(entity)
        else:
            raise ValueError('PartitionKey and RowKey were not provided in entity')
        self._batch_create_entity(
            table=self.table_name,
            entity=entity,
            cls=kwargs.pop('cls', _return_headers_and_deserialized),
            **kwargs)


    def _batch_create_entity(
        self,
        table, # type: str
        entity, # type: Union[Dict, TableEntity]
        timeout=None, # type: Optional[int]
        request_id_parameter=None, # type: Optional[str]
        response_preference=None, # type: Optional[Union[str, "models.ResponseFormat"]]
        query_options=None, # type: Optional["models.QueryOptions"]
        **kwargs # type: Any
    ):
        # (...) -> None
        '''
        Adds an insert operation to the batch. See
        :func:`azure.data.tables.TableClient.insert_entity` for more information
        on insert operations.

        The operation will not be executed until the batch is committed

        :param: table:
            The table to perform the operation on
        :type: table: str
        :param: entity:
            The entity to insert. Can be a dict or an entity object
            Must contain a PartitionKey and a RowKey.
        :type: entity: dict or :class:`~azure.data.tables.models.Entity`
        '''
        self._verify_partition_key(entity)
        if "PartitionKey" in entity and "RowKey" in entity:
            entity = _add_entity_properties(entity)
        else:
            raise ValueError('PartitionKey and RowKey were not provided in entity')

        cls = kwargs.pop('cls', None)  # type: ClsType[Optional[Dict[str, object]]]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json;odata=nometadata")
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_create_entity.metadata['url']  # type: ignore
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", self.table_name, 'str'),
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query("timeout", timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        if response_preference is not None:
            header_parameters['Prefer'] = self._serialize.header("response_preference", response_preference, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        if entity is not None:
            body_content = self._serialize.body(entity, '{object}')
        else:
            body_content = None
        body_content_kwargs['content'] = body_content
        request = self._client._client.post(url, query_parameters, header_parameters, **body_content_kwargs)
        self._requests.append(request)
    _batch_create_entity.metadata = {'url': '/{table}'}  # type: ignore


    def update_entity(
            self,
            entity,  # type: Union[TableEntity, Dict[str,str]]
            mode=UpdateMode.MERGE,  # type: UpdateMode
            **kwargs  # type: Any
    ):
        # (...) -> None
        if_match, _ = _get_match_headers(kwargs=dict(kwargs, etag=kwargs.pop('etag', None),
                                                                match_condition=kwargs.pop('match_condition', None)),
                                                    etag_param='etag', match_param='match_condition')

        partition_key = entity['PartitionKey']
        row_key = entity['RowKey']
        entity = _add_entity_properties(entity)
        if mode is UpdateMode.REPLACE:
            self._batch_update_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                table_entity_properties=entity,
                if_match=if_match or "*",
                cls=kwargs.pop('cls', _return_headers_and_deserialized),
                **kwargs)
        elif mode is UpdateMode.MERGE:
            self._batch_merge_entity(
                table=self.table_name,
                partition_key=partition_key,
                row_key=row_key,
                if_match=if_match or "*",
                table_entity_properties=entity,
                cls=kwargs.pop('cls', _return_headers_and_deserialized),
                **kwargs)


    def _batch_update_entity(
        self,
        table, # type: str
        partition_key,  # type: str
        row_key,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        if_match=None,  # type: Optional[str]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Update entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param if_match: Match condition for an entity to be updated. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional update, set to the
         wildcard character (*). If not specified, an insert will be performed when no existing entity
         is found to update and a replace will be performed if an existing entity is found.
        :type if_match: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_update_entity.metadata['url']  # type: ignore
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", table, 'str'),
            'partitionKey': self._serialize.url("partition_key", partition_key, 'str'),
            'rowKey': self._serialize.url("row_key", row_key, 'str'),
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query("timeout", timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        if if_match is not None:
            header_parameters['If-Match'] = self._serialize.header("if_match", if_match, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        if table_entity_properties is not None:
            body_content = self._serialize.body(table_entity_properties, '{object}')
        else:
            body_content = None
        body_content_kwargs['content'] = body_content
        request = self._client._client.put(url, query_parameters, header_parameters, **body_content_kwargs)
        self._requests.append(request)
    _batch_update_entity.metadata = {'url': '/{table}(PartitionKey=\'{partitionKey}\',RowKey=\'{rowKey}\')'}  # type: ignore


    def _batch_merge_entity(
        self,
        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        if_match=None,  # type: Optional[str]
        table_entity_properties=None,  # type: Optional[Dict[str, object]]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Merge entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param if_match: Match condition for an entity to be updated. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional update, set to the
         wildcard character (*). If not specified, an insert will be performed when no existing entity
         is found to update and a merge will be performed if an existing entity is found.
        :type if_match: str
        :param table_entity_properties: The properties for the table entity.
        :type table_entity_properties: dict[str, object]
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json")
        accept = "application/json"

        # Construct URL
        url = self._batch_merge_entity.metadata['url']  # type: ignore
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", table, 'str'),
            'partitionKey': self._serialize.url("partition_key", partition_key, 'str'),
            'rowKey': self._serialize.url("row_key", row_key, 'str'),
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query("timeout", timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        if if_match is not None:
            header_parameters['If-Match'] = self._serialize.header("if_match", if_match, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        if table_entity_properties is not None:
            body_content = self._serialize.body(table_entity_properties, '{object}')
        else:
            body_content = None
        body_content_kwargs['content'] = body_content
        request = self._client._client.patch(url, query_parameters, header_parameters, **body_content_kwargs)
    _batch_merge_entity.metadata = {'url': '/{table}(PartitionKey=\'{partitionKey}\',RowKey=\'{rowKey}\')'}  # type: ignore


    def delete_entity(
        self,
        partition_key,  # type: str
        row_key,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.

        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :keyword str etag: Etag of the entity
        :keyword ~azure.core.MatchConditions match_condition: MatchCondition
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_insert_delete_entities.py
                :start-after: [START delete_entity]
                :end-before: [END delete_entity]
                :language: python
                :dedent: 8
                :caption: Deleting an entity to a Table
        """

        if_match, _ = _get_match_headers(kwargs=dict(kwargs, etag=kwargs.pop('etag', None),
                                                                match_condition=kwargs.pop('match_condition', None)),
                                                    etag_param='etag', match_param='match_condition')

        self._batch_delete_entity(
            table=self.table_name,
            partition_key=partition_key,
            row_key=row_key,
            if_match=if_match or '*',
            **kwargs)


    def _batch_delete_entity(
        self,
        table,  # type: str
        partition_key,  # type: str
        row_key,  # type: str
        if_match,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Deletes the specified entity in a table.

        :param table: The name of the table.
        :type table: str
        :param partition_key: The partition key of the entity.
        :type partition_key: str
        :param row_key: The row key of the entity.
        :type row_key: str
        :param if_match: Match condition for an entity to be deleted. If specified and a matching
         entity is not found, an error will be raised. To force an unconditional delete, set to the
         wildcard character (*).
        :type if_match: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: None, or the result of cls(response)
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType[None]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_delete_entity.metadata['url']  # type: ignore
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", table, 'str'),
            'partitionKey': self._serialize.url("partition_key", partition_key, 'str'),
            'rowKey': self._serialize.url("row_key", row_key, 'str'),
        }
        url = self._client_client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query("timeout", timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        header_parameters['If-Match'] = self._serialize.header("if_match", if_match, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        request = self._client._client.delete(url, query_parameters, header_parameters)
    _batch_delete_entity.metadata = {'url': '/{table}(PartitionKey=\'{partitionKey}\',RowKey=\'{rowKey}\')'}  # type: ignore


    def upsert_entity(  # pylint:disable=R1710
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        mode=UpdateMode.MERGE,  # type: UpdateMode
        **kwargs  # type: Any
    ):
        # type: (...) -> Dict[str,str]
        """Update/Merge or Insert entity into table.

        :param entity: The properties for the table entity.
        :type entity: Union[TableEntity, dict[str,str]]
        :param mode: Merge or Replace and Insert on fail
        :type mode: ~azure.data.tables.UpdateMode
        :return: Dictionary mapping operation metadata returned from the service
        :rtype: dict[str,str]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_update_upsert_merge_entities.py
                :start-after: [START upsert_entity]
                :end-before: [END upsert_entity]
                :language: python
                :dedent: 8
                :caption: Update/merge or insert an entity into a table
        """

        partition_key = entity['PartitionKey']
        row_key = entity['RowKey']
        entity = _add_entity_properties(entity)

        # if mode is UpdateMode.MERGE:
        #     self._client.table.merge_entity(
        #         table=self.table_name,
        #         partition_key=partition_key,
        #         row_key=row_key,
        #         table_entity_properties=entity,
        #         cls=kwargs.pop('cls', _return_headers_and_deserialized),
        #         **kwargs
        #     )
        # elif mode is UpdateMode.REPLACE:
        #     self._client.table.update_entity(
        #         table=self.table_name,
        #         partition_key=partition_key,
        #         row_key=row_key,
        #         table_entity_properties=entity,
        #         cls=kwargs.pop('cls', _return_headers_and_deserialized),
        #         **kwargs)


    def query_entities(
        self,
        filter,  # type: str  # pylint: disable = W0622
        **kwargs
    ):
        # type: (...) -> ItemPaged[TableEntity]
        """Lists entities in a table.

        :param str filter: Specify a filter to return certain entities
        :keyword int results_per_page: Number of entities per page in return ItemPaged
        :keyword Union[str, list[str]] select: Specify desired properties of an entity to return certain entities
        :keyword dict parameters: Dictionary for formatting query with additional, user defined parameters
        :return: Query of table entities
        :rtype: ItemPaged[TableEntity]
        :raises: ~azure.core.exceptions.HttpResponseError

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_query_table.py
                :start-after: [START query_entities]
                :end-before: [END query_entities]
                :language: python
                :dedent: 8
                :caption: Query entities held within a table
        """
        parameters = kwargs.pop('parameters', None)
        filter = self._parameter_filter_substitution(parameters, filter)  # pylint: disable = W0622

        user_select = kwargs.pop('select', None)
        if user_select and not isinstance(user_select, str):
            user_select = ", ".join(user_select)

        query_options = QueryOptions(top=kwargs.pop('results_per_page', None), select=user_select,
                                     filter=filter)
        self._batch_query(self.table_name, **kwargs)


    def _batch_query(
        self,
        table,  # type: str
        timeout=None,  # type: Optional[int]
        request_id_parameter=None,  # type: Optional[str]
        next_partition_key=None,  # type: Optional[str]
        next_row_key=None,  # type: Optional[str]
        query_options=None,  # type: Optional["models.QueryOptions"]
        **kwargs  # type: Any
    ):
        # type: (...) -> "models.TableEntityQueryResponse"
        """Queries entities in a table.

        :param table: The name of the table.
        :type table: str
        :param timeout: The timeout parameter is expressed in seconds.
        :type timeout: int
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param next_partition_key: An entity query continuation token from a previous call.
        :type next_partition_key: str
        :param next_row_key: An entity query continuation token from a previous call.
        :type next_row_key: str
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableEntityQueryResponse, or the result of cls(response)
        :rtype: ~azure.data.tables.models.TableEntityQueryResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        cls = kwargs.pop('cls', None)  # type: ClsType["models.TableEntityQueryResponse"]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        _top = None
        _select = None
        _filter = None
        if query_options is not None:
            _format = query_options.format
            _top = query_options.top
            _select = query_options.select
            _filter = query_options.filter
        data_service_version = "3.0"
        accept = "application/json;odata=minimalmetadata"

        # Construct URL
        url = self._batch_query.metadata['url']  # type: ignore
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", table, 'str'),
        }
        url = self._client._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query("timeout", timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')
        if _top is not None:
            query_parameters['$top'] = self._serialize.query("top", _top, 'int', minimum=0)
        if _select is not None:
            query_parameters['$select'] = self._serialize.query("select", _select, 'str')
        if _filter is not None:
            query_parameters['$filter'] = self._serialize.query("filter", _filter, 'str')
        if next_partition_key is not None:
            query_parameters['NextPartitionKey'] = self._serialize.query("next_partition_key", next_partition_key, 'str')
        if next_row_key is not None:
            query_parameters['NextRowKey'] = self._serialize.query("next_row_key", next_row_key, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        request = self._client._client.get(url, query_parameters, header_parameters)
        self._requests.append(request)
    _batch_query.metadata = {'url': '/{table}()'}  # type: ignore


    def _add_to_batch(
            self, partition_key, # type: str
            row_key, # type: str
            request # type: ???  # TODO
    ):
        '''
        Validates batch-specific rules.

        :param str partition_key:
            PartitionKey of the entity.
        :param str row_key:
            RowKey of the entity.
        :param request:
            the request to insert, update or delete entity
        '''
        if self._partition_key:
            if self._partition_key != partition_key:
                # TODO
                # raise PartialBatchErrorException()
                pass
        else:
            self._partition_key = partition_key

        if row_key in self._row_keys:
            # TODO
            # how should we handle multiple operations on a certain row
            # raise PartialBatchErrorException
            pass
        else:
            self._row_keys.append(row_key)

        if len(self._requests) >= 100:
            # TODO
            # Is this limit real?
            # riase PartialBatchErrorException
            pass

        self._requests.append((row_key, request))


    def __enter__(self):
        # type: (...) -> TableBatchOperations
        # TODO: self._client should probably be a PipelineClient of some sorts
        self._client.__enter__() # TODO: borrowing from search
        return self


    def __exit__(
            self, *args # type: Any
    ):
        # (...) -> None
        self.close()
        self._client.__exit__(*args)