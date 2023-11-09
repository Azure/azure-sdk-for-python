# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
from azure.eventgrid import EventGridClient
from azure.eventgrid.models import *
from azure.identity import DefaultAzureCredential

EVENTGRID_ENDPOINT: str = os.environ["EVENTGRID_ENDPOINT"]

# Create a client using DefaultAzureCredential
client = EventGridClient(EVENTGRID_ENDPOINT, DefaultAzureCredential())