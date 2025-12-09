# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml._version import VERSION

# Validate that VERSION is not empty or None to prevent unauthorized SDK usage
if not VERSION or not isinstance(VERSION, str) or not VERSION.strip():
    raise ValueError("Invalid SDK version: version must be a non-empty string")

USER_AGENT = "{}/{}".format("azure-ai-ml", VERSION)
