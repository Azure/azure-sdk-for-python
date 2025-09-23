# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Run AOAI score-model graders on purposely disordered data to spot row-mapping bugs."""

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
    AzureOpenAIModelConfiguration,
    AzureOpenAIScoreModelGrader,
    ContentSafetyEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    evaluate,
)
from azure.ai.evaluation._constants import ROW_ID_COLUMN


load_dotenv()


def _build_dataset() -> Tuple[str, pd.DataFrame]:
    """Create a JSONL file with varied conversations and shuffle ordering to stress row alignment."""

    scenarios: List[Dict[str, object]] = [
        {
            "context": "Physics explanation",
            "expected_quality": "high",
            "messages": [
                ("user", "Rate the clarity of this message about quantum tunneling."),
                (
                    "assistant",
                    "Quantum tunneling lets particles cross barriers even when classical mechanics forbids it.",
                ),
            ],
        },
        {
            "context": "Gardening guidance",
            "expected_quality": "low",
            "messages": [
                ("user", "Evaluate this reply about caring for house plants."),
                ("assistant", "Always water daily even if the soil is wet."),
            ],
        },
        {
            "context": "Code review",
            "expected_quality": "medium",
            "messages": [
                ("user", "Does this code sample follow Python best practices?"),
                (
                    "assistant",
                    "def add(a,b):\n    return a+b\n\nIt works but should space operands and add type hints.",
                ),
            ],
        },
        {
            "context": "Testing advice",
            "expected_quality": "high",
            "messages": [
                ("user", "Help me summarise the benefits of unit testing."),
                ("assistant", "Unit tests catch regressions early, document intent, and enable safe refactoring."),
            ],
        },
        {
            "context": "Travel recommendation",
            "expected_quality": "medium",
            "messages": [
                ("user", "Assess whether this travel recommendation is comprehensive."),
                (
                    "assistant",
                    "Paris offers the Eiffel Tower, Louvre, café culture, and calming Seine river cruises.",
                ),
            ],
        },
        {
            "context": "Customer support guidance",
            "expected_quality": "low",
            "messages": [
                ("user", "Judge the professionalism of this customer support response."),
                ("assistant", "Hey there! Chill out, your package will arrive whenever it feels like it."),
            ],
        },
        {
            "context": "Computer science tutoring",
            "expected_quality": "high",
            "messages": [
                ("user", "Evaluate how well this explanation teaches recursion."),
                (
                    "assistant",
                    "Recursion solves problems by calling itself on smaller inputs until a base case is reached;"
                    " factorial(n) = n * factorial(n-1) with factorial(1) = 1.",
                ),
            ],
        },
        {
            "context": "Nutrition advice",
            "expected_quality": "medium",
            "messages": [
                ("user", "Rate this advice about balanced diets."),
                (
                    "assistant",
                    "Aim for half the plate vegetables, a quarter protein, and a quarter whole grains each meal.",
                ),
            ],
        },
        {
            "context": "Career advice",
            "expected_quality": "high",
            "messages": [
                ("user", "Assess this career advice for switching to data science."),
                (
                    "assistant",
                    "Build portfolio projects, learn statistics, and contribute to open-source to showcase skills.",
                ),
            ],
        },
        {
            "context": "Music recommendation",
            "expected_quality": "medium",
            "messages": [
                ("user", "Rate this playlist suggestion for focus work."),
                (
                    "assistant",
                    "Try lo-fi hip hop instrumentals, soft piano, and light rain sounds for sustained focus.",
                ),
            ],
        },
        {
            "context": "History summary",
            "expected_quality": "high",
            "messages": [
                ("user", "How accurate is this overview of the printing press?"),
                (
                    "assistant",
                    "Gutenberg combined movable type, oil-based inks, and a modified wine press, sparking mass literacy.",
                ),
            ],
        },
        {
            "context": "Language learning",
            "expected_quality": "medium",
            "messages": [
                ("user", "Evaluate this method for learning vocabulary."),
                (
                    "assistant",
                    "Just cram word lists once a weekend; repetition isn't needed if you read carefully once.",
                ),
            ],
        },
        {
            "context": "Project planning",
            "expected_quality": "high",
            "messages": [
                ("user", "Rate the quality of this sprint plan."),
                (
                    "assistant",
                    "Set clear sprint goals, leave buffer for spikes, and review backlog grooming every Thursday.",
                ),
            ],
        },
        {
            "context": "Cooking guidance",
            "expected_quality": "medium",
            "messages": [
                ("user", "Assess this answer about making sourdough starter."),
                (
                    "assistant",
                    "Mix equal parts flour and water, feed daily, discard half, and wait for bubbles and doubling.",
                ),
            ],
        },
        {
            "context": "Financial literacy",
            "expected_quality": "high",
            "messages": [
                ("user", "Evaluate this budgeting recommendation."),
                (
                    "assistant",
                    "Track expenses weekly, save 20% when possible, and adjust budget categories each quarter.",
                ),
            ],
        },
        {
            "context": "Mindfulness coaching",
            "expected_quality": "medium",
            "messages": [
                ("user", "Assess this meditation routine."),
                (
                    "assistant",
                    "Sit upright, focus on breathing for five minutes, notice distractions, and gently refocus.",
                ),
            ],
        },
        {
            "context": "Homework help",
            "expected_quality": "low",
            "messages": [
                ("user", "Evaluate this homework response."),
                ("assistant", "Here are all the answers copied from the back of the book—no explanation needed."),
            ],
        },
        {
            "context": "Cybersecurity",
            "expected_quality": "high",
            "messages": [
                ("user", "Judge this security hardening advice."),
                (
                    "assistant",
                    "Enable MFA, monitor logs daily, patch quickly, and enforce least-privilege access controls.",
                ),
            ],
        },
        {
            "context": "Public speaking",
            "expected_quality": "medium",
            "messages": [
                ("user", "Rate this tip for handling stage fright."),
                (
                    "assistant",
                    "Imagine the audience embarrassed instead of practicing; it'll make you instantly confident.",
                ),
            ],
        },
        {
            "context": "Science fiction writing",
            "expected_quality": "high",
            "messages": [
                ("user", "Assess this short sci-fi prompt."),
                (
                    "assistant",
                    "On the twelfth terraformed moon, android archivists discover music that rewrites their core rules.",
                ),
            ],
        },
        {
            "context": "Urban planning",
            "expected_quality": "medium",
            "messages": [
                ("user", "Evaluate this plan for revitalizing downtown parks."),
                (
                    "assistant",
                    "Add shaded seating, weekend markets, better lighting, and collect resident feedback quarterly.",
                ),
            ],
        },
        {
            "context": "Astronomy lesson",
            "expected_quality": "high",
            "messages": [
                ("user", "Judge this explanation of exoplanet detection."),
                (
                    "assistant",
                    "Transit methods watch brightness dips while radial velocity tracks stellar wobbles via spectra.",
                ),
            ],
        },
        {
            "context": "Art critique",
            "expected_quality": "medium",
            "messages": [
                ("user", "Assess this feedback on a watercolor landscape."),
                (
                    "assistant",
                    "The palette is cohesive, but layering washes for depth in the hills would add atmosphere.",
                ),
            ],
        },
        {
            "context": "Study habits",
            "expected_quality": "high",
            "messages": [
                ("user", "Evaluate this study technique."),
                (
                    "assistant",
                    "Use spaced repetition flashcards, teach topics aloud, and run timed self-quizzes weekly.",
                ),
            ],
        },
        {
            "context": "Sustainability advice",
            "expected_quality": "medium",
            "messages": [
                ("user", "Rate this plan for reducing household waste."),
                (
                    "assistant",
                    "Compost scraps, switch to refillable goods, and audit trash output monthly for quick wins.",
                ),
            ],
        },
    ]

    rows = [
        {
            "conversation": {
                "messages": [{"role": role, "content": content} for role, content in scenario["messages"]]
            },
            "expected_quality": scenario["expected_quality"],
            "context": scenario["context"],
        }
        for scenario in scenarios
    ]

    df = pd.DataFrame(rows)
    shuffled_df = df.sample(frac=1.0, random_state=123).reset_index(drop=True)

    output_path = Path(tempfile.gettempdir()) / "aoai_order_debug.jsonl"
    shuffled_df.to_json(output_path, orient="records", lines=True, force_ascii=False)

    return str(output_path), shuffled_df


