from IPython.display import display
import pandas as pd
import numpy as np
import json
import re
from itertools import combinations
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Sequence, Tuple


from azure.ai.evaluation import AzureOpenAIModelConfiguration
from azure.ai.evaluation._evaluators._workflow_planning import _WorkflowPlanningEvaluator
from datetime import datetime
import os
from dotenv import load_dotenv

print(f"Loading environment variables")
load_dotenv()
print("Loaded environment variables")

models_config = {
    "gpt-5.1": {
        "model_config": AzureOpenAIModelConfiguration(
            azure_endpoint=os.environ["EVAL_GPT5_1_ENDPOINT"],
            api_key=os.environ["EVAL_GPT5_1_API_KEY"],
            api_version=os.environ["EVAL_GPT5_1_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT5_1_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "gpt-5": {
        "model_config": AzureOpenAIModelConfiguration(
            azure_endpoint=os.environ["EVAL_GPT5_ENDPOINT"],
            api_key=os.environ["EVAL_GPT5_API_KEY"],
            api_version=os.environ["EVAL_GPT5_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT5_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "gpt-4o": {
        "model_config": AzureOpenAIModelConfiguration(  # 10.00$ per 1M output tokens
            azure_endpoint=os.environ["EVAL_GPT4O_ENDPOINT"],
            api_key=os.environ["EVAL_GPT4O_API_KEY"],
            api_version=os.environ["EVAL_GPT4O_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT4O_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "gpt-4.1": {
        "model_config": AzureOpenAIModelConfiguration(  # 8.00$ per 1M output tokens
            azure_endpoint=os.environ["EVAL_GPT4_1_ENDPOINT"],
            api_key=os.environ["EVAL_GPT4_1_API_KEY"],
            api_version=os.environ["EVAL_GPT4_1_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT4_1_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "gpt-4.1-mini": {
        "model_config": AzureOpenAIModelConfiguration(  # 0.60$ per 1M output tokens
            azure_endpoint=os.environ["EVAL_GPT4_1_MINI_ENDPOINT"],
            api_key=os.environ["EVAL_GPT4_1_MINI_API_KEY"],
            api_version=os.environ["EVAL_GPT4_1_MINI_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT4_1_MINI_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "gpt-4.1-nano": {
        "model_config": AzureOpenAIModelConfiguration(  # 0.40$ per 1M output tokens
            azure_endpoint=os.environ["EVAL_GPT4_1_NANO_ENDPOINT"],
            api_key=os.environ["EVAL_GPT4_1_NANO_API_KEY"],
            api_version=os.environ["EVAL_GPT4_1_NANO_API_VERSION"],
            azure_deployment=os.environ["EVAL_GPT4_1_NANO_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": False,
    },
    "o4-mini": {
        "model_config": AzureOpenAIModelConfiguration(  # 0.60$ per 1M output tokens
            azure_endpoint=os.environ["EVAL_O4_MINI_ENDPOINT"],
            api_key=os.environ["EVAL_O4_MINI_API_KEY"],
            api_version=os.environ["EVAL_O4_MINI_API_VERSION"],
            azure_deployment=os.environ["EVAL_O4_MINI_DEPLOYMENT_NAME"],
        ),
        "is_reasoning_model": True,
    },
}


def create_evaluators(model_settings, **evaluator_kwargs):
    """Create evaluators for the given model configuration."""
    return {
        "WorkflowPlanningEvaluator": _WorkflowPlanningEvaluator(**model_settings, **evaluator_kwargs),
    }


def create_evaluators_for_models(
    enabled_models: list = ["gpt-5.1", "gpt-5", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4.1", "gpt-4o", "o4-mini"],
    **evaluator_kwargs,
):
    # don't create evaluator for o4-mini as it is not supported yet
    print(f"Creating evaluators for models: {enabled_models}")
    per_model_evals = {k: create_evaluators(m, **evaluator_kwargs) for k, m in models_config.items() if k in enabled_models}
    print(f"Evaluators created: {per_model_evals.keys()}")
    return per_model_evals


def load_ground_truth_data(csv_path: str, base_dir: str) -> pd.DataFrame:
    """Load ground truth CSV and the corresponding JSON trace files.

    Parameters
    ----------
    csv_path : str
        Path to ground_truth.csv with columns: path, ground_truth.
    base_dir : str
        Base directory to resolve relative trace file paths.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: trace_id, workflow_trace, ground_truth.
    """
    df = pd.read_csv(csv_path)
    records = []
    for _, row in df.iterrows():
        trace_path = os.path.join(base_dir, row["path"])
        trace_id = os.path.splitext(os.path.basename(row["path"]))[0]
        with open(trace_path, encoding="utf-8") as f:
            workflow_trace = json.load(f)
        records.append({
            "trace_id": trace_id,
            "workflow_trace": workflow_trace,
            "ground_truth": int(row["ground_truth"]),
        })
    result_df = pd.DataFrame(records)
    print(f"Loaded {len(result_df)} traces from {csv_path}")
    print(f"  ground_truth=1: {(result_df['ground_truth'] == 1).sum()}, ground_truth=0: {(result_df['ground_truth'] == 0).sum()}")
    return result_df


import time
import pandas as pd
import numpy as np
import concurrent.futures


def evaluate_single_model(
    model, workflow_trace, num_runs, evaluator_func, eval_key, num_workers=3
):
    """
    Evaluate a single model multiple times with the given workflow trace.
    This function runs in a thread, so it uses the global per_model_evals.
    Now supports parallel execution of individual runs.
    Updated for binary scoring (True/False).
    """
    print(f"Evaluating {model} with {num_workers} threads...")
    start = time.time()
    # initialize counts for binary scores: False (0) and True (1)
    counts = {0: 0, 1: 0}  # False and True counts

    def run_single_evaluation(run_idx):
        """Helper function to run a single evaluation"""
        try:
            res = evaluator_func(workflow_trace=workflow_trace)
            score = res[eval_key]
            # Convert boolean to int (False -> 0, True -> 1)
            score_int = int(score) if isinstance(score, bool) else (1 if score else 0)
            print(f"For {run_idx+1}/{num_runs} execution of model {model} got score: {score} ({score_int})")
            return score_int
        except Exception as e:
            print(f"Error in {model} run {run_idx+1}: {e}")
            return None

    # Run evaluations in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_run = {executor.submit(run_single_evaluation, i): i for i in range(num_runs)}

        for future in concurrent.futures.as_completed(future_to_run):
            score = future.result()
            if score is not None:
                counts[score] += 1

    elapsed = time.time() - start
    result = {
        "model": model,
        "secs_taken": round(elapsed, 1),
        "Score_False": counts[0],  # Count of False results
        "Score_True": counts[1],  # Count of True results
    }
    print(f"Final result for {model}: {result}")
    return result


def evaluate_models(
    per_model_evals,
    df,
    evaluator_name,
    eval_key,
    runs_per_input=5,
    num_workers=3,
    human_labels=False,
    output_filename=None,
    cooldown_every=2,
    cooldown_secs=45,
):
    """
    For each row in df (i.e. trace_id, workflow_trace), evaluate each model in models,
    runs_per_input times with the given evaluator and eval_key.

    Saves results incrementally per (trace_id, model) so evaluation can resume if interrupted.

    Updated for binary scoring (True/False).
    Uses ThreadPoolExecutor instead of ProcessPoolExecutor to avoid serialization issues.
    Reduced default num_workers to 3 to be more conservative with API rate limits.
    """
    key_cols = ["trace_id", "workflow_trace"]
    assert all(col in df.columns for col in key_cols), f"DataFrame must contain columns: {key_cols}"
    models = list(per_model_evals.keys())

    # Determine output filename
    n = len(df)
    k = runs_per_input
    if output_filename is None:
        output_filename = f"{evaluator_name}_n{n}_k{k}_now.tsv"

    # Load existing results for resume support
    completed_pairs = set()
    if os.path.exists(output_filename):
        existing_df = pd.read_csv(output_filename, sep="\t")
        for _, row in existing_df.iterrows():
            completed_pairs.add((str(row["trace_id"]), str(row["model"])))
        print(f"Resuming: found {len(completed_pairs)} completed (trace_id, model) pairs in {output_filename}")
    else:
        # Write header for new file
        header_cols = [
            "model", "secs_taken", "Score_False", "Score_True",
            "num_runs", "success_rate", "failure_rate", "mean_score", "variance", "trace_id",
        ]
        pd.DataFrame(columns=header_cols).to_csv(output_filename, sep="\t", index=False)
        print(f"Created new output file: {output_filename}")

    print(f"Starting evaluation with {len(models)} models, {len(df)} traces, {runs_per_input} runs per input")
    print(f"Rate limit cooldown: {cooldown_secs}s every {cooldown_every} traces")

    traces_since_cooldown = 0

    # Run models in parallel using ThreadPoolExecutor
    for idx, row in df.iterrows():
        trace_id = row["trace_id"]
        workflow_trace = row["workflow_trace"]

        # Filter out models already completed for this trace
        remaining_models = [m for m in models if (str(trace_id), m) not in completed_pairs]
        if not remaining_models:
            print(f"\nSkipping trace {idx + 1}/{len(df)} (trace_id: {trace_id}) — all models already completed")
            continue

        records = []
        print(f"\nProcessing trace {idx + 1}/{len(df)} (trace_id: {trace_id}), {len(remaining_models)}/{len(models)} models remaining...")

        # Use ThreadPoolExecutor instead of ProcessPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(remaining_models)) as executor:
            future_to_model = {
                executor.submit(
                    evaluate_single_model,
                    model,
                    workflow_trace,
                    runs_per_input,
                    per_model_evals[model][evaluator_name],
                    eval_key,
                    num_workers,
                ): model
                for model in remaining_models
            }

            for future in concurrent.futures.as_completed(future_to_model):
                model = future_to_model[future]
                try:
                    result = future.result()
                    records.append(result)
                    print(f"✓ Completed evaluation for {model}")
                except concurrent.futures.TimeoutError:
                    print(f"✗ Timeout for {model} - skipping")
                except Exception as exc:
                    print(f"✗ {model} generated an exception: {exc}")
                    import traceback

                    traceback.print_exc()

        if records:
            results_df = pd.DataFrame(records)
            # Calculate metrics for binary scores
            results_df["num_runs"] = results_df["Score_False"] + results_df["Score_True"]
            results_df["success_rate"] = results_df["Score_True"] / results_df["num_runs"]
            results_df["failure_rate"] = results_df["Score_False"] / results_df["num_runs"]
            results_df["mean_score"] = results_df["success_rate"]
            results_df["variance"] = results_df["success_rate"] * results_df["failure_rate"]
            results_df["trace_id"] = trace_id

            # Append incrementally to TSV
            results_df.to_csv(output_filename, sep="\t", index=False, mode="a", header=False)
            print(f"Saved {len(results_df)} results for trace_id: {trace_id}")
        else:
            print(f"No successful results for trace with trace_id: {trace_id}")

        # Rate limit cooldown
        traces_since_cooldown += 1
        if traces_since_cooldown >= cooldown_every:
            traces_since_cooldown = 0
            print(f"⏳ Cooldown: sleeping {cooldown_secs}s to avoid rate limits...")
            time.sleep(cooldown_secs)

    # Read back the full results file
    final_df = pd.read_csv(output_filename, sep="\t")
    print(f"\nEvaluation complete! Total results: {len(final_df)} rows in {output_filename}")
    return final_df


def compute_intra_model_variance(results_df, models_to_use=None):
    """
    Compute the intra-model variance for binary results.
    """
    assert "model" in results_df.columns, "DataFrame must contain 'model' column"
    assert "variance" in results_df.columns, "DataFrame must contain 'variance' column"
    assert "success_rate" in results_df.columns, "DataFrame must contain 'success_rate' column"

    print()
    print(f"Computing intra-model variance for binary scores")
    print(f"*" * 50)

    if models_to_use is not None:
        print(f"Using models: {models_to_use}")
        results_df = results_df[results_df["model"].isin(models_to_use)]

    df = (
        results_df.groupby("model")
        .agg(
            {
                "variance": ["count", "mean"],
                "success_rate": ["mean", "std"],  # Using standard deviation instead of custom function
            }
        )
        .reset_index()
    )
    df.columns = ["model", "num_runs", "mean_variance", "mean_success_rate", "success_rate_std"]
    display(df)
    print(f"Intra-model variance computed for {len(df)} models.")
    print(f"Average intra-model variance: {df['mean_variance'].mean():.4f}")
    print(f"Average success rate: {df['mean_success_rate'].mean():.2%}")
    return df


def compute_inter_model_variance_df(results_df, models_to_use=None):
    """
    Compute inter-model variance statistics from the binary results DataFrame.

    Parameters:
    -----------
    results_df : pd.DataFrame
        DataFrame containing binary evaluation results.
    models_to_use : list, optional
        List of models to include in the computation.

    Returns:
    --------
    pd.DataFrame
        DataFrame with aggregated statistics per run_id.
    """
    if "trace_id" not in results_df.columns:
        raise ValueError("results_df must contain 'trace_id' column")

    print()
    print(f"Computing inter-model variance for binary scores")
    print(f"*" * 50)
    if models_to_use:
        print(f"Filtering results for models: {models_to_use}")
        results_df = results_df[results_df["model"].isin(models_to_use)]
    else:
        print(f"Using all models: {results_df['model'].unique()}")

    # Group by trace_id and aggregate binary scores
    inter_model_variance = (
        results_df.groupby("trace_id")
        .agg(
            {
                "Score_False": "sum",
                "Score_True": "sum",
                "model": "nunique",
            }
        )
        .reset_index()
    )

    inter_model_variance["num_runs"] = inter_model_variance["Score_False"] + inter_model_variance["Score_True"]
    inter_model_variance["success_rate"] = inter_model_variance["Score_True"] / inter_model_variance["num_runs"]
    inter_model_variance["failure_rate"] = inter_model_variance["Score_False"] / inter_model_variance["num_runs"]

    # For binary outcomes, variance is p(1-p)
    inter_model_variance["variance"] = inter_model_variance["success_rate"] * inter_model_variance["failure_rate"]

    # Percentage of most frequent outcome (max of success_rate and failure_rate)
    inter_model_variance["pct_mode"] = np.maximum(
        inter_model_variance["success_rate"], inter_model_variance["failure_rate"]
    )

    inter_model_variance.rename(columns={"model": "num_models"}, inplace=True)
    return inter_model_variance


def show_inter_model_variance_stats(inter_model_variance_df, show_individual_run_stats=True):
    """Display inter-model variance statistics for binary scores."""
    # Compute weighted averages
    total_runs = inter_model_variance_df["num_runs"].sum()
    weighted_avg_variance = (
        inter_model_variance_df["variance"] * inter_model_variance_df["num_runs"]
    ).sum() / total_runs
    weighted_avg_pct_mode = (
        inter_model_variance_df["pct_mode"] * inter_model_variance_df["num_runs"]
    ).sum() / total_runs
    weighted_avg_success_rate = (
        inter_model_variance_df["success_rate"] * inter_model_variance_df["num_runs"]
    ).sum() / total_runs

    print(f"Total runs across all conversations: {total_runs}")
    print(f"Weighted average variance: {weighted_avg_variance:.4f}")
    print(f"Weighted average percentage of mode: {weighted_avg_pct_mode:.4f}")
    print(f"Weighted average success rate: {weighted_avg_success_rate:.2%}")

    # Create summary statistics DataFrame
    summary_stats = pd.DataFrame(
        {
            "metric": ["total_runs", "weighted_avg_variance", "weighted_avg_pct_mode", "weighted_avg_success_rate"],
            "value": [int(total_runs), weighted_avg_variance, weighted_avg_pct_mode, weighted_avg_success_rate],
        }
    )

    if show_individual_run_stats:
        # Show individual run statistics
        print(f"\nIndividual run statistics:")
        display(inter_model_variance_df)
    print("\nSummary Statistics:")
    display(summary_stats)
    return summary_stats


def compute_pairwise_agreement_matrix(results_df):
    """
    Compute pairwise agreement matrix between models for binary scores.
    Since we already have binary scores, binarize_threshold is ignored.

    Args:
        results_df: DataFrame with binary model results
        binarize_threshold: Ignored for binary scores
    """
    # Get unique models and trace_ids
    models = results_df["model"].unique()
    trace_ids = results_df["trace_id"].unique()

    # Create agreement matrix
    agreement_matrix = pd.DataFrame(index=models, columns=models, dtype=float)

    # Fill diagonal with 100% (model agrees with itself)
    np.fill_diagonal(agreement_matrix.values, 1.0)

    # Compute pairwise agreements
    for model1, model2 in combinations(models, 2):
        total_overlap = 0
        total_n = 0

        for trace_id in trace_ids:
            # Get data for both models for this trace_id
            data1 = results_df[(results_df["model"] == model1) & (results_df["trace_id"] == trace_id)]
            data2 = results_df[(results_df["model"] == model2) & (results_df["trace_id"] == trace_id)]

            # Skip if either model doesn't have data for this trace_id
            if len(data1) == 0 or len(data2) == 0:
                continue

            # Get the binary counts [False_count, True_count]
            counts1 = np.array([data1["Score_False"].iloc[0], data1["Score_True"].iloc[0]])
            counts2 = np.array([data2["Score_False"].iloc[0], data2["Score_True"].iloc[0]])

            # Calculate overlap as minimum count for each outcome
            overlap = np.sum(np.minimum(counts1, counts2))
            n = max(np.sum(counts1), np.sum(counts2))

            total_overlap += overlap
            total_n += n

        # Calculate percentage agreement
        if total_n > 0:
            pct_agreement = total_overlap / total_n
        else:
            pct_agreement = np.nan

        # Fill both symmetric positions
        agreement_matrix.loc[model1, model2] = pct_agreement
        agreement_matrix.loc[model2, model1] = pct_agreement

    agreement_matrix["mean"] = agreement_matrix.mean(axis=1)
    agreement_matrix["std"] = agreement_matrix.drop(columns=["mean"]).std(axis=1)
    # Sort by mean agreement (descending)
    agreement_matrix = agreement_matrix.sort_values(by="mean", ascending=False)
    return agreement_matrix


def display_agreement_matrix(results_df, label: str, do_sns_plot=True):
    """
    Display the agreement matrix for binary scores.
    pass_threshold is ignored since we already have binary data.
    """
    print(f"Agreement Matrix for {label} (Binary Scores)")
    print("*" * 50)

    agreement_matrix = compute_pairwise_agreement_matrix(results_df)

    display(
        agreement_matrix.style.set_caption(f"Binary Pairwise Agreement Matrix with Mean and Std Dev").format(
            na_rep="NaN", formatter={col: "{:.1%}" for col in agreement_matrix.columns}
        )
    )

    if do_sns_plot:
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            agreement_matrix.astype(float),
            annot=True,
            fmt=".1%",
            cmap="viridis",
            square=True,
            cbar_kws={"label": "Agreement (%)"},
        )
        plt.title("Model Pairwise Agreement Matrix (Binary Scores)")
        plt.tight_layout()
        plt.show()


def compute_evaluator_metrics(results_df, label, models_to_use=None, show_individual_run_stats=False):
    print(f"*" * 50)
    print(f"Metrics for {label}")
    print(f"*" * 50)
    model_variance = compute_intra_model_variance(results_df, models_to_use)
    inter_model_variance = compute_inter_model_variance_df(results_df, models_to_use=models_to_use)
    inter_model_variance_stats = show_inter_model_variance_stats(inter_model_variance, show_individual_run_stats)
    return model_variance, inter_model_variance, inter_model_variance_stats


def create_evaluator_summary_metrics(metrics, label):
    """
    Create a summary dataframe with key statistics.

    Args:
        model_variance: DataFrame with intra-model variance statistics
        inter_model_variance: DataFrame with inter-model variance statistics

    Returns:
        DataFrame with summary statistics
    """
    model_variance, inter_model_variance, inter_model_variance_stats = metrics

    # Calculate pct_mode stats
    pct_mode_stats = inter_model_variance["pct_mode"].describe().loc[["min", "max", "std", "mean"]]

    # Calculate inter-model variance stats
    inter_variance_stats = inter_model_variance["variance"].describe().loc[["min", "max", "std", "mean"]]

    # Calculate intra-model variance stats
    intra_variance_stats = model_variance["mean_variance"].describe().loc[["min", "max", "std", "mean"]]

    # Create summary dataframe
    summary_df = pd.DataFrame(
        {
            "intra_variance": intra_variance_stats.values,
            "pct_mode": pct_mode_stats.values,
            "inter_variance": inter_variance_stats.values,
        },
        index=["min", "max", "std", "mean"],
    )
    display(summary_df.style.set_caption(f"Summary Statistics for {label}"))
    return summary_df


def derive_mode_label(score_true, score_false, tie_value=np.nan):
    """Derive a binary label from Score_True/Score_False counts using mode logic."""
    if score_true > score_false:
        return 1
    if score_false > score_true:
        return 0
    return tie_value


def append_mode_label_column(
    df: pd.DataFrame,
    label_col: str = "model_score",
    score_true_col: str = "Score_True",
    score_false_col: str = "Score_False",
    tie_value=np.nan,
) -> pd.DataFrame:
    """Return a copy of df with a mode-based label column appended."""
    required_cols = {score_true_col, score_false_col}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"DataFrame missing required columns: {sorted(missing_cols)}")

    labeled_df = df.copy()
    labeled_df[label_col] = np.select(
        [labeled_df[score_true_col] > labeled_df[score_false_col], labeled_df[score_false_col] > labeled_df[score_true_col]],
        [1, 0],
        default=tie_value,
    )
    return labeled_df


def build_disagreement_inventory(results_df: pd.DataFrame, ground_truth_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build model-vs-ground-truth disagreement tables."""
    required_result_cols = {"trace_id", "model", "Score_False", "Score_True"}
    missing_result_cols = required_result_cols - set(results_df.columns)
    if missing_result_cols:
        raise ValueError(f"results_df missing required columns: {sorted(missing_result_cols)}")

    required_truth_cols = {"trace_id", "ground_truth"}
    missing_truth_cols = required_truth_cols - set(ground_truth_df.columns)
    if missing_truth_cols:
        raise ValueError(f"ground_truth_df missing required columns: {sorted(missing_truth_cols)}")

    comparison_df = results_df.merge(
        ground_truth_df[["trace_id", "ground_truth"]].drop_duplicates(subset=["trace_id"]),
        on="trace_id",
        how="inner",
    ).copy()
    comparison_df = append_mode_label_column(comparison_df, label_col="model_label", tie_value=1)
    comparison_df["model_label"] = comparison_df["model_label"].astype(int)
    comparison_df["is_mismatch"] = comparison_df["model_label"] != comparison_df["ground_truth"]

    trace_disagreement_df = (
        comparison_df.groupby("trace_id")
        .agg(
            ground_truth=("ground_truth", "first"),
            models_evaluated=("model", "nunique"),
            models_predict_true=("model_label", "sum"),
            mismatch_models=("is_mismatch", "sum"),
        )
        .reset_index()
    )
    trace_disagreement_df["models_predict_false"] = (
        trace_disagreement_df["models_evaluated"] - trace_disagreement_df["models_predict_true"]
    )
    true_rate = trace_disagreement_df["models_predict_true"] / trace_disagreement_df["models_evaluated"]
    false_rate = trace_disagreement_df["models_predict_false"] / trace_disagreement_df["models_evaluated"]
    trace_disagreement_df["inter_model_variance"] = true_rate * false_rate

    if "path" in ground_truth_df.columns:
        trace_disagreement_df = trace_disagreement_df.merge(
            ground_truth_df[["trace_id", "path"]].drop_duplicates(subset=["trace_id"]),
            on="trace_id",
            how="left",
        )

    return comparison_df, trace_disagreement_df


def select_disagreement_cases(trace_disagreement_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Select top disagreement cases by mismatch count and inter-model variance."""
    required_cols = {"trace_id", "mismatch_models", "inter_model_variance"}
    missing_cols = required_cols - set(trace_disagreement_df.columns)
    if missing_cols:
        raise ValueError(f"trace_disagreement_df missing required columns: {sorted(missing_cols)}")

    candidates = trace_disagreement_df[trace_disagreement_df["mismatch_models"] > 0].copy()
    candidates = candidates.sort_values(["mismatch_models", "inter_model_variance"], ascending=[False, False])
    return candidates.head(top_n).reset_index(drop=True)


def run_single_case_with_reasoning(
    workflow_trace: Dict,
    model: str,
    eval_key: str = "workflow_planning",
) -> Dict:
    """Run one evaluator call and return score with reasoning metadata."""
    if model not in models_config:
        raise ValueError(f"Unknown model '{model}'. Available models: {sorted(models_config.keys())}")

    evaluator = _WorkflowPlanningEvaluator(**models_config[model])
    result = evaluator(workflow_trace=workflow_trace)

    raw_score = result.get(eval_key, 0)
    score = int(raw_score) if isinstance(raw_score, bool) else (1 if raw_score else 0)
    return {
        "model": model,
        eval_key: score,
        f"{eval_key}_result": result.get(f"{eval_key}_result", ""),
        f"{eval_key}_reason": result.get(f"{eval_key}_reason", ""),
        f"{eval_key}_details": result.get(f"{eval_key}_details", ""),
        f"{eval_key}_prompt_tokens": result.get(f"{eval_key}_prompt_tokens", 0),
        f"{eval_key}_completion_tokens": result.get(f"{eval_key}_completion_tokens", 0),
        f"{eval_key}_total_tokens": result.get(f"{eval_key}_total_tokens", 0),
        f"{eval_key}_finish_reason": result.get(f"{eval_key}_finish_reason", ""),
        f"{eval_key}_sample_input": result.get(f"{eval_key}_sample_input", ""),
        f"{eval_key}_sample_output": result.get(f"{eval_key}_sample_output", ""),
    }


def collect_reasoning_for_cases(
    case_trace_ids: Sequence[str],
    ground_truth_df: pd.DataFrame,
    models_to_run: Sequence[str],
    eval_key: str = "workflow_planning",
) -> pd.DataFrame:
    """Collect per-case reasoning for a list of traces and models."""
    required_cols = {"trace_id", "workflow_trace", "ground_truth"}
    missing_cols = required_cols - set(ground_truth_df.columns)
    if missing_cols:
        raise ValueError(f"ground_truth_df missing required columns: {sorted(missing_cols)}")

    trace_lookup = {
        row["trace_id"]: row for _, row in ground_truth_df[["trace_id", "workflow_trace", "ground_truth"]].iterrows()
    }
    missing_trace_ids = [trace_id for trace_id in case_trace_ids if trace_id not in trace_lookup]
    if missing_trace_ids:
        raise ValueError(f"trace_id(s) not found in ground_truth_df: {missing_trace_ids}")

    records = []
    for trace_id in case_trace_ids:
        trace_row = trace_lookup[trace_id]
        for model in models_to_run:
            reasoning_result = run_single_case_with_reasoning(
                workflow_trace=trace_row["workflow_trace"],
                model=model,
                eval_key=eval_key,
            )
            reasoning_result["trace_id"] = trace_id
            reasoning_result["ground_truth"] = int(trace_row["ground_truth"])
            records.append(reasoning_result)
    return pd.DataFrame(records)


def _normalize_text_for_overlap(value: str) -> str:
    return re.sub(r"\s+", " ", str(value)).strip().lower()


def _extract_text_parts(messages: List[Dict]) -> List[str]:
    texts: List[str] = []
    for msg in messages:
        for part in msg.get("parts", []):
            if part.get("type") == "text" and part.get("content"):
                texts.append(str(part.get("content")))
    return texts


def compute_trace_duplication_metrics(workflow_trace: Dict) -> Dict:
    """Compute duplication metrics for one workflow trace."""
    invocations = workflow_trace.get("invocations", [])
    previous_output_texts = set()
    seen_input_texts = set()

    total_input_texts = 0
    input_texts_matching_previous_output = 0
    repeated_input_texts = 0
    truncated_input_invocations = 0

    for inv in invocations:
        input_payload = inv.get("input_messages", {})
        output_payload = inv.get("output_messages", {})
        if input_payload.get("_truncated"):
            truncated_input_invocations += 1

        input_messages = input_payload.get("value", [])
        output_messages = output_payload.get("value", [])

        input_texts = [_normalize_text_for_overlap(t) for t in _extract_text_parts(input_messages)]
        input_texts = [text for text in input_texts if text]
        output_texts = {_normalize_text_for_overlap(t) for t in _extract_text_parts(output_messages)}
        output_texts = {text for text in output_texts if text}

        total_input_texts += len(input_texts)
        input_texts_matching_previous_output += sum(1 for text in input_texts if text in previous_output_texts)
        repeated_input_texts += sum(1 for text in input_texts if text in seen_input_texts)

        seen_input_texts.update(input_texts)
        previous_output_texts = output_texts

    if total_input_texts == 0:
        previous_overlap_ratio = 0.0
        repeated_input_ratio = 0.0
    else:
        previous_overlap_ratio = input_texts_matching_previous_output / total_input_texts
        repeated_input_ratio = repeated_input_texts / total_input_texts

    return {
        "invocation_count": len(invocations),
        "total_input_texts": total_input_texts,
        "input_texts_matching_previous_output": input_texts_matching_previous_output,
        "input_texts_matching_previous_output_ratio": previous_overlap_ratio,
        "repeated_input_texts": repeated_input_texts,
        "repeated_input_texts_ratio": repeated_input_ratio,
        "truncated_input_invocations": truncated_input_invocations,
    }


def audit_trace_duplication(ground_truth_df: pd.DataFrame) -> pd.DataFrame:
    """Compute duplication metrics for all traces in the ground-truth dataframe."""
    required_cols = {"trace_id", "workflow_trace"}
    missing_cols = required_cols - set(ground_truth_df.columns)
    if missing_cols:
        raise ValueError(f"ground_truth_df missing required columns: {sorted(missing_cols)}")

    rows = []
    for _, row in ground_truth_df.iterrows():
        metrics = compute_trace_duplication_metrics(row["workflow_trace"])
        metrics["trace_id"] = row["trace_id"]
        if "ground_truth" in ground_truth_df.columns:
            metrics["ground_truth"] = int(row["ground_truth"])
        if "path" in ground_truth_df.columns:
            metrics["path"] = row["path"]
        rows.append(metrics)

    metrics_df = pd.DataFrame(rows)
    return metrics_df.sort_values(
        ["input_texts_matching_previous_output_ratio", "repeated_input_texts_ratio"],
        ascending=[False, False],
    ).reset_index(drop=True)


def compare_reasoning_with_and_without_dedup(
    case_trace_ids: Sequence[str],
    ground_truth_df: pd.DataFrame,
    models_to_run: Sequence[str],
    eval_key: str = "workflow_planning",
) -> pd.DataFrame:
    """Collect reasoning for selected traces (formatter is always deduplicated)."""
    baseline_df = collect_reasoning_for_cases(
        case_trace_ids=case_trace_ids,
        ground_truth_df=ground_truth_df,
        models_to_run=models_to_run,
        eval_key=eval_key,
    )
    baseline_df["formatter_mode"] = "deduplicated"
    comparison_df = baseline_df
    comparison_df["matches_ground_truth"] = comparison_df[eval_key] == comparison_df["ground_truth"]
    return comparison_df
