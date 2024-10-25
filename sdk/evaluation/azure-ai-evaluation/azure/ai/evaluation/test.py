from azure.ai.evaluation import evaluate, RelevanceEvaluator, HateUnfairnessEvaluator, ProtectedMaterialEvaluator
from azure.identity import AzureCliCredential
import os

if __name__ == "__main__":
    model_config = {
        # OpenAI API key
        "type": "azure_openai",
        "azure_deployment": "gpt-35-turbo",
        "azure_endpoint": "https://ai-neduvvurai952818858670.openai.azure.com",
        "api_key": "dc2f807bc52448deafb28b23e2f146f6",
    }
    
    
    relevance_eval = RelevanceEvaluator(model_config)

    relevance_eval

    hate_unfairness_evaluator = ProtectedMaterialEvaluator(
        azure_ai_project={
            "subscription_id": "b17253fa-f327-42d6-9686-f3e553e24763",
            "resource_group_name": "rg-neduvvurai",
            "project_name": "neduvvur-4217",
        },
        credential=AzureCliCredential(),
    )

    print(hate_unfairness_evaluator(
        query="Which tent is the most waterproof?",
        response="The Alpine Explorer Tent is the most waterproof.",
    ))

    """os.environ["PF_EVALS_BATCH_USE_ASYNC"] = "false"

    datasets_folderpath = os.path.abspath(".")
    input_path = os.path.join(datasets_folderpath, "data.jsonl")

    print(input_path)

    eval_result = evaluate(
        evaluators={
            "relevance": relevance_eval,
            "hate_unfairness": hate_unfairness_evaluator,
        },
        data="C:/Users/neduvvur/azure-sdk-for-python/data.jsonl",
    )

    print(eval_result)"""


    """print(relevance_eval(
            query="Which tent is the most waterproof?",
            response="The Alpine Explorer Tent is the most waterproof.",
            context="From the our product list, the alpine explorer tent is the most waterproof. The Adventure Dining Table has higher weight.",
        )
    )"""