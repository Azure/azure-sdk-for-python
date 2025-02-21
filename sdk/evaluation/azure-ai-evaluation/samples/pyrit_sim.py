"""
please install the pyrit extra to run this example

cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
pip install -e ".[pyrit]"
"""


from azure.ai.evaluation._safety_evaluation._safety_evaluation import _SafetyEvaluation
import os
from azure.identity import DefaultAzureCredential


async def main():
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
        "azure_deployment": os.environ.get("AZURE_DEPLOYMENT_NAME"),
    }
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }
    safety_eval = _SafetyEvaluation(
        azure_ai_project=azure_ai_project,
        model_config=model_config,
        credential=DefaultAzureCredential(),
    )

    outputs = await safety_eval(
        target=model_config,
        num_rows=8,
    )
    print(outputs)

if __name__ == "__main__":
    import asyncio
    import time
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()
    print(f"Runtime: {end - start:.2f} seconds")

