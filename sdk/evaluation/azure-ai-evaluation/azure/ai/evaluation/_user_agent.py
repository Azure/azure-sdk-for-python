# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.core.pipeline.policies import UserAgentPolicy
from azure.ai.evaluation._version import VERSION
import platform

# Format is "azsdk-python-this-package/version language/version (platform info)"

# USER_AGENT = "azsdk-python-evaluation/{} Python/{} ({})".format(VERSION, platform.python_version(), platform.platform())
USER_AGENT = UserAgentPolicy(sdk_moniker="{}/{}".format("azure-ai-evaluation", VERSION)).user_agent
