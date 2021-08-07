# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import datetime
import time
import logging
import calendar
import dateutil.parser

#from azure.eventhub import CheckpointStore
from azure.eventhub.exceptions import OwnershipLostError
from azure.data.tables import TableClient, UpdateMode
from azure.data.tables._base_client import parse_connection_str
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError, ResourceNotFoundError

logger = logging.getLogger(__name__)

def _utc_to_local(utc_dt):
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def _to_timestamp(date):
    timestamp = None
    if not date:
        return timestamp
    try:
        timestamp = date.timestamp()
    except AttributeError:  # python2.7 compatible
        timestamp = time.mktime(_utc_to_local(date).timetuple())
        timestamp += date.microsecond / 1e6
    return timestamp

class TableCheckpointStore():
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
            The Storage API version to use for requests. Default value is '2018-03-28'.
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
            The Storage API version to use for requests. Default value is '2018-03-28'.
        :returns: A table checkpoint store.
        :rtype: ~azure.eventhub.extensions.checkpointstoretable.TableCheckpointStore
        """
        endpoint, credential = parse_connection_str(
            conn_str=conn_str, credential=None, keyword_args=kwargs
        )
        return cls(endpoint, table_name=table_name, credential=credential, **kwargs)

    @classmethod
    def _create_ownership_entity(cls, ownership):
        """
        create a dictionary with the new ownership attributes so that it can be updated in tables
        """
        ownership_entity = {
            u'PartitionKey': "{} {} {} Ownership".format(ownership["fully_qualified_namespace"],
        ownership["eventhub_name"], ownership['consumer_group']),
            u'RowKey': ownership['partition_id'],
            u'ownerid' : ownership['owner_id'],
        }
        return ownership_entity

    @classmethod
    def _create_checkpoint_entity(cls, checkpoint):
        """
        create a dictionary with the new checkpoint attributes so that it can be updated in tables
        """
        checkpoint_entity = {
            u'PartitionKey': "{} {} {} Checkpoint".format(checkpoint["fully_qualified_namespace"],
        checkpoint["eventhub_name"], checkpoint['consumer_group']),
            u'RowKey': checkpoint['partition_id'],
            u'offset' : checkpoint['offset'],
            u'sequencenumber' : checkpoint['sequence_number'],}
        return checkpoint_entity

    def list_ownership(self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs):
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
                - `last_modified_time` (float): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """
        partition_key = "{} {} {} Ownership".format(fully_qualified_namespace,
        eventhub_name, consumer_group)
        my_filter = "PartitionKey eq '"+ partition_key + "'"
        entities = self.table_client.query_entities(my_filter, **kwargs)
        ownershiplist = []
        for entity in entities:
            dic = {}
            dic[u'fully_qualified_namespace'] = fully_qualified_namespace
            dic[u'eventhub_name'] = eventhub_name
            dic[u'consumer_group'] = consumer_group
            dic[u'partition_id'] = entity[u'RowKey']
            dic[u'owner_id'] = entity[u'ownerid']
            dic[u'last_modified_time'] = _to_timestamp(entity.metadata.get('timestamp'))
            dic[u'etag'] = entity.metadata.get('etag')
            ownershiplist.append(dic)
        return ownershiplist

    def list_checkpoints(self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs):
        """List the updated checkpoints from the storage table.
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
        partition_key = "{} {} {} Checkpoint".format(fully_qualified_namespace,
        eventhub_name, consumer_group)
        my_filter = "PartitionKey eq '"+ partition_key + "'"
        entities = self.table_client.query_entities(my_filter, **kwargs)
        checkpointslist = []
        for entity in entities:
            dic = {}
            dic[u'fully_qualified_namespace'] = fully_qualified_namespace
            dic[u'eventhub_name'] = eventhub_name
            dic[u'consumer_group'] = consumer_group
            dic[u'partition_id'] = entity[u'RowKey']
            dic[u'sequence_number'] = entity[u'sequencenumber']
            dic[u'offset'] = str(entity[u'offset'])
            checkpointslist.append(dic)
        return checkpointslist

    def update_checkpoint(self, checkpoint, **kwargs):
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
        checkpoint_entity = self._create_checkpoint_entity(checkpoint)
        try:
            self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=checkpoint_entity, **kwargs)
        except ResourceNotFoundError:
            self.table_client.create_entity(entity=checkpoint_entity, **kwargs)

    def _update_ownership(self, ownership):
        """_update_ownership mutates the passed in ownership."""
        ownership_entity = self._create_ownership_entity(ownership)
        try:
            if ownership['etag'] is None:
                metadata = self.table_client.create_entity(entity=ownership_entity,
                headers={'Prefer': 'return-content'})
                ownership['etag'] = metadata['etag']
                ownership['last_modified_time'] = _to_timestamp(dateutil.parser.isoparse
                (metadata['content']['Timestamp']))
                return ownership
            metadata = self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=ownership_entity,
            etag=ownership['etag'], match_condition=MatchConditions.IfNotModified)
            ownership['etag'] = metadata['etag']
            updated_entity = self.table_client.get_entity(partition_key=ownership_entity['PartitionKey']
            , row_key=ownership_entity['RowKey'])
            ownership['last_modified_time'] = _to_timestamp(updated_entity.metadata.get('timestamp'))
            return ownership
        except (ResourceModifiedError, ResourceExistsError, ResourceNotFoundError):
            raise OwnershipLostError()

    def _claim_one_partition(self, ownership, **kwargs):
        newownership = ownership.copy()
        try:
            self._update_ownership(newownership, **kwargs)
            return newownership
        except OwnershipLostError:
            raise OwnershipLostError()
        except Exception as error:  # pylint:disable=broad-except
            logger.warning(
                "An exception occurred when EventProcessor instance %r claim_ownership for "
                "namespace %r eventhub %r consumer group %r partition %r. "
                "The ownership is now lost. Exception "
                "is %r",
                newownership['owner_id'],
                newownership['fully_qualified_namespace'],
                newownership['eventhub_name'],
                newownership['consumer_group'],
                newownership['partition_id'],
                error,
            )
            return newownership  # Keep the ownership if an unexpected error happens

    def claim_ownership(self, ownership_list, **kwargs):
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
                - `last_modified_time` (float): The last time this ownership was claimed.
                - `etag` (str): The Etag value for the last time this ownership was modified. Optional depending
                  on storage implementation.
        """
        newlist = []
        for x in ownership_list:
            newlist.append(self._claim_one_partition(x))
        return newlist
