# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.evaluation.legacy.prompty._prompty import AsyncPrompty
from azure.ai.evaluation.legacy.prompty._connection import Connection, OpenAIConnection, AzureOpenAIConnection
from azure.ai.evaluation.legacy.prompty._exceptions import (
    PromptyException,
    MissingRequiredInputError,
    InvalidInputError,
    JinjaTemplateError,
    NotSupportedError,
)

# =========================================================================================================
# NOTE: All of the code here is largely copy of code from the Promptflow repo. Generally speaking, the
#       following changes were made:
#       - Added type annotations
#       - Removed some unused/unneeded code
#       - Minor obvious tweaks to improve code readability
#       - Helper classes may have been reworked for simplicity, but the core logic remains the same
#       - Legacy or deprecated functionality has been removed (e.g. no more support for completions API)
# =========================================================================================================

__all__ = [
    "AsyncPrompty",
    "Connection",
    "AzureOpenAIConnection",
    "OpenAIConnection",
    "PromptyException",
    "MissingRequiredInputError",
    "InvalidInputError",
    "JinjaTemplateError",
    "NotSupportedError",
]
