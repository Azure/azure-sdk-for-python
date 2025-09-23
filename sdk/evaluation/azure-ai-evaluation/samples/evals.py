# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Run built-in evaluators on conversation data."""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import (
    AzureAIProject,
    ContentSafetyEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    GroundednessEvaluator,
    RelevanceEvaluator,
    SimilarityEvaluator,
    F1ScoreEvaluator,
    evaluate,
)


load_dotenv()


def _build_datasets() -> Tuple[str, str]:
    """Create two JSONL datasets: one conversation-only, one ground-truth based."""

    scenarios: List[Dict[str, object]] = [
        {
            "context": "Physics explanation",
            "ground_truth": "Quantum tunneling allows particles to pass through energy barriers that classical physics would prohibit.",
            "messages": [
                ("user", "Explain quantum tunneling in simple terms."),
                (
                    "assistant",
                    "Quantum tunneling lets particles cross barriers even when classical mechanics forbids it. "
                    "It's like a ball going through a wall instead of over it.",
                ),
            ],
        },
        {
            "context": "Gardening guidance",
            "ground_truth": "Water plants when the top inch of soil is dry, typically every 2-3 days for most houseplants.",
            "messages": [
                ("user", "How often should I water my houseplants?"),
                (
                    "assistant",
                    "Water your plants when the soil feels dry about an inch down. This is usually every few days.",
                ),
            ],
        },
        {
            "context": "Code review",
            "ground_truth": "Python code should follow PEP 8 guidelines including proper spacing and type hints.",
            "messages": [
                ("user", "Review this Python function for best practices."),
                (
                    "assistant",
                    "def add(a: int, b: int) -> int:\n    return a + b\n\n"
                    "This follows PEP 8 with type hints and proper spacing.",
                ),
            ],
        },
        {
            "context": "Testing advice",
            "ground_truth": "Unit tests verify individual components, catch bugs early, and serve as documentation.",
            "messages": [
                ("user", "What are the benefits of unit testing?"),
                ("assistant", "Unit tests catch regressions early, document intent, and enable safe refactoring."),
            ],
        },
        {
            "context": "Travel recommendation",
            "ground_truth": "Paris offers iconic landmarks, world-class museums, and rich cultural experiences.",
            "messages": [
                ("user", "What makes Paris a good travel destination?"),
                (
                    "assistant",
                    "Paris offers the Eiffel Tower, Louvre, café culture, and calming Seine river cruises.",
                ),
            ],
        },
        {
            "context": "Customer support guidance",
            "ground_truth": "Customer support should be professional, empathetic, and solution-focused.",
            "messages": [
                ("user", "How should customer support respond to complaints?"),
                (
                    "assistant",
                    "Listen actively, acknowledge concerns, apologize sincerely, and offer clear solutions with timelines.",
                ),
            ],
        },
        {
            "context": "Computer science tutoring",
            "ground_truth": "Recursion is a programming technique where a function calls itself to solve smaller subproblems.",
            "messages": [
                ("user", "Explain recursion with an example."),
                (
                    "assistant",
                    "Recursion solves problems by calling itself on smaller inputs until a base case is reached. "
                    "For example: factorial(n) = n * factorial(n-1) with factorial(1) = 1.",
                ),
            ],
        },
        {
            "context": "Nutrition advice",
            "ground_truth": "A balanced diet includes vegetables, proteins, whole grains, and healthy fats in appropriate portions.",
            "messages": [
                ("user", "What does a balanced meal look like?"),
                (
                    "assistant",
                    "Aim for half the plate vegetables, a quarter protein, and a quarter whole grains each meal.",
                ),
            ],
        },
        {
            "context": "Career advice",
            "ground_truth": "Switching to data science requires learning statistics, programming, and building a portfolio.",
            "messages": [
                ("user", "How do I transition into data science?"),
                (
                    "assistant",
                    "Build portfolio projects, learn statistics and Python/R, and contribute to open-source to showcase skills.",
                ),
            ],
        },
        {
            "context": "Music recommendation",
            "ground_truth": "Focus music should be instrumental, consistent tempo, and without distracting lyrics.",
            "messages": [
                ("user", "What music helps with concentration?"),
                (
                    "assistant",
                    "Try lo-fi hip hop instrumentals, soft piano, and light rain sounds for sustained focus.",
                ),
            ],
        },
        {
            "context": "History summary",
            "ground_truth": "Gutenberg's printing press revolutionized communication and literacy in the 15th century.",
            "messages": [
                ("user", "What was the impact of the printing press?"),
                (
                    "assistant",
                    "Gutenberg combined movable type, oil-based inks, and a modified wine press, sparking mass literacy and the spread of ideas.",
                ),
            ],
        },
        {
            "context": "Language learning",
            "ground_truth": "Effective vocabulary learning uses spaced repetition and contextual practice.",
            "messages": [
                ("user", "What's the best way to learn new vocabulary?"),
                (
                    "assistant",
                    "Use spaced repetition flashcards, read extensively, and practice words in context through writing and speaking.",
                ),
            ],
        },
        {
            "context": "Project planning",
            "ground_truth": "Agile sprint planning includes clear goals, estimated tasks, and buffer time.",
            "messages": [
                ("user", "How should I plan a two-week sprint?"),
                (
                    "assistant",
                    "Set clear sprint goals, estimate story points, leave 20% buffer for unexpected issues, and review backlog weekly.",
                ),
            ],
        },
        {
            "context": "Cooking guidance",
            "ground_truth": "Sourdough starter requires flour, water, time, and consistent feeding schedule.",
            "messages": [
                ("user", "How do I make sourdough starter?"),
                (
                    "assistant",
                    "Mix equal parts flour and water, feed daily, discard half, and wait for bubbles and doubling in size.",
                ),
            ],
        },
        {
            "context": "Financial literacy",
            "ground_truth": "Budgeting involves tracking income, expenses, and savings goals systematically.",
            "messages": [
                ("user", "What's a good budgeting approach?"),
                (
                    "assistant",
                    "Track expenses weekly, follow the 50/30/20 rule (needs/wants/savings), and adjust budget categories quarterly.",
                ),
            ],
        },
    ]

    # Conversation-only dataset (no extra fields)
    conv_rows = [
        {"conversation": {"messages": [{"role": role, "content": content} for role, content in scenario["messages"]]}}
        for scenario in scenarios
    ]

    # Ground-truth dataset with explicit columns
    gt_rows = []
    for scenario in scenarios:
        msgs = scenario["messages"]
        # Extract the last user/assistant turn
        last_user = next((m[1] for m in reversed(msgs) if m[0] == "user"), "")
        last_assistant = next((m[1] for m in reversed(msgs) if m[0] == "assistant"), "")
        gt_rows.append(
            {
                "query": last_user,
                "response": last_assistant,
                "ground_truth": scenario["ground_truth"],
                "context": scenario["context"],
            }
        )

    conv_df = pd.DataFrame(conv_rows)
    gt_df = pd.DataFrame(gt_rows)

    conv_path = Path(tempfile.gettempdir()) / "builtin_eval_conversation.jsonl"
    gt_path = Path(tempfile.gettempdir()) / "builtin_eval_ground_truth.jsonl"
    conv_df.to_json(conv_path, orient="records", lines=True, force_ascii=False)
    gt_df.to_json(gt_path, orient="records", lines=True, force_ascii=False)

    return str(conv_path), str(gt_path)


