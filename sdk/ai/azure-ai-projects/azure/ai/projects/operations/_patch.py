# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from ._patch_datasets import DatasetsOperations
from ._patch_telemetry import TelemetryOperations
from ._patch_connections import ConnectionsOperations
from ._patch_memories import BetaMemoryStoresOperations
from ._operations import BetaOperations as GenerateBetaOperations


class BetaOperations(GenerateBetaOperations):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.ai.projects.AIProjectClient`'s
        :attr:`beta` attribute.
    """

    memory_stores: BetaMemoryStoresOperations  # type override for mypy

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Override memory_stores with the patched version that has begin_update_memories
        self.memory_stores = BetaMemoryStoresOperations(self._client, self._config, self._serialize, self._deserialize)


__all__: List[str] = [
    "TelemetryOperations",
    "DatasetsOperations",
    "ConnectionsOperations",
    "BetaMemoryStoresOperations",
    "BetaOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
