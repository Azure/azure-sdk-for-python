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
from ._evaluators._document_retrieval import DocumentRetrievalEvaluator
from ._evaluators._tool_output_utilization import _ToolOutputUtilizationEvaluator
from ._model_configurations import (
    AzureAIProject,
    AzureOpenAIModelConfiguration,
    Conversation,
    EvaluationResult,
    EvaluatorConfig,
    Message,
    OpenAIModelConfiguration,
)
from ._aoai.aoai_grader import AzureOpenAIGrader
from ._aoai.label_grader import AzureOpenAILabelGrader
from ._aoai.string_check_grader import AzureOpenAIStringCheckGrader
from ._aoai.text_similarity_grader import AzureOpenAITextSimilarityGrader
from ._aoai.score_model_grader import AzureOpenAIScoreModelGrader
from ._aoai.python_grader import AzureOpenAIPythonGrader


_patch_all = []

# The converter from the AI service to the evaluator schema requires a dependency on
# ai.projects, but we also don't want to force users installing ai.evaluations to pull
# in ai.projects. So we only import it if it's available and the user has ai.projects.
# We use lazy loading to avoid printing messages during import unless the classes are actually used.
_lazy_imports = {}


def _create_lazy_import(class_name, module_path, dependency_name):
    """Create a lazy import function for optional dependencies.

    Args:
        class_name: Name of the class to import
        module_path: Module path to import from
        dependency_name: Name of the dependency package for error message

    Returns:
        A function that performs the lazy import when called
    """

    def lazy_import():
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            _patch_all.append(class_name)
            return cls
        except ImportError:
            raise ImportError(
                f"Could not import {class_name}. Please install the dependency with `pip install {dependency_name}`."
            )

    return lazy_import


_lazy_imports["AIAgentConverter"] = _create_lazy_import(
    "AIAgentConverter",
    "azure.ai.evaluation._converters._ai_services",
    "azure-ai-projects",
)
_lazy_imports["SKAgentConverter"] = _create_lazy_import(
    "SKAgentConverter",
    "azure.ai.evaluation._converters._sk_services",
    "semantic-kernel",
)

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
    "_ToolOutputUtilizationEvaluator",
    "AzureOpenAIGrader",
    "AzureOpenAILabelGrader",
    "AzureOpenAIStringCheckGrader",
    "AzureOpenAITextSimilarityGrader",
    "AzureOpenAIScoreModelGrader",
    "AzureOpenAIPythonGrader",
]

__all__.extend([p for p in _patch_all if p not in __all__])


def __getattr__(name):
    """Handle lazy imports for optional dependencies."""
    if name in _lazy_imports:
        return _lazy_imports[name]()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
