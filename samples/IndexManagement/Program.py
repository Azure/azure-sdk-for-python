import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors

import requests
import traceback
import urllib3
from requests.utils import DEFAULT_CA_BUNDLE_PATH as CaCertPath

import config as cfg

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = "index-samples"

# A typical collection has the following properties within it's indexingPolicy property
#   indexingMode
#   automatic
#   includedPaths
#   excludedPaths
#   
# We can toggle 'automatic' to eiher be True or False depending upon whether we want to have indexing over all columns by default or not.
# indexingMode can be either of consistent, lazy or none
#   
# We can provide options while creating documents. indexingDirective is one such, 
# by which we can tell whether it should be included or excluded in the index of the parent collection.
# indexingDirective can be either 'Include', 'Exclude' or 'Default'


# To run this Demo, please provide your own CA certs file or download one from
#     http://curl.haxx.se/docs/caextract.html
# Setup the certificate file in .pem format. 
# If you still get an SSLError, try disabling certificate verification and suppress warnings

def ObtainClient():
    connection_policy = documents.ConnectionPolicy()
    connection_policy.SSLConfiguration = documents.SSLConfiguration()
    # Try to setup the cacert.pem
    # connection_policy.SSLConfiguration.SSLCaCerts = CaCertPath
    # Else, disable verification
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    connection_policy.SSLConfiguration.SSLCaCerts = False

    return document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY}, connection_policy)

def test_ssl_connection():
    client = ObtainClient()
    # Read databases after creation.
    try:
        databases = list(client.ReadDatabases())
        print(databases)
        return True
    except requests.exceptions.SSLError as e:
        print("SSL error occured. ", e)
    except OSError as e:
        print("OSError occured. ", e)
    except Exception as e:
        print(traceback.format_exc())
    return False

def GetDatabaseLink(database_id):
    return "dbs" + "/" + database_id

def GetCollectionLink(database_id, collection_id):
    return GetDatabaseLink(database_id) +  "/" + "colls" + "/" +  collection_id

def GetDocumentLink(database_id, collection_id, document_id):
    return GetCollectionLink(database_id, collection_id) + "/" + "docs" + "/" + document_id

# Query for Entity / Entities 
def Query_Entities(client, entity_type, id = None, parent_link = None):
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
                entities = list(client.ReadDatabases())
            else:
                entities = list(client.QueryDatabases(find_entity_by_id_query))

        elif entity_type == 'collection':
            if parent_link == None:
                raise ValueError('Database link not provided to search collection(s)')
            if id == None:
                entities = list(client.ReadCollections(parent_link))
            else:
                entities = list(client.QueryCollections(parent_link, find_entity_by_id_query))

        elif entity_type == 'document':
            if parent_link == None:
                raise ValueError('Database / Collection link not provided to search document(s)')
            if id == None:
                entities = list(client.ReadDocuments(parent_link))
            else:
                entities = list(client.QueryDocuments(parent_link, find_entity_by_id_query))
    except errors.DocumentDBError as e:
        print("The following error occured while querying for the entity / entities ", entity_type, id if id != None else "")
        print(e)
        raise
    if id == None:
        return entities
    if len(entities) == 1:
        return entities[0]
    return None

def CreateDatabaseIfNotExists(client, database_id):
    try:
        database = Query_Entities(client, 'database', id = database_id)
        if database == None:
            database = client.CreateDatabase({"id": database_id})
        return database
    except errors.DocumentDBError as e:
        if e.status_code == 409: # Move these constants to an enum
            pass
        else: 
            raise errors.HTTPFailure(e.status_code)

def DeleteCollectionIfExists(client, database_id, collection_id):
    try:
        collection_link = GetCollectionLink(database_id, collection_id)
        
        client.DeleteCollection(collection_link)
        print('Collection with id \'{0}\' was deleted'.format(collection_id))
    except errors.DocumentDBError as e:
        if e.status_code == 404:
            pass
        elif e.status_code == 400:
            print("Bad request for collection link", collection_link)
            raise
        else:
            raise

def print_dictionary_items(dict):
    for k, v in dict.items():
        print("{:<15}".format(k), v)
    print()

