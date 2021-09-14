# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from typing import Dict, Optional, Any, Iterable, Union
import datetime
import time
import logging
import calendar
from azure.core import MatchConditions
from azure.eventhub import CheckpointStore  # type: ignore  # pylint: disable=no-name-in-module
from azure.eventhub.exceptions import OwnershipLostError  # type: ignore
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from ._vendor.data.tables import TableClient, UpdateMode
from ._vendor.data.tables._base_client import parse_connection_str
from ._vendor.data.tables._deserialize import clean_up_dotnet_timestamps
from ._vendor.data.tables._common_conversion import TZ_UTC

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

def _timestamp_to_datetime(value):
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = clean_up_dotnet_timestamps(value)
    try:
        dt_obj = datetime.datetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
            tzinfo=TZ_UTC
        )
    except ValueError:
        dt_obj = datetime.datetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=TZ_UTC
        )
    return dt_obj


class TableCheckpointStore(CheckpointStore):
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
        # type: (str, str, Optional[Any], Any) -> None
        self._table_client = kwargs.pop("table_client", None)
        if not self._table_client:
            api_version = kwargs.pop("api_version", None)
            if api_version:
                headers = kwargs.get("headers")
                if headers:
                    headers["x-ms-version"] = api_version
                else:
                    kwargs["headers"] = {"x-ms-version": api_version}
            self._table_client = TableClient(
                table_account_url, table_name, credential=credential, **kwargs
            )

    @classmethod
    def from_connection_string(cls, conn_str, table_name, credential=None, **kwargs):
        # type: (str, str, Optional[Any], Any) -> TableCheckpointStore
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

    def __enter__(self):
        self._table_client.__enter__()
        return self

    def __exit__(self, *args):
        self._table_client.__exit__(*args)

    @classmethod
    def _create_ownership_entity(cls, ownership):
        """
        Create a dictionary with the `ownership` attributes.
        """
        ownership_entity = {
            "PartitionKey": u"{} {} {} Ownership".format(
                ownership["fully_qualified_namespace"],
                ownership["eventhub_name"],
                ownership["consumer_group"],
            ),
            "RowKey": u"{}".format(ownership["partition_id"]),
            "ownerid": u"{}".format(ownership["owner_id"]),
        }
        return ownership_entity

    @classmethod
    def _create_checkpoint_entity(cls, checkpoint):
        """
        Create a dictionary with `checkpoint` attributes.
        """
        checkpoint_entity = {
            "PartitionKey": u"{} {} {} Checkpoint".format(
                checkpoint["fully_qualified_namespace"],
                checkpoint["eventhub_name"],
                checkpoint["consumer_group"],
            ),
            "RowKey": u"{}".format(checkpoint["partition_id"]),
            "offset": u"{}".format(checkpoint["offset"]),
            "sequencenumber": u"{}".format(checkpoint["sequence_number"]),
        }
        return checkpoint_entity

    def _update_ownership(self, ownership, **kwargs):
        """_update_ownership mutates the passed in ownership."""
        ownership_entity = TableCheckpointStore._create_ownership_entity(ownership)
        try:
            metadata = self._table_client.update_entity(
                mode=UpdateMode.REPLACE,
                entity=ownership_entity,
                etag=ownership["etag"],
                match_condition=MatchConditions.IfNotModified,
                **kwargs
            )
            ownership["etag"] = metadata["etag"]
            updated_entity = self._table_client.get_entity(
                partition_key=ownership_entity["PartitionKey"],
                row_key=ownership_entity["RowKey"],
                **kwargs
            )
            ownership["last_modified_time"] = _to_timestamp(
                updated_entity.metadata.get("timestamp")
            )
        except (ResourceNotFoundError, ValueError):
            metadata = self._table_client.create_entity(
                entity=ownership_entity, headers={"Prefer": "return-content"}, **kwargs
            )
            ownership["etag"] = metadata["etag"]
            ownership["last_modified_time"] = _to_timestamp(
                _timestamp_to_datetime(metadata["content"]["Timestamp"])
            )

    def _claim_one_partition(self, ownership, **kwargs):
        new_ownership = ownership.copy()
        try:
            self._update_ownership(new_ownership, **kwargs)
            return new_ownership
        except (ResourceModifiedError, ResourceExistsError):
            logger.info(
                "EventProcessor instance %r of namespace %r eventhub %r consumer group %r "
                "lost ownership to partition %r",
                new_ownership["owner_id"],
                new_ownership["fully_qualified_namespace"],
                new_ownership["eventhub_name"],
                new_ownership["consumer_group"],
                new_ownership["partition_id"],
            )
            raise OwnershipLostError()
        except Exception as error:  # pylint:disable=broad-except
            logger.warning(
                "An exception occurred when EventProcessor instance %r claim_ownership for "
                "namespace %r eventhub %r consumer group %r partition %r. "
                "The ownership is now lost. Exception "
                "is %r",
                new_ownership["owner_id"],
                new_ownership["fully_qualified_namespace"],
                new_ownership["eventhub_name"],
                new_ownership["consumer_group"],
                new_ownership["partition_id"],
                error,
            )
            return new_ownership  # Keep the ownership if an unexpected error happens

    def list_ownership(
        self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs
    ):
    # type: (str, str, str, Any) -> Iterable[Dict[str, Any]]
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
        try:
            partition_key = "{} {} {} Ownership".format(
                fully_qualified_namespace, eventhub_name, consumer_group
            )
            partition_key_filter = "PartitionKey eq '{}'".format(partition_key)
            entities = self._table_client.query_entities(partition_key_filter, **kwargs)
            result = []
            for entity in entities:
                ownership = {
                    "fully_qualified_namespace": fully_qualified_namespace,
                    "eventhub_name": eventhub_name,
                    "consumer_group": consumer_group,
                    "partition_id": entity[u"RowKey"],
                    "owner_id": entity[u"ownerid"],
                    "last_modified_time": _to_timestamp(
                        entity.metadata.get("timestamp")
                    ),
                    "etag": entity.metadata.get("etag"),
                }
                result.append(ownership)
            return result
        except Exception as error:
            logger.warning(
                "An exception occurred during list_ownership for "
                "namespace %r eventhub %r consumer group %r. "
                "Exception is %r",
                fully_qualified_namespace,
                eventhub_name,
                consumer_group,
                error,
            )
            raise

    def list_checkpoints(
        self, fully_qualified_namespace, eventhub_name, consumer_group, **kwargs
    ):
    # type: (str, str, str, Any) -> Iterable[Dict[str, Any]]
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
        partition_key = "{} {} {} Checkpoint".format(
            fully_qualified_namespace, eventhub_name, consumer_group
        )
        partition_key_filter = "PartitionKey eq '{}'".format(partition_key)
        entities = self._table_client.query_entities(partition_key_filter, **kwargs)
        checkpoints_list = []
        for entity in entities:
            checkpoint = {
                "fully_qualified_namespace": fully_qualified_namespace,
                "eventhub_name": eventhub_name,
                "consumer_group": consumer_group,
                "partition_id": entity[u"RowKey"],
                "sequence_number": int(entity[u"sequencenumber"]),
                "offset": str(entity[u"offset"]),
            }
            checkpoints_list.append(checkpoint)
        return checkpoints_list

    def update_checkpoint(self, checkpoint, **kwargs):
    # type: (Dict[str, Optional[Union[str, int]]], Any) -> None
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
        checkpoint_entity = TableCheckpointStore._create_checkpoint_entity(
            checkpoint
        )
        entity_name = "{}/{}/{}/checkpoint/{}".format(
            checkpoint["fully_qualified_namespace"],
            checkpoint["eventhub_name"],
            checkpoint["consumer_group"],
            checkpoint["partition_id"],
        )
        try:
            self._table_client.update_entity(
                mode=UpdateMode.REPLACE, entity=checkpoint_entity, **kwargs
            )
        except ResourceNotFoundError:
            logger.info(
                "Create checkpoint entity %r because it hasn't existed in the table yet.",
                entity_name,
            )
            self._table_client.create_entity(entity=checkpoint_entity, **kwargs)

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
        gathered_results = []
        for x in ownership_list:
            gathered_results.append(self._claim_one_partition(x, **kwargs))
        return gathered_results

    def close(self):
        self._container_client.__exit__()
