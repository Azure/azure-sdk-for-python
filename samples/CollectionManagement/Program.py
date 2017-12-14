import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors

import config as cfg

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure Cosmos DB account - 
#    https://azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure DocumentDB PyPi package - 
#    https://pypi.python.org/pypi/pydocumentdb/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Collection resource for Azure Cosmos DB
# 
# 1. Query for Collection
#  
# 2. Create Collection
#    2.1 - Basic Create
#    2.2 - Create collection with custom IndexPolicy
#    2.3 - Create collection with offerType set
#
# 3. Manage Collection OfferType
#    3.1 - Get Collection performance tier
#    3.2 - Change performance tier
#
# 4. Get a Collection by its Id property
#
# 5. List all Collection resources in a Database
#
# 6. Delete Collection
# ----------------------------------------------------------------------------------------------------------
# Note - 
# 
# Running this sample will create (and delete) multiple DocumentCollections on your account. 
# Each time a DocumentCollection is created the account will be billed for 1 hour of usage based on
# the performance tier of that account. 
# ----------------------------------------------------------------------------------------------------------

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = cfg.settings['collection_id']

database_link = 'dbs/' + DATABASE_ID

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

class CollectionManagement:
    @staticmethod
    def find_collection(client, id):
        print('1. Query for Collection')

        collections = list(client.QueryCollections(
            database_link,
            {
                "query": "SELECT * FROM r WHERE r.id=@id",
                "parameters": [
                    { "name":"@id", "value": id }
                ]
            }
        ))

        if len(collections) > 0:
            print('Collection with id \'{0}\' was found'.format(id))
        else:
            print('No collection with id \'{0}\' was found'. format(id))
        
    @staticmethod
    def create_collection(client, id):
        """ Execute the most basic Create of collection. 
        This will create a collection with OfferType = S1 and default indexing policy """

        print("\n2.1 Create Collection - Basic")
        
        try:
            client.CreateCollection(database_link, {"id": id})
            print('Collection with id \'{0}\' created'.format(id))

        except errors.DocumentDBError as e:
            if e.status_code == 409:
               print('A collection with id \'{0}\' already exists'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)               

        print("\n2.2 Create Collection - With custom index policy")
        
        try:
            coll = {
                "id": "collection_custom_index_policy",
                "indexingPolicy": {
                    "indexingMode": "lazy",
                    "automatic": False
                }
            }

            collection = client.CreateCollection(database_link, coll)
            print('Collection with id \'{0}\' created'.format(collection['id']))
            print('IndexPolicy Mode - \'{0}\''.format(collection['indexingPolicy']['indexingMode']))
            print('IndexPolicy Automatic - \'{0}\''.format(collection['indexingPolicy']['automatic']))
            
        except errors.DocumentDBError as e:
            if e.status_code == 409:
               print('A collection with id \'{0}\' already exists'.format(collection['id']))
            else: 
                raise errors.HTTPFailure(e.status_code) 

            
        print("\n2.3 Create Collection - With custom offerType")
        
        try:
            coll = {"id": "collection_custom_offertype"}

            collection = client.CreateCollection(database_link, coll, {'offerType': 'S2'} )
            print('Collection with id \'{0}\' created'.format(collection['id']))
            
        except errors.DocumentDBError as e:
            if e.status_code == 409:
               print('A collection with id \'{0}\' already exists'.format(collection['id']))
            else: 
                raise errors.HTTPFailure(e.status_code) 

    @staticmethod
    def manage_offertype(client, id):
        print("\n3.1 Get Collection Performance tier")
        
        #Collections have offers which are of type S1, S2, or S3. 
        #Each of these determine the performance throughput of a collection. 
        #A Collection is loosely coupled to Offer through the Offer's offerResourceId
        #Offer.offerResourceId == Collection._rid
        #Offer.resource == Collection._self
        
        try:
            # read the collection, so we can get its _self
            collection_link = database_link + '/colls/{0}'.format(id)
            collection = client.ReadCollection(collection_link)

            # now use its _self to query for Offers
            offer = list(client.QueryOffers('SELECT * FROM c WHERE c.resource = \'{0}\''.format(collection['_self'])))[0]
            
            print('Found Offer \'{0}\' for Collection \'{1}\' and its offerType is \'{2}\''.format(offer['id'], collection['_self'], offer['offerType']))

        except errors.DocumentDBError as e:
            if e.status_code == 404:
                print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)

        print("\n3.2 Change OfferType of Collection")
                           
        #The OfferType of a collection controls the throughput allocated to the Collection
        #To increase (or decrease) the throughput of any Collection you need to adjust the Offer.offerType
        #of the Offer record linked to the Collection
        
        #setting it S1, doesn't do anything because by default Collections are created with S1 Offer.offerType
        #just doing it in the sample to demonstrate how to do it and not create resources (and incur costs) we don't need
        #valid values for offerType are (currently) S1, S2 or S3
        offer['offerType'] = 'S2'
        offer = client.ReplaceOffer(offer['_self'], offer)

        print('Replaced Offer. OfferType is now \'{0}\''.format(offer['offerType']))
                                
    @staticmethod
    def read_collection(client, id):
        print("\n4. Get a Collection by id")

        try:
            # All Azure Cosmos DB resources are addressable via a link
            # This link is constructed from a combination of resource hierachy and 
            # the resource id. 
            # Eg. The link for collection with an id of Bar in database Foo would be dbs/Foo/colls/Bar
            collection_link = database_link + '/colls/{0}'.format(id)

            collection = client.ReadCollection(collection_link)
            print('Collection with id \'{0}\' was found, it\'s _self is {1}'.format(collection['id'], collection['_self']))

        except errors.DocumentDBError as e:
            if e.status_code == 404:
               print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)    
    
    @staticmethod
    def list_collections(client):
        print("\n5. List all Collection in a Database")
        
        print('Collections:')
        
        collections = list(client.ReadCollections(database_link))
        
        if not collections:
            return

        for collection in collections:
            print(collection['id'])          
        
    @staticmethod
    def delete_collection(client, id):
        print("\n6. Delete Collection")
        
        try:
           collection_link = database_link + '/colls/{0}'.format(id)
           client.DeleteCollection(collection_link)

           print('Collection with id \'{0}\' was deleted'.format(id))

        except errors.DocumentDBError as e:
            if e.status_code == 404:
               print('A collection with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)   

def run_sample():

    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        try:
            # setup database for this sample
            try:
                client.CreateDatabase({"id": DATABASE_ID})
            
            except errors.DocumentDBError as e:
                if e.status_code == 409:
                   pass
                else: 
                    raise errors.HTTPFailure(e.status_code)
            
            # query for a collection            
            CollectionManagement.find_collection(client, COLLECTION_ID)
            
            # create a collection
            CollectionManagement.create_collection(client, COLLECTION_ID)
            
            # get & change OfferType of collection
            CollectionManagement.manage_offertype(client, COLLECTION_ID)

            # get a collection using its id
            CollectionManagement.read_collection(client, COLLECTION_ID)

            # list all collection on an account
            CollectionManagement.list_collections(client)

            # delete collection by id
            CollectionManagement.delete_collection(client, COLLECTION_ID)

            # cleanup database after sample
            try:
                client.DeleteDatabase(database_link)
            
            except errors.DocumentDBError as e:
                if e.status_code == 404:
                   pass
                else: 
                    raise errors.HTTPFailure(e.status_code)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))
        
        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    try:
        run_sample()

    except Exception as e:
            print("Top level Error: args:{0}, message:{1}".format(e.args,e.message))