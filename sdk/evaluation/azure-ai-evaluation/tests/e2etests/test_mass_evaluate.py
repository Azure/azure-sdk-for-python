# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import pathlib
import pandas as pd
import pytest
from regex import F
from devtools_testutils import is_live


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
    SexualEvaluator,
    CodeVulnerabilityEvaluator,
    UngroundedAttributesEvaluator,
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


@pytest.fixture
def code_based_data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data_with_code.jsonl")


@pytest.fixture
def chat_based_data_file():
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, "evaluate_test_data_with_chat.jsonl")


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

    @pytest.mark.skipif(not is_live(), reason="Skip in playback due to inconsistency in evaluation results.")
    def test_evaluate_singleton_inputs(self, model_config, azure_cred, project_scope, data_file):
        # qa fails in playback but ONLY when using the pf proxy for some reason, and
        # using it without pf proxy causes CI to hang and timeout after 3 hours.
        evaluators = {
            "f1_score": F1ScoreEvaluator(),
            "gleu": GleuScoreEvaluator(),
            "bleu": BleuScoreEvaluator(),
            "rouge": RougeScoreEvaluator(RougeType.ROUGE_L),
            "meteor": MeteorScoreEvaluator(),
            "grounded": GroundednessEvaluator(model_config),
            "coherence": CoherenceEvaluator(model_config),
            "fluency": FluencyEvaluator(model_config),
            "relevance": RelevanceEvaluator(model_config),
            "similarity": SimilarityEvaluator(model_config),
            "qa": QAEvaluator(model_config),
            "grounded_pro": GroundednessProEvaluator(azure_cred, project_scope),
            "protected_material": ProtectedMaterialEvaluator(azure_cred, project_scope),
            "indirect_attack": IndirectAttackEvaluator(azure_cred, project_scope),
            "eci": ECIEvaluator(azure_cred, project_scope),
            "content_safety": ContentSafetyEvaluator(azure_cred, project_scope),
        }

        # run the evaluation
        result = evaluate(
            data=data_file,
            evaluators=evaluators,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        assert len(row_result_df.keys()) == 110
        assert len(row_result_df["inputs.query"]) == 3
        assert len(row_result_df["inputs.context"]) == 3
        assert len(row_result_df["inputs.response"]) == 3
        assert len(row_result_df["inputs.ground_truth"]) == 3
        assert len(row_result_df["outputs.f1_score.f1_score"]) == 3
        assert len(row_result_df["outputs.gleu.gleu_score"]) == 3
        assert len(row_result_df["outputs.bleu.bleu_score"]) == 3
        assert len(row_result_df["outputs.rouge.rouge_precision"]) == 3
        assert len(row_result_df["outputs.rouge.rouge_recall"]) == 3
        assert len(row_result_df["outputs.rouge.rouge_f1_score"]) == 3
        assert len(row_result_df["outputs.meteor.meteor_score"]) == 3
        assert len(row_result_df["outputs.grounded.groundedness"]) == 3
        assert len(row_result_df["outputs.grounded.gpt_groundedness"]) == 3
        assert len(row_result_df["outputs.grounded.groundedness_reason"]) == 3
        assert len(row_result_df["outputs.coherence.coherence"]) == 3
        assert len(row_result_df["outputs.coherence.gpt_coherence"]) == 3
        assert len(row_result_df["outputs.coherence.coherence_reason"]) == 3
        assert len(row_result_df["outputs.fluency.fluency"]) == 3
        assert len(row_result_df["outputs.fluency.gpt_fluency"]) == 3
        assert len(row_result_df["outputs.fluency.fluency_reason"]) == 3
        assert len(row_result_df["outputs.relevance.relevance"]) == 3
        assert len(row_result_df["outputs.relevance.gpt_relevance"]) == 3
        assert len(row_result_df["outputs.relevance.relevance_reason"]) == 3
        assert len(row_result_df["outputs.similarity.similarity"]) == 3
        assert len(row_result_df["outputs.similarity.gpt_similarity"]) == 3
        assert len(row_result_df["outputs.grounded_pro.groundedness_pro_label"]) == 3
        assert len(row_result_df["outputs.grounded_pro.groundedness_pro_reason"]) == 3
        assert len(row_result_df["outputs.protected_material.protected_material_label"]) == 3
        assert len(row_result_df["outputs.protected_material.protected_material_reason"]) == 3
        assert len(row_result_df["outputs.indirect_attack.xpia_label"]) == 3
        assert len(row_result_df["outputs.indirect_attack.xpia_reason"]) == 3
        assert len(row_result_df["outputs.indirect_attack.xpia_manipulated_content"]) == 3
        assert len(row_result_df["outputs.indirect_attack.xpia_intrusion"]) == 3
        assert len(row_result_df["outputs.indirect_attack.xpia_information_gathering"]) == 3
        assert len(row_result_df["outputs.eci.eci_label"]) == 3
        assert len(row_result_df["outputs.eci.eci_reason"]) == 3
        assert len(row_result_df["outputs.content_safety.sexual"]) == 3
        assert len(row_result_df["outputs.content_safety.sexual_score"]) == 3
        assert len(row_result_df["outputs.content_safety.sexual_reason"]) == 3
        assert len(row_result_df["outputs.content_safety.self_harm"]) == 3
        assert len(row_result_df["outputs.content_safety.self_harm_score"]) == 3
        assert len(row_result_df["outputs.content_safety.self_harm_reason"]) == 3
        assert len(row_result_df["outputs.content_safety.hate_unfairness"]) == 3
        assert len(row_result_df["outputs.content_safety.hate_unfairness_score"]) == 3
        assert len(row_result_df["outputs.content_safety.hate_unfairness_reason"]) == 3
        assert len(row_result_df["outputs.content_safety.violence"]) == 3
        assert len(row_result_df["outputs.content_safety.violence_score"]) == 3
        assert len(row_result_df["outputs.content_safety.violence_reason"]) == 3
        assert len(row_result_df["outputs.qa.f1_score"]) == 3
        assert len(row_result_df["outputs.qa.groundedness"]) == 3
        assert len(row_result_df["outputs.qa.gpt_groundedness"]) == 3
        assert len(row_result_df["outputs.qa.groundedness_reason"]) == 3
        assert len(row_result_df["outputs.qa.coherence"]) == 3
        assert len(row_result_df["outputs.qa.gpt_coherence"]) == 3
        assert len(row_result_df["outputs.qa.coherence_reason"]) == 3
        assert len(row_result_df["outputs.qa.fluency"]) == 3
        assert len(row_result_df["outputs.qa.gpt_fluency"]) == 3
        assert len(row_result_df["outputs.qa.fluency_reason"]) == 3
        assert len(row_result_df["outputs.qa.relevance"]) == 3
        assert len(row_result_df["outputs.qa.gpt_relevance"]) == 3
        assert len(row_result_df["outputs.qa.relevance_reason"]) == 3
        assert len(row_result_df["outputs.qa.similarity"]) == 3
        assert len(row_result_df["outputs.qa.gpt_similarity"]) == 3

        assert len(metrics.keys()) == 62
        assert metrics["f1_score.f1_score"] >= 0
        assert metrics["gleu.gleu_score"] >= 0
        assert metrics["bleu.bleu_score"] >= 0
        assert metrics["rouge.rouge_precision"] >= 0
        assert metrics["rouge.rouge_recall"] >= 0
        assert metrics["rouge.rouge_f1_score"] >= 0
        assert metrics["meteor.meteor_score"] >= 0
        assert metrics["grounded.groundedness"] >= 0
        assert metrics["grounded.gpt_groundedness"] >= 0
        assert metrics["coherence.coherence"] >= 0
        assert metrics["coherence.gpt_coherence"] >= 0
        assert metrics["fluency.fluency"] >= 0
        assert metrics["fluency.gpt_fluency"] >= 0
        assert metrics["relevance.relevance"] >= 0
        assert metrics["relevance.gpt_relevance"] >= 0
        assert metrics["similarity.similarity"] >= 0
        assert metrics["similarity.gpt_similarity"] >= 0
        assert metrics["indirect_attack.xpia_manipulated_content"] >= 0
        assert metrics["indirect_attack.xpia_intrusion"] >= 0
        assert metrics["indirect_attack.xpia_information_gathering"] >= 0
        assert metrics["content_safety.sexual_defect_rate"] >= 0
        assert metrics["content_safety.self_harm_defect_rate"] >= 0
        assert metrics["content_safety.hate_unfairness_defect_rate"] >= 0
        assert metrics["content_safety.violence_defect_rate"] >= 0
        assert metrics["grounded_pro.groundedness_pro_passing_rate"] >= 0
        assert metrics["protected_material.protected_material_defect_rate"] >= 0
        assert metrics["indirect_attack.xpia_defect_rate"] >= 0
        assert metrics["eci.eci_defect_rate"] >= 0
        assert metrics["qa.f1_score"] >= 0
        assert metrics["qa.groundedness"] >= 0
        assert metrics["qa.gpt_groundedness"] >= 0
        assert metrics["qa.coherence"] >= 0
        assert metrics["qa.gpt_coherence"] >= 0
        assert metrics["qa.fluency"] >= 0
        assert metrics["qa.gpt_fluency"] >= 0
        assert metrics["qa.relevance"] >= 0
        assert metrics["qa.gpt_relevance"] >= 0
        assert metrics["qa.similarity"] >= 0
        assert metrics["qa.gpt_similarity"] >= 0

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
        assert len(row_result_df.keys()) >= 43
        assert len(row_result_df["inputs.conversation"]) >= 2
        assert len(row_result_df["outputs.grounded.groundedness"]) >= 2
        assert len(row_result_df["outputs.grounded.gpt_groundedness"]) >= 2
        assert len(row_result_df["outputs.grounded.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.coherence.coherence"]) >= 2
        assert len(row_result_df["outputs.coherence.gpt_coherence"]) >= 2
        assert len(row_result_df["outputs.coherence.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.fluency.fluency"]) >= 2
        assert len(row_result_df["outputs.fluency.gpt_fluency"]) >= 2
        assert len(row_result_df["outputs.fluency.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.relevance.relevance"]) >= 2
        assert len(row_result_df["outputs.relevance.gpt_relevance"]) >= 2
        assert len(row_result_df["outputs.relevance.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.grounded_pro.groundedness_pro_label"]) >= 2
        assert len(row_result_df["outputs.grounded_pro.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.protected_material.protected_material_label"]) >= 2
        assert len(row_result_df["outputs.protected_material.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.indirect_attack.xpia_label"]) >= 2
        assert len(row_result_df["outputs.indirect_attack.xpia_manipulated_content"]) >= 2
        assert len(row_result_df["outputs.indirect_attack.xpia_intrusion"]) >= 2
        assert len(row_result_df["outputs.indirect_attack.xpia_information_gathering"]) >= 2
        assert len(row_result_df["outputs.indirect_attack.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.eci.eci_label"]) >= 2
        assert len(row_result_df["outputs.eci.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.content_safety.sexual_score"]) >= 2
        assert len(row_result_df["outputs.content_safety.violence_score"]) >= 2
        assert len(row_result_df["outputs.content_safety.self_harm_score"]) >= 2
        assert len(row_result_df["outputs.content_safety.hate_unfairness_score"]) >= 2
        assert len(row_result_df["outputs.content_safety.evaluation_per_turn"]) >= 2
        assert len(row_result_df["outputs.retrieval.retrieval"]) >= 2
        assert len(row_result_df["outputs.retrieval.gpt_retrieval"]) >= 2
        assert len(row_result_df["outputs.retrieval.evaluation_per_turn"]) >= 2

        assert len(metrics.keys()) == 32
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

    @pytest.mark.parametrize(
        "multi_modal_input_type",
        [
            "imageurls",
            "imageurls_with_target",
            "b64_images",
        ],
    )
    def test_evaluate_multimodal(
        self,
        multi_modal_input_type,
        multimodal_input_selector,
        azure_cred,
        project_scope,
        run_from_temp_dir,
    ):
        evaluators = {
            "content_safety": ContentSafetyEvaluator(credential=azure_cred, azure_ai_project=project_scope),
            "protected_material": ProtectedMaterialEvaluator(credential=azure_cred, azure_ai_project=project_scope),
            "sexual": SexualEvaluator(credential=azure_cred, azure_ai_project=project_scope),
        }

        evaluator_config = None  # use default column mapping normally
        target = None
        # imageurls_with_target has special column mapping to convert target function into inputted conversation.
        if multi_modal_input_type == "imageurls_with_target":
            evaluator_config = {}
            for key in evaluators.keys():
                evaluator_config[key] = {"conversation": "${target.conversation}"}
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

        if multi_modal_input_type == "imageurls_with_target":
            # imageurls_with_target has 1 extra column: outputs.conversation due to the target mapping
            assert len(row_result_df.keys()) >= 33
        else:
            assert len(row_result_df.keys()) == 32
        known_keys = [
            "outputs.content_safety.hate_unfairness",
            "outputs.content_safety.hate_unfairness_score",
            "outputs.content_safety.hate_unfairness_reason",
            "outputs.content_safety.hate_unfairness_result",
            "outputs.content_safety.self_harm",
            "outputs.content_safety.self_harm_score",
            "outputs.content_safety.self_harm_reason",
            "outputs.content_safety.self_harm_result",
            "outputs.content_safety.sexual",
            "outputs.content_safety.sexual_score",
            "outputs.content_safety.sexual_reason",
            "outputs.content_safety.sexual_result",
            "outputs.content_safety.violence",
            "outputs.content_safety.violence_score",
            "outputs.content_safety.violence_reason",
            "outputs.content_safety.violence_result",
            "outputs.protected_material.fictional_characters_label",
            "outputs.protected_material.fictional_characters_reason",
            "outputs.protected_material.logos_and_brands_label",
            "outputs.protected_material.logos_and_brands_reason",
            "outputs.protected_material.artwork_label",
            "outputs.protected_material.artwork_reason",
            "outputs.sexual.sexual",
            "outputs.sexual.sexual_score",
            "outputs.sexual.sexual_reason",
            "outputs.sexual.sexual_result",
        ]
        for key in known_keys:
            assert key in row_result_df.keys()

        assert len(metrics) == 15
        assert 0 <= metrics.get("content_safety.sexual_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.violence_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.self_harm_defect_rate") <= 1
        assert 0 <= metrics.get("content_safety.hate_unfairness_defect_rate") <= 1
        assert 0 <= metrics.get("protected_material.fictional_characters_defect_rate") <= 1
        assert 0 <= metrics.get("protected_material.logos_and_brands_defect_rate") <= 1
        assert 0 <= metrics.get("protected_material.artwork_defect_rate") <= 1
        assert 0 <= metrics.get("sexual.sexual_defect_rate") <= 1

    def test_evaluate_code_based_inputs(self, azure_cred, project_scope, code_based_data_file):
        evaluators = {
            "code_vulnerability": CodeVulnerabilityEvaluator(azure_cred, project_scope),
        }

        # run the evaluation
        result = evaluate(
            data=code_based_data_file,
            evaluators=evaluators,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        assert len(row_result_df.keys()) == 5
        assert len(row_result_df["inputs.query"]) == 2
        assert len(row_result_df["inputs.response"]) == 2
        assert len(row_result_df["outputs.code_vulnerability.code_vulnerability_label"]) == 2
        assert len(row_result_df["outputs.code_vulnerability.code_vulnerability_reason"]) == 2
        assert len(row_result_df["outputs.code_vulnerability.code_vulnerability_details"]) == 2

        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["code_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["code_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["full_ssrf"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["full_ssrf"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["path_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["path_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["hardcoded_credentials"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["hardcoded_credentials"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["stack_trace_exposure"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["stack_trace_exposure"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "incomplete_url_substring_sanitization"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "incomplete_url_substring_sanitization"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["flask_debug"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["flask_debug"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "potentially_weak_cryptographic_algorithm"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "potentially_weak_cryptographic_algorithm"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "clear_text_logging_sensitive_data"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "clear_text_logging_sensitive_data"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "incomplete_hostname_regexp"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "incomplete_hostname_regexp"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["sql_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["sql_injection"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["insecure_randomness"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["insecure_randomness"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "bind_socket_all_network_interfaces"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "bind_socket_all_network_interfaces"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "client_side_unvalidated_url_redirection"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "client_side_unvalidated_url_redirection"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["likely_bugs"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["likely_bugs"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "server_side_unvalidated_url_redirection"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "server_side_unvalidated_url_redirection"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0][
            "clear_text_storage_sensitive_data"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1][
            "clear_text_storage_sensitive_data"
        ] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["tarslip"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["tarslip"] in [True, False]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][0]["reflected_xss"] in [
            True,
            False,
        ]
        assert row_result_df["outputs.code_vulnerability.code_vulnerability_details"][1]["reflected_xss"] in [
            True,
            False,
        ]

        assert len(metrics.keys()) == 20
        assert metrics["code_vulnerability.code_vulnerability_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.code_injection_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.full_ssrf_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.path_injection_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.hardcoded_credentials_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.stack_trace_exposure_defect_rate"] >= 0
        assert (
            metrics["code_vulnerability.code_vulnerability_details.incomplete_url_substring_sanitization_defect_rate"]
            >= 0
        )
        assert metrics["code_vulnerability.code_vulnerability_details.flask_debug_defect_rate"] >= 0
        assert (
            metrics[
                "code_vulnerability.code_vulnerability_details.potentially_weak_cryptographic_algorithm_defect_rate"
            ]
            >= 0
        )
        assert (
            metrics["code_vulnerability.code_vulnerability_details.clear_text_logging_sensitive_data_defect_rate"] >= 0
        )
        assert metrics["code_vulnerability.code_vulnerability_details.incomplete_hostname_regexp_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.sql_injection_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.insecure_randomness_defect_rate"] >= 0
        assert (
            metrics["code_vulnerability.code_vulnerability_details.bind_socket_all_network_interfaces_defect_rate"] >= 0
        )
        assert (
            metrics["code_vulnerability.code_vulnerability_details.client_side_unvalidated_url_redirection_defect_rate"]
            >= 0
        )
        assert metrics["code_vulnerability.code_vulnerability_details.likely_bugs_defect_rate"] >= 0
        assert (
            metrics["code_vulnerability.code_vulnerability_details.server_side_unvalidated_url_redirection_defect_rate"]
            >= 0
        )
        assert (
            metrics["code_vulnerability.code_vulnerability_details.clear_text_storage_sensitive_data_defect_rate"] >= 0
        )
        assert metrics["code_vulnerability.code_vulnerability_details.tarslip_defect_rate"] >= 0
        assert metrics["code_vulnerability.code_vulnerability_details.reflected_xss_defect_rate"] >= 0

    def test_evaluate_chat_inputs(self, azure_cred, project_scope, chat_based_data_file):
        evaluators = {
            "ungrounded_attributes": UngroundedAttributesEvaluator(azure_cred, project_scope),
        }

        # run the evaluation
        result = evaluate(
            data=chat_based_data_file,
            evaluators=evaluators,
        )

        row_result_df = pd.DataFrame(result["rows"])
        metrics = result["metrics"]
        # todo: change this once binary results are added to the evaluator
        assert len(row_result_df.keys()) == 6
        assert len(row_result_df["inputs.query"]) == 2
        assert len(row_result_df["inputs.response"]) == 2
        assert len(row_result_df["inputs.context"]) == 2
        assert len(row_result_df["outputs.ungrounded_attributes.ungrounded_attributes_label"]) == 2
        assert len(row_result_df["outputs.ungrounded_attributes.ungrounded_attributes_reason"]) == 2
        assert len(row_result_df["outputs.ungrounded_attributes.ungrounded_attributes_details"]) == 2

        assert len(metrics.keys()) == 4
        assert metrics["ungrounded_attributes.ungrounded_attributes_defect_rate"] >= 0
        assert metrics["ungrounded_attributes.ungrounded_attributes_details.emotional_state_defect_rate"] >= 0
        assert metrics["ungrounded_attributes.ungrounded_attributes_details.protected_class_defect_rate"] >= 0
        assert metrics["ungrounded_attributes.ungrounded_attributes_details.groundedness_defect_rate"] >= 0
