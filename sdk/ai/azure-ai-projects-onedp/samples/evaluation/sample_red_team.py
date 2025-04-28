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

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) AZURE_OPENAI_DEPLOYMENT - Required. Your Azure OpenAI deployment name.
"""
import asyncio
import os

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.onedp.aio import AIProjectClient
from azure.ai.projects.onedp.models import (
    RedTeam,
    AzureOpenAIModelConfiguration,
    AttackStrategy,
    RiskCategory
)
from dotenv import load_dotenv

load_dotenv()


async def sample_red_team_async() -> None:
    """Demonstrates how to perform Red Team operations using the AIProjectClient."""
    
    endpoint = os.environ["PROJECT_ENDPOINT"]
    model_deployment_name = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

    async with AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
    ) as project_client:

        # [START red_team_sample]
        print("Creating a Red Team scan for direct model testing")
        
        # Create target configuration for testing an Azure OpenAI model
        target_config = AzureOpenAIModelConfiguration(
            # type="AzureOpenAIModel",
            modelDeploymentName=model_deployment_name
        )

        # Create the Red Team configuration
        red_team = RedTeam(
            scanName="Red-Team-1DP-Test",
            numTurns=3,  # Number of simulation rounds
            attackStrategies=[
                AttackStrategy.Base64,
                AttackStrategy.ROT13,
                AttackStrategy.UnicodeConfusable
            ],
            simulationOnly=False,  # False means simulation + evaluation
            riskCategories=[
                RiskCategory.Violence, 
                RiskCategory.HateUnfairness
            ],
            applicationScenario="A customer service chatbot for a retail company",
            tags={"environment": "test", "purpose": "security evaluation"},
            properties={"version": "1.0"},
            targetConfig=target_config
        )
        
        # Create and run the Red Team scan
        red_team_response = await project_client.red_team.create_run(red_team)
        print(f"Red Team scan created with ID: {red_team_response.id}")

        print("Getting Red Team scan details")
        get_red_team_response = await project_client.red_team.get(red_team_response.id)
        print(f"Red Team scan status: {get_red_team_response.status}")

        print("Listing all Red Team scans")
        async for scan in project_client.red_team.list():
            print(f"Found scan: {scan.id}, Status: {scan.status}")
        # [END red_team_sample]


async def main():
    """Main function to run the sample."""
    await sample_red_team_async()


if __name__ == "__main__":
    asyncio.run(main())
