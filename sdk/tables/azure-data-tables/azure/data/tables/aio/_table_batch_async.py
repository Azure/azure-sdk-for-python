from azure.core.exceptions import  ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline import PipelineResponse

from .._deserialize import _return_headers_and_deserialized
from .._models import PartialBatchErrorException, UpdateMode
from .._serialize import _get_match_headers, _add_entity_properties
from .._generated.models import (
    QueryOptions
)

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

    def create_entity(
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
            cls=kwargs.pop('cls', _return_headers_and_deserialized),
            **kwargs)

