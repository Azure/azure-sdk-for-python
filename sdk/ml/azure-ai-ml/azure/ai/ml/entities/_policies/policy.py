# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from typing import Dict, Any
from enum import Enum
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_06_01_preview.models import ComputePolicyRequest, ComputePolicyDto


class PolicyDefinition(Enum):
    MaxJobInstanceCount = "MaxJobInstanceCount"
    MaxJobExecutionTime = "MaxJobExecutionTime"
    MaxTotalVcpuUsage = "MaxTotalVcpuUsage"
    MaxPerUserVcpuUsage = "MaxPerUserVcpuUsage"
    CiIdleShutdown = "CiIdleShutdown"
    RequireCiLatestSoftware = "RequireCiLatestSoftware"

    @staticmethod
    def get(name: str) -> "PolicyDefinition":
        try:
            # by default try PascalCase
            return PolicyDefinition[name]
        except KeyError:
            # fall back to snake case
            return PolicyDefinition[name.replace("_", " ").title().replace(" ", "")]


class PolicyEffect(Enum):
    Deny = "Deny"
    Audit = "Audit"


@experimental
class Policy(object):
    def __init__(
        self, name: str,
        scope: str,
        definition: PolicyDefinition,
        parameters: Dict[str, Any] = None,
        effect: PolicyEffect = None
    ) -> None:
        self.name = name
        self.scope = scope
        self.definition = definition
        self.parameters = parameters or {}
        self.effect = effect or PolicyEffect.Deny

    def _to_rest_object(self) -> ComputePolicyRequest:
        return ComputePolicyRequest(
            arm_scope=self.scope,
            definition=self.definition.value,
            parameters=self.parameters,
            effect=self.effect.value,
        )

    @classmethod
    def _from_rest_object(cls, obj: ComputePolicyDto) -> "Policy":
        return Policy(
            name=obj.name,
            scope=obj.arm_scope,
            parameters=obj.parameters,
            effect=PolicyEffect[obj.effect],
            definition=PolicyDefinition[obj.definition],
        )

    def _to_dict(self):
        return {
            "name": self.name,
            "scope": self.scope,
            "definition": self.definition,
            "parameters": self.parameters,
            "effect": self.effect,
        }
