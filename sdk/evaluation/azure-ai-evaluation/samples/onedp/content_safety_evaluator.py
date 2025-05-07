import os
from pprint import pprint

from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import ContentSafetyEvaluator

os.environ["1DP_PROJECT_URL"] = "https://anksingtest1rp.cognitiveservices.azure.com/api/projects/anksingtest1rpproject"

if __name__ == '__main__':


    azure_ai_project = os.environ.get("1DP_PROJECT_URL")
    azure_cred = DefaultAzureCredential()

    print("===== Starting Content Safety Evaluator =======")
    cs_eval = ContentSafetyEvaluator(credential=azure_cred, azure_ai_project=azure_ai_project)
    
    cs_eval_result = cs_eval(
        query="Tokyo is the capital of which country?",
        response="Japan",
    )
        
    print("======= Eval Results ======")
    pprint(cs_eval_result)