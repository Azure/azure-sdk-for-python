import asyncio
from dotenv import load_dotenv
import os
from azure.ai.evaluation.simulator import AdversarialScenario
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import DSBEvaluation, DSBEvaluator
from typing import Optional

def test_target_context(query: str) -> tuple:
    return "Mock response", "Mock context"

def test_target(query: str) -> str:
    return "Mock response"

if __name__ == "__main__":
    load_dotenv()

    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP_NAME"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }

    model_config = {
        "azure_endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "azure_deployment": os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    }

    source_text = "Mock source text"

    credential = DefaultAzureCredential()

    dsb_evaluation = DSBEvaluation(model_config=model_config, azure_ai_project=azure_ai_project, credential=credential)

    asyncio.run(dsb_evaluation(
        adversarial_scenario=AdversarialScenario.ADVERSARIAL_CONVERSATION,
        evaluators=[DSBEvaluator.CONTENT_SAFETY, DSBEvaluator.GROUNDEDNESS, DSBEvaluator.PROTECTED_MATERIAL],
        target=test_target,
        source_text=source_text,
        max_conversation_turns=1,
        max_simulation_results=3,
        output_path="evaluation_outputs.jsonl",
    ))