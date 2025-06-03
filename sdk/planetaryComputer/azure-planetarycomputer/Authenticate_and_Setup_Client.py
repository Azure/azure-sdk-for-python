from azure.identity import DefaultAzureCredential
from azure.planetarycomputer import MicrosoftPlanetaryComputerProClient

# Set your test endpoint
endpoint = "https://testcatalog-3480.a5cwawdkcbdfgtcw.uksouth.geocatalog.spatio-ppe.azure-test.net"
credential = DefaultAzureCredential()

# Initialize client
client = MicrosoftPlanetaryComputerProClient(endpoint=endpoint, credential=credential)
