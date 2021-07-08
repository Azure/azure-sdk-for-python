from typing import Sequence
from azure.data.tables import TableClient
from collections import defaultdict
from azure.eventhub.aio import CheckpointStore 
from azure.data.tables import TableServiceClient
from datetime import datetime
from azure.data.tables import UpdateMode
from azure.eventhub.aio import EventHubConsumerClient
from azure.core.exceptions import ResourceModifiedError, ResourceExistsError, ResourceNotFoundError 

class TableCheckpointStore:
    """A CheckpointStore that uses Azure Table Storage to store the partition ownership and checkpoint data.
    This class implements methods list_ownership, claim_ownership, update_checkpoint and list_checkpoints that are
    defined in class azure.eventhub.aio.CheckpointStore of package azure-eventhub.
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

    def __init__(self):
        # type(str, str, Optional[Any], Any) -> None
        self.table_service_client = TableServiceClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=josuegstorageaccount;AccountKey=QWw2cDNY0IygiCDbOHgR3/PNYgSOXNWsZgRgRANGbpLLZwrufkeR3IvSRD9wwuyT3sbe6uj99kZOMBvHpFwB7Q==;EndpointSuffix=core.windows.net")
        self.table_client = self.table_service_client.get_table_client(table_name="firstTable")
        eventhubnamespaceconnectionstring = "Endpoint=sb://josuegarciatable.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=eB0jgMTH4zpu0uQEhUAOpTc8i1MsEzdbc0PxrjPKkVc="
        eventhubname = "my-demo"
        #client = EventHubConsumerClient.from_connection_string(eventhubnamespaceconnectionstring , consumer_group="$Default", eventhub_name=eventhubname, checkpoint_store=self.table_client)
        """self._table_client = kwargs.pop("table_client", None)
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
        self._cached_table_clients = defaultdict()  # type: Dict[str, TableClient]"""
    
    def create_the_entity_checkpoint(self,eventhubname,namespace,consumergroup,partition_id,offset,sequencenumber):
        x = datetime.now()
        currenttime = x.strftime("%I")+ ':' + x.strftime("%M") + ' ' + x.strftime("%p")
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'Consumergroup': consumergroup,
            u'Namespace': namespace,
            u'Eventhubname': eventhubname,
            u'Partition_id': partition_id,
            u'offset' : offset,
            u'sequencenumber' : sequencenumber,
            u'owner_id' : None,
            u'last_modified_time' : None,
        }
        my_new_entity['RowKey'] = my_new_entity['Partition_id'] 
        my_new_entity['PartitionKey'] = my_new_entity['Eventhubname'] + ' ' + my_new_entity['Namespace'] + ' ' + my_new_entity['Consumergroup'] + ' ' + 'Checkpoint'
        new_entity = self.table_client.create_entity(entity=my_new_entity)
    
    def create_the_entity_ownership(self,eventhubname,namespace,consumergroup,partition_id,owner_id,time):
        my_new_entity = {
            u'PartitionKey': u'',
            u'RowKey': u'',
            u'Consumergroup': consumergroup,
            u'Namespace': namespace,
            u'Eventhubname': eventhubname,
            u'Partition_id': partition_id,
            u'owner_id' : owner_id,
            u'last_modified_time' : time,
        }
        my_new_entity['RowKey'] = my_new_entity['Partition_id'] 
        my_new_entity['PartitionKey'] = my_new_entity['Eventhubname'] + ' ' + my_new_entity['Namespace'] + ' ' + my_new_entity['Consumergroup'] + ' ' + 'Ownership'
        new_entity = self.table_client.create_entity(entity=my_new_entity)

    def list_ownership(self,eventhub,namespace,consumergroup):
        thePartitionKey = eventhub + ' ' + namespace +' ' + consumergroup+ ' '+ 'Ownership'
        my_filter = "PartitionKey eq '"+ thePartitionKey + "'"
        entities = self.table_client.query_entities(my_filter)
        ownershiplist = []
        for entity in entities:
                dic = {}
                dic[u'Namespace'] = entity[u'Namespace']
                dic[u'Eventhubname'] = entity[u'Eventhubname']
                dic[u'Consumergroup'] = entity[u'Consumergroup']
                dic[u'Partition_id'] = entity[u'Partition_id']
                dic[u'owner_id'] = entity[u'owner_id']
                dic[u'last_modified_time'] = entity[u'last_modified_time']
                dic[u'etag'] = entity.metadata.get('etag')
                ownershiplist.append(dic)
        return ownershiplist

    def list_checkpoints(self,eventhub,namespace,consumergroup):
        thePartitionKey = eventhub + ' ' + namespace +' ' + consumergroup + ' '+ 'Checkpoint'
        my_filter = "PartitionKey eq '"+ thePartitionKey + "'"
        entities = self.table_client.query_entities(my_filter)
        checkpointslist = []
        for entity in entities:
                dic = {}
                dic[u'Namespace'] = entity[u'Namespace']
                dic[u'Eventhubname'] = entity[u'Eventhubname']
                dic[u'Consumergroup'] = entity[u'Consumergroup']
                dic[u'Partition_id'] = entity[u'Partition_id']
                dic[u'sequencenumber'] = entity[u'sequencenumber']
                dic[u'offset'] = entity[u'offset']
                checkpointslist.append(dic)
        return checkpointslist

    def update_checkpoint(self,checkpoint):
        try:
            thePartitionKey = checkpoint['Eventhubname'] + ' ' + checkpoint['Namespace'] +' ' + checkpoint['Consumergroup'] + ' '+ "Checkpoint"
            therowkey = checkpoint['Partition_id']
            theentity = self.table_client.get_entity(partition_key=thePartitionKey, row_key=therowkey)
            theentity[u"offset"] = checkpoint["offset"]
            theentity[u"sequencenumber"] = checkpoint["sequencenumber"]
            self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=theentity)
        except ResourceNotFoundError:
            self.create_the_entity_checkpoint(checkpoint['Eventhubname'],checkpoint['Namespace'],checkpoint['Consumergroup'],checkpoint['Partition_id'],checkpoint['offset'],checkpoint['sequencenumber'])


    def upload_ownership(self,ownership,metadata):
        try:
            thePartitionKey = ownership['Eventhubname'] + ' ' + ownership['Namespace'] +' ' + ownership['Consumergroup'] + ' '+ "Ownership"
            therowkey = ownership['Partition_id']
            theentity = self.table_client.get_entity(partition_key=thePartitionKey, row_key=therowkey)
            theentity[u"owner_id"] = ownership["owner_id"]
            theentity[u"last_modified_time"] = datetime.now()
            self.table_client.update_entity(mode=UpdateMode.REPLACE, entity=theentity)
        except ResourceNotFoundError:
            self.create_the_entity_ownership(ownership['Eventhubname'],ownership['Namespace'],ownership['Consumergroup'],ownership['Partition_id'],ownership['owner_id'],datetime.now())


    def claim_one_partition(self,ownership):
            partition_id = ownership["Partition_id"]
            namespace = ownership["Namespace"]
            eventhub_name = ownership["Eventhubname"]
            consumer_group = ownership["Consumergroup"]
            owner_id = ownership["owner_id"]
            metadata = {"ownerid": owner_id}
            self.upload_ownership(ownership,metadata)

    def claim_ownership(self,ownershiplist):
            for x in ownershiplist:
                    self.claim_one_partition(x)


