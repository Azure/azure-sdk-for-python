# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.documents as documents
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import urllib3
from requests.utils import DEFAULT_CA_BUNDLE_PATH as CaCertPath

import asyncio
import config

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = "index-samples"
PARTITION_KEY = PartitionKey(path='/id', kind='Hash')

# A typical container has the following properties within it's indexingPolicy property
#   indexingMode
#   automatic
#   includedPaths
#   excludedPaths
#
# We can toggle 'automatic' to either be True or False depending upon whether we want to have indexing over all columns by default or not.
#
# We can provide options while creating documents. indexingDirective is one such,
# by which we can tell whether it should be included or excluded in the index of the parent container.
# indexingDirective can be either 'Include', 'Exclude' or 'Default'


# To run this Demo, please provide your own CA certs file or download one from
#     http://curl.haxx.se/docs/caextract.html
# Setup the certificate file in .pem format.
# If you still get an SSLError, try disabling certificate verification and suppress warnings

find_entity_by_id_query = {
        "query": "SELECT * FROM r WHERE r.id=@id",
        "parameters": [
            { "name":"@id", "value": id }
        ]
    }

def obtain_client():
    # Try to setup the cacert.pem
    # connection_policy.SSLConfiguration.SSLCaCerts = CaCertPath
    # Else, disable verification
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return CosmosClient(HOST, MASTER_KEY)


# Query for Entity / Entities
async def query_entities(parent, entity_type, id = None):
    find_entity_by_id_query = {
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }
    entities = None
    try:
        if entity_type == 'database':
            if id == None:
                entities = [entity async for entity in parent.list_databases()]
            else:
                entities = [entity async for entity in parent.query_databases(find_entity_by_id_query)]

        elif entity_type == 'container':
            if id == None:
                entities = [entity async for entity in parent.list_containers()]
            else:
                entities = [entity async for entity in parent.query_containers(find_entity_by_id_query)]

        elif entity_type == 'document':
            if id == None:
                entities = [entity async for entity in parent.read_all_items()]
            else:
                entities = [entity async for entity in parent.query_items(find_entity_by_id_query)]
    except exceptions.AzureError as e:
        print("The following error occurred while querying for the entity / entities ", entity_type, id if id != None else "")
        print(e)
        raise
    if id == None:
        return entities
    if len(entities) == 1:
        return entities[0]
    return None


async def delete_container_if_exists(db, container_id):
    try:
        await db.delete_container(container_id)
        print('Container with id \'{0}\' was deleted'.format(container_id))
    except exceptions.CosmosResourceNotFoundError:
        pass
    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 400:
            print("Bad request for container link", container_id)
        raise


def print_dictionary_items(dict):
    for k, v in dict.items():
        print("{:<15}".format(k), v)
    print()


async def fetch_all_databases(client):
    databases = await query_entities(client, 'database')
    print("-" * 41)
    print("-" * 41)
    for db in databases:
        print_dictionary_items(db)
        print("-" * 41)


async def query_documents_with_custom_query(container, query_with_optional_parameters, message = "Document(s) found by query: "):
    try:
        results = container.query_items(query_with_optional_parameters)
        print(message)
        async for doc in results:
            print(doc)
        return results
    except exceptions.CosmosResourceNotFoundError:
        print("Document doesn't exist")
    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 400:
            # Can occur when we are trying to query on excluded paths
            print("Bad Request exception occurred: ", e)
            pass
        else:
            raise
    finally:
        print()


