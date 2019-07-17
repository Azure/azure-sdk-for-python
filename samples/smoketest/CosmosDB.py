import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
from azure.cosmos.partition_key import PartitionKey
import os

class CosmosDB:
    def __init__(self):
        URL = os.environ["COSMOS_ENDPOINT"]
        KEY = os.environ["COSMOS_KEY"]
        self.client = cosmos_client.CosmosClient(URL,{'masterKey': KEY})

    def createDatabase(self):
        dbName="pySolarSystem"
        print("Creating '{0}' database...".format(dbName))
        return self.client.create_database(dbName)

    def createContainer(self, db):
        collectionName = "Planets"
        print("Creating '{0}' collection...".format(collectionName))
        partition_key = PartitionKey(path='/id', kind='Hash')
        return db.create_container(id="Planets", partition_key=partition_key)

    def createDocuments(self, container):
        planets = []

        # Cosmos will look for an 'id' field in the items, if the 'id' is not specify Cosmos is going to assing a random key.
        planets.append({
            'id' : "Earth",
            'HasRings' : False,
            'Radius' : 3959,
            'Moons' : 
                [
                    {
                        'Name' : "Moon"
                    }
                ]
                })

        planets.append({
                "id" : "Mars",
                "HasRings" : False,
                "Radius" : 2106,
                "Moons" : 
                    [
                        {
                            "Name" : "Phobos"
                        },
                        {
                            "Name" : "Deimos"
                        }
                    ]
            })

        print("Inserting items in the collection...")
        for planet in planets:
            container.create_item(planet)
            print("\t'{0}' created".format(planet['id']))
        print("\tdone")

    def simpleQuery(self, container):
        print("Quering the container...")
        items = list(container.query_items(
            query="SELECT c.id FROM c",
            enable_cross_partition_query = True
        ))
        print("\tdone: {0}".format(items))
    
    def deleteDatabase(self):
        print("Cleaning up the resource...")
        self.client.delete_database("pySolarSystem")
        print("\tdone")

    def Run(self):
        print()
        print("------------------------")
        print("Cosmos DB")
        print("------------------------")
        print("1) Create a Database")
        print("2) Create a Container in the database")
        print("3) Insert Documents (items) into the Container")
        print("4) Delete Database (Clean up the resource)")
        print()
        
        # Ensure that the database does not exists
        try:
            self.deleteDatabase()
        except:
            pass
        
        try:
            db = self.createDatabase()
            container = self.createContainer(db=db)
            self.createDocuments(container=container)
            self.simpleQuery(container=container)            
        finally:
            # if something goes wrong, the resource should be cleaned anyway
            self.deleteDatabase()