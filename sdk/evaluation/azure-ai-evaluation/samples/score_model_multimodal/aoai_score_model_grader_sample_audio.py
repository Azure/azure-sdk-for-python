# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Sample demonstrating the use of AzureOpenAIScoreModelGrader for continuous
scoring evaluation.

This sample shows how to:
1. Configure an Azure OpenAI model for grading
2. Create a score model grader with custom prompts
3. Run evaluation using the evaluate() method with both foundry and hub-based projects
4. Interpret continuous scoring results

Prerequisites:
- Azure OpenAI resource with API key and endpoint
- Model deployment (e.g., gpt-4, gpt-4o-mini)
- Sample conversation data in JSONL format
- Environment variables configured in .env file
- Azure AI project configuration (either foundry-based or hub-based)

Azure AI Project Configuration Options:
1. Foundry-based project (recommended):
   - AZURE_AI_PROJECT_ENDPOINT
2. Hub-based project (legacy):
   - AZURE_SUBSCRIPTION_ID
   - AZURE_RESOURCE_GROUP_NAME  
   - AZURE_PROJECT_NAME
"""

import json
import os
from dotenv import load_dotenv
import pandas as pd
from azure.ai.evaluation import evaluate, AzureOpenAIScoreModelGrader
from azure.ai.evaluation import AzureOpenAIModelConfiguration, AzureAIProject

# Load environment variables
load_dotenv()


def create_sample_data() -> str:
    """Create sample conversation data for testing."""
    sample_conversations = [
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cheerful assistant that speaks in audio with a natural style. Keep responses under 10 seconds.",
                },
                {"role": "user", "content": [{"type": "input_text", "text": "Introduce yourself in one sentence."}]},
            ]
        },
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are a flat, monotone, robotic assistant that speaks in audio. Avoid sounding cheerful or friendly. Keep responses under 10 seconds.",
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Greet the listener and wish them a great day."}],
                },
            ]
        },
        {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an enthusiastic assistant that speaks in audio with a fast pace. Keep responses under 10 seconds.",
                },
                {"role": "user", "content": [{"type": "input_text", "text": "Tell a quick joke suitable for kids."}]},
            ]
        },
    ]

    # Create JSONL file
    filename = "sample_conversations.jsonl"
    with open(filename, "w") as f:
        for conv in sample_conversations:
            f.write(json.dumps(conv) + "\n")

    print(f"Created sample data file: {filename}")
    return filename


def get_azure_ai_project():
    """
    Get Azure AI project configuration based on available environment variables.

    Returns either:
    1. Foundry-based project (preferred): Uses AZURE_AI_PROJECT_ENDPOINT
    2. Hub-based project (legacy): Uses subscription_id, resource_group_name, project_name
    """
    # Try foundry-based project first (newer approach)
    foundry_endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if foundry_endpoint:
        print("✅ Using foundry-based Azure AI project")
        return foundry_endpoint

    # Fall back to hub-based project (legacy approach)
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID")
    resource_group = os.environ.get("AZURE_RESOURCE_GROUP_NAME")
    project_name = os.environ.get("AZURE_PROJECT_NAME")

    if subscription_id and resource_group and project_name:
        print("✅ Using hub-based Azure AI project (legacy)")
        return AzureAIProject(
            subscription_id=subscription_id,
            resource_group_name=resource_group,
            project_name=project_name,
        )

    print("⚠️  No Azure AI project configuration found")
    return None


def demonstrate_score_model_grader():
    """Demonstrate the AzureOpenAIScoreModelGrader usage with real credentials."""

    # Create sample data
    data_file = create_sample_data()

    print("=== Azure OpenAI Score Model Grader Demo ===\n")

    endpoint = os.getenv("endpoint", "")
    deployment = os.getenv("deployment_name_audio", "gpt-4o-audio-preview")
    api_key = os.getenv("api_key", "")

    print(f"Endpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Key: {api_key}")

    try:
        # 1. Configure Azure OpenAI model using environment variables
        model_config = AzureOpenAIModelConfiguration(
            azure_endpoint=endpoint,
            api_key=api_key,
            azure_deployment=deployment,
            api_version="2025-01-01-preview",
        )

        print("✅ Model configuration loaded successfully")

        # 2. Get Azure AI project configuration (supports both foundry and hub-based projects)
        azure_ai_project = get_azure_ai_project()
        if not azure_ai_project:
            print("❌ No Azure AI project configuration found. Please set either:")
            print("   - AZURE_AI_PROJECT_ENDPOINT (for foundry-based projects), or")
            print("   - AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP_NAME, AZURE_PROJECT_NAME (for hub-based projects)")
            return

        # 3. Create conversation quality grader
        score_model = AzureOpenAIScoreModelGrader(
            model_config=model_config,
            name="Tone/Emotion Grader",
            model="gpt-4o-audio-preview",
            input=[
                {
                    "role": "system",
                    "content": "Evaluate the provided audio for tone and emotion. Return a float score in [0,1] where 1 means the speaker sounds cheerful and friendly.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Listen to this clip and score tone/emotion."},
                        {
                            "type": "input_audio",
                            "input_audio": {"data": "{{ sample.output_audio.data }}", "format": "wav"},
                        },
                    ],
                },
            ],
            range=[0.0, 1.0],
            pass_threshold=0.5,
        )

        print("✅ Conversation quality grader created successfully")

        # 4. Run evaluation with the score model grader
        print("\n🚀 Running evaluation with score model grader...")
        result = evaluate(
            data=data_file,
            evaluators={"score_model": score_model},
            azure_ai_project=azure_ai_project,
            tags={
                "grader_type": "score_model",
                "model": "gpt-4o-audio-preview",
                "evaluation_focus": "score_model",
                "sample_size": "demo",
                "automation_level": "full",
            },
            data_source_config={
                "type": "custom",
                "item_schema": {
                    "type": "object",
                    "properties": {"messages": {"type": "array"}},
                    "required": ["messages"],
                },
                "include_sample_schema": True,
            },
            data_source={
                "type": "completions",
                "model": "gpt-4o-audio-preview",
                "input_messages": {"type": "item_reference", "item_reference": "item.messages"},
                "sampling_params": {"temperature": 0.8},
                "modalities": ["text", "audio"],
            },
        )

        # 5. Display results
        print("\n=== Evaluation Results ===")
        print(f"Total samples evaluated: {len(result['rows'])}")

        # Show metrics
        print("\n=== Metrics Summary ===")
        for metric_name, metric_value in result["metrics"].items():
            print(f"{metric_name}: {metric_value:.3f}")

        # Show detailed results
        print("\n=== Sample Results ===")
        df = pd.DataFrame(result["rows"])

        for i, row in df.head(3).iterrows():
            print(f"\nSample {i+1}:")
            print(f"  Context: {row.get('context', 'N/A')}")

            # Show grader results
            for col in df.columns:
                if col.startswith("outputs."):
                    grader_name = col.split(".")[1]
                    print(f"  {grader_name} - {col} : {row[col]}")

        print("\n✅ Evaluation completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during evaluation: {str(e)}")

    # Clean up
    if os.path.exists(data_file):
        os.remove(data_file)
        print(f"\n🧹 Cleaned up temporary file: {data_file}")


if __name__ == "__main__":
    print("🚀 Starting Azure OpenAI Score Model Grader Demo\n")

    # Check if environment variables are set
    required_vars = ["endpoint", "api_key", "deployment_name_audio"]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
    else:
        print("✅ All environment variables found")
        demonstrate_score_model_grader()

    print("\n🎉 Demo completed!")
