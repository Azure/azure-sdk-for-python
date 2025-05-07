import os
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import RelevanceEvaluator

# os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.services.ai.azure.com/api/projects/anksingtest1rpproject"

if __name__ == '__main__':

    model_config = {
        "azure_endpoint": "https://build-2025-fdp-test-account1.services.ai.azure.com",
        "api_version": "2024-12-01-preview",
        "azure_deployment": "gpt-4.1"
    }
    
    print("===== Starting Relevance Evaluator =======")
    rel_eval = RelevanceEvaluator(model_config)
    
    rel_eval_result = rel_eval(
        query="Tokyo is the capital of which country?",
        response="Japan",
    )
        
    print("======= Evaluation Results ======")
    pprint(rel_eval_result)