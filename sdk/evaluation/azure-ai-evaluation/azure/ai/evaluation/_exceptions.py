# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This includes enums and classes for exceptions for use in azure-ai-evaluation."""

from enum import Enum
from typing import Optional

from azure.core.exceptions import AzureError


class ErrorCategory(Enum):
    """Error category to be specified when using EvaluationException class.

    When using EvaluationException, specify the type that best describes the nature of the error being captured.

    * INVALID_VALUE -> One or more inputs are invalid (e.g. incorrect type or format)
    * UNKNOWN_FIELD -> A least one unrecognized parameter is specified
    * MISSING_FIELD -> At least one required parameter is missing
    * FILE_OR_FOLDER_NOT_FOUND -> One or more files or folder paths do not exist
    * RESOURCE_NOT_FOUND -> Resource could not be found
    * FAILED_EXECUTION -> Execution failed
    * SERVICE_UNAVAILABLE -> Service is unavailable
    * MISSING_PACKAGE -> Required package is missing
    * FAILED_REMOTE_TRACKING -> Remote tracking failed
    * PROJECT_ACCESS_ERROR -> Access to project failed
    * UNKNOWN -> Undefined placeholder. Avoid using.
    """

    INVALID_VALUE = "INVALID VALUE"
    UNKNOWN_FIELD = "UNKNOWN FIELD"
    MISSING_FIELD = "MISSING FIELD"
    FILE_OR_FOLDER_NOT_FOUND = "FILE OR FOLDER NOT FOUND"
    RESOURCE_NOT_FOUND = "RESOURCE NOT FOUND"
    FAILED_EXECUTION = "FAILED_EXECUTION"
    SERVICE_UNAVAILABLE = "SERVICE UNAVAILABLE"
    MISSING_PACKAGE = "MISSING PACKAGE"
    FAILED_REMOTE_TRACKING = "FAILED REMOTE TRACKING"
    PROJECT_ACCESS_ERROR = "PROJECT ACCESS ERROR"
    UNKNOWN = "UNKNOWN"


class ErrorBlame(Enum):
    """Source of blame to be specified when using EvaluationException class.

    When using EvaluationException, specify whether the error is due to user actions or the system.
    """

    USER_ERROR = "UserError"
    SYSTEM_ERROR = "SystemError"
    UNKNOWN = "Unknown"


class ErrorTarget(Enum):
    """Error target to be specified when using EvaluationException class.

    When using EvaluationException, specify the code area that was being targeted when the
    exception was triggered.
    """

    EVAL_RUN = "EvalRun"
    CODE_CLIENT = "CodeClient"
    RAI_CLIENT = "RAIClient"
    COHERENCE_EVALUATOR = "CoherenceEvaluator"
    COMPLETENESS_EVALUATOR = "CompletenessEvaluator"
    CONTENT_SAFETY_CHAT_EVALUATOR = "ContentSafetyEvaluator"
    ECI_EVALUATOR = "ECIEvaluator"
    F1_EVALUATOR = "F1Evaluator"
    GROUNDEDNESS_EVALUATOR = "GroundednessEvaluator"
    PROTECTED_MATERIAL_EVALUATOR = "ProtectedMaterialEvaluator"
    INTENT_RESOLUTION_EVALUATOR = "IntentResolutionEvaluator"
    RELEVANCE_EVALUATOR = "RelevanceEvaluator"
    SIMILARITY_EVALUATOR = "SimilarityEvaluator"
    FLUENCY_EVALUATOR = "FluencyEvaluator"
    RETRIEVAL_EVALUATOR = "RetrievalEvaluator"
    TASK_ADHERENCE_EVALUATOR = "TaskAdherenceEvaluator"
    INDIRECT_ATTACK_EVALUATOR = "IndirectAttackEvaluator"
    INDIRECT_ATTACK_SIMULATOR = "IndirectAttackSimulator"
    ADVERSARIAL_SIMULATOR = "AdversarialSimulator"
    DIRECT_ATTACK_SIMULATOR = "DirectAttackSimulator"
    EVALUATE = "Evaluate"
    CALLBACK_CONVERSATION_BOT = "CallbackConversationBot"
    MODELS = "Models"
    UNKNOWN = "Unknown"
    CONVERSATION = "Conversation"
    TOOL_CALL_ACCURACY_EVALUATOR = "ToolCallAccuracyEvaluator"
    RED_TEAM = "RedTeam"


class EvaluationException(AzureError):
    """The base class for all exceptions raised in azure-ai-evaluation. If there is a need to define a custom
    exception type, that custom exception type should extend from this class.

    :param message: A message describing the error. This is the error message the user will see.
    :type message: str
    :param internal_message: The error message without any personal data. This will be pushed to telemetry logs.
    :type internal_message: str
    :param target: The name of the element that caused the exception to be thrown.
    :type target: ~azure.ai.evaluation._exceptions.ErrorTarget
    :param category: The error category, defaults to Unknown.
    :type category: ~azure.ai.evaluation._exceptions.ErrorCategory
    :param blame: The source of blame for the error, defaults to Unknown.
    :type balance: ~azure.ai.evaluation._exceptions.ErrorBlame
    :param tsg_link: A link to the TSG page for troubleshooting the error.
    :type tsg_link: str
    """

    def __init__(
        self,
        message: str,
        *args,
        internal_message: Optional[str] = None,
        target: ErrorTarget = ErrorTarget.UNKNOWN,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        blame: ErrorBlame = ErrorBlame.UNKNOWN,
        tsg_link: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.category = category
        self.target = target
        self.blame = blame
        self.internal_message = internal_message
        self.tsg_link = tsg_link
        super().__init__(message, *args, **kwargs)

    def __str__(self):
        error_blame = "InternalError" if self.blame != ErrorBlame.USER_ERROR else "UserError"
        msg = f"({error_blame}) {super().__str__()}"
        if self.tsg_link:
            msg += f"\nVisit {self.tsg_link} to troubleshoot this issue."

        return msg
