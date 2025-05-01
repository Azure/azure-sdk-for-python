import os
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate, ContentSafetyEvaluator

os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.cognitiveservices.azure.com/api/projects/anksingtest1rpproject"

if __name__ == '__main__':


    azure_ai_project = os.environ.get("1DP_PROJECT_URL")
    azure_cred = DefaultAzureCredential()
    path = "./sdk/evaluation/azure-ai-evaluation/samples/data/evaluate_test_data.jsonl"

    print("===== Calling Evaluate API for Content Safety Eval =======")
    
    eval_output = evaluate(
        data=path,
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