"""
please install the pyrit extra to run this example

cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
pip install -e ".[pyrit]"
"""


from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation, _AttackBudget
import os
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.simulator import AdversarialScenario


async def main():
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
        "azure_deployment": os.environ.get("AZURE_DEPLOYMENT_NAME"),
    }

    def test_target_fn(query: str) -> str:
        return "mock response"

    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }

    safety_eval_callback_target = _SafetyEvaluation(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await safety_eval_callback_target(
        target=test_target_fn,
        num_rows=1,
        attack_budget=[_AttackBudget.LOW],
        evaluation_name="CallbackTarget"
    )

    print(outputs)

    safety_eval_model_target = _SafetyEvaluation(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await safety_eval_model_target(
        target=model_config,
        num_rows=1,
        attack_budget=[_AttackBudget.LOW],
        evaluation_name="ModelTarget"
    )
    print(outputs)

if __name__ == "__main__":
    import asyncio
    import time
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()
    print(f"Runtime: {end - start:.2f} seconds")

