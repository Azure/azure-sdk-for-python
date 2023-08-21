# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    MonitorServerlessSparkCompute,
    AmlTokenComputeIdentity,
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
