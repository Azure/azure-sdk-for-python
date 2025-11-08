# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a basic responses operation
    using the synchronous AIProject and OpenAI clients, while defining
    a desired JSON schema for the response ("structured output").

    This sample is inspired by the OpenAI example here:
    https://platform.openai.com/docs/guides/structured-outputs/supported-schemas

USAGE:
    python sample_responses_structured_output.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" openai azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from pydantic import BaseModel, Field

load_dotenv()


class CalendarEvent(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    date: str = Field(description="Date in YYYY-MM-DD format")
    participants: list[str]


project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    response = openai_client.responses.create(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions="""
            Extracts calendar event information from the input messages,
            and return it in the desired structured output format.
            """,
        text={
            "format": {
                "type": "json_schema",
                "name": "CalendarEvent",
                "schema": CalendarEvent.model_json_schema(),
            }
        },
        input="Alice and Bob are going to a science fair this Friday, November 7, 2025.",
    )
    print(f"Response output: {response.output_text}")
