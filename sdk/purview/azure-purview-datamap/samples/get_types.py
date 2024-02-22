import logging
import os
from azure.identity import ClientSecretCredential
from azure.purview.datamap import DataMapClient

logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout, )
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
try:
    endpoint = os.environ["PURVIEW_ENDPOINT"]
    tenantId = os.environ["PURVIEW_TENANT_ID"]
    clientId = os.environ["PURVIEW_CLIENT_ID"]
    clientSecret = os.environ["PURVIEW_CLIENT_SECRET"]
    authority = os.environ["AUTHORITY_HOST"] #e.g"https://login.microsoftonline.com/"
except KeyError:
    LOG.error("Missing environment variable - please set if before running the example")
    exit()

credential = ClientSecretCredential(tenantId, clientId, clientSecret,authority = authority)
client = DataMapClient(endpoint=endpoint, credential=credential)
response = client.type_definition.get()



