import os
from azure.common.credentials import ServicePrincipalCredentials
from azure.identity import ClientSecretCredential

TENANT_ID= os.environ.get("AZURE_TENANT_ID", None)
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", None)
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", None)

client_credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

service_credential = ServicePrincipalCredentials(
    tenant=TENANT_ID,
    client_id=CLIENT_ID,
    secret=CLIENT_SECRET
)
