# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a responses operation with image input
    using the synchronous AIProject and OpenAI clients. The sample shows how to
    send both text and image content to a model for analysis.

    See also https://platform.openai.com/docs/api-reference/responses/create?lang=python

USAGE:
    python sample_responses_image_input.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" openai azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import base64
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


def image_to_base64(image_path: str) -> str:
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc


with project_client:

    openai_client = project_client.get_openai_client()

    image_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/image_input.png"))

    response = openai_client.responses.create(
        input=[
            {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "what's in this image?"},
                    {
                        "type": "input_image",
                        "detail": "auto",
                        "image_url": f"data:image/png;base64,{image_to_base64(image_file_path)}",
                    },
                ],
            }
        ],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
    )
    print(f"Response output: {response.output_text}")
