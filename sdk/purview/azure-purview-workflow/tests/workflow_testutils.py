import os
from azure.identity import UsernamePasswordCredential

def get_credential():
    username = os.getenv("Username")
    password = os.getenv("Password")
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    return UsernamePasswordCredential(client_id=client_id, username=username, password=password, tenant_id=tenant_id)
