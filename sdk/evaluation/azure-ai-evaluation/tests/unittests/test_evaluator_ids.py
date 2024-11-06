import pytest

from azure.ai.evaluation import (
    CoherenceEvaluator,
    F1ScoreEvaluator,
    FluencyEvaluator,
    F1ScoreEvaluator,
    GroundednessEvaluator,
    RelevanceEvaluator,
    SimilarityEvaluator,
    QAEvaluator,
    ViolenceEvaluator,
    SexualEvaluator,
    HateUnfairnessEvaluator,
    SelfHarmEvaluator,
    ContentSafetyEvaluator,
    IndirectAttackEvaluator,
    BleuScoreEvaluator,
    GleuScoreEvaluator,
    MeteorScoreEvaluator,
    RetrievalEvaluator,
    RougeScoreEvaluator,
    RougeType,
    ProtectedMaterialEvaluator,
    HateUnfairnessMultimodalEvaluator,
    SelfHarmMultimodalEvaluator,
    ViolenceMultimodalEvaluator,
    SexualMultimodalEvaluator,
    IndirectAttackEvaluator,
    GroundednessProEvaluator,
    ProtectedMaterialMultimodalEvaluator,
    RetrievalEvaluator,
)


# Evaluators are dummy ids for testing purposes to be replaced once the actual ids are available
class TestEvaluatorIds:

    def test_content_safety_evaluator_ids(self):
        assert ViolenceEvaluator.id == "violence"
        assert SexualEvaluator.id == "sexual"
        assert SelfHarmEvaluator.id == "self_harm"
        assert HateUnfairnessEvaluator.id == "hate_unfairness"

    def test_content_safety_multimodal_evaluator_ids(self):
        assert ViolenceMultimodalEvaluator.id == "violence_multimodal"
        assert SexualMultimodalEvaluator.id == "sexual_multimodal"
        assert SelfHarmMultimodalEvaluator.id == "self_harm_multimodal"
        assert HateUnfairnessMultimodalEvaluator.id == "hate_unfairness_multimodal"
        assert ProtectedMaterialMultimodalEvaluator.id == "protected_material_multimodal"

    def test_service_based_evaluator_ids(self):
        assert GroundednessProEvaluator.id == "groundedness_pro"
        assert IndirectAttackEvaluator.id == "xpia"
        assert ProtectedMaterialEvaluator.id == "protected_material"

    def test_quality_evaluator_ids(self):
        assert RelevanceEvaluator.id == "relevance"
        assert CoherenceEvaluator.id == "coherence"
        assert FluencyEvaluator.id == "fluency"
        assert SimilarityEvaluator.id == "similarity"
        assert QAEvaluator.id == "qa"
        assert GroundednessEvaluator.id == "groundedness"
        assert RetrievalEvaluator.id == "retrieval"

    def test_mathematical_evaluator_ids(self):
        assert BleuScoreEvaluator.id == "bleu"
        assert GleuScoreEvaluator.id == "gleu_score"
        assert MeteorScoreEvaluator.id == "meteor"
        assert RougeScoreEvaluator.id == "rouge"
        assert F1ScoreEvaluator.id == "f1_score"
