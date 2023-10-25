# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.metrics import constants

QA = "qa"
QA_RAG = "qa-rag"
CHAT_RAG = "chat-rag"

SUPPORTED_TASK_TYPE = [QA, QA_RAG, CHAT_RAG]

SUPPORTED_TO_METRICS_TASK_TYPE_MAPPING = {
    "qa": constants.QUESTION_ANSWERING,
    "qa-rag": constants.RAG_EVALUATION,
    "chat-rag": constants.RAG_EVALUATION,
}

TYPE_TO_KWARGS_MAPPING = {
    constants.QUESTION_ANSWERING: ["questions", "contexts", "y_pred", "y_test"],
    constants.RAG_EVALUATION: ["y_pred"]
}
