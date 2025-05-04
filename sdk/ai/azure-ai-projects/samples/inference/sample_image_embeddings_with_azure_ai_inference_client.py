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
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
    3) DATA_FOLDER - Optional. The folder path where the image file is located.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference.models import ImageEmbeddingInput

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

# Construct the path to the image file used in this sample
data_folder = os.environ.get("DATA_FOLDER", os.path.dirname(os.path.abspath(__file__)))
image_file = os.path.join(data_folder, "sample1.png")

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        with project_client.inference.get_image_embeddings_client() as client:

            response = client.embed(
                model=model_deployment_name,
                input=[ImageEmbeddingInput.load(image_file=image_file, image_format="png")],
            )

            for item in response.data:
                length = len(item.embedding)
                print(
                    f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                    f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                )
