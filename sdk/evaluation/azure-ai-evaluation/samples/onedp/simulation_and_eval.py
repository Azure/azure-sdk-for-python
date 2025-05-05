import os
from pprint import pprint
import asyncio
from typing import Any, Dict, List
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate, ContentSafetyEvaluator
from azure.ai.evaluation.simulator import AdversarialScenario, AdversarialSimulator
from azure.ai.evaluation.simulator._utils import JsonLineChatProtocol

os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.services.ai.azure.com/api/projects/anksingtest1rpproject"

if __name__ == '__main__':

    azure_ai_project = os.environ.get("1DP_PROJECT_URL")
    azure_cred = DefaultAzureCredential()
    
    async def callback(
        messages: List[Dict],
        stream: bool = False,
        session_state: Any = None,
        context: Dict[str, Any] = None,
    ) -> dict:
        query = messages["messages"][0]["content"]
        response_from_llm = "SELECT * FROM users WHERE username = {user_input};" 
        temperature = 0.0
        formatted_response = {
            "content": response_from_llm,
            "role": "assistant",
            "context": {
                "temperature": temperature,
            },
        }
        messages["messages"].append(formatted_response)
        return {
            "messages": messages["messages"],
            "stream": stream,
            "session_state": session_state,
            "context": context,
        }
        
    simulator = AdversarialSimulator(azure_ai_project=azure_ai_project, credential=azure_cred)
        
    simulator_output = asyncio.run(
        simulator(
            scenario=AdversarialScenario.ADVERSARIAL_CODE_VULNERABILITY,
            max_conversation_turns=1,
            max_simulation_results=1,
            target=callback,
        )
    )
    
    print("======= Simulator Results ======")
    pprint(simulator_output)
    
    # Write simulator output to file
    file_name = "content_safety_eval_test_data.jsonl"
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", file_name)

    # Write the output to the file
    with open(path, "w") as file:
        file.write(JsonLineChatProtocol(simulator_output[0]).to_eval_qr_json_lines())    

    print("===== Calling Evaluate API for Content Safety Eval =======")
    
    eval_output = evaluate(
        data=path,
        azure_ai_project=azure_ai_project,
        evaluators={
            "content_safety" : ContentSafetyEvaluator(credential=azure_cred, azure_ai_project=azure_ai_project),
        },
        evaluator_config={
            "content_safety": {
                "column_mapping": {
                    "response": "${data.response}",
                    "query": "${data.query}",
                },
            },
        },
    )
        
    print("======= Eval Results ======")
    pprint(eval_output)