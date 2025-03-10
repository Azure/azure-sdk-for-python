"""
please install the pyrit extra to run this example

cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
pip install -e ".[pyrit]"
"""


from azure.ai.evaluation._safety_evaluation import RedTeamAgent, AttackStrategy, AttackObjectiveGenerator, RiskCategory
import os
from azure.identity import DefaultAzureCredential


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


    ## Minimal inputs
    attack_objective_generator = AttackObjectiveGenerator(
        risk_categories=[
            RiskCategory.HateUnfairness,
        ],
        num_objectives=10,
    )
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=test_target_fn, # type: ignore
        attack_objective_generator=attack_objective_generator,
    )
    print(outputs)


    ## Maximal inputs
    attack_objective_generator = AttackObjectiveGenerator(
        risk_categories=[
            RiskCategory.HateUnfairness,
            RiskCategory.Violence,
            RiskCategory.Sexual,
            RiskCategory.SelfHarm,
        ],
        num_objectives=10,
    )
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        evaluation_name="Racoon red-team evaluation",
        target=test_target_fn,
        attack_strategy=[AttackStrategy.Compose([AttackStrategy.Flip, AttackStrategy.Base64]), 
            AttackStrategy.LOW,
            AttackStrategy.Morse],
        output_path="RacoonRedTeamEvalResults.jsonl", 
        attack_objective_generator=attack_objective_generator,
    )

    print(outputs)

    ## High budget with duplicates and model config as target
    attack_objective_generator = AttackObjectiveGenerator(
        risk_categories=[
            RiskCategory.HateUnfairness,
            RiskCategory.Violence
        ],
        num_objectives=10,
    )

    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        evaluation_name="HighBudget-Duplicates",
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.HIGH, AttackStrategy.Compose([AttackStrategy.Math, AttackStrategy.Tense])],
        output_path="HighBudget-Duplicates.jsonl",
        attack_objective_generator=attack_objective_generator,
    )

    print(outputs)

if __name__ == "__main__":
    import asyncio
    import time
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()
    print(f"Runtime: {end - start:.2f} seconds")