"""Example for creating an entity:
start = TableCheckpointStore()
start.create_the_entity('Green-eventhub','Green-storage','$default','5')"""

#Example for list_ownership:
start = TableCheckpointStore()
print(start.list_ownership(input("what is your eventhub called? "),input("what is your namespace called? "),input("what is your consumer group? ")))

#Example for list_checkpoint:
#start = TableCheckpointStore()
#print(start.list_checkpoints(input("what is your eventhub called? "),input("what is your namespace called? "),input("what is your consumer group? ")))

#Example for update_checkpoint:
#start = TableCheckpointStore()
#some = {'Namespace': 'Green-storage', 'Eventhubname': 'Green-eventhub', 'Consumergroup': '$default', 'Partition_id': '232', 'sequencenumber': '21', 'offset': '1220'}
#new = start.update_checkpoint(some)


#thenewownershiplist = [{'Namespace': 'Green-storage', 'Eventhubname': 'Green-eventhub', 'Consumergroup': '$default', 'Partition_id': '4', 'owner_id': 'Rob', 
#'last_modified_time': None},{'Namespace': 'Green-storage', 'Eventhubname': 'Green-eventhub', 'Consumergroup': '$default', 'Partition_id': '4', 'owner_id': 'Job', 
#'last_modified_time': None}]
#start = TableCheckpointStore()
#start.claim_ownership(thenewownershiplist)