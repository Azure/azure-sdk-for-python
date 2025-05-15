# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Note: This was removed from the normal constants file due to circular import issues.

# In the future, it would be nice to instead rely on the id value
# of each eval class, but I wouldn't like to rely on those before
# we simplify them into version-less, static values, instead of the
# problematic registry references they currently are.

# Import all evals
from azure.ai.evaluation._evaluators._eci._eci import ECIEvaluator
from azure.ai.evaluation import (
    BleuScoreEvaluator,
    CodeVulnerabilityEvaluator,
    CoherenceEvaluator,
    ContentSafetyEvaluator,
    DocumentRetrievalEvaluator,
    F1ScoreEvaluator,
    FluencyEvaluator,
    GleuScoreEvaluator,
    GroundednessEvaluator,
    GroundednessProEvaluator,
    HateUnfairnessEvaluator,
    IndirectAttackEvaluator,
    IntentResolutionEvaluator,
    MeteorScoreEvaluator,
    ProtectedMaterialEvaluator,
    QAEvaluator,
    RelevanceEvaluator,
    ResponseCompletenessEvaluator,
    RetrievalEvaluator,
    RougeScoreEvaluator,
    SelfHarmEvaluator,
    SexualEvaluator,
    SimilarityEvaluator,
    TaskAdherenceEvaluator,
    ToolCallAccuracyEvaluator,
    UngroundedAttributesEvaluator,
    ViolenceEvaluator
)

EVAL_CLASS_MAP = {
    BleuScoreEvaluator: "bleu_score",
    CodeVulnerabilityEvaluator: "code_vulnerability",
    CoherenceEvaluator: "coherence",
    ContentSafetyEvaluator: "content_safety",
    DocumentRetrievalEvaluator: "document_retrieval",
    ECIEvaluator: "eci",
    F1ScoreEvaluator: "f1_score",
    FluencyEvaluator: "fluency",
    GleuScoreEvaluator: "gleu_score",
    GroundednessEvaluator: "groundedness",
    GroundednessProEvaluator: "groundedness_pro",
    HateUnfairnessEvaluator: "hate_unfairness",
    IndirectAttackEvaluator: "indirect_attack",
    IntentResolutionEvaluator: "intent_resolution",
    MeteorScoreEvaluator: "meteor_score",
    ProtectedMaterialEvaluator: "protected_material",
    QAEvaluator: "qa",
    RelevanceEvaluator: "relevance",
    ResponseCompletenessEvaluator: "response_completeness",
    RetrievalEvaluator: "retrieval",
    RougeScoreEvaluator: "rouge_score",
    SelfHarmEvaluator: "self_harm",
    SexualEvaluator: "sexual",
    SimilarityEvaluator: "similarity",
    TaskAdherenceEvaluator: "task_adherence",
    ToolCallAccuracyEvaluator: "tool_call_accuracy",
    UngroundedAttributesEvaluator: "ungrounded_attributes",
    ViolenceEvaluator: "violence",
}