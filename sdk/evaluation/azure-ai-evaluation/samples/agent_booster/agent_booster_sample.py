from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.ai.evaluation._boost._agent_booster import _AgentBooster
from azure.ai.evaluation import AzureOpenAIModelConfiguration

import os
import dotenv
dotenv.load_dotenv()


def example_with_default_evaluators():
    """Example using default evaluators."""
    model_config = AzureOpenAIModelConfiguration(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
    )
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    )
    booster = _AgentBooster(
        project_client=project_client,
        model_config=model_config,
        agent_id=os.environ["AGENT_ID"],
        verbose=True,
    )
    return booster

booster = example_with_default_evaluators()

refine_result = booster.refine(
    data_file="queries.jsonl",
    max_iterations=1,
)

print(refine_result)
