# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, Mapping, Optional, overload

from .._utils.model_base import Model as _Model, rest_field


class FromCheckpoint(_Model):
    """Identifies a saved training checkpoint to bootstrap a new session from.

    When passed to :meth:`~azure.ai.finetuning_sessions.FineTuningSession.create`,
    the new session's LoRA weights, optimizer state, and scheduler step are all
    initialised from the referenced checkpoint (continual fine-tuning).

    :ivar source_session_id: The ``model_<session_id>`` of the session that saved
        the checkpoint.
    :vartype source_session_id: str
    :ivar checkpoint_id: Name of the checkpoint within the source session.
    :vartype checkpoint_id: str
    """

    source_session_id: str = rest_field()
    """The ``model_<session_id>`` of the session that saved the checkpoint."""

    checkpoint_id: str = rest_field()
    """Name of the checkpoint within the source session."""

    @overload
    def __init__(
        self,
        *,
        source_session_id: str,
        checkpoint_id: str,
    ) -> None: ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]) -> None:
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


__all__: list[str] = [
    "FromCheckpoint",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
