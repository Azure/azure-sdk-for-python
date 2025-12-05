import os
from azure.mgmt.all import ManagementClient
from azure.identity import DefaultAzureCredential


client = ManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["SUBSCRIPTION_ID"],
    )