def _create_azure_ai_project():
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


def _build_model_config() -> Tuple[AzureOpenAIModelConfiguration, Dict[str, str]]:
    api_key = os.environ.get("key") or os.environ.get("AZURE_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    endpoint = os.environ.get("endpoint") or os.environ.get("AZURE_OPENAI_ENDPOINT")
    deployment = os.environ.get("deployment_name") or os.environ.get("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    if not all([api_key, endpoint, deployment]):
        raise RuntimeError(
            "Azure OpenAI configuration missing. Ensure 'key', 'endpoint', and 'deployment_name' (or AZURE_OPENAI_*) are set."
        )

    model_settings = {
        "api_key": api_key,
        "azure_endpoint": endpoint,
        "azure_deployment": deployment,
        "api_version": api_version,
    }

    return (
        AzureOpenAIModelConfiguration(
            api_key=api_key,
            azure_endpoint=endpoint,
            azure_deployment=deployment,
            api_version=api_version,
        ),
        model_settings,
    )


def _create_graders(model_config: AzureOpenAIModelConfiguration) -> Dict[str, AzureOpenAIScoreModelGrader]:
    base_prompt = (
        "You are grading assistant helpfulness on a 0-5 scale. Provide rationale and numeric score."
        "\n"
        "RowId: {{ item." + ROW_ID_COLUMN + " }}\n"
        "Conversation:{{ item.conversation }}"
    )
    grader = AzureOpenAIScoreModelGrader(
        model_config=model_config,
        name="helpfulness_grader",
        model="gpt-5-nano",
        input=[{"role": "system", "content": base_prompt}],
        range=[0.0, 5.0],
        pass_threshold=3.0,
    )
    depth_prompt = (
        "You are reviewing responses for thoroughness. Judge whether the assistant fully addressed the user's goals,"
        " covered important details, and explained reasoning when appropriate."
        "\nRowId: {{ item." + ROW_ID_COLUMN + " }}\n"
        "Conversation: {{ item.conversation }}"
    )
    thoroughness_grader = AzureOpenAIScoreModelGrader(
        model_config=model_config,
        name="thoroughness_grader",
        model="gpt-5-nano",
        input=[{"role": "system", "content": depth_prompt}],
        range=[0.0, 5.0],
        pass_threshold=3.5,
    )
    return {"helpfulness": grader, "thoroughness": thoroughness_grader}


def _create_model_based_evaluators(model_settings: Dict[str, str]) -> Dict[str, object]:
    generic_model_config = {
        "azure_endpoint": model_settings["azure_endpoint"],
        "api_key": model_settings["api_key"],
        "azure_deployment": model_settings["azure_deployment"],
        "api_version": model_settings["api_version"],
    }

    fluency = FluencyEvaluator(model_config=generic_model_config, is_reasoning_model=True)
    coherence = CoherenceEvaluator(model_config=generic_model_config, is_reasoning_model=True)
    return {"fluency": fluency, "coherence": coherence}


def run_evaluation():
    dataset_path, shuffled_df = _build_dataset()
    model_config, model_settings = _build_model_config()
    graders = _create_graders(model_config)
    azure_ai_project = _create_azure_ai_project()
    additional_evaluators = _create_model_based_evaluators(model_settings)

    results = evaluate(
        evaluation_name="aoai_and_other_reasoning",
        data=dataset_path,
        evaluators={
            **graders,
            **additional_evaluators,
            "content_safety": ContentSafetyEvaluator(
                azure_ai_project=azure_ai_project, credential=DefaultAzureCredential()
            ),
        },
        azure_ai_project=azure_ai_project,
        tags={"purpose": "aoai_order_debug"},
    )

    evaluation_rows = pd.DataFrame(results["rows"])  # type: ignore[index]
    _inspect_alignment(shuffled_df, evaluation_rows)


def _inspect_alignment(input_df: pd.DataFrame, eval_df: pd.DataFrame) -> None:
    def _normalize_conversation(conv: object) -> List[Tuple[str, str]]:
        if isinstance(conv, dict):
            messages = conv.get("messages", [])
        else:
            messages = []
        normalized: List[Tuple[str, str]] = []
        for message in messages:
            if isinstance(message, dict):
                role = str(message.get("role", ""))
                content = str(message.get("content", ""))
            else:
                role, content = "", str(message)
            normalized.append((role, content))
        return normalized

    print("\n======= Input ordering (shuffled) =======")
    display_cols = [col for col in ["context", "expected_quality"] if col in input_df.columns]
    print(input_df[display_cols])

    print("\n======= Evaluation ordering =======")
    score_columns = sorted(col for col in eval_df.columns if col.startswith("outputs.") and col.endswith(".score"))
    eval_display_cols = [
        col for col in [ROW_ID_COLUMN, "inputs.context", "inputs.expected_quality", "context"] if col in eval_df.columns
    ] + [col for col in score_columns if col in eval_df.columns]
    print(eval_df[eval_display_cols])

    mismatches = []
    expected_conversations = input_df["conversation"].apply(_normalize_conversation)
    eval_conversations_column = eval_df.get("inputs.conversation")
    if eval_conversations_column is None:
        eval_conversations = pd.Series([[] for _ in range(len(eval_df))], dtype=object)
    else:
        eval_conversations = eval_conversations_column.apply(_normalize_conversation)

    max_len = max(len(input_df), len(eval_df))
    for idx in range(max_len):
        if idx >= len(eval_df):
            mismatches.append((idx, "<missing>", "evaluation output missing for this row"))
            continue
        eval_row = eval_df.iloc[idx]
        sdk_row_id = str(eval_row.get(ROW_ID_COLUMN, "<missing>"))

        if idx >= len(input_df):
            mismatches.append((idx, sdk_row_id, "extra evaluation row with no matching input"))
            continue

        expected_conv = expected_conversations.iloc[idx]
        result_conv = eval_conversations.iloc[idx]
        if expected_conv != result_conv:
            mismatches.append((idx, sdk_row_id, "conversation content differs"))
            continue

        expected_context = input_df.iloc[idx].get("context")
        result_context = eval_row.get("inputs.context", eval_row.get("context"))
        if expected_context != result_context:
            mismatches.append((idx, sdk_row_id, "context value differs"))

    if not mismatches:
        print("\nAll rows preserved their conversation content and order.")
    else:
        print("\n⚠️  Alignment issues detected:")
        for idx, row_id, reason in mismatches:
            print(f"  - Eval row {idx} (row_id={row_id}): {reason}")


if __name__ == "__main__":
    run_evaluation()