def FetchAllDatabases(client):
    databases = Query_Entities(client, 'database')
    print("-" * 41)
    print("-" * 41)
    for db in databases:
        print_dictionary_items(db)
        print("-" * 41)

def QueryDocumentsWithCustomQuery(client, collection_link, query_with_optional_parameters, message = "Document(s) found by query: "):
    try:
        results = list(client.QueryDocuments(collection_link, query_with_optional_parameters))
        print(message)
        for doc in results:
            print(doc)
        return results
    except errors.DocumentDBError as e:
        if e.status_code == 404:
            print("Document doesn't exist")
        elif e.status_code == 400:
            # Can occur when we are trying to query on excluded paths
            print("Bad Request exception occured: ", e)
            pass
        else:
            raise
    finally:
        print()

def ExplicitlyExcludeFromIndex(client, database_id):
    """ The default index policy on a DocumentCollection will AUTOMATICALLY index ALL documents added.
        There may be scenarios where you want to exclude a specific doc from the index even though all other 
        documents are being indexed automatically. 
        This method demonstrates how to use an index directive to control this

    """
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)

        # Create a collection with default index policy (i.e. automatic = true)
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID})
        print(created_collection)

        print("\n" + "-" * 25 + "\n1. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # Create a document and query on it immediately.
        # Will work as automatic indexing is still True
        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc = client.CreateDocument(collection_link, { "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        # Now, create a document but this time explictly exclude it from the collection using IndexingDirective
        # Then query for that document
        # Shoud NOT find it, because we excluded it from the index
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        doc2 = client.CreateDocument(collection_link, { "id" : "doc2", "orderId" : "order2" }, {'indexingDirective' : documents.IndexingDirective.Exclude})
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
                }
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        docRead = client.ReadDocument(GetDocumentLink(database_id, COLLECTION_ID, "doc2"))
        print("Document read by ID: \n", docRead["id"])

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")
    
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def UseManualIndexing(client, database_id):
    """The default index policy on a DocumentCollection will AUTOMATICALLY index ALL documents added.
       There may be cases where you can want to turn-off automatic indexing and only selectively add only specific documents to the index. 
       This method demonstrates how to control this by setting the value of automatic within indexingPolicy to False

    """
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)
        
        # Create a collection with manual (instead of automatic) indexing
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID, "indexingPolicy" : { "automatic" : False} })
        print(created_collection)

        print("\n" + "-" * 25 + "\n2. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # Create a document
        # Then query for that document
        # We should find nothing, because automatic indexing on the collection level is False
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc = client.CreateDocument(collection_link, { "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        docRead = client.ReadDocument(GetDocumentLink(database_id, COLLECTION_ID, "doc1"))
        print("Document read by ID: \n", docRead["id"])

        # Now create a document, passing in an IndexingDirective saying we want to specifically index this document
        # Query for the document again and this time we should find it because we manually included the document in the index
        doc2 = client.CreateDocument(collection_link, { "id" : "doc2", "orderId" : "order2" }, {'indexingDirective' : documents.IndexingDirective.Include})
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
            }
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")

    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def ExcludePathsFromIndex(client, database_id):
    """The default behavior is for DocumentDB to index every attribute in every document automatically.
       There are times when a document contains large amounts of information, in deeply nested structures
       that you know you will never search on. In extreme cases like this, you can exclude paths from the 
       index to save on storage cost, improve write performance and also improve read performance because the index is smaller
       
       This method demonstrates how to set excludedPaths within indexingPolicy
    """
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)

        doc_with_nested_structures = {
            "id" : "doc1",
            "foo" : "bar",
            "metaData" : "meta",
            "subDoc" : { "searchable" : "searchable", "nonSearchable" : "value" },
            "excludedNode" : { "subExcluded" : "something",  "subExcludedNode" : { "someProperty" : "value" } }
            }
        collection_to_create = { "id" : COLLECTION_ID ,
                                "indexingPolicy" : 
                                { 
                                    "includedPaths" : [ {'path' : "/*"} ], # Special mandatory path of "/*" required to denote include entire tree
                                    "excludedPaths" : [ {'path' : "/metaData/*"}, # exclude metaData node, and anything under it
                                                        {'path' : "/subDoc/nonSearchable/*"}, # exclude ONLY a part of subDoc    
                                                        {'path' : "/\"excludedNode\"/*"} # exclude excludedNode node, and anything under it
                                                      ]
                                    } 
                                }
        print(collection_to_create)
        print(doc_with_nested_structures)
        # Create a collection with the defined properties
        # The effect of the above IndexingPolicy is that only id, foo, and the subDoc/searchable are indexed
        created_collection = client.CreateCollection(database_link, collection_to_create)
        print(created_collection)
        print("\n" + "-" * 25 + "\n4. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # The effect of the above IndexingPolicy is that only id, foo, and the subDoc/searchable are indexed
        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc = client.CreateDocument(collection_link, doc_with_nested_structures)
        print("\n" + "-" * 25 + "Document doc1 created with nested structures" +  "-" * 25)
        print(doc)

        # Querying for a document on either metaData or /subDoc/subSubDoc/someProperty > fail because these paths were excluded and they raise a BadRequest(400) Exception
        query = {"query": "SELECT * FROM r WHERE r.metaData=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "meta" }]}
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.nonSearchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        query = {"query": "SELECT * FROM r WHERE r.excludedNode.subExcludedNode.someProperty=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        # Querying for a document using foo, or even subDoc/searchable > succeed because they were not excluded
        query = {"query": "SELECT * FROM r WHERE r.foo=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "bar" }]}
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.searchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "searchable" }]}
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")

    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def RangeScanOnHashIndex(client, database_id):
    """When a range index is not available (i.e. Only hash or no index found on the path), comparisons queries can still 
       be performed as scans using Allow scan request headers passed through options

       This method demonstrates how to force a scan when only hash indexes exist on the path

       ===== Warning=====
       This was made an opt-in model by design. 
       Scanning is an expensive operation and doing this will have a large impact 
       on RequstUnits charged for an operation and will likely result in queries being throttled sooner.
    """
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)

        # Force a range scan operation on a hash indexed path
        collection_to_create = { "id" : COLLECTION_ID ,
                                "indexingPolicy" : 
                                { 
                                    "includedPaths" : [ {'path' : "/"} ],
                                    "excludedPaths" : [ {'path' : "/length/*"} ] # exclude length
                                    } 
                                }
        created_collection = client.CreateCollection(database_link, collection_to_create)
        print(created_collection)
        print("\n" + "-" * 25 + "\n5. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc1 = client.CreateDocument(collection_link, { "id" : "dyn1", "length" : 10, "width" : 5, "height" : 15 })
        doc2 = client.CreateDocument(collection_link, { "id" : "dyn2", "length" : 7, "width" : 15 })
        doc3 = client.CreateDocument(collection_link, { "id" : "dyn3", "length" : 2 })
        print("Three docs created with ids : ", doc1["id"], doc2["id"], doc3["id"])

        # Query for length > 5 - fail, this is a range based query on a Hash index only document
        query = { "query": "SELECT * FROM r WHERE r.length > 5" }
        QueryDocumentsWithCustomQuery(client, collection_link, query)

        # Now add IndexingDirective and repeat query
        # expect 200 OK because now we are explicitly allowing scans in a query
        # using the enableScanInQuery directive
        QueryDocumentsWithCustomQuery(client, collection_link, query)
        results = list(client.QueryDocuments(collection_link, query, {"enableScanInQuery" : True}))
        print("Printing documents queried by range by providing enableScanInQuery = True")
        for doc in results: print(doc["id"])

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def UseRangeIndexesOnStrings(client, database_id):
    """Showing how range queries can be performed even on strings.

    """
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)

        # Use range indexes on strings
        
        # This is how you can specify a range index on strings (and numbers) for all properties.
        # This is the recommended indexing policy for collections. i.e. precision -1
        indexingPolicy = { 
            'indexingPolicy': {
                'includedPaths': [
                    {
                        'indexes': [
                            {
                                'kind': documents.IndexKind.Range,
                                'dataType': documents.DataType.String,
                                'precision': -1
                            }
                        ]
                    }
                ]
            }
        }

        # For demo purposes, we are going to use the default (range on numbers, hash on strings) for the whole document (/* )
        # and just include a range index on strings for the "region".
        collection_definition = {
            'id': COLLECTION_ID,
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

        created_collection = client.CreateCollection(database_link, collection_definition)
        print(created_collection)
        print("\n" + "-" * 25 + "\n6. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc1 = client.CreateDocument(collection_link, { "id" : "doc1", "region" : "USA" })
        doc2 = client.CreateDocument(collection_link, { "id" : "doc2", "region" : "UK" })
        doc3 = client.CreateDocument(collection_link, { "id" : "doc3", "region" : "Armenia" })
        doc4 = client.CreateDocument(collection_link, { "id" : "doc4", "region" : "Egypt" })

        # Now ordering against region is allowed. You can run the following query
        query = { "query" : "SELECT * FROM r ORDER BY r.region" }
        message = "Documents ordered by region"
        QueryDocumentsWithCustomQuery(client, collection_link, query, message)

        # You can also perform filters against string comparison like >= 'UK'. Note that you can perform a prefix query, 
        # the equivalent of LIKE 'U%' (is >= 'U' AND < 'U')
        query = { "query" : "SELECT * FROM r WHERE r.region >= 'U'" }
        message = "Documents with region begining with U"
        QueryDocumentsWithCustomQuery(client, collection_link, query, message)

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def PerformIndexTransformations(client, database_id):
    try:
        DeleteCollectionIfExists(client, database_id, COLLECTION_ID)
        database_link = GetDatabaseLink(database_id)
        # collections = Query_Entities(client, 'collection', parent_link = database_link)
        # print(collections)

        # Create a collection with default indexing policy
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID})
        print(created_collection)

        print("\n" + "-" * 25 + "\n7. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # Insert some documents
        collection_link = GetCollectionLink(database_id, COLLECTION_ID)
        doc1 = client.CreateDocument(collection_link, { "id" : "dyn1", "length" : 10, "width" : 5, "height" : 15 })
        doc2 = client.CreateDocument(collection_link, { "id" : "dyn2", "length" : 7, "width" : 15 })
        doc3 = client.CreateDocument(collection_link, { "id" : "dyn3", "length" : 2 })
        print("Three docs created with ids : ", doc1["id"], doc2["id"], doc3["id"], " with indexing mode", created_collection['indexingPolicy']['indexingMode'])

        # Switch to use string & number range indexing with maximum precision.
        print("Changing to string & number range indexing with maximum precision (needed for Order By).")

        created_collection['indexingPolicy']['includedPaths'][0]['indexes'] = [{
            'kind': documents.IndexKind.Range, 
            'dataType': documents.DataType.String, 
            'precision': -1
        }]

        created_collection = client.ReplaceCollection(collection_link, created_collection)

        # Check progress and wait for completion - should be instantaneous since we have only a few documents, but larger
        # collections will take time.
        print_dictionary_items(created_collection["indexingPolicy"])

        # Now exclude a path from indexing to save on storage space.
        print("Now excluding the path /length/ to save on storage space")
        created_collection['indexingPolicy']['excludedPaths'] = [{"path" : "/length/*"}]

        created_collection = client.ReplaceCollection(collection_link, created_collection)
        print_dictionary_items(created_collection["indexingPolicy"])

        # Cleanup
        client.DeleteCollection(collection_link)
        print("\n")
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def RunIndexDemo():
    try:
        client = ObtainClient()
        FetchAllDatabases(client)

        # Create database if doesn't exist already.
        created_db = CreateDatabaseIfNotExists(client, DATABASE_ID)
        print(created_db)

        # 1. Exclude a document from the index
        ExplicitlyExcludeFromIndex(client, DATABASE_ID)

        # 2. Use manual (instead of automatic) indexing
        UseManualIndexing(client, DATABASE_ID)

        # 4. Exclude specified document paths from the index
        ExcludePathsFromIndex(client, DATABASE_ID)

        # 5. Force a range scan operation on a hash indexed path
        RangeScanOnHashIndex(client, DATABASE_ID)

        # 6. Use range indexes on strings
        UseRangeIndexesOnStrings(client, DATABASE_ID)

        # 7. Perform an index transform
        PerformIndexTransformations(client, DATABASE_ID)

    except errors.DocumentDBError as e:
        raise

if __name__ == '__main__':
    print("Hello!")
    for i in [HOST, MASTER_KEY, DATABASE_ID, COLLECTION_ID] : print(i)
    if test_ssl_connection() == True:
        RunIndexDemo()