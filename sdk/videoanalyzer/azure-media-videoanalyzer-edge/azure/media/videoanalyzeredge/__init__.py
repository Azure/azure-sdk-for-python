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
    topology_body = PipelineTopologySetRequestBody(name=self.pipeline_topology.name)
    topology_body.system_data = self.pipeline_topology.system_data
    topology_body.properties = self.pipeline_topology.properties

    return topology_body.serialize()

PipelineTopologySetRequest.serialize = _OverrideTopologySetRequestSerialize

def _OverrideInstanceSetRequestSerialize(self):
    live_pipeline_body = LivePipelineSetRequestBody(name=self.live_pipeline.name)
    live_pipeline_body.system_data = self.live_pipeline.system_data
    live_pipeline_body.properties = self.live_pipeline.properties

    return live_pipeline_body.serialize()

LivePipelineSetRequest.serialize = _OverrideInstanceSetRequestSerialize

def _OverrideRemoteDeviceAdapterSetRequestSerialize(self):
    remote_device_adapter_body = RemoteDeviceAdapterSetRequestBody(name=self.remote_device_adapter.name)
    remote_device_adapter_body.system_data = self.remote_device_adapter.system_data
    remote_device_adapter_body.properties = self.remote_device_adapter.properties

    return remote_device_adapter_body.serialize()

RemoteDeviceAdapterSetRequest.serialize = _OverrideRemoteDeviceAdapterSetRequestSerialize
