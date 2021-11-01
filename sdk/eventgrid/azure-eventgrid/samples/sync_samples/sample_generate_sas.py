# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_generate_sas.py
DESCRIPTION:
    These samples demonstrate creating a shared access signature for eventgrid.
USAGE:
    python sample_generate_sas.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
# [START generate_sas]
import os
from azure.eventgrid import generate_sas
from datetime import datetime, timedelta

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

#represents the expiration date for sas
expiration_date_utc = datetime.utcnow() + timedelta(hours=10)

signature = generate_sas(endpoint, topic_key, expiration_date_utc)

# [END generate_sas]

print(signature)