# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import pathlib
import pandas as pd
import pytest


from azure.ai.evaluation import (
    F1ScoreEvaluator,
    GleuScoreEvaluator,
    BleuScoreEvaluator,
    RougeScoreEvaluator,
    MeteorScoreEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
    RelevanceEvaluator,
    SimilarityEvaluator,
    GroundednessEvaluator,
    QAEvaluator,
    ContentSafetyEvaluator,
    GroundednessProEvaluator,
    ProtectedMaterialEvaluator,
    IndirectAttackEvaluator,
    RetrievalEvaluator,
    # ContentSafetyMultimodalEvaluator,
    ProtectedMaterialMultimodalEvaluator,
    RougeType,
    evaluate,
)
from azure.ai.evaluation._evaluators._eci._eci import ECIEvaluator


@pytest.fixture
def data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data.jsonl")


@pytest.fixture
def data_convo_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data_conversation.jsonl")


# I didn't feel like using gross-looking package manipulation commands,
# or importing the lazy_fixture 3p decorator. So we have this monster instead,
# to allow for 'parameterized' fixtures.
@pytest.fixture
def multimodal_input_selector():
    def selector(selection: str):
        if selection == "imageurls":
            data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
            return os.path.join(data_path, "dataset_messages_image_urls.jsonl")
        if selection == "imageurls_with_target":
            data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
            return os.path.join(data_path, "dataset_messages_image_urls_target.jsonl")
        if selection == "b64_images":
            data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
            return os.path.join(data_path, "dataset_messages_b64_images.jsonl")

    return selector


@pytest.mark.usefixtures("recording_injection", "recorded_test")
class TestMassEvaluate:
    """
    Testing file for testing evaluators within the actual `evaluate` wrapper function. Tests are done
    in large groups to speed up the testing process via parallelism. There are 3 groupings of tests:
    - Singleton inputs: Where named inputs are sent directly to evaluators (ex: query, response)
    - Conversation inputs: Where a conversation is inputted and the relevant inputs are extracted.
    - Multi-modal inputs: This one has some parameters for the different types of multi-modal inputs.
    """

    @pytest.mark.parametrize(
        "multi_modal_input_type",
        [
            "imageurls",
            "imageurls_with_target",
            "b64_images",
        ],
    )
    # @pytest.mark.skipif(True, reason="test see if this fixes CI cleanup bug")
    def test_evaluate_multimodal(self, multi_modal_input_type, multimodal_input_selector, azure_cred, project_scope):
        # Content safety is removed due to being unstable in playback mode
        evaluators = {
            # "content_safety" : ContentSafetyMultimodalEvaluator(credential=azure_cred, azure_ai_project=project_scope),
            "protected_material": ProtectedMaterialMultimodalEvaluator(
                credential=azure_cred, azure_ai_project=project_scope
            ),
        }

        evaluator_config = None  # use default normally
        target = None
        if multi_modal_input_type == "imageurls_with_target":
            evaluator_config = {
                # "content_safety": {"conversation": "${target.conversation}"},
                "protected_material": {"conversation": "${target.conversation}"},
            }
            from .target_fn import target_multimodal_fn1

            target = target_multimodal_fn1

        # run the evaluation
        result = evaluate(
            data=multimodal_input_selector(multi_modal_input_type),
            evaluators=evaluators,
            evaluator_config=evaluator_config,
            target=target,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        # validate the results
        assert result is not None
        assert result["rows"] is not None

        assert "outputs.protected_material.artwork_label" in row_result_df.columns.to_list()
        assert "outputs.protected_material.artwork_reason" in row_result_df.columns.to_list()
        assert "outputs.protected_material.fictional_characters_label" in row_result_df.columns.to_list()
        assert "outputs.protected_material.fictional_characters_reason" in row_result_df.columns.to_list()
        assert "outputs.protected_material.logos_and_brands_label" in row_result_df.columns.to_list()
        assert "outputs.protected_material.logos_and_brands_reason" in row_result_df.columns.to_list()

        # assert "outputs.content_safety.sexual" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.violence" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.self_harm" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.hate_unfairness" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.sexual_score" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.violence_score" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.self_harm_score" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.hate_unfairness_score" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.sexual_reason" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.violence_reason" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.self_harm_reason" in row_result_df.columns.to_list()
        # assert "outputs.content_safety.hate_unfairness_reason" in row_result_df.columns.to_list()

        # assert "content_safety.sexual_defect_rate" in metrics.keys()
        # assert "content_safety.violence_defect_rate" in metrics.keys()
        # assert "content_safety.self_harm_defect_rate" in metrics.keys()
        # assert "content_safety.hate_unfairness_defect_rate" in metrics.keys()
        assert "protected_material.fictional_characters_label" in metrics.keys()
        assert "protected_material.logos_and_brands_label" in metrics.keys()
        assert "protected_material.artwork_label" in metrics.keys()

        # assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        # assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        # assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        # assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1
        assert 0 <= metrics.get("protected_material.fictional_characters_label") <= 1
        assert 0 <= metrics.get("protected_material.logos_and_brands_label") <= 1
        assert 0 <= metrics.get("protected_material.artwork_label") <= 1
