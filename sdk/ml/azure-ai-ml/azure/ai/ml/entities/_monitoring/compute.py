# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitorServerlessSparkCompute,
    MonitorComputeIdentityBase,
    AmlTokenComputeIdentity,
)


@experimental
class ComputeIdentity:
    def __init__(
        self,
        *,
        identity_type: str,
    ):
        self.identity_type = identity_type

    def _to_rest_object(self) -> MonitorComputeIdentityBase:
        return AmlTokenComputeIdentity(
            compute_identity_type=self.identity_type,
        )

    @classmethod
    def _from_rest_object(cls, obj: MonitorComputeIdentityBase) -> "ComputeIdentity":
        return cls(
            identity_type="AmlToken",
        )


@experimental
class ServerlessSparkCompute:
    def __init__(
        self,
        *,
        runtime_version: str,
        instance_type: str,
    ):
        self.runtime_version = runtime_version
        self.instance_type = instance_type

    def _to_rest_object(self) -> MonitorServerlessSparkCompute:
        return MonitorServerlessSparkCompute(
            runtime_version=self.runtime_version,
            instance_type=self.instance_type,
            compute_identity=AmlTokenComputeIdentity(
                compute_identity_type="AmlToken",
            ),
        )

    @classmethod
    def _from_rest_object(cls, obj: MonitorServerlessSparkCompute) -> "ServerlessSparkCompute":
        return cls(
            runtime_version=obj.runtime_version,
            instance_type=obj.instance_type,
        )
