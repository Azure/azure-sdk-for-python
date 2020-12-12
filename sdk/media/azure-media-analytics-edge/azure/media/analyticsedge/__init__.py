# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from ._generated.models import *
from ._generated import models
from ._version import VERSION

__version__ = VERSION
__all__ = models.__all__

def _OverrideTopologySetRequestSerialize(self):
    graph_body = MediaGraphTopologySetRequestBody(name=self.graph.name)
    graph_body.system_data = self.graph.system_data
    graph_body.properties = self.graph.properties

    return graph_body.serialize()

MediaGraphTopologySetRequest.serialize = _OverrideTopologySetRequestSerialize

def _OverrideInstanceSetRequestSerialize(self):
    graph_body = MediaGraphInstanceSetRequestBody(name=self.instance.name)
    graph_body.system_data = self.instance.system_data
    graph_body.properties = self.instance.properties

    return graph_body.serialize()

MediaGraphInstanceSetRequest.serialize = _OverrideInstanceSetRequestSerialize
