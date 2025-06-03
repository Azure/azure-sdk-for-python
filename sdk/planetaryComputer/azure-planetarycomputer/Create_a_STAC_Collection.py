from azure.identity import DefaultAzureCredential
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient

# Initialize client
client = MicrosoftPlanetaryComputerProClient(
    endpoint="https://testcatalog-3480.a5cwawdkcbdfgtcw.uksouth.geocatalog.spatio-ppe.azure-test.net",
    credential=DefaultAzureCredential(),
)

# Define the collection payload
collection_body = {
    "description": "A collection for integration tests purposes",
    "extent": {
        "spatial": {"bbox": [[-180, -90, 180, 90]]},
        "temporal": {"interval": [["2020-01-01T00:00:00Z", None]]},
    },
    "id": "test-collection-d45537668d06",
    "license": "CC-BY-4.0",
    "links": [],
    "stac_version": "1.0.0",
    "title": "Test Collection d45537668d06",
    "type": "Collection",
}

# Create the collection
client.stac_collection_operations.begin_create(body=collection_body).result()
