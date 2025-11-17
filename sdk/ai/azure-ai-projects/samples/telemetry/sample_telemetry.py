# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.telemetry` methods to get the Application Insights connection string and
    enable tracing.

USAGE:
    python sample_telemetry.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    print("Get the Application Insights connection string:")
    connection_string = project_client.telemetry.get_application_insights_connection_string()
    print(connection_string)
