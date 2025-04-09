# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    ImageEmbeddingsClient from the azure.ai.inference package, and perform one image
    embeddings operation. For more information on the azure.ai.inference package see
    https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_image_embeddings_with_azure_ai_inference_client.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
"""

import os
from azure.core.credentials import AzureKeyCredential # TODO: Remove me when EntraID is supported # TODO: Remove me when EntraID is supported
from azure.identity import DefaultAzureCredential
from azure.ai.projects.onedp import AIProjectClient
from azure.ai.inference.models import ImageEmbeddingInput

# TODO: Remove console logging
import sys
import logging
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# End logging

endpoint = os.environ["PROJECT_ENDPOINT"]
deployment_name = os.environ["DEPLOYMENT_NAME"]

with AIProjectClient(
    endpoint=endpoint,
    # credential=DefaultAzureCredential(),
    credential=AzureKeyCredential(os.environ["PROJECT_API_KEY"]),
    logging_enable=True,  # TODO: Remove console logging
) as project_client:

    with project_client.inference.get_image_embeddings_client() as client:

        response = client.embed(
            model=deployment_name, input=[ImageEmbeddingInput.load(image_file="sample1.png", image_format="png")]
        )

        for item in response.data:
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )
