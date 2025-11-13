# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    methods to create, get, list, and run Red Team scans.

USAGE:
    python sample_red_team_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. Your model deployment name.
    3) MODEL_ENDPOINT - Required. The Azure AI Model endpoint, as found in the overview page of your
       Microsoft Foundry project. Example: https://<account_name>.services.ai.azure.com
    4) MODEL_API_KEY - Required. The API key for your Azure AI Model.
"""
import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    RedTeam,
    AzureOpenAIModelConfiguration,
    AttackStrategy,
    RiskCategory,
)

load_dotenv()


async def sample_red_team_async() -> None:
    """Demonstrates how to perform Red Team operations using the AIProjectClient."""

    endpoint = os.environ[
        "AZURE_AI_PROJECT_ENDPOINT"
    ]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>
    model_endpoint = os.environ["MODEL_ENDPOINT"]  # Sample : https://<account_name>.services.ai.azure.com
    model_api_key = os.environ["MODEL_API_KEY"]
    model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]  # Sample : gpt-4o-mini

    async with (
        DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):

        # [START red_team_sample]
        print("Creating a Red Team scan for direct model testing")

        # Create target configuration for testing an Azure OpenAI model
        target_config = AzureOpenAIModelConfiguration(model_deployment_name=model_deployment_name)

        # Create the Red Team configuration
        red_team = RedTeam(
            attack_strategies=[AttackStrategy.BASE64],
            risk_categories=[RiskCategory.VIOLENCE],
            display_name="redteamtest1",  # Use a simpler name
            target=target_config,
        )

        # Create and run the Red Team scan
        red_team_response = await project_client.red_teams.create(
            red_team=red_team,
            headers={
                "model-endpoint": model_endpoint,
                "model-api-key": model_api_key,
            },
        )
        print(f"Red Team scan created with scan name: {red_team_response.name}")

        print("Getting Red Team scan details")
        # Use the name returned by the create operation for the get call
        get_red_team_response = await project_client.red_teams.get(name=red_team_response.name)
        print(f"Red Team scan status: {get_red_team_response.status}")

        print("Listing all Red Team scans")
        async for scan in project_client.red_teams.list():
            print(f"Found scan: {scan.name}, Status: {scan.status}")
        # [END red_team_sample]


if __name__ == "__main__":
    asyncio.run(sample_red_team_async())
