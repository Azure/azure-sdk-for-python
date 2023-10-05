# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_eg_client_authentication.py
DESCRIPTION:
    These samples demonstrate authenticating an EventGridClient.
USAGE:
    python sample_eg_client_authentication.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_KEY - The access key of your eventgrid account.
    2) EVENTGRID_ENDPOINT - The namespace hostname. Typically it exists in the format
    "https://<YOUR-NAMESPACE-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
# [START client_auth_with_key_cred]
import os
from azure.eventgrid import EventGridClient
from azure.core.credentials import AzureKeyCredential

key: str = os.environ["EVENTGRID_KEY"]
endpoint: str = os.environ["EVENTGRID_ENDPOINT"]

credential = AzureKeyCredential(key)
client = EventGridClient(endpoint, credential)
# [END client_auth_with_key_cred]
