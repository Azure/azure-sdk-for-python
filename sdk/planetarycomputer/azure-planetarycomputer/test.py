from azure.planetarycomputer import PlanetaryComputerProClient
from azure.identity import DefaultAzureCredential

client = PlanetaryComputerProClient(
    endpoint="https://pctiler2026.fsgcc8ava0apb2a5.uksouth.geocatalog.ppe.spatio.azure-test.net",
    credential=DefaultAzureCredential(),
)

# get_collection() says it returns pystac.Collection
collection = client.stac.get_collection(collection_id="karthick-example-collection")

print(collection)

# So you SHOULD be able to do this (pystac API):
print(collection.id)  # "naip"
print(collection.title)  # "NAIP Imagery"
print(collection.extent)  # pystac Extent object
print(type(collection))  # <class 'pystac.collection.Collection'>
