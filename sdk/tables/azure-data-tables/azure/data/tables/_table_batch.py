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

from ._models import PartialBatchErrorException, UpdateMode
from ._serialize import _add_entity_properties

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
        # self._request_entities = []
        self._requests = []

        # self._initialize_request()

    def _initialize_request(
        self, **kwargs # type: Any
    ):
        # (...) -> None

        cls = kwargs.pop('cls', None)
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        query_options = kwargs.pop('query_options', None)
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json;odata=nometadata")

        # Construct url
        url = self.insert_entity_metadata['url']
        path_format_arguments = {
            'url': self._serialize.url("self._config.url", self._config.url, 'str', skip_quote=True),
            'table': self._serialize.url("table", self.table_name, 'str')
        }
        url = self._client.format_url(url, **path_format_arguments)
        print("URL: {}".format(url))

        # Construct parameters
        # TODO: are query_parameters necessary?
        query_parameters = {}
        if timeout is not None:
            query_parameters['timeout'] = self._serialize.query('timeout', timeout, 'int', minimum=0)
        if _format is not None:
            query_parameters['$format'] = self._serialize.query('format', _format, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['x-ms-version'] = self._serialize.headers('self._config.version', self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header("request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header("data_service_version", data_service_version, 'str')
        if response_preference is not None:
            header_parameters['Prefer'] = self._serialize.header("response_preference", response_preference, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = 'application/json;odata=minimalmetadata'


        self._url = url
        self._query_parameters = query_parameters
        self._header_parameters = header_parameters
        print(url)
        print(query_parameters)
        print(header_parameters)
        print(body_content_kwargs)
        # request = self._client.post(url, query_parameters, header_parameters, **body_content_kwargs)
        # print(request)
        print(type(self._client._pipeline))


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

        # request = HttpRequest()
        # request.method = 'POST'
        # request.host_locations = self._get_host_locations()
        # request.path = '/' + '$batch'
        # request.query = {'timeout': _int_to_str(timeout)}

        # # Update the batch operation requests with table and client specific info
        # for row_key, batch_request in batch._requests:
        #     if batch_request.method == 'POST':
        #         batch_request.path = '/' + _to_str(table_name)
        #     else:
        #         batch_request.path = _get_entity_path(table_name, batch._partition_key, row_key)
        #     if self.is_emulated:
        #         batch_request.path = '/' + DEV_ACCOUNT_NAME + batch_request.path
        #     _update_request(batch_request, X_MS_VERSION, USER_AGENT_STRING)

        # # Construct the batch body
        # request.body, boundary = _convert_batch_to_json(batch._requests)
        # request.headers = {'Content-Type': boundary}

        # # Perform the batch request and return the response
        # return self._perform_request(request, _parse_batch_response)



        # self._client.post()
        # pass


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

        cls = kwargs.pop('cls', None)  # type: ClsType[Dict[str, object]]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        _format = None
        if query_options is not None:
            _format = query_options.format
        data_service_version = "3.0"
        content_type = kwargs.pop("content_type", "application/json;odata=nometadata")

        # Construct URL
        url = self.create_entity.metadata['url']  # type: ignore
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
        header_parameters['Accept'] = 'application/json;odata=minimalmetadata'

        # Construct and send request
        body_content_kwargs = {}  # type: Dict[str, Any]
        if entity is not None:
            body_content = self._serialize.body(entity, '{object}')
        else:
            body_content = None
        body_content_kwargs['content'] = body_content
        print("URL: {}".format(url))
        print("QPs: {}".format(query_parameters))
        print("HPs: {}".format(header_parameters))
        print("BCkwargs: {}".format(body_content_kwargs))
        print("TYPE: {}".format(type(self._client._client)))
        request = self._client._client.post(url, query_parameters, header_parameters, **body_content_kwargs)
        print("REQ BODY: {}".format(request.body))
        print("\n\n")
        self._requests.append(request)
    create_entity.metadata = {'url': '/{table_name}'}  # type: ignore


    def update_entity(
            self, entity, # type: Union[Entity, dict]
            if_match="*" # type: str
    ):
        # (...) -> None

        '''
        Adds an update entity operation to the batch. See
        :func:`~azure.data.tables.TableClient.update_entity` for more
        information on updates.

        The operation will not be executed until the batch is committed.
        :param entity:
            The entity to update. Can be a dict or an entity object.
            Must contain a PartitionKey and a RowKey.
        :type entity: dict or :class:`~azure.data.tables.Entity`
        :param str if_match:
            The client may specify the ETag for the entity on the
            request in order to compare to the ETag maintained by the service
            for the purpose of optimistic concurrency. The update operation
            will be performed only if the ETag sent by the client matches the
            value maintained by the server, indicating that the entity has
            not been modified since it was retrieved by the client. To force
            an unconditional update, set If-Match to the wildcard character (*).
        '''
        # TODO: verify the if_match param is necessary

        pass


    def merge_entity(
            self, entity, # type: Union[Entity, dict]
            if_match="*" # type: str
    ):
        # (...) -> None
        '''
        Adds a merge entity operation to the batch. See
        :func:`~azure.data.tables.TableClient.merge_entity` for more
        information on merges.

        The operation will not be executed until the batch is committed.
        :param entity:
            The entity to merge. Could be a dict or an entity object.
            Must contain a PartitionKey and a RowKey.
        :type entity: dict or :class:`~azure.data.tables.Entity`
        :param str if_match:
            The client may specify the ETag for the entity on the
            request in order to compare to the ETag maintained by the service
            for the purpose of optimistic concurrency. The merge operation
            will be performed only if the ETag sent by the client matches the
            value maintained by the server, indicating that the entity has
            not been modified since it was retrieved by the client. To force
            an unconditional merge, set If-Match to the wildcard character (*).
        '''

        pass

    def delete_entity(
            self, partition_key, # type: str
            row_key, # type: str
            if_match='*' # type: str
    ):
        # (...) -> None
        '''
        Adds a delete entity operation to the batch. See
        :func:`~azure.data.tables.TableClient.delete_entity` for more
        information on deletes.
        The operation will not be executed until the batch is committed.
        :param str partition_key:
            The PartitionKey of the entity.
        :param str row_key:
            The RowKey of the entity.
        :param str if_match:
            The client may specify the ETag for the entity on the
            request in order to compare to the ETag maintained by the service
            for the purpose of optimistic concurrency. The delete operation
            will be performed only if the ETag sent by the client matches the
            value maintained by the server, indicating that the entity has
            not been modified since it was retrieved by the client. To force
            an unconditional delete, set If-Match to the wildcard character (*).
        '''

        pass

    def upsert_entity(
            self,
            entity,  # type: Union[TableEntity, dict[str,str]]
            mode=UpdateMode.MERGE,  # type: UpdateMode
            **kwargs  # type: Any
    ):
        # (...) -> None
        '''
        Update/Merge or Insert entity into table.

        :func:`~azure.data.tables.TableClient.upsert_entity` for more
        information on insert or replace operations.
        The operation will not be executed until the batch is committed.
        :param entity:
            The entity to insert or replace. Could be a dict or an entity object.
            Must contain a PartitionKey and a RowKey.
        :type entity: dict or :class:`~azure.data.tables.Entity`
       '''

        pass

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