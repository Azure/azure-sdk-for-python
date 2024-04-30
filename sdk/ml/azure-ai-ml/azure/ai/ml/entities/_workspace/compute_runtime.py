# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional

from azure.ai.ml._restclient.v2023_06_01_preview.models import ComputeRuntimeDto as RestComputeRuntimeDto
from azure.ai.ml.entities._mixins import RestTranslatableMixin


class ComputeRuntime(RestTranslatableMixin):
    """Spark compute runtime configuration.

    :keyword spark_runtime_version: Spark runtime version.
    :paramtype spark_runtime_version: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_compute.py
            :start-after: [START compute_runtime]
            :end-before: [END compute_runtime]
            :language: python
            :dedent: 8
            :caption: Creating a ComputeRuntime object.
    """

    def __init__(
        self,
        *,
        spark_runtime_version: Optional[str] = None,
    ) -> None:
        self.spark_runtime_version = spark_runtime_version

    def _to_rest_object(self) -> RestComputeRuntimeDto:
        return RestComputeRuntimeDto(spark_runtime_version=self.spark_runtime_version)

    @classmethod
    def _from_rest_object(cls, obj: RestComputeRuntimeDto) -> Optional["ComputeRuntime"]:
        if not obj:
            return None
        return ComputeRuntime(spark_runtime_version=obj.spark_runtime_version)
