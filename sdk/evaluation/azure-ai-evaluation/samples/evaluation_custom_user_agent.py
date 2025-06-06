# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import os
from azure.ai.evaluation import evaluate, GroundednessEvaluator
from azure.identity import DefaultAzureCredential


def main():
    """Sample demonstrating how to use custom user agent with evaluate function."""
    
    # Setup Azure AI Project (replace with your actual project details)
    azure_ai_project = {
        "subscription_id": "your-subscription-id",
        "resource_group_name": "your-resource-group",  
        "project_name": "your-project-name",
    }
    credential = DefaultAzureCredential()
    
    # Create sample data
    sample_data = [
        {
            "query": "What is the capital of France?",
            "response": "The capital of France is Paris.",
            "context": "France is a country in Western Europe. Its capital city is Paris, which is also the largest city in France."
        },
        {
            "query": "What is machine learning?", 
            "response": "Machine learning is a subset of artificial intelligence that uses algorithms to analyze data and make predictions.",
            "context": "Artificial intelligence is a broad field that includes machine learning, deep learning, and other techniques for creating intelligent systems."
        }
    ]
    
    # Save sample data to a file
    data_file = "sample_evaluation_data.jsonl"
    with open(data_file, "w") as f:
        for item in sample_data:
            f.write(json.dumps(item) + "\n")
    
    try:
        # [START evaluate_with_custom_user_agent]
        # Run evaluation with custom user agent
        result = evaluate(
            data=data_file,
            evaluators={
                "groundedness": GroundednessEvaluator(
                    azure_ai_project=azure_ai_project,
                    credential=credential
                )
            },
            azure_ai_project=azure_ai_project,
            user_agent="MyApp/1.0.0 CustomEvaluation"  # Custom user agent to append to default
        )
        
        print("Evaluation completed successfully!")
        print(f"Results: {result}")
        # [END evaluate_with_custom_user_agent]
        
    finally:
        # Clean up sample data file
        if os.path.exists(data_file):
            os.remove(data_file)


if __name__ == "__main__":
    main()