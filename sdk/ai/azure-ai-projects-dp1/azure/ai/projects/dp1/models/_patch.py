# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from typing import Any, Dict, Iterator, List, Literal, Mapping, Optional, TYPE_CHECKING, Union, overload

from .. import _model_base
from .._model_base import rest_discriminator, rest_field
from ._enums import AuthorRole, CredentialType, DatasetType, DeploymentType, IndexType, PendingUploadType

if TYPE_CHECKING:
    from .. import models as _models

from ._models import Agent as AgentGenerated
from ._models import Run as RunGenerated


class Agent(AgentGenerated):
    @overload
    def __init__(
        self,
        *,
        creation_options: "_models.AgentCreationOptions",
        description: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class Run(RunGenerated):
    @property
    def text_messages(self) -> Iterator["_models.TextContent"]:
        """Iterates over messages and yields only those of type TextMessage."""
        if not self.output:  # Handle None or empty output
            return
        for message in self.output:
            for content in message.content:
                if isinstance(content, _models.TextContent):
                    yield content.text

    def __iter__(self) -> Iterator["_models.ChatMessage"]:
        """Allows iteration over all messages."""
        return iter(self.run_outputs.messages)


__all__: List[str] = [
    "Agent",
    "Run",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
