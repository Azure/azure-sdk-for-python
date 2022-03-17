# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import TYPE_CHECKING
from ._models_py3 import (
    MediaGraphTopologySetRequest as MediaGraphTopologySetRequestGenerated,
    MediaGraphInstanceSetRequest as MediaGraphInstanceSetRequestGenerated,
    MediaGraphTopologySetRequestBody,
    MediaGraphInstanceSetRequestBody,
)

class MediaGraphTopologySetRequest(MediaGraphTopologySetRequestGenerated):

    def serialize(self):
        graph_body = MediaGraphTopologySetRequestBody(name=self.graph.name)
        graph_body.system_data = self.graph.system_data
        graph_body.properties = self.graph.properties
        return graph_body.serialize()

class MediaGraphInstanceSetRequest(MediaGraphInstanceSetRequestGenerated):

    def serialize(self):
        graph_body = MediaGraphInstanceSetRequestBody(name=self.instance.name)
        graph_body.system_data = self.instance.system_data
        graph_body.properties = self.instance.properties

        return graph_body.serialize()

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import List

__all__ = ["MediaGraphTopologySetRequest", "MediaGraphInstanceSetRequest"]  # type: List[str]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
