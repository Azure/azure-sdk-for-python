
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to ...

USAGE:
    python sample_datasets.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

from azure.identity import DefaultAzureCredential
from azure.ai.projects.dp1 import AIProjectClient


client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

client.datasets.create_dataset(
    name="my_dataset_name",
    file="sample_file.pdf",
    connection_name="my_train_data_connection"
)
