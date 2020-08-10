# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from ._models import UpdateMode

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

    def __init__(self):
        self.client = 
        self._requests = []
        self._partition_key = None
        self._row_keys = []

    def insert_entity(
            self, entity # type: Union[Entity, dict]
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
        # TODO: insert entity
        cls = kwargs.pop('cls', None)  # type: ClsType[Dict[str, object]]
        error_map = {404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop('error_map', {}))

        # Construct URL

        # Construct parameters

        # Construct headers

        # Construct request



        pass

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
            self, entity # type: Union[Entity, dict]
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
