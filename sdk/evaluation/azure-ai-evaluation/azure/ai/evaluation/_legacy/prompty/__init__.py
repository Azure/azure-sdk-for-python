# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.evaluation._legacy.prompty._prompty import AsyncPrompty
from azure.ai.evaluation._legacy.prompty._connection import Connection, OpenAIConnection, AzureOpenAIConnection
from azure.ai.evaluation._legacy.prompty._exceptions import (
    PromptyException,
    MissingRequiredInputError,
    InvalidInputError,
    JinjaTemplateError,
    NotSupportedError,
)

# =========================================================================================================
# NOTE: All of the code here is largely copy of code from Promptflow. Generally speaking, the following
#       changes were made:
#       - Added type annotations
#       - Legacy or deprecated functionality has been removed (e.g. no more support for completions API)
#       - Reworked the way images are handled to 1) Reduce the amount of code brought over, 2) remove
#         the need to do two passes over the template to insert images, 3) remove the completely unnecessary
#         loading of image data from the internet when it is not actually needed
#       - Minor obvious tweaks to improve code readability, and removal of unused code paths
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
