# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from typing import Dict, Optional, Any
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml._restclient.v2023_06_01_preview.models import ComputePolicyRequest, ComputePolicyDto

from enum import Enum


class PolicyDefinition(Enum):
    MaxJobInstanceCount = 'MaxJobInstanceCount'
    MaxJobExecutionTime = 'MaxJobExecutionTime'
    MaxTotalVcpuUsage = 'MaxTotalVcpuUsage'
    MaxPerUserVcpuUsage = 'MaxPerUserVcpuUsage'
    CiIdleShutdown = 'CiIdleShutdown'
    RequireCiLatestSoftware = 'RequireCiLatestSoftware'


class PolicyEffect(Enum):
    Deny = 'Deny'
    Audit = 'Audit'


@experimental
class Policy(object):
    
    def __init__(self,
                 name: str,
                 arm_scope: str,
                 definition: PolicyDefinition,
                 parameters: Dict[str, Any],
                 effect: PolicyEffect,
                 id: Optional[str] = None) -> None:
        self.id = id
        self.name = name
        self.arm_scope = arm_scope
        self.definition = definition
        self.parameters = parameters
        self.effect = effect

    def _to_rest_object(self) -> ComputePolicyRequest:
        return ComputePolicyRequest(
            arm_scope=self.arm_scope,
            definition=self.definition.value,
            parameters=self.parameters,
            effect=self.effect.value,
        )

    @classmethod
    def _from_rest_object(cls, obj: ComputePolicyDto) -> "Policy":
        return Policy(
            name=obj.name,
            arm_scope=obj.arm_scope,
            parameters=obj.parameters,
            effect=PolicyEffect[obj.effect],
            definition=PolicyDefinition[obj.definition],
            id=obj.id,
        )

    def __dict__(self):
        return {
            "id": self.id,
            "name": self.name,
            "arm_scope": self.arm_scope,
            "definition": self.definition,
            "parameters": self.parameters,
            "effect": self.effect,
        }
