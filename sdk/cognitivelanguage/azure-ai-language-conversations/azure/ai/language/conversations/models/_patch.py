# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Mapping, Optional, Dict, IO, cast, List, TypeVar
import json
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller, AsyncLROPoller
from azure.core.polling.base_polling import LROBasePolling, PollingMethod
from azure.core.rest import HttpRequest
from azure.core.polling.async_base_polling import (
    AsyncLROBasePolling,
)
from azure.core.polling._async_poller import AsyncPollingMethod
from ._models import (
    AnalyzeConversationOperationInput,
    MultiLanguageConversationInput,
    SummarizationOperationAction,
    ConversationSummarizationActionContent,
    AnalyzeConversationOperationAction,
    AnalyzeConversationOperationState,
    ConversationPiiActionContent,
    PiiOperationAction,
    CharacterMaskPolicyType,
    EntityMaskTypePolicyType,
    NoMaskPolicyType,
)
from ._enums import RedactionCharacter


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__ = [
    "AnalyzeConversationOperationInput",
    "MultiLanguageConversationInput",
    "SummarizationOperationAction",
    "ConversationSummarizationActionContent",
    "AnalyzeConversationOperationAction",
    "ConversationPiiActionContent",
    "PiiOperationAction",
    "CharacterMaskPolicyType",
    "RedactionCharacter",
    "EntityMaskTypePolicyType",
    "NoMaskPolicyType",
]
