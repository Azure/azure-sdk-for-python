import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors

import samples.Shared.config as cfg

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure Cosmos account - 
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos PyPi package - 
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure Cosmos
#
# 1. Query for Database (QueryDatabases)
#
# 2. Create Database (CreateDatabase)
#
# 3. Get a Database by its Id property (ReadDatabase)
#
# 4. List all Database resources on an account (ReadDatabases)
#
# 5. Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']

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

class DatabaseManagement:
    @staticmethod
    def find_database(client, id):
        print('1. Query for Database')

        databases = list(client.query_databases({
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }))

        if len(databases) > 0:
            print('Database with id \'{0}\' was found'.format(id))
        else:
            print('No database with id \'{0}\' was found'. format(id))
        
    @staticmethod
    def create_database(client, id):
        print("\n2. Create Database")
        
        try:
            client.create_database(id=id)
            print('Database with id \'{0}\' created'.format(id))

        except errors.HTTPFailure as e:
            if e.status_code == 409:
               print('A database with id \'{0}\' already exists'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)               
    
    @staticmethod
    def read_database(client, id):
        print("\n3. Get a Database by id")

        try:
            database = client.get_database(id)
            print('Database with id \'{0}\' was found, it\'s link is {1}'.format(id, database.database_link))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A database with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)    

    @staticmethod
    def list_databases(client):
        print("\n4. List all Databases on an account")
        
        print('Databases:')
        
        databases = list(client.list_databases())
        
        if not databases:
            return

        for database in databases:
            print(database['id'])          

    @staticmethod
    def delete_database(client, id):
        print("\n5. Delete Database")
        
        try:
           client.delete_database(id)

           print('Database with id \'{0}\' was deleted'.format(id))

        except errors.HTTPFailure as e:
            if e.status_code == 404:
               print('A database with id \'{0}\' does not exist'.format(id))
            else: 
                raise errors.HTTPFailure(e.status_code)

def run_sample():     
    with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        try:
            # query for a database
            DatabaseManagement.find_database(client, DATABASE_ID)
            
            # create a database
            DatabaseManagement.create_database(client, DATABASE_ID)
                        
            # get a database using its id
            DatabaseManagement.read_database(client, DATABASE_ID)

            # list all databases on an account
            DatabaseManagement.list_databases(client)

            # delete database by id
            DatabaseManagement.delete_database(client, DATABASE_ID)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))
        
        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    try:
        run_sample()

    except Exception as e:
            print("Top level Error: args:{0}, message:{1}".format(e.args,e.message))