async def explicitly_exclude_from_index(db):
    """ The default index policy on a DocumentContainer will AUTOMATICALLY index ALL documents added.
        There may be scenarios where you want to exclude a specific doc from the index even though all other
        documents are being indexed automatically.
        This method demonstrates how to use an index directive to control this

    """
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        # Create a container with default index policy (i.e. automatic = true)
        created_Container = await db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)
        print(created_Container)

        print("\n" + "-" * 25 + "\n1. Container created with index policy")
        properties = await created_Container.read()
        print_dictionary_items(properties["indexingPolicy"])

        # Create a document and query on it immediately.
        # Will work as automatic indexing is still True
        doc = await created_Container.create_item(body={ "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        await query_documents_with_custom_query(created_Container, query)

        # Now, create a document but this time explicitly exclude it from the container using IndexingDirective
        # Then query for that document
        # Should NOT find it, because we excluded it from the index
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        doc2 = await created_Container.create_item(
            body={ "id" : "doc2", "orderId" : "order2" },
            indexing_directive=documents.IndexingDirective.Exclude
        )
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
                }
        await query_documents_with_custom_query(created_Container, query)

        docRead = await created_Container.read_item(item="doc2", partition_key="doc2")
        print("Document read by ID: \n", docRead["id"])

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def use_manual_indexing(db):
    """The default index policy on a DocumentContainer will AUTOMATICALLY index ALL documents added.
       There may be cases where you can want to turn-off automatic indexing and only selectively add only specific documents to the index.
       This method demonstrates how to control this by setting the value of automatic within indexingPolicy to False

    """
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        # Create a container with manual (instead of automatic) indexing
        created_Container = await db.create_container(
            id=CONTAINER_ID,
            indexing_policy={"automatic" : False},
            partition_key=PARTITION_KEY
        )
        properties = await created_Container.read()
        print(created_Container)

        print("\n" + "-" * 25 + "\n2. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        # Create a document
        # Then query for that document
        # We should find nothing, because automatic indexing on the container level is False
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        doc = await created_Container.create_item(body={ "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        await query_documents_with_custom_query(created_Container, query)

        docRead = await created_Container.read_item(item="doc1", partition_key="doc1")
        print("Document read by ID: \n", docRead["id"])

        # Now create a document, passing in an IndexingDirective saying we want to specifically index this document
        # Query for the document again and this time we should find it because we manually included the document in the index
        doc2 = await created_Container.create_item(
            body={ "id" : "doc2", "orderId" : "order2" },
            indexing_directive=documents.IndexingDirective.Include
        )
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
            }
        await query_documents_with_custom_query(created_Container, query)

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def exclude_paths_from_index(db):
    """The default behavior is for Cosmos to index every attribute in every document automatically.
       There are times when a document contains large amounts of information, in deeply nested structures
       that you know you will never search on. In extreme cases like this, you can exclude paths from the
       index to save on storage cost, improve write performance and also improve read performance because the index is smaller

       This method demonstrates how to set excludedPaths within indexingPolicy
    """
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        doc_with_nested_structures = {
            "id" : "doc1",
            "foo" : "bar",
            "metaData" : "meta",
            "subDoc" : { "searchable" : "searchable", "nonSearchable" : "value" },
            "excludedNode" : { "subExcluded" : "something",  "subExcludedNode" : { "someProperty" : "value" } }
            }
        container_to_create = { "id" : CONTAINER_ID ,
                                "indexingPolicy" :
                                {
                                    "includedPaths" : [ {'path' : "/*"} ], # Special mandatory path of "/*" required to denote include entire tree
                                    "excludedPaths" : [ {'path' : "/metaData/*"}, # exclude metaData node, and anything under it
                                                        {'path' : "/subDoc/nonSearchable/*"}, # exclude ONLY a part of subDoc
                                                        {'path' : "/\"excludedNode\"/*"} # exclude excludedNode node, and anything under it
                                                      ]
                                    }
                                }
        print(container_to_create)
        print(doc_with_nested_structures)
        # Create a container with the defined properties
        # The effect of the above IndexingPolicy is that only id, foo, and the subDoc/searchable are indexed
        created_Container = await db.create_container(
            id=container_to_create['id'],
            indexing_policy=container_to_create['indexingPolicy'],
            partition_key=PARTITION_KEY
        )
        properties = await created_Container.read()
        print(created_Container)
        print("\n" + "-" * 25 + "\n4. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        # The effect of the above IndexingPolicy is that only id, foo, and the subDoc/searchable are indexed
        doc = await created_Container.create_item(body=doc_with_nested_structures)
        print("\n" + "-" * 25 + "Document doc1 created with nested structures" +  "-" * 25)
        print(doc)

        # Querying for a document on either metaData or /subDoc/subSubDoc/someProperty > fail because these paths were excluded and they raise a BadRequest(400) Exception
        query = {"query": "SELECT * FROM r WHERE r.metaData=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "meta" }]}
        await query_documents_with_custom_query(created_Container, query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.nonSearchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        await query_documents_with_custom_query(created_Container, query)

        query = {"query": "SELECT * FROM r WHERE r.excludedNode.subExcludedNode.someProperty=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        await query_documents_with_custom_query(created_Container, query)

        # Querying for a document using foo, or even subDoc/searchable > succeed because they were not excluded
        query = {"query": "SELECT * FROM r WHERE r.foo=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "bar" }]}
        await query_documents_with_custom_query(created_Container, query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.searchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "searchable" }]}
        await query_documents_with_custom_query(created_Container, query)

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def range_scan_on_hash_index(db):
    """When a range index is not available (i.e. Only hash or no index found on the path), comparisons queries can still
       be performed as scans using Allow scan request headers passed through options

       This method demonstrates how to force a scan when only hash indexes exist on the path

       ===== Warning=====
       This was made an opt-in model by design.
       Scanning is an expensive operation and doing this will have a large impact
       on RequestUnits charged for an operation and will likely result in queries being throttled sooner.
    """
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        # Force a range scan operation on a hash indexed path
        container_to_create = { "id" : CONTAINER_ID ,
                                "indexingPolicy" :
                                {
                                    "includedPaths" : [ {'path' : "/"} ],
                                    "excludedPaths" : [ {'path' : "/length/*"} ] # exclude length
                                    }
                                }
        created_Container = await db.create_container(
            id=container_to_create['id'],
            indexing_policy=container_to_create['indexingPolicy'],
            partition_key=PARTITION_KEY
        )
        properties = await created_Container.read()
        print(created_Container)
        print("\n" + "-" * 25 + "\n5. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        doc1 = await created_Container.create_item(body={ "id" : "dyn1", "length" : 10, "width" : 5, "height" : 15 })
        doc2 = await created_Container.create_item(body={ "id" : "dyn2", "length" : 7, "width" : 15 })
        doc3 = await created_Container.create_item(body={ "id" : "dyn3", "length" : 2 })
        print("Three docs created with ids : ", doc1["id"], doc2["id"], doc3["id"])

        # Query for length > 5 - fail, this is a range based query on a Hash index only document
        query = { "query": "SELECT * FROM r WHERE r.length > 5" }
        await query_documents_with_custom_query(created_Container, query)

        # Now add IndexingDirective and repeat query
        # expect 200 OK because now we are explicitly allowing scans in a query
        # using the enableScanInQuery directive
        results = created_Container.query_items(
            query,
            enable_scan_in_query=True
        )
        print("Printing documents queried by range by providing enableScanInQuery = True")
        async for doc in results: print(doc["id"])

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def use_range_indexes_on_strings(db):
    """Showing how range queries can be performed even on strings.

    """
    try:
        await delete_container_if_exists(db, CONTAINER_ID)
        # containers = query_entities(client, 'container', parent_link = database_link)
        # print(containers)

        # Use range indexes on strings

        # This is how you can specify a range index on strings (and numbers) for all properties.
        # This is the recommended indexing policy for containers. i.e. precision -1
        #indexingPolicy = {
        #    'indexingPolicy': {
        #        'includedPaths': [
        #            {
        #                'indexes': [
        #                    {
        #                        'kind': documents.IndexKind.Range,
        #                        'dataType': documents.DataType.String,
        #                        'precision': -1
        #                    }
        #                ]
        #            }
        #        ]
        #    }
        #}

        # For demo purposes, we are going to use the default (range on numbers, hash on strings) for the whole document (/* )
        # and just include a range index on strings for the "region".
        container_definition = {
            'id': CONTAINER_ID,
            'indexingPolicy': {
                'includedPaths': [
                    {
                        'path': '/region/?',
                        'indexes': [
                            {
                                'kind': documents.IndexKind.Range,
                                'dataType': documents.DataType.String,
                                'precision': -1
                            }
                        ]
                    },
                    {
                        'path': '/*'
                    }
                ]
            }
        }

        created_Container = await db.create_container(
            id=container_definition['id'],
            indexing_policy=container_definition['indexingPolicy'],
            partition_key=PARTITION_KEY
        )
        properties = await created_Container.read()
        print(created_Container)
        print("\n" + "-" * 25 + "\n6. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        await created_Container.create_item(body={ "id" : "doc1", "region" : "USA" })
        await created_Container.create_item(body={ "id" : "doc2", "region" : "UK" })
        await created_Container.create_item(body={ "id" : "doc3", "region" : "Armenia" })
        await created_Container.create_item(body={ "id" : "doc4", "region" : "Egypt" })

        # Now ordering against region is allowed. You can run the following query
        query = { "query" : "SELECT * FROM r ORDER BY r.region" }
        message = "Documents ordered by region"
        await query_documents_with_custom_query(created_Container, query, message)

        # You can also perform filters against string comparison like >= 'UK'. Note that you can perform a prefix query,
        # the equivalent of LIKE 'U%' (is >= 'U' AND < 'U')
        query = { "query" : "SELECT * FROM r WHERE r.region >= 'U'" }
        message = "Documents with region begining with U"
        await query_documents_with_custom_query(created_Container, query, message)

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def perform_index_transformations(db):
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        # Create a container with default indexing policy
        created_Container = await db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)
        properties = await created_Container.read()
        print(created_Container)

        print("\n" + "-" * 25 + "\n7. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        # Insert some documents
        doc1 = await created_Container.create_item(body={ "id" : "dyn1", "length" : 10, "width" : 5, "height" : 15 })
        doc2 = await created_Container.create_item(body={ "id" : "dyn2", "length" : 7, "width" : 15 })
        doc3 = await created_Container.create_item(body={ "id" : "dyn3", "length" : 2 })
        print("Three docs created with ids : ", doc1["id"], doc2["id"], doc3["id"], " with indexing mode", properties['indexingPolicy']['indexingMode'])

        # Switch to use string & number range indexing with maximum precision.
        print("Changing to string & number range indexing with maximum precision (needed for Order By).")

        properties['indexingPolicy']['includedPaths'][0]['indexes'] = [{
            'kind': documents.IndexKind.Range,
            'dataType': documents.DataType.String,
            'precision': -1
        }]

        created_Container = await db.replace_container(
            container=created_Container.id,
            partition_key=PARTITION_KEY,
            indexing_policy=properties['indexingPolicy']
        )
        properties = await created_Container.read()

        # Check progress and wait for completion - should be instantaneous since we have only a few documents, but larger
        # containers will take time.
        print_dictionary_items(properties["indexingPolicy"])

        # Now exclude a path from indexing to save on storage space.
        print("Now excluding the path /length/ to save on storage space")
        properties['indexingPolicy']['excludedPaths'] = [{"path" : "/length/*"}]

        created_Container = await db.replace_container(
            container=created_Container.id,
            partition_key=PARTITION_KEY,
            indexing_policy=properties['indexingPolicy']
        )
        properties = await created_Container.read()
        print_dictionary_items(properties["indexingPolicy"])

        # Cleanup
        await db.delete_container(created_Container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def perform_multi_orderby_query(db):
    try:
        await delete_container_if_exists(db, CONTAINER_ID)

        # Create a container with composite indexes
        indexing_policy = {
            "compositeIndexes": [
                [
                    {
                        "path": "/numberField",
                        "order": "ascending"
                    },
                    {
                        "path": "/stringField",
                        "order": "descending"
                    }
                ],
                [
                    {
                        "path": "/numberField",
                        "order": "descending"
                    },
                    {
                        "path": "/stringField",
                        "order": "ascending"
                    },
                    {
                        "path": "/numberField2",
                        "order": "descending"
                    },
                    {
                        "path": "/stringField2",
                        "order": "ascending"
                    }
                ]
            ]
        }

        created_container = await db.create_container(
            id=CONTAINER_ID,
            indexing_policy=indexing_policy,
            partition_key=PARTITION_KEY
        )
        print(created_container)
        properties = await created_container.read()

        print("\n" + "-" * 25 + "\n8. Container created with index policy")
        print_dictionary_items(properties["indexingPolicy"])

        # Insert some documents
        await created_container.create_item(body={"id": "doc1", "numberField": 1, "stringField": "1", "numberField2": 1, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc2", "numberField": 1, "stringField": "1", "numberField2": 1, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc3", "numberField": 1, "stringField": "1", "numberField2": 2, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc4", "numberField": 1, "stringField": "1", "numberField2": 2, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc5", "numberField": 1, "stringField": "2", "numberField2": 1, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc6", "numberField": 1, "stringField": "2", "numberField2": 1, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc7", "numberField": 1, "stringField": "2", "numberField2": 2, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc8", "numberField": 1, "stringField": "2", "numberField2": 2, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc9", "numberField": 2, "stringField": "1", "numberField2": 1, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc10", "numberField": 2, "stringField": "1", "numberField2": 1, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc11", "numberField": 2, "stringField": "1", "numberField2": 2, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc12", "numberField": 2, "stringField": "1", "numberField2": 2, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc13", "numberField": 2, "stringField": "2", "numberField2": 1, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc14", "numberField": 2, "stringField": "2", "numberField2": 1, "stringField2": "2"})
        await created_container.create_item(body={"id": "doc15", "numberField": 2, "stringField": "2", "numberField2": 2, "stringField2": "1"})
        await created_container.create_item(body={"id": "doc16", "numberField": 2, "stringField": "2", "numberField2": 2, "stringField2": "2"})

        print("Query documents and Order by 1st composite index: Ascending numberField and Descending stringField:")

        query = {
                "query": "SELECT * FROM r ORDER BY r.numberField ASC, r.stringField DESC",
                }
        await query_documents_with_custom_query(created_container, query)

        print("Query documents and Order by inverted 2nd composite index -")
        print("Ascending numberField, Descending stringField, Ascending numberField2, Descending stringField2")

        query = {
                "query": "SELECT * FROM r ORDER BY r.numberField ASC, r.stringField DESC, r.numberField2 ASC, r.stringField2 DESC",
                }
        await query_documents_with_custom_query(created_container, query)

        # Cleanup
        await db.delete_container(created_container)
        print("\n")
    except exceptions.CosmosResourceExistsError:
        print("Entity already exists")
    except exceptions.CosmosResourceNotFoundError:
        print("Entity doesn't exist")


async def run_sample():
    try:
        async with obtain_client() as client:
            await fetch_all_databases(client)

            # Create database if doesn't exist already.
            created_db = await client.create_database_if_not_exists(DATABASE_ID)
            print(created_db)

            # 1. Exclude a document from the index
            await explicitly_exclude_from_index(created_db)

            # 2. Use manual (instead of automatic) indexing
            await use_manual_indexing(created_db)

            # 4. Exclude specified document paths from the index
            await exclude_paths_from_index(created_db)

            # 5. Force a range scan operation on a hash indexed path
            await range_scan_on_hash_index(created_db)

            # 6. Use range indexes on strings
            await use_range_indexes_on_strings(created_db)

            # 7. Perform an index transform
            await perform_index_transformations(created_db)

            # 8. Perform Multi Orderby queries using composite indexes
            await perform_multi_orderby_query(created_db)

            print('Sample done, cleaning up sample-generated data')
            await client.delete_database(DATABASE_ID)

    except exceptions.AzureError as e:
        raise e

if __name__ == '__main__':
    asyncio.run(run_sample())
