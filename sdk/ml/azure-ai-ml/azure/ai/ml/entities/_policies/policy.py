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
class PolicyList(Resource):
    pass


@experimental
class Policy(Resource):

    class Definition(Enum):
        MaxJobInstanceCount = 'MaxJobInstanceCount'
        MaxJobExecutionTime = 'MaxJobExecutionTime'
        MaxTotalVcpuUsage = 'MaxTotalVcpuUsage'
        MaxPerUserVcpuUsage = 'MaxPerUserVcpuUsage'
        CiIdleShutdown = 'CiIdleShutdown'
        RequireCiLatestSoftware = 'RequireCiLatestSoftware'


    class Effect(Enum):
        Deny = 'Deny'
        Audit = 'Audit'
    
    def __init__(self,
                 name: str,
                 arm_scope: str,
                 definition: Definition,
                 parameters: Dict[str, Any],
                 effect: Effect,
                 id: Optional[str] = None) -> None:
        super().__init__(name=name)
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
            effect=Policy.Effect[obj.effect],
            definition=Policy.Definition[obj.definition],
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

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Policy":
        pass

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the object content into a file.

        :param dest: The local path or file stream to write the YAML content to.
            If dest is a file path, a new file will be created.
            If dest is an open file, the file will be written to directly.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        pass