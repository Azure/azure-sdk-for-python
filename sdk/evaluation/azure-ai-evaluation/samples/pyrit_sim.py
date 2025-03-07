"""
please install the pyrit extra to run this example

cd azure-sdk-for-python/sdk/evaluation/azure-ai-evaluation
pip install -e ".[pyrit]"
"""


from typing import Dict, List, Optional
from azure.ai.evaluation._safety_evaluation._red_team_agent import RedTeamAgent, AttackStrategy
import os
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.simulator import AdversarialScenario
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.common import initialize_pyrit, DUCK_DB


async def main():
    azure_ai_project = {
        "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
        "resource_group_name": os.environ.get("AZURE_RESOURCE_GROUP"),
        "project_name": os.environ.get("AZURE_PROJECT_NAME"),
    }


    # [START red_team_agent_targets]
    # Model config target 
    model_config = {
        "azure_endpoint": os.environ.get("AZURE_ENDPOINT"),
        "azure_deployment": os.environ.get("AZURE_DEPLOYMENT_NAME"),
    }

    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
    )
    print(outputs)

    # Mock function target to simulate an AI application
    def call_to_ai_application(query: str) -> str:
        return "mock response"
    
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=call_to_ai_application, # type: ignore
    )
    print(outputs)
    
    # Mock function callback target to simulate an AI application wrapped with the openAI chat protocol
    def callback_target(
        messages: List[Dict],
        stream: bool = False,
        session_state: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> dict:
        messages_list = [self._message_to_dict(chat_message) for chat_message in messages] # type: ignore
        latest_message = messages_list[-1]
        application_input = latest_message["content"]
        try:
            response = call_to_ai_application(query=application_input)
        except Exception as e:
            response = f"Something went wrong {e!s}"

        ## Format the response to follow the openAI chat protocol format
        formatted_response = {
            "content": response,
            "role": "assistant",
            "context":{},
        }
        messages_list.append(formatted_response) # type: ignore
        return {"messages": messages_list, "stream": stream, "session_state": session_state, "context": {}}
    
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=callback_target, # type: ignore
    )
    print(outputs)

    # Pyrit target
    initialize_pyrit(memory_db_type=DUCK_DB)
    pyrit_target = OpenAIChatTarget(
        deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME"),
        endpoint = os.environ.get("AZURE_ENDPOINT"),
        use_aad_auth=True
    )

    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=pyrit_target, # type: ignore
    )
    print(outputs)
    # [END red_team_agent_targets]

    # [START red_team_agent_attack_strategies]
    # Only baseline
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=call_to_ai_application, # type: ignore
    )
    print(outputs)

    # Low budget
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=call_to_ai_application, # type: ignore
        attack_strategy=[AttackStrategy.LOW]
    )
    print(outputs)

    # Medium budget
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )
    
    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.MEDIUM]
    )
    print(outputs)

    # High budget
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.HIGH]
    )

    # Compose attack strategies
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.Compose([AttackStrategy.Flip, AttackStrategy.Base64]), 
            AttackStrategy.LOW,
            AttackStrategy.Morse],
    )
    print(outputs)

    # Duplicate attack strategies
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.HIGH, AttackStrategy.Compose([AttackStrategy.Math, AttackStrategy.Tense])],
    )
    print(outputs)

    # Low, medium, and high
    red_team_agent = RedTeamAgent(
        azure_ai_project=azure_ai_project,
        credential=DefaultAzureCredential(),
    )

    outputs = await red_team_agent.attack(
        target=model_config, # type: ignore
        attack_strategy=[AttackStrategy.LOW, AttackStrategy.MEDIUM, AttackStrategy.HIGH]
    )
    print(outputs)

    # [END red_team_agent_attack_strategies]

if __name__ == "__main__":
    import asyncio
    import time
    from dotenv import load_dotenv
    load_dotenv()
    start = time.perf_counter()
    asyncio.run(main())
    end = time.perf_counter()
    print(f"Runtime: {end - start:.2f} seconds")

