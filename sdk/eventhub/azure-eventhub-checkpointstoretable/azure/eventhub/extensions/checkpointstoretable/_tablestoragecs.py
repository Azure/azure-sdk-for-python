# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from collections import defaultdict
from azure.data.tables import TableClient, UpdateMode
from azure.core import MatchConditions
from azure.data.tables._base_client import parse_connection_str
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError, ResourceNotFoundError

class TableCheckpointStore:
    """A CheckpointStore that uses Azure Table Storage to store the partition ownership and checkpoint data.
    This class implements methods list_ownership, claim_ownership, update_checkpoint and list_checkpoints.
    :param str table_account_url:
        The URI to the storage account.
    :param table_name:
        The name of the table for the tables.
    :type table_name: str
    :param credential:
        The credentials with which to authenticate. This is optional if the
        account URL already has a SAS token. The value can be a SAS token string, an account
        shared access key, or an instance of a TokenCredentials class from azure.identity.
        If the URL already has a SAS token, specifying an explicit credential will take priority.
    :keyword str api_version:
            The Storage API version to use for requests. Default value is '2019-07-07'.
    :keyword str secondary_hostname:
        The hostname of the secondary endpoint.
    """

    def __init__(self, table_account_url, table_name, credential=None, **kwargs):
        # type(str, str, Optional[Any], Any) -> None
        self.table_client = kwargs.pop("table_client", None)
        if not self.table_client:
            api_version = kwargs.pop("api_version", None)
            if api_version:
                headers = kwargs.get("headers")
                if headers:
                    headers["x-ms-version"] = api_version
                else:
                    kwargs["headers"] = {"x-ms-version": api_version}
            self.table_client = TableClient(
                table_account_url, table_name, credential=credential, **kwargs
            )
        self._cached_table_clients = defaultdict()  # type: Dict[str, TableClient]

    @classmethod
    def from_connection_string(cls, conn_str, table_name, credential=None, **kwargs):
        """Create TableCheckpointStore from a storage connection string.
        :param str conn_str:
            A connection string to an Azure Storage account.
        :param table_name:
            The table name.
        :type table_name: str
        :param credential:
            The credentials with which to authenticate. This is optional if the
            account URL already has a SAS token, or the connection string already has shared
            access key values. The value can be a SAS token string, an account shared access
            key, or an instance of a TokenCredentials class from azure.identity.
            Credentials provided here will take precedence over those in the connection string.
        :keyword str api_version:
            The Storage API version to use for requests. Default value is '2019-07-07'.
        :keyword str secondary_hostname:
        :returns: A table checkpoint store.
        :rtype: ~azure.eventhub.extensions.checkpointstoretable.TableCheckpointStore
        """
        endpoint, credential = parse_connection_str(
            conn_str=conn_str, credential=None, keyword_args=kwargs
        )
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    def _create_entity_checkpoint(self, checkpoint):
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'consumer_group': checkpoint['consumer_group'],
            u'fully_qualified_namespace': checkpoint['fully_qualified_namespace'],
            u'eventhub_name': checkpoint['eventhub_name'],
            u'partition_id': checkpoint['partition_id'],
            u'offset' : checkpoint['offset'],
            u'sequence_number' : checkpoint['sequence_number'],
        }
        my_new_entity['RowKey'] = my_new_entity['partition_id']
        my_new_entity['PartitionKey'] = my_new_entity['eventhub_name'] + ' ' + \
        my_new_entity['fully_qualified_namespace'] + ' ' + my_new_entity['consumer_group'] + ' ' + 'Checkpoint'
        self.table_client.create_entity(entity=my_new_entity)

    def _create_entity_ownership(self, ownership):
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'consumer_group': ownership['consumer_group'],
            u'fully_qualified_namespace': ownership['fully_qualified_namespace'],
            u'eventhub_name': ownership['eventhub_name'],
            u'partition_id':  ownership['partition_id'],
            u'owner_id' : ownership['owner_id'],
        }
        my_new_entity['RowKey'] = my_new_entity['partition_id']
        my_new_entity['PartitionKey'] = my_new_entity['eventhub_name'] + ' ' \
        + my_new_entity['fully_qualified_namespace'] + ' ' + my_new_entity['consumer_group'] + ' ' + 'Ownership'
        new_entity = self.table_client.create_entity(entity=my_new_entity)
        return new_entity

    @classmethod
    def _modify_entity_ownership(cls, ownership):
        """
        create a dictionary with the new ownership attributes so that it can be updated in tables
        """
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'consumer_group': ownership['consumer_group'],
            u'fully_qualified_namespace': ownership['fully_qualified_namespace'],
            u'eventhub_name': ownership['eventhub_name'],
            u'partition_id':  ownership['partition_id'],
            u'owner_id' : ownership['owner_id'],
        }
        my_new_entity['RowKey'] = my_new_entity['partition_id']
        my_new_entity['PartitionKey'] = my_new_entity['eventhub_name'] + ' ' \
        + my_new_entity['fully_qualified_namespace'] + ' ' + my_new_entity['consumer_group'] + ' ' + 'Ownership'
        return my_new_entity

    @classmethod
    def _modify_entity_checkpoint(cls, checkpoint):
        """
        create a dictionary with the new checkpoint attributes so that it can be updated in tables
        """
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'consumer_group': checkpoint['consumer_group'],
            u'fully_qualified_namespace': checkpoint['fully_qualified_namespace'],
            u'eventhub_name': checkpoint['eventhub_name'],
            u'partition_id': checkpoint['partition_id'],
            u'offset' : checkpoint['offset'],
            u'sequence_number' : checkpoint['sequence_number'],}
        my_new_entity['RowKey'] = my_new_entity['partition_id']
        my_new_entity['PartitionKey'] = my_new_entity['eventhub_name'] + ' ' \
        + my_new_entity['fully_qualified_namespace'] + ' ' + my_new_entity['consumer_group'] + ' ' + 'Checkpoint'
        return my_new_entity

    def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group):
        """Retrieves a complete ownership list from the storage table.
        :param str fully_qualified_namespace: The fully qualified namespace that the Event Hub belongs to.
         The format is like "<namespace>.servicebus.windows.net".
        :param str eventhub_name: The name of the specific Event Hub the partition ownerships are associated with,
         relative to the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the ownerships are associated with.
        :rtype: Iterable[Dict[str, Any]], Iterable of dictionaries containing partition ownership information:
                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the ownership are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `owner_id` (str): A UUID representing the current owner of this partition.
                - `last_modified_time` (UTC datetime.datetime): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """
        thePartitionKey = eventhub_name + ' ' + fully_qualified_namespace +' ' + consumer_group + ' '+ 'Ownership'
        my_filter = "PartitionKey eq '"+ thePartitionKey + "'"
        entities = self.table_client.query_entities(my_filter)
        ownershiplist = []
        for entity in entities:
            dic = {}
            dic[u'fully_qualified_namespace'] = entity[u'fully_qualified_namespace']
            dic[u'eventhub_name'] = entity[u'eventhub_name']
            dic[u'consumer_group'] = entity[u'consumer_group']
            dic[u'partition_id'] = entity[u'partition_id']
            dic[u'owner_id'] = entity[u'owner_id']
            dic[u'etag'] = entity.metadata.get('etag')
            ownershiplist.append(dic)
        return ownershiplist

    def list_checkpoints(self, fully_qualified_namespace, eventhub_name, consumer_group):
        """List the updated checkpoints from the storage blob.
        :param str fully_qualified_namespace: The fully qualified namespace that the Event Hub belongs to.
         The format is like "<namespace>.servicebus.windows.net".
        :param str eventhub_name: The name of the specific Event Hub the checkpoints are associated with, relative to
         the Event Hubs namespace that contains it.
        :param str consumer_group: The name of the consumer group the checkpoints are associated with.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition checkpoint information:
                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoints are associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the checkpoints are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `sequence_number` (int): The sequence number of the :class:`EventData<azure.eventhub.EventData>`.
                - `offset` (str): The offset of the :class:`EventData<azure.eventhub.EventData>`.
        """
        thePartitionKey = eventhub_name + ' ' + fully_qualified_namespace +' ' + consumer_group + ' '+ 'Checkpoint'
        my_filter = "PartitionKey eq '"+ thePartitionKey + "'"
        entities = self.table_client.query_entities(my_filter)
        checkpointslist = []
        for entity in entities:
            dic = {}
            dic[u'fully_qualified_namespace'] = entity[u'fully_qualified_namespace']
            dic[u'eventhub_name'] = entity[u'eventhub_name']
            dic[u'consumer_group'] = entity[u'consumer_group']
            dic[u'partition_id'] = entity[u'partition_id']
            dic[u'sequence_number'] = entity[u'sequence_number']
            dic[u'offset'] = entity[u'offset']
            checkpointslist.append(dic)
        return checkpointslist

    def update_checkpoint(self, checkpoint):
        """Updates the checkpoint using the given information for the offset, associated partition and
        consumer group in the storage table.
        Note: If you plan to implement a custom checkpoint store with the intention of running between
        cross-language EventHubs SDKs, it is recommended to persist the offset value as an integer.
        :param Dict[str,Any] checkpoint: A dict containing checkpoint information:
                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the checkpoint is associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `sequence_number` (int): The sequence number of the :class:`EventData<azure.eventhub.EventData>`
                  the new checkpoint will be associated with.
                - `offset` (str): The offset of the :class:`EventData<azure.eventhub.EventData>`
                  the new checkpoint will be associated with.
        :rtype: None
        """
        try:
            theentity = self._modify_entity_checkpoint(checkpoint)
            self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=theentity)
        except ResourceNotFoundError:
            self._create_entity_checkpoint(checkpoint)

    def _upload_ownership(self, ownership):
        try:
            theentity = self._modify_entity_ownership(ownership)
            entity = self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=theentity,
            etag=ownership['etag'], match_condition=MatchConditions.IfNotModified)
            ownership['etag'] = entity['etag']
            ownership['last_modified_time'] = entity['date']
        except (ResourceNotFoundError, ValueError):
            try:
                entity = self._create_entity_ownership(ownership)
                ownership['etag'] = entity['etag']
                ownership['last_modified_time'] = entity['date']
            except ResourceExistsError:
                raise'your etag does not match the last time this ownership was modified.'
        except ResourceModifiedError:
            raise'your etag does not match the last time this ownership was modified.'


    def _claim_one_partition(self, ownership):
        self._upload_ownership(ownership)
        return ownership

    def claim_ownership(self, ownershiplist):
        # type: (Iterable[Dict[str, Any]], Any) -> Iterable[Dict[str, Any]]
        """Tries to claim ownership for a list of specified partitions.
        :param Iterable[Dict[str,Any]] ownership_list: Iterable of dictionaries containing all the ownerships to claim.
        :rtype: Iterable[Dict[str,Any]], Iterable of dictionaries containing partition ownership information:
                - `fully_qualified_namespace` (str): The fully qualified namespace that the Event Hub belongs to.
                  The format is like "<namespace>.servicebus.windows.net".
                - `eventhub_name` (str): The name of the specific Event Hub the checkpoint is associated with,
                  relative to the Event Hubs namespace that contains it.
                - `consumer_group` (str): The name of the consumer group the ownership are associated with.
                - `partition_id` (str): The partition ID which the checkpoint is created for.
                - `owner_id` (str): A UUID representing the owner attempting to claim this partition.
                - `last_modified_time` (UTC datetime.datetime): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """
        newlist = []
        for x in ownershiplist:
            newlist.append(self._claim_one_partition(x))
        return newlist
