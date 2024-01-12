# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.generative._version import VERSION

USER_AGENT = "{}/{}".format("azure-ai-generative", VERSION)
OPENAI_USER_AGENT = f"AzureOpenAI/Python 1.7.1 {USER_AGENT}"
