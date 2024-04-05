# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import sys
from typing import List, Any, Union, IO, Optional, Dict
from azure.core.tracing.decorator import distributed_trace
from ._client import ModelClient as ModelClientGenerated
from . import models as _models

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
_Unset: Any = object()

class ModelClient(ModelClientGenerated):

        @distributed_trace
        def get_streaming_chat_completions(
            self,
            body: Union[JSON, IO[bytes]] = _Unset,
            *,
            messages: List[_models.ChatRequestMessage] = _Unset,
            extra_parameters: Optional[Union[str, _models.ExtraParameters]] = None,
            model_deployment: Optional[str] = None,
            extras: Optional[Dict[str, str]] = None,
            frequency_penalty: Optional[float] = None,
            presence_penalty: Optional[float] = None,
            temperature: Optional[float] = None,
            top_p: Optional[float] = None,
            max_tokens: Optional[int] = None,
            response_format: Optional[_models.ChatCompletionsResponseFormat] = None,
            stop: Optional[List[str]] = None,
            stream_parameter: Optional[bool] = None,
            tools: Optional[List[_models.ChatCompletionsToolDefinition]] = None,
            tool_choice: Optional[
                Union[str, _models.ChatCompletionsToolSelectionPreset, _models.ChatCompletionsNamedToolSelection]
            ] = None,
            seed: Optional[int] = None,
            **kwargs: Any
        ) -> None:
            print("This is a placeholder for the actual implementation")

__all__: List[str] = [
    "ModelClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
