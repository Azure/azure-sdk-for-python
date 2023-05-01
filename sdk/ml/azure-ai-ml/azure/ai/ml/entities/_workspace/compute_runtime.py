# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import ComputeRuntimeDto as RestComputeRuntimeDto
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental


@experimental
class ComputeRuntime(RestTranslatableMixin):
    def __init__(
        self,
        *,
        spark_runtime_version: Optional[str] = None,
    ):
        """
        :keyword spark_runtime_version:
        :paramtype spark_runtime_version: str
        """
        self.spark_runtime_version = spark_runtime_version

    def _to_rest_object(self) -> RestComputeRuntimeDto:
        return RestComputeRuntimeDto(spark_runtime_version=self.spark_runtime_version)

    @classmethod
    def _from_rest_object(cls, obj: RestComputeRuntimeDto) -> "ComputeRuntime":
        if not obj:
            return None
        return ComputeRuntime(spark_runtime_version=obj.spark_runtime_version)
