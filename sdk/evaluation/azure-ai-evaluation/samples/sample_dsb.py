import asyncio
from dotenv import load_dotenv
import os
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.ai.evaluation._model_configurations import AzureAIProject
from azure.ai.evaluation import evaluate_dsb, DSBEvaluator
from typing import Optional

def test_target(query: Optional[str], response: Optional[str], conversation: Optional[str]) -> str:
    return f"Res: {query}"

if __name__ == "__main__":
    load_dotenv()

    azure_ai_project = AzureAIProject(
        subscription_id=os.environ.get("AZURE_SUBSCRIPTION_ID") or "<your-subscription-id>",
        resource_group_name=os.environ.get("AZURE_RESOURCE_GROUP_NAME") or "<your-resource-group>",
        project_name=os.environ.get("AZURE_PROJECT_NAME") or "<your-workspace-name>",
    )

    model_config = {
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    }

    asyncio.run(evaluate_dsb(
        adversarial_scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
        azure_ai_project=azure_ai_project,
        evaluators=[DSBEvaluator.CONTENT_SAFETY],
        target=test_target,
        model_config=model_config,
        max_conversation_turns=1,
        max_simulation_results=3,
        output_path="evaluation_outputs.jsonl",
    ))