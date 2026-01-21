# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import pathlib
from typing import Callable

import pandas as pd
import pytest
from devtools_testutils import is_live

from openai.types.graders import StringCheckGrader
from azure.core.credentials import TokenCredential
from azure.ai.evaluation import (
    F1ScoreEvaluator,
    evaluate,
    AzureOpenAIGrader,
    AzureOpenAILabelGrader,
    AzureOpenAIStringCheckGrader,
    AzureOpenAITextSimilarityGrader,
    AzureOpenAIScoreModelGrader,
    AzureOpenAIPythonGrader,
)


@pytest.fixture
def data_file() -> pathlib.Path:
    return pathlib.Path(__file__).parent.resolve() / "data" / "evaluate_test_data.jsonl"


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestAoaiEvaluation:
    @pytest.mark.skipif(
        not is_live(), reason="AOAI recordings have bad recording scrubbing"
    )
    def test_evaluate_all_aoai_graders(self, model_config, data_file):
        # create a normal evaluator for comparison
        f1_eval = F1ScoreEvaluator()

        ## ---- Initialize specific graders ----

        # Corresponds to https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_text_similarity_grader.py#L11
        sim_grader = AzureOpenAITextSimilarityGrader(
            model_config=model_config,
            evaluation_metric="fuzzy_match",
            input="{{item.query}}",
            name="similarity",
            pass_threshold=1,
            reference="{{item.query}}",
        )

        # Corresponds to https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_string_check_grader_param.py#L10
        string_grader = AzureOpenAIStringCheckGrader(
            model_config=model_config,
            input="{{item.query}}",
            name="starts with what is",
            operation="like",
            reference="What is",
        )

        # Corresponds to https://github.com/openai/openai-python/blob/ed53107e10e6c86754866b48f8bd862659134ca8/src/openai/types/eval_create_params.py#L132
        label_grader = AzureOpenAILabelGrader(
            model_config=model_config,
            input=[{"content": "{{item.query}}", "role": "user"}],
            labels=["too short", "just right", "too long"],
            passing_labels=["just right"],
            model="gpt-4o",
            name="label",
        )

        # ---- General Grader Initialization ----

        # Define an string check grader config directly using the OAI SDK
        oai_string_check_grader = StringCheckGrader(
            input="{{item.query}}",
            name="contains hello",
            operation="like",
            reference="hello",
            type="string_check",
        )
        # Plug that into the general grader
        general_grader = AzureOpenAIGrader(
            model_config=model_config, grader_config=oai_string_check_grader
        )

        evaluators = {
            "f1_score": f1_eval,
            "similarity": sim_grader,
            "string_check": string_grader,
            "label_model": label_grader,
            "general_grader": general_grader,
        }

        # run the evaluation
        result = evaluate(
            data=data_file, evaluators=evaluators, _use_run_submitter_client=True
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        assert len(row_result_df.keys()) == 23
        assert len(row_result_df["outputs.f1_score.f1_score"]) == 3
        assert len(row_result_df["outputs.similarity.similarity_result"]) == 3
        assert len(row_result_df["outputs.similarity.passed"]) == 3
        assert len(row_result_df["outputs.similarity.score"]) == 3
        assert len(row_result_df["outputs.similarity.sample"]) == 3
        assert len(row_result_df["outputs.string_check.string_check_result"]) == 3
        assert len(row_result_df["outputs.string_check.passed"]) == 3
        assert len(row_result_df["outputs.string_check.score"]) == 3
        assert len(row_result_df["outputs.string_check.sample"]) == 3
        assert len(row_result_df["outputs.label_model.label_model_result"]) == 3
        assert len(row_result_df["outputs.label_model.passed"]) == 3
        assert len(row_result_df["outputs.label_model.score"]) == 3
        assert len(row_result_df["outputs.label_model.sample"]) == 3
        assert len(row_result_df["outputs.general_grader.general_grader_result"]) == 3
        assert len(row_result_df["outputs.general_grader.passed"]) == 3
        assert len(row_result_df["outputs.general_grader.score"]) == 3
        assert len(row_result_df["outputs.general_grader.sample"]) == 3

        assert len(metrics.keys()) == 11
        assert metrics["f1_score.f1_score"] >= 0
        assert metrics["f1_score.f1_score"] >= 0
        assert metrics["f1_score.f1_threshold"] >= 0
        assert metrics["f1_score.binary_aggregate"] >= 0
        assert metrics["f1_score.prompt_tokens"] == 0
        assert metrics["f1_score.completion_tokens"] == 0
        assert metrics["f1_score.total_tokens"] == 0
        assert metrics["f1_score.duration"] >= 0
        assert metrics["similarity.pass_rate"] == 1.0
        assert metrics["string_check.pass_rate"] == 0.3333333333333333
        assert metrics["label_model.pass_rate"] >= 0
        assert metrics["general_grader.pass_rate"] == 0.0

    @pytest.mark.skipif(
        not is_live(), reason="AOAI recordings have bad recording scrubbing"
    )
    def test_evaluate_with_column_mapping_and_target(self, model_config, data_file):
        sim_grader = AzureOpenAITextSimilarityGrader(
            model_config=model_config,
            evaluation_metric="fuzzy_match",
            input="{{item.target_output}}",
            name="similarity",
            pass_threshold=1,
            reference="{{item.query}}",
        )

        string_grader = AzureOpenAIStringCheckGrader(
            model_config=model_config,
            input="{{item.query}}",
            name="starts with what is",
            operation="like",
            reference="What is",
        )

        def target(query: str):
            return {"target_output": query}

        evaluators = {
            "similarity": sim_grader,
            "string_check": string_grader,
        }

        evaluation_config = {
            "similarity": {
                "column_mapping": {
                    "query": "${data.query}",  # test basic mapping
                    "target_output": "${target.target_output}",
                },
            },
            "string_check": {  # test mapping across value names
                "column_mapping": {"query": "${target.target_output}"},
            },
        }

        # run the evaluation
        result = evaluate(
            data=data_file,
            evaluators=evaluators,
            _use_run_submitter_client=True,
            target=target,
            evaluation_config=evaluation_config,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        assert len(row_result_df.keys()) == 13
        assert len(row_result_df["outputs.similarity.similarity_result"]) == 3
        assert len(row_result_df["outputs.similarity.passed"]) == 3
        assert len(row_result_df["outputs.similarity.score"]) == 3
        assert len(row_result_df["outputs.similarity.sample"]) == 3
        assert len(row_result_df["outputs.string_check.string_check_result"]) == 3
        assert len(row_result_df["outputs.string_check.passed"]) == 3
        assert len(row_result_df["outputs.string_check.score"]) == 3
        assert len(row_result_df["outputs.string_check.sample"]) == 3

        assert len(metrics.keys()) == 2
        assert metrics["similarity.pass_rate"] == 1.0
        assert metrics["string_check.pass_rate"] == 0.3333333333333333

    @pytest.mark.skipif(
        not is_live(), reason="AOAI recordings have bad recording scrubbing"
    )
    def test_evaluate_with_large_dataset_pagination(self, model_config):
        """Test AOAI graders with a large dataset that requires pagination"""
        # Create a large dataset that will trigger pagination (>100 rows)
        large_data = []
        for i in range(150):  # Create 150 rows to ensure pagination
            large_data.append(
                {
                    "query": f"What is {i}?",
                    "ground_truth": f"This is item {i}",
                    "answer": f"Item {i}",
                }
            )

        # Create a temporary file with the large dataset
        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for item in large_data:
                f.write(json.dumps(item) + "\n")
            temp_file = f.name

        try:
            # Use a simple string check grader
            string_grader = AzureOpenAIStringCheckGrader(
                model_config=model_config,
                input="{{item.query}}",
                name="contains_what",
                operation="like",
                reference="What",
            )

            evaluators = {
                "string_check": string_grader,
            }

            # Run evaluation with large dataset
            result = evaluate(
                data=temp_file, evaluators=evaluators, _use_run_submitter_client=True
            )

            row_result_df = pd.DataFrame(result["rows"])
            metrics = result["metrics"]

            # Verify all 150 rows were processed
            assert len(row_result_df) == 150
            assert len(row_result_df["outputs.string_check.passed"]) == 150
            assert len(row_result_df["outputs.string_check.score"]) == 150

            # Verify metrics
            assert "string_check.pass_rate" in metrics
            assert metrics["string_check.pass_rate"] == 1.0  # All should pass

        finally:
            # Clean up temp file
            os.unlink(temp_file)

    @pytest.mark.skipif(
        not is_live(), reason="AOAI recordings have bad recording scrubbing"
    )
    def test_evaluate_multiple_graders_with_pagination(self, model_config):
        """Test multiple AOAI graders with pagination to ensure proper result mapping"""
        # Create dataset with 120 rows
        large_data = []
        for i in range(120):
            large_data.append({"query": f"Hello world {i}", "answer": f"Response {i}"})

        import tempfile
        import json

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for item in large_data:
                f.write(json.dumps(item) + "\n")
            temp_file = f.name

        try:
            # Create multiple graders
            string_grader1 = AzureOpenAIStringCheckGrader(
                model_config=model_config,
                input="{{item.query}}",
                name="contains_hello",
                operation="like",
                reference="Hello",
            )

            string_grader2 = AzureOpenAIStringCheckGrader(
                model_config=model_config,
                input="{{item.query}}",
                name="contains_world",
                operation="like",
                reference="world",
            )

            evaluators = {
                "hello_check": string_grader1,
                "world_check": string_grader2,
            }

            # Run evaluation
            result = evaluate(
                data=temp_file, evaluators=evaluators, _use_run_submitter_client=True
            )

            row_result_df = pd.DataFrame(result["rows"])

            # Verify all rows processed for both graders
            assert len(row_result_df) == 120
            assert len(row_result_df["outputs.hello_check.passed"]) == 120
            assert len(row_result_df["outputs.world_check.passed"]) == 120

            # Verify both graders have 100% pass rate
            metrics = result["metrics"]
            assert metrics["hello_check.pass_rate"] == 1.0
            assert metrics["world_check.pass_rate"] == 1.0

        finally:
            os.unlink(temp_file)

    @pytest.mark.skipif(
        not is_live(), reason="AOAI recordings have bad recording scrubbing"
    )
    @pytest.mark.parametrize(
        "grader_factory",
        [
            lambda model_config, credential: AzureOpenAILabelGrader(
                model_config=model_config,
                input=[{"content": "{{item.query}}", "role": "user"}],
                labels=["too short", "just right", "too long"],
                passing_labels=["just right"],
                model="gpt-4.1",
                name="label",
                credential=credential,
            ),
            lambda model_config, credential: AzureOpenAIStringCheckGrader(
                model_config=model_config,
                input="{{item.query}}",
                name="starts with what is",
                operation="like",
                reference="What is",
                credential=credential,
            ),
            lambda model_config, credential: AzureOpenAITextSimilarityGrader(
                model_config=model_config,
                evaluation_metric="fuzzy_match",
                input="{{item.query}}",
                name="similarity",
                pass_threshold=1,
                reference="{{item.query}}",
                credential=credential,
            ),
            lambda model_config, credential: AzureOpenAIScoreModelGrader(
                model_config=model_config,
                name="Conversation Quality Assessment",
                model="gpt-4.1",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert conversation quality evaluator. "
                            "Assess the quality of AI assistant responses based on "
                            "helpfulness, completeness, accuracy, and "
                            "appropriateness. Return a score between 0.0 (very "
                            "poor) and 1.0 (excellent)."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "Evaluate this conversation:\n"
                            "Message: {{ item.query }}\n\n"
                            "Provide a quality score from 0.0 to 1.0."
                        ),
                    },
                ],
                range=[0.0, 1.0],
                sampling_params={"temperature": 0.0},
                credential=credential,
            ),
            lambda model_config, credential: AzureOpenAIPythonGrader(
                model_config=model_config,
                name="custom_accuracy",
                image_tag="2025-05-08",
                pass_threshold=0.8,  # 80% threshold for passing
                source="""def grade(sample: dict, item: dict) -> float:
            \"\"\"
            Custom grading logic that compares model output to expected label.

            Args:
                sample: Dictionary that is typically empty in Azure AI Evaluation
                item: Dictionary containing ALL the data including model output and ground truth

            Returns:
                Float score between 0.0 and 1.0
            \"\"\"
            # Important: In Azure AI Evaluation, all data is in 'item', not 'sample'
            # The 'sample' parameter is typically an empty dictionary

            # Get the model's response/output from item
            output = item.get("response", "") or item.get("output", "") or item.get("output_text", "")
            output = output.lower()

            # Get the expected label/ground truth from item
            label = item.get("ground_truth", "") or item.get("label", "") or item.get("expected", "")
            label = label.lower()

            # Handle empty cases
            if not output or not label:
                return 0.0

            # Exact match gets full score
            if output == label:
                return 1.0

            # Partial match logic (customize as needed)
            if output in label or label in output:
                return 0.5

            return 0.0
        """,
                credential=credential,
            ),
        ],
    )
    def test_evaluate_aoai_grader_with_credential(
        self,
        data_file: pathlib.Path,
        model_config: dict,
        grader_factory: Callable[[dict, TokenCredential], AzureOpenAIGrader],
        azure_cred: TokenCredential,
    ) -> None:
        """Validate that prompty based evaluators support passing custom credentials"""
        config = {**model_config}
        # ensure that we aren't using an api_key for auth
        config.pop("api_key", None)

        grader = grader_factory(config, azure_cred)

        result = evaluate(data=data_file, evaluators={"grader": grader})
