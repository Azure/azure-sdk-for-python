# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=too-many-instance-attributes,protected-access

from typing import Dict, Optional, Any
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml._restclient.v2023_06_01_preview.models import ComputePolicyRequest, ComputePolicyDto
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Union
from enum import Enum

@experimental
class Policy(object):
    class Definition(Enum):
        MaxJobInstanceCount = 'MaxJobInstanceCount'
        MaxJobExecutionTime = 'MaxJobExecutionTime'
        MaxTotalVcpuUsage = 'MaxTotalVcpuUsage'
        MaxPerUserVcpuUsage = 'MaxPerUserVcpuUsage'
        CiIdleShutdown = 'CiIdleShutdown'
        RequireCiLatestSoftware = 'RequireCiLatestSoftware'

        @staticmethod
        def get(name: str) -> "Policy.Definition":
            try:
                # by default try PascalCase
                return Policy.Definition[name]
            except KeyError:
                # fall back to snake case
                return Policy.Definition[name.replace("_", " ").title().replace(" ", "")]

    class Effect(Enum):
        Deny = 'Deny'
        Audit = 'Audit'
    
    def __init__(self,
                 name: str,
                 scope: str,
                 definition: Definition,
                 parameters: Dict[str, Any] = None,
                 effect: Effect = None) -> None:
        self.name = name
        self.scope = scope
        self.definition = definition
        self.parameters = parameters or {}
        self.effect = effect or Effect.Deny

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
            effect=Policy.Effect[obj.effect],
            definition=Policy.Definition[obj.definition]
        )

    def __dict__(self):
        return {
            "name": self.name,
            "scope": self.scope,
            "definition": self.definition,
            "parameters": self.parameters,
            "effect": self.effect,
        }

    def _to_dict(self):
        return self.__dict__()