def _create_azure_ai_project():
    """Create Azure AI project configuration from environment variables."""
    endpoint = os.environ.get("AZURE_AI_PROJECT_ENDPOINT")
    if endpoint:
        print("✅ Using foundry-based Azure AI project")
        return endpoint

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

    raise RuntimeError("Azure AI project configuration missing. Set AZURE_AI_PROJECT_ENDPOINT or the hub-based trio.")


def _get_model_config() -> Dict[str, str]:
    """Get Azure OpenAI model configuration from environment variables."""
    # Prefer Azure-specific variables first to avoid unintentionally selecting
    # incompatible deployments from generic env vars.
    api_key = os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("key")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT") or os.environ.get("endpoint")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT") or os.environ.get("deployment_name")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not all([api_key, endpoint, deployment]):
        raise RuntimeError(
            "Azure OpenAI configuration missing. Ensure 'key', 'endpoint', and 'deployment_name' (or AZURE_OPENAI_*) are set."
        )

    cfg = {
        "api_key": api_key,
        "azure_endpoint": endpoint,
        "azure_deployment": deployment,
        "api_version": api_version,
    }
    print(f"🔧 Using deployment '{deployment}' at '{endpoint}' (api_version={api_version})")
    return cfg


def _create_conv_evaluators(model_settings: Dict[str, str], azure_ai_project) -> Dict[str, object]:
    """Evaluators that accept conversation input only."""
    fluency = FluencyEvaluator(model_config=model_settings, is_reasoning_model=True)
    coherence = CoherenceEvaluator(model_config=model_settings, is_reasoning_model=True)
    relevance = RelevanceEvaluator(model_config=model_settings, is_reasoning_model=True)
    content_safety = ContentSafetyEvaluator(azure_ai_project=azure_ai_project, credential=DefaultAzureCredential())
    return {
        "fluency": fluency,
        "coherence": coherence,
        "relevance": relevance,
        "content_safety": content_safety,
    }


