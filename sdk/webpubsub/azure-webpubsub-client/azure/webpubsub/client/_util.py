# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Optional
import time
from azure.core.pipeline.policies import UserAgentPolicy
from ._version import VERSION


def delay(delay_seconds: float):
    time.sleep(delay_seconds)


def format_user_agent(user_agent: Optional[str] = None):
    return UserAgentPolicy(user_agent=user_agent, sdk_moniker=f"webpubsub-client/{VERSION}").user_agent
