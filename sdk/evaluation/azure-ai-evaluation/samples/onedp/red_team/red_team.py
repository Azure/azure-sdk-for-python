import asyncio
import os

from azure.ai.evaluation.red_team import (
    RedTeam,
    AttackStrategy,
    RiskCategory
)
from azure.identity import DefaultAzureCredential

azure_ai_project = os.environ["1DP_PROJECT_URL"]

credential = DefaultAzureCredential()
agent = RedTeam(azure_ai_project=azure_ai_project, credential=credential, risk_categories=[RiskCategory.Violence, RiskCategory.HateUnfairness], num_objectives=2)

# Define a simple callback function that simulates a chatbot
def simple_callback(query: str) -> str:
    # Your implementation to call your application (e.g., RAG system, chatbot)
    return "I'm an AI assistant that follows ethical guidelines. I cannot provide harmful content."

async def run_scan():
    # Run the scan with basic attack strategies
    results = await agent.scan(
        target=simple_callback,
        scan_name="Basic-Callback-Test",
        attack_strategies=[AttackStrategy.Base64, AttackStrategy.ROT13],
        application_scenario="A customer service chatbot for a retail company"
    )

    print(f"Scan completed with {len(results.scan_result) if results.scan_result else 0} conversations")
    # [END red_team_basic_callback]
    return results


if __name__ == "__main__":  # Run the async samples
    asyncio.run(run_scan())