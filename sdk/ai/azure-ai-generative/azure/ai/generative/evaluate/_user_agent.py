# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.generative._version import VERSION

USER_AGENT = "{package}/{version} {action}/{version}".format(
    package="azure-ai-generative", version=VERSION, action="evaluate"
)
