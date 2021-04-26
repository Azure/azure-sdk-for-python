# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_K8S.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents using dict representations
    and sending them as a list to a kubernetes cluster.
    Note that K8S only supports cloudevents schema.
USAGE:
    python sample_K8S.py
    Set the environment variables with your own values before running the sample:
    1) K8S_ACCESS_KEY - The access key of your eventgrid account.
    2) K8S_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
import urllib3
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

# this line is to disable the following warning from urlib3.
# InsecureRequestWarning: Unverified HTTPS request is being made to host.
# Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
urllib3.disable_warnings()


topic_key = os.environ["K8S_ACCESS_KEY"]
endpoint = os.environ["K8S_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential, connection_verify=False)

# [START publish_cloud_event_dict]
client.send([
    {
        "type": "Contoso.Items.ItemReceived",
        "source": "/contoso/items",	
        "data": {	
            "itemSku": "Contoso Item SKU #1"	
        },	
        "subject": "Door1",	
        "specversion": "1.0",	
        "id": "randomclouduuid11"
    }
])
# [END publish_cloud_event_dict]
