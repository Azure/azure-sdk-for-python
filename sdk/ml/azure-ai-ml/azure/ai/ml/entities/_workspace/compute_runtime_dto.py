# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2022_12_01_preview.models import ComputeRuntimeDto as RestComputeRuntimeDto
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ComputeRuntimeDto(RestTranslatableMixin):
    def __init__(
        self,
        *,
        spark_runtime_version: Optional[str] = None,
        **kwargs
    ):
        """
        :keyword spark_runtime_version:
        :paramtype spark_runtime_version: str
        """
        self.spark_runtime_version = spark_runtime_version

    def _to_rest_object(self) -> RestComputeRuntimeDto:
        return RestComputeRuntimeDto(
            spark_runtime_version=self.spark_runtime_version
        )
        pass

    @classmethod
    def _from_rest_object(cls, rest_obj: RestComputeRuntimeDto) -> "ComputeRuntimeDto":
        if not rest_obj:
            return None
        return ComputeRuntimeDto(
            spark_runtime_version=rest_obj.spark_runtime_version
        )
