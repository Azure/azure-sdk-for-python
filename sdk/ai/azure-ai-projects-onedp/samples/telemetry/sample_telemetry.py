# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.telemtry` methods to get the Application Insights connection string.

USAGE:
    python sample_telemetry.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential  # TODO: Remove me when EntraID is supported
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.projects.onedp.models import ConnectionType

# Start remove me -- logging
import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# End remove me

endpoint = os.environ["PROJECT_ENDPOINT"]

with AIProjectClient(
    endpoint=endpoint,
    # credential=DefaultAzureCredential(),
    credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
    logging_enable=True,
) as project_client:

    print("Get the Application Insights connection string:")
    connection_string = project_client.telemetry.get_connection_string()
    print(connection_string)
