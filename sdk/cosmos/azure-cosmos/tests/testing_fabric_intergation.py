from azure.cosmos import PartitionKey, cosmos_client
from tests import fabric_token_credential, test_config


def run_sample():
    print("Running sample")
    fabric_credential = fabric_token_credential.FabricTokenCredential()
    fabric_host = test_config.TestConfig.fabric_host
    client = cosmos_client.CosmosClient(fabric_host, credential=fabric_credential)
    databaseForTest = client.get_database_client("dkunda-fabric-cdb")
    created_collection = databaseForTest.create_container("testing-container", partition_key=PartitionKey("/pk"))
    document_definition = {'id': 'document',
                           'key': 'value',
                           'pk': 'pk'}

    created_document = created_collection.create_item(
        body=document_definition
    )

    assert created_document.get('id'), document_definition.get('id')
    assert created_document.get('key'), document_definition.get('key')

    # read document
    read_document = created_collection.read_item(
        item=created_document.get('id'),
        partition_key=created_document.get('pk')
    )

    assert read_document.get('id'), created_document.get('id')
    assert read_document.get('key'), created_document.get('key')

    # Read document feed doesn't require partitionKey as it's always a cross partition query
    documentlist = list(created_collection.read_all_items())
    assert 1, len(documentlist)

    # replace document
    document_definition['key'] = 'new value'

    replaced_document = created_collection.replace_item(
        item=read_document,
        body=document_definition
    )

    assert replaced_document.get('key'), document_definition.get('key')

    # upsert document(create scenario)
    document_definition['id'] = 'document2'
    document_definition['key'] = 'value2'

    upserted_document = created_collection.upsert_item(body=document_definition)

    assert upserted_document.get('id'), document_definition.get('id')
    assert upserted_document.get('key'), document_definition.get('key')

    documentlist = list(created_collection.read_all_items())
    assert 2, len(documentlist)

    # delete document
    created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('pk'))

    # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
    documentlist = list(created_collection.query_items(
        {
            'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
        }, enable_cross_partition_query=True))
    assert 1, len(documentlist)

    # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
    try:
        list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
            }))
    except Exception:
        pass

    # cross partition query
    documentlist = list(created_collection.query_items(
        query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
        enable_cross_partition_query=True
    ))

    assert 1, len(documentlist)

    # query document by providing the partitionKey value
    documentlist = list(created_collection.query_items(
        query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
        partition_key=replaced_document.get('pk')
    ))

    assert 1, len(documentlist)
    databaseForTest.delete_container(created_collection.id)


if __name__ == '__main__':
    run_sample()
