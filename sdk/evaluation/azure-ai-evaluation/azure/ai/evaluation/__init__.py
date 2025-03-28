# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from ._evaluate._evaluate import evaluate
from ._evaluators._bleu import BleuScoreEvaluator
from ._evaluators._coherence import CoherenceEvaluator
from ._evaluators._content_safety import (
    ContentSafetyEvaluator,
    HateUnfairnessEvaluator,
    SelfHarmEvaluator,
    SexualEvaluator,
    ViolenceEvaluator,
)
from ._evaluators._f1_score import F1ScoreEvaluator
from ._evaluators._fluency import FluencyEvaluator
from ._evaluators._gleu import GleuScoreEvaluator
from ._evaluators._groundedness import GroundednessEvaluator
from ._evaluators._service_groundedness import GroundednessProEvaluator
from ._evaluators._intent_resolution import IntentResolutionEvaluator
from ._evaluators._meteor import MeteorScoreEvaluator
from ._evaluators._protected_material import ProtectedMaterialEvaluator
from ._evaluators._qa import QAEvaluator
from ._evaluators._response_completeness import ResponseCompletenessEvaluator
from ._evaluators._task_adherence import TaskAdherenceEvaluator
from ._evaluators._relevance import RelevanceEvaluator
from ._evaluators._retrieval import RetrievalEvaluator
from ._evaluators._rouge import RougeScoreEvaluator, RougeType
from ._evaluators._similarity import SimilarityEvaluator
from ._evaluators._xpia import IndirectAttackEvaluator
from ._evaluators._code_vulnerability import CodeVulnerabilityEvaluator
from ._evaluators._ungrounded_attributes import UngroundedAttributesEvaluator
from ._evaluators._tool_call_accuracy import ToolCallAccuracyEvaluator
from ._model_configurations import (
    AzureAIProject,
    AzureOpenAIModelConfiguration,
    Conversation,
    EvaluationResult,
    EvaluatorConfig,
    Message,
    OpenAIModelConfiguration,
)

_patch_all = []

# The converter from the AI service to the evaluator schema requires a dependency on
# ai.projects, but we also don't want to force users installing ai.evaluations to pull
# in ai.projects. So we only import it if it's available and the user has ai.projects.
try:
    from ._converters._ai_services import AIAgentConverter
    _patch_all.append("AIAgentConverter")
except ImportError:
    print("[INFO] Could not import AIAgentConverter. Please install the dependency with `pip install azure-ai-projects`.")

# RedTeam requires a dependency on pyrit, but python 3.9 is not supported by pyrit.
# So we only import it if it's available and the user has pyrit.
try:
    from ._red_team._red_team import RedTeam
    from ._red_team._attack_strategy import AttackStrategy
    from ._red_team._attack_objective_generator import RiskCategory
    from ._red_team._red_team_result import RedTeamOutput
    _patch_all.extend([
        "RedTeam",
        "RedTeamOutput",
        "AttackStrategy",
        "RiskCategory",
    ])
except ImportError:
    print("[INFO] Could not import RedTeam. Please install the dependency with `pip install azure-ai-evaluation[redteam]`.")


__all__ = [
    "evaluate",
    "CoherenceEvaluator",
    "F1ScoreEvaluator",
    "FluencyEvaluator",
    "GroundednessEvaluator",
    "GroundednessProEvaluator",
    "ResponseCompletenessEvaluator",
    "TaskAdherenceEvaluator",
    "IntentResolutionEvaluator",
    "RelevanceEvaluator",
    "SimilarityEvaluator",
    "QAEvaluator",
    "ViolenceEvaluator",
    "SexualEvaluator",
    "SelfHarmEvaluator",
    "HateUnfairnessEvaluator",
    "ContentSafetyEvaluator",
    "IndirectAttackEvaluator",
    "BleuScoreEvaluator",
    "GleuScoreEvaluator",
    "MeteorScoreEvaluator",
    "RetrievalEvaluator",
    "RougeScoreEvaluator",
    "RougeType",
    "ProtectedMaterialEvaluator",
    "AzureAIProject",
    "AzureOpenAIModelConfiguration",
    "OpenAIModelConfiguration",
    "EvaluatorConfig",
    "Conversation",
    "Message",
    "EvaluationResult",
    "CodeVulnerabilityEvaluator",
    "UngroundedAttributesEvaluator",
    "ToolCallAccuracyEvaluator",
]

__all__.extend([p for p in _patch_all if p not in __all__])