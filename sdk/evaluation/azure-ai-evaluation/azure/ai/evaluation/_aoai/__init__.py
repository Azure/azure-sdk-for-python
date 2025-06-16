# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from .aoai_grader import AzureOpenAIGrader
from .score_model_grader import AzureOpenAIScoreModelGrader

__all__ = [
    "AzureOpenAIGrader",
    "AzureOpenAIScoreModelGrader",
]