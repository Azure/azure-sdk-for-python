import os
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate, RelevanceEvaluator

os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.services.ai.azure.com/api/projects/anksingtest1rpproject"

if __name__ == '__main__':

    azure_ai_project = os.environ.get("1DP_PROJECT_URL")
    azure_cred = DefaultAzureCredential()
    
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(parent_dir, "data", "evaluate_test_data.jsonl")

    model_config = {
        "azure_endpoint": "https://build-2025-fdp-test-account1.services.ai.azure.com",
        "api_version": "2024-12-01-preview",
        "azure_deployment": "gpt-4.1"
    }
    
    print("===== Starting Relevance Evaluator =======")
    
    
    eval_output = evaluate(
        data=path,
        azure_ai_project=azure_ai_project,
        evaluators={
            "relevance" : RelevanceEvaluator(model_config),
        },
        evaluator_config={
            "relevance": {
                "column_mapping": {
                    "response": "${data.response}",
                    "query": "${data.query}",
                },
            },
        },
    )
        
    print("======= Eval Results ======")
    pprint(eval_output)
