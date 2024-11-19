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
@pytest.mark.localtest
class TestMassEvaluate:
    """
    Testing file for testing evaluators within the actual `evaluate` wrapper function. Tests are done
    in large groups to speed up the testing process via parallelism. There are 3 groupings of tests:
    - Singleton inputs: Where named inputs are sent directly to evaluators (ex: query, response)
    - Conversation inputs: Where a conversation is inputted and the relevant inputs are extracted.
    - Multi-modal inputs: This one has some parameters for the different types of multi-modal inputs.
    """

    # @pytest.mark.skipif(True, reason="test see if this fixes CI cleanup bug")
    def test_evaluate_conversation(self, model_config, data_convo_file, azure_cred, project_scope):
        evaluators = {
            "grounded": GroundednessEvaluator(model_config),
            "coherence": CoherenceEvaluator(model_config),
            "fluency": FluencyEvaluator(model_config),
            "relevance": RelevanceEvaluator(model_config),
            "grounded_pro": GroundednessProEvaluator(azure_cred, project_scope),
            "protected_material": ProtectedMaterialEvaluator(azure_cred, project_scope),
            "indirect_attack": IndirectAttackEvaluator(azure_cred, project_scope),
            "eci": ECIEvaluator(azure_cred, project_scope),
            "content_safety": ContentSafetyEvaluator(azure_cred, project_scope),
            "retrieval": RetrievalEvaluator(model_config),
        }

        # run the evaluation
        result = evaluate(
            data=data_convo_file,
            evaluators=evaluators,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]

        assert len(row_result_df.keys()) == 32
        assert len(row_result_df["inputs.conversation"]) == 2
        assert len(row_result_df["outputs.grounded.groundedness"]) == 2
        assert len(row_result_df["outputs.grounded.gpt_groundedness"]) == 2
        assert len(row_result_df["outputs.grounded.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.coherence.coherence"]) == 2
        assert len(row_result_df["outputs.coherence.gpt_coherence"]) == 2
        assert len(row_result_df["outputs.coherence.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.fluency.fluency"]) == 2
        assert len(row_result_df["outputs.fluency.gpt_fluency"]) == 2
        assert len(row_result_df["outputs.fluency.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.relevance.relevance"]) == 2
        assert len(row_result_df["outputs.relevance.gpt_relevance"]) == 2
        assert len(row_result_df["outputs.relevance.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.grounded_pro.groundedness_pro_label"]) == 2
        assert len(row_result_df["outputs.grounded_pro.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.protected_material.protected_material_label"]) == 2
        assert len(row_result_df["outputs.protected_material.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.indirect_attack.xpia_label"]) == 2
        assert len(row_result_df["outputs.indirect_attack.xpia_manipulated_content"]) == 2
        assert len(row_result_df["outputs.indirect_attack.xpia_intrusion"]) == 2
        assert len(row_result_df["outputs.indirect_attack.xpia_information_gathering"]) == 2
        assert len(row_result_df["outputs.indirect_attack.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.eci.eci_label"]) == 2
        assert len(row_result_df["outputs.eci.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.content_safety.sexual_score"]) == 2
        assert len(row_result_df["outputs.content_safety.violence_score"]) == 2
        assert len(row_result_df["outputs.content_safety.self_harm_score"]) == 2
        assert len(row_result_df["outputs.content_safety.hate_unfairness_score"]) == 2
        assert len(row_result_df["outputs.content_safety.evaluation_per_turn"]) == 2
        assert len(row_result_df["outputs.retrieval.retrieval"]) == 2
        assert len(row_result_df["outputs.retrieval.gpt_retrieval"]) == 2
        assert len(row_result_df["outputs.retrieval.evaluation_per_turn"]) == 2

        assert len(metrics.keys()) == 21
        assert metrics["coherence.coherence"] >= 0
        assert metrics["coherence.gpt_coherence"] >= 0
        assert metrics["fluency.fluency"] >= 0
        assert metrics["fluency.gpt_fluency"] >= 0
        assert metrics["relevance.relevance"] >= 0
        assert metrics["relevance.gpt_relevance"] >= 0
        assert metrics["grounded.gpt_groundedness"] >= 0
        assert metrics["grounded.groundedness"] >= 0
        assert metrics["retrieval.retrieval"] >= 0
        assert metrics["retrieval.gpt_retrieval"] >= 0
        assert metrics["indirect_attack.xpia_manipulated_content"] >= 0
        assert metrics["indirect_attack.xpia_intrusion"] >= 0
        assert metrics["indirect_attack.xpia_information_gathering"] >= 0
        assert metrics["content_safety.sexual_defect_rate"] >= 0
        assert metrics["content_safety.violence_defect_rate"] >= 0
        assert metrics["content_safety.hate_unfairness_defect_rate"] >= 0
        assert metrics["content_safety.self_harm_defect_rate"] >= 0
        assert metrics["grounded_pro.groundedness_pro_passing_rate"] >= 0
        assert metrics["protected_material.protected_material_defect_rate"] >= 0
        assert metrics["indirect_attack.xpia_defect_rate"] >= 0
        assert metrics["eci.eci_defect_rate"] >= 0
