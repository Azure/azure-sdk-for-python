# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional
from azure.ai.evaluation._version import VERSION

USER_AGENT = "{}/{}".format("azure-ai-evaluation", VERSION)


def construct_user_agent_string(base_user_agent: str = USER_AGENT) -> str:
    """Construct a user agent string with custom user agent from context if available.
    
    :param base_user_agent: The base user agent string to use. Defaults to USER_AGENT.
    :type base_user_agent: str
    :return: The constructed user agent string.
    :rtype: str
    """
    from azure.ai.evaluation._context import get_current_user_agent
    custom_user_agent = get_current_user_agent()
    if custom_user_agent:
        return f"{base_user_agent} {custom_user_agent}"
    else:
        return base_user_agent
