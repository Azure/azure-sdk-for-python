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
# We can toggle 'automatic' to eiher be True or False depending upon iwhether we want to have indexing over all columns by default or not.
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

class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

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

def DeleteCollectionIfExists(client, database_link, collection_id):
    try:
        collection_link = "dbs/{0}".format(DATABASE_ID) + "/" + 'colls/{0}'.format(collection_id)
        #collection_link =  database_link +  'colls/{0}'.format(collection_id) 
        # having some trouble with this format of querying, raised an issue
        # https://github.com/Azure/azure-documentdb-python/issues/106
        
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

def FetchAllDatabases(client):
    databases = Query_Entities(client, 'database')
    print("-" * 41)
    print("-" * 41)
    for db in databases:
        print_dictionary_items(db)
        print("-" * 41)

def QueryDocumentsWithCustomQuery(client, collection_link, query_with_optional_parameters):
    try:
        results = list(client.QueryDocuments(collection_link, query_with_optional_parameters))
        print("Document found by query: ")
        print(results)
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

def ExplicitlyExcludeFromIndex(client, database_link):
    """ The default index policy on a DocumentCollection will AUTOMATICALLY index ALL documents added.
        There may be scenarios where you want to exclude a specific doc from the index even though all other 
        documents are being indexed automatically. 
        This method demonstrates how to use an index directive to control this

    """
    try:
        DeleteCollectionIfExists(client, database_link, COLLECTION_ID)
        collections = Query_Entities(client, 'collection', parent_link = database_link)
        print(collections)

        # Create a collection with default index policy (i.e. automatic = true)
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID})
        print(created_collection)

        print("-" * 25 + "\n1. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # Create a document and query on it immediately.
        # Will work as automatic indexing is still True
        doc = client.CreateDocument(created_collection["_self"], { "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        # Now, create a document but this time explictly exclude it from the collection using IndexingDirective
        # Then query for that document
        # Shoud NOT find it, because we excluded it from the index
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        doc2 = client.CreateDocument(created_collection["_self"], { "id" : "doc2", "orderId" : "order2" }, {'indexingDirective' : documents.IndexingDirective.Exclude})
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
                }
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        docRead = client.ReadDocument(doc2["_self"])
        print("Document read by ID: \n", docRead["id"])

        # Cleanup
        client.DeleteCollection(created_collection["_self"])
        print("\n")
    
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def UseManualIndexing(client, database_link):
    """The default index policy on a DocumentCollection will AUTOMATICALLY index ALL documents added.
       There may be cases where you can want to turn-off automatic indexing and only selectively add only specific documents to the index. 
       This method demonstrates how to control this by setting the value of automatic within indexingPolicy to False

    """
    try:
        DeleteCollectionIfExists(client, database_link, COLLECTION_ID)
        collections = Query_Entities(client, 'collection', parent_link = database_link)
        print(collections)
        
        # Create a collection with manual (instead of automatic) indexing
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID, "indexingPolicy" : { "automatic" : False} })
        print(created_collection)

        print("-" * 25 + "\n2. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # Create a document
        # Then query for that document
        # We should find nothing, because automatic indexing on the collection level is False
        # BUT, the document is there and doing a ReadDocument by Id will prove it
        doc = client.CreateDocument(created_collection["_self"], { "id" : "doc1", "orderId" : "order1" })
        print("\n" + "-" * 25 + "Document doc1 created with order1" +  "-" * 25)
        print(doc)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order1" } ]
            }
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        docRead = client.ReadDocument(doc["_self"])
        print("Document read by ID: \n", docRead["id"])

        # Now create a document, passing in an IndexingDirective saying we want to specifically index this document
        # Query for the document again and this time we should find it because we manually included the document in the index
        doc2 = client.CreateDocument(created_collection["_self"], { "id" : "doc2", "orderId" : "order2" }, {'indexingDirective' : documents.IndexingDirective.Include})
        print("\n" + "-" * 25 + "Document doc2 created with order2" +  "-" * 25)
        print(doc2)

        query = {
                "query": "SELECT * FROM r WHERE r.orderId=@orderNo",
                "parameters": [ { "name":"@orderNo", "value": "order2" } ]
            }
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        # Cleanup
        client.DeleteCollection(created_collection["_self"])
        print("\n")

    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def UseLazyIndexing(client, database_link):
    """DocumentDB offers synchronous (consistent) and asynchronous (lazy) index updates. 
        By default, the index is updated synchronously on each insert, replace or delete of a document to the collection. 
        There are times when you might want to configure certain collections to update their index asynchronously. 
        Lazy indexing boosts write performance and is ideal for bulk ingestion scenarios for primarily read-heavy collections
        It is important to note that you might get inconsistent reads whilst the writes are in progress,
        However once the write volume tapers off and the index catches up, then reads continue as normal
        
        This method demonstrates how to switch IndexMode to Lazy

    """
    try:
        DeleteCollectionIfExists(client, database_link, COLLECTION_ID)
        collections = Query_Entities(client, 'collection', parent_link = database_link)
        print(collections)
        
        # Create a collection with lazy (instead of consistent) indexing
        created_collection = client.CreateCollection(database_link, {"id" : COLLECTION_ID, "indexingPolicy" : {"indexingMode" : documents.IndexingMode.Lazy} })
        print(created_collection)

        print("-" * 25 + "\n3. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # it is very difficult to demonstrate lazy indexing as you only notice the difference under sustained heavy write load
        # because we're using an S1 collection in this demo we'd likely get throttled long before we were able to replicate sustained high throughput
        # which would give the index time to catch-up.

        # Cleanup
        client.DeleteCollection(created_collection["_self"])
        print("\n")

    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def ExcludePathsFromIndex(client, database_link):
    """The default behavior is for DocumentDB to index every attribute in every document automatically.
       There are times when a document contains large amounts of information, in deeply nested structures
       that you know you will never search on. In extreme cases like this, you can exclude paths from the 
       index to save on storage cost, improve write performance and also improve read performance because the index is smaller
       
       This method demonstrates how to set excludedPaths within indexingPolicy
    """
    try:
        DeleteCollectionIfExists(client, database_link, COLLECTION_ID)
        collections = Query_Entities(client, 'collection', parent_link = database_link)
        print(collections)

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
        print("-" * 25 + "\n4. Collection created with index policy")
        print_dictionary_items(created_collection["indexingPolicy"])

        # The effect of the above IndexingPolicy is that only id, foo, and the subDoc/searchable are indexed
        doc = client.CreateDocument(created_collection["_self"], doc_with_nested_structures)
        print("\n" + "-" * 25 + "Document doc1 created with nested structures" +  "-" * 25)
        print(doc)

        # Querying for a document on either metaData or /subDoc/subSubDoc/someProperty > fail because these paths were excluded and they raise a BadRequest(400) Exception
        query = {"query": "SELECT * FROM r WHERE r.metaData=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "meta" }]}
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.nonSearchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        query = {"query": "SELECT * FROM r WHERE r.excludedNode.subExcludedNode.someProperty=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "value" }]}
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        # Querying for a document using foo, or even subDoc/searchable > succeed because they were not excluded
        query = {"query": "SELECT * FROM r WHERE r.foo=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "bar" }]}
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        query = {"query": "SELECT * FROM r WHERE r.subDoc.searchable=@desiredValue", "parameters" : [{ "name":"@desiredValue", "value": "searchable" }]}
        QueryDocumentsWithCustomQuery(client, created_collection["_self"], query)

        # Cleanup
        client.DeleteCollection(created_collection["_self"])
        print("\n")

    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def RangeScanOnHashIndex(client, database_link):
    """When a range index is not available (i.e. Only hash or no index found on the path), comparisons queries can still 
       be performed as scans using Allow scan request headers passed through options

       This method demonstrates how to force a scan when only hash indexes exist on the path

       ===== Warning=====
       This was made an opt-in model by design. 
       Scanning is an expensive operation and doing this will have a large impact 
       on RequstUnits charged for an operation and will likely result in queries being throttled sooner.
    """
    try:
        DeleteCollectionIfExists(client, database_link, COLLECTION_ID)
        collections = Query_Entities(client, 'collection', parent_link = database_link)
        print(collections)

        # Cleanup
        client.DeleteCollection(created_collection["_self"])
        print("\n")
    except errors.DocumentDBError as e:
        if e.status_code == 409:
            print("Entity already exists")
        elif e.status_code == 404:
            print("Entity doesn't exist")
        else:
            raise

def RunIndexDemo():
    with IDisposable(ObtainClient()) as client:
        try:
            FetchAllDatabases(client)

            # Create database if doesn't exist already.
            created_db = CreateDatabaseIfNotExists(client, DATABASE_ID)
            print(created_db)

            # 1. Exclude a document from the index
            ExplicitlyExcludeFromIndex(client, created_db["_self"])

            # 2. Use manual (instead of automatic) indexing
            UseManualIndexing(client, created_db["_self"])

            # 3. Use lazy (instead of consistent) indexing
            UseLazyIndexing(client, created_db["_self"])

            # 4. Exclude specified document paths from the index
            ExcludePathsFromIndex(client, created_db["_self"])

            # 5. Force a range scan operation on a hash indexed path
            RangeScanOnHashIndex(client, created_db["_self"])

        except errors.DocumentDBError as e:
            raise


if __name__ == '__main__':
    print("Hello!")
    for i in [HOST, MASTER_KEY, DATABASE_ID, COLLECTION_ID] : print(i)
    if test_ssl_connection() == True:
        RunIndexDemo()