def _create_gt_evaluators(model_settings: Dict[str, str], azure_ai_project) -> Dict[str, object]:
    """Evaluators that require explicit ground truth/response (no conversation)."""
    groundedness = GroundednessEvaluator(model_config=model_settings, is_reasoning_model=True)
    similarity = SimilarityEvaluator(model_config=model_settings, is_reasoning_model=True)
    f1_score = F1ScoreEvaluator()
    return {
        "groundedness": groundedness,
        "similarity": similarity,
        "f1_score": f1_score,
    }


def run_evaluation():
    """Run two evaluations: conversation-based and ground-truth-based."""
    print("🚀 Starting built-in evaluators sample (split runs)")

    # Prepare data (two datasets)
    conv_path, gt_path = _build_datasets()
    print(f"✅ Created conversation dataset at: {conv_path}")
    print(f"✅ Created ground-truth dataset at: {gt_path}")

    # Configure models and project
    model_settings = _get_model_config()
    azure_ai_project = _create_azure_ai_project()
    # Create evaluator sets
    conv_evaluators = _create_conv_evaluators(model_settings, azure_ai_project)
    gt_evaluators = _create_gt_evaluators(model_settings, azure_ai_project)

    print(f"✅ Configured {len(conv_evaluators)} conversation evaluators")
    print(f"✅ Configured {len(gt_evaluators)} ground-truth evaluators")

    # Run conversation-based evaluation
    print("\n📊 Running conversation-based evaluation...")
    results_conv = evaluate(
        evaluation_name="builtin_evaluators_conversation",
        data=conv_path,
        evaluators=conv_evaluators,
        azure_ai_project=azure_ai_project,
        tags={
            "purpose": "builtin_evaluation_conversation",
            "evaluator_count": str(len(conv_evaluators)),
        },
    )

    # Run ground-truth-based evaluation
    print("\n📊 Running ground-truth-based evaluation...")
    results_gt = evaluate(
        evaluation_name="builtin_evaluators_ground_truth",
        data=gt_path,
        evaluators=gt_evaluators,
        azure_ai_project=azure_ai_project,
        tags={
            "purpose": "builtin_evaluation_ground_truth",
            "evaluator_count": str(len(gt_evaluators)),
        },
    )

    # Display brief results summary for each run
    def _summarize(result_obj, title: str):
        print(f"\n📈 {title}")
        print("=" * 50)
        if "metrics" in result_obj:
            metrics = result_obj["metrics"]
            print("\nOverall Metrics:")
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, (int, float)):
                    print(f"  {metric_name}: {metric_value:.3f}")
                else:
                    print(f"  {metric_name}: {metric_value}")
        if "rows" in result_obj:
            df = pd.DataFrame(result_obj["rows"])
            print(f"\nEvaluated {len(df)} rows")

    _summarize(results_conv, "Conversation Evaluation Results Summary")
    _summarize(results_gt, "Ground-Truth Evaluation Results Summary")

    print("\n✅ Evaluation complete!")
    return {"conversation": results_conv, "ground_truth": results_gt}


if __name__ == "__main__":
    run_evaluation()
