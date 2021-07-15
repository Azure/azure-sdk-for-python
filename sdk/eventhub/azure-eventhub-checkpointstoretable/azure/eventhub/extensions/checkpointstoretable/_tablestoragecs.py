# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
#from typing import Sequence
#from collections import defaultdict
#from datetime import datetime
#from azure.eventhub import CheckpointStore, EventHubConsumerClient
#from azure.data.tables import TableClient, TableServiceClient, UpdateMode
#from azure.core.exceptions import ResourceModifiedError, ResourceExistsError, ResourceNotFoundError

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

    def __init__(self, **kwargs):
        pass

    def _create_entity_checkpoint(self, checkpoint, **kwargs):
        pass

    def _create_entity_ownership(self, ownership, **kwargs):
        pass

    def _look_entity_ownership(self, ownership, **kwargs):
        pass

    def _look_entity_checkpoint(self, checkpoint, **kwargs):
        pass

    def list_ownership(self, namespace, eventhub, consumergroup, **kwargs):
        pass

    def list_checkpoints(self, namespace, eventhub, consumergroup, **kwargs):
        pass

    def update_checkpoint(self, checkpoint, **kwargs):
        pass

    def upload_ownership(self, ownership, metadata, **kwargs):
        pass

    def claim_one_partition(self, ownership, **kwargs):
        pass

    def claim_ownership(self, ownershiplist, **kwargs):
        pass
