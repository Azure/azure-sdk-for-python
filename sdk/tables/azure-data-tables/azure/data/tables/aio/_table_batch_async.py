# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (
    Dict,
    Any,
    Optional,
    Union
)
import msrest

from azure.core.pipeline import PipelineResponse
from azure.core.exceptions import (  # pylint:disable=unused-import
    ClientAuthenticationError,
    ResourceNotFoundError,
    ResourceExistsError
)

from ._table_client_async import TableClient
from .._models import PartialBatchErrorException, UpdateMode
from .._serialize import _get_match_headers, _add_entity_properties  # pylint:disable=unused-import
from .._generated.models import (  # pylint:disable=unused-import
    QueryOptions
)
from .._generated.aio._azure_table import AzureTable
from .._generated.aio._configuration import AzureTableConfiguration

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

    def __init__(
        self,
        client: AzureTable,
        serializer: msrest.Serializer,
        deserializer: msrest.Deserializer,
        config: AzureTableConfiguration,
        table_name: str,
        table_client: TableClient,
        **kwargs: Dict[str, Any],
    ) -> None:
        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer
        self._config = config
        self.table_name = table_name
        self._table_client = table_client

        self._partition_key = kwargs.pop('partition_key', None)
        self._requests = []

    def _verify_partition_key(
        self, entity # type: Union[Entity, dict]
    ):
        # (...) -> None
        if self._partition_key is None:
            self._partition_key = entity['PartitionKey']
        elif 'PartitionKey' in entity:
            if entity['PartitionKey'] != self._partition_key:
                raise PartialBatchErrorException("Partition Keys must all be the same", None, None)

    async def create_entity(
        self,
        entity,  # type: Union[TableEntity, Dict[str,str]]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
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
            **kwargs)



    async def _batch_create_entity(
        self,
        table_properties: "models.TableProperties",
        request_id_parameter: Optional[str] = None,
        response_preference: Optional[Union[str, "models.ResponseFormat"]] = None,
        query_options: Optional["models.QueryOptions"] = None,
        **kwargs
    ) -> Optional["models.TableResponse"]:
        """Creates a new table under the given account.

        :param table_properties: The Table properties.
        :type table_properties: ~azure.data.tables.models.TableProperties
        :param request_id_parameter: Provides a client-generated, opaque value with a 1 KB character
         limit that is recorded in the analytics logs when analytics logging is enabled.
        :type request_id_parameter: str
        :param response_preference: Specifies whether the response should include the inserted entity
         in the payload. Possible values are return-no-content and return-content.
        :type response_preference: str or ~azure.data.tables.models.ResponseFormat
        :param query_options: Parameter group.
        :type query_options: ~azure.data.tables.models.QueryOptions
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: TableResponse, or the result of cls(response)
        :rtype: ~azure.data.tables.models.TableResponse or None
        :raises: ~azure.core.exceptions.HttpResponseError
        """

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
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}  # type: Dict[str, Any]
        if _format is not None:
            query_parameters['$format'] = self._serialize.query("format", _format, 'str')

        # Construct headers
        header_parameters = {}  # type: Dict[str, Any]
        header_parameters['x-ms-version'] = self._serialize.header("self._config.version", self._config.version, 'str')
        if request_id_parameter is not None:
            header_parameters['x-ms-client-request-id'] = self._serialize.header(
                "request_id_parameter", request_id_parameter, 'str')
        header_parameters['DataServiceVersion'] = self._serialize.header(
            "data_service_version", data_service_version, 'str')
        if response_preference is not None:
            header_parameters['Prefer'] = self._serialize.header("response_preference", response_preference, 'str')
        header_parameters['Content-Type'] = self._serialize.header("content_type", content_type, 'str')
        header_parameters['Accept'] = self._serialize.header("accept", accept, 'str')

        body_content_kwargs = {}  # type: Dict[str, Any]
        body_content = self._serialize.body(table_properties, 'TableProperties')
        body_content_kwargs['content'] = body_content
        request = self._client.post(url, query_parameters, header_parameters, **body_content_kwargs)
        self._requests.append(request)

    _batch_create_entity.metadata = {'url': '/Tables'}  # type: ignore
