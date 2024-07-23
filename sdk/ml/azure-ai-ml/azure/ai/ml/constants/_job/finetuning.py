# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


# pylint: disable=protected-access


class FineTuningConstants:
    AzureOpenAI = "azure-openai"
    Custom = "custom"

    TaskType = "task"
    ModelProvider = "model_provider"
    HyperParameters = "hyperparameters"


class FineTuningTaskTypes:
    CHAT_COMPLETION = "ChatCompletion"
    TEXT_COMPLETION = "TextCompletion"
    TEXT_CLASSIFICATION = "TextClassification"
    QUESTION_ANSWERING = "QuestionAnswering"
    TEXT_SUMMARIZATION = "TextSummarization"
    TOKEN_CLASSIFICATION = "TokenClassification"
    TEXT_TRANSLATION = "TextTranslation"
    IMAGE_CLASSIFICATION = "ImageClassification"
    IMAGE_INSTANCE_SEGMENTATION = "ImageInstanceSegmentation"
    IMAGE_OBJECT_DETECTION = "ImageObjectDetection"
    VIDEO_MULTI_OBJECT_TRACKING = "VideoMultiObjectTracking"
