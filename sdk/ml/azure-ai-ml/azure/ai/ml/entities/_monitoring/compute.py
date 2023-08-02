# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_06_01_preview.models import(
    MonitorServerlessSparkCompute,
    MonitorComputeIdentityBase,
    AmlTokenComputeIdentity,
)

class ComputeIdentity:
    def __init__(
        self, 
        *, 
        identity_type: str,
    ):
        self.identity_type = identity_type
    
    def _to_rest_object(self) -> MonitorComputeIdentityBase:
        return (
            AmlTokenComputeIdentity(
                identity_type=self.identity_type,
            )
        )
    
    def _from_rest_object(cls, obj: MonitorComputeIdentityBase) -> "ComputeIdentity":
        return cls(
            identity_type=obj.identity_type,
        )

    
class ComputeConfiguration:
    def __init__(self, *, compute_type: str):
        self.compute_type = compute_type


class ServerLessSparkCompute(ComputeConfiguration):
    def __init__(
        self,
        *,
        runtime_version: str,
        instance_type: str,
        compute_identity: Optional[ComputeIdentity] = None,
    ):
        super().__init__(compute_type="ServerLessSpark")
        self.runtime_version = runtime_version
        self.instance_type = instance_type
        self.compute_identity = compute_identity

    def _to_rest_object(self) -> MonitorServerlessSparkCompute:
        return MonitorServerlessSparkCompute(
            compute_type=self.compute_type,
            runtime_version=self.runtime_version,
            instance_type=self.instance_type,
            compute_identity=self.compute_identity._to_rest_object() if self.compute_identity else None,
        )

    @classmethod
    def _from_rest_object(cls, obj: MonitorServerlessSparkCompute) -> "ServerLessSparkCompute":
        return cls(
            runtime_version=obj.runtime_version,
            instance_type=obj.instance_type,
            compute_identity=ComputeIdentity._from_rest_object(obj.compute_identity),
        )
