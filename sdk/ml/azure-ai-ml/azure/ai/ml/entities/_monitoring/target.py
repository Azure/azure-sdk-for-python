# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringTarget as RestMonitoringTarget
from azure.ai.ml.constants._monitoring import MonitorTargetTasks


class MonitoringTarget:
    """Monitoring target.

    :keyword ml_task: Type of task. Allowed values: Classification, Regression, and QuestionAnswering
    :paramtype ml_task: Optional[Union[str, MonitorTargetTasks]]
    :keyword endpoint_deployment_id: The ARM ID of the target deployment. Mutually exclusive with model_id.
    :paramtype endpoint_deployment_id: Optional[str]
    :keyword model_id: ARM ID of the target model ID. Mutually exclusive with endpoint_deployment_id.
    :paramtype model_id: Optional[str]

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_monitor_definition]
            :end-before: [END spark_monitor_definition]
            :language: python
            :dedent: 8
            :caption: Setting a monitoring target using endpoint_deployment_id.
    """

    def __init__(
        self,
        *,
        ml_task: Optional[Union[str, MonitorTargetTasks]] = None,
        endpoint_deployment_id: Optional[str] = None,
        model_id: Optional[str] = None,
    ):
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id
        self.ml_task = ml_task

    def _to_rest_object(self) -> RestMonitoringTarget:
        return RestMonitoringTarget(
            task_type=self.ml_task if self.ml_task else "classification",
            deployment_id=self.endpoint_deployment_id,
            model_id=self.model_id,
        )

    @classmethod
    def _from_rest_object(cls, obj: RestMonitoringTarget) -> "MonitoringTarget":
        return cls(
            ml_task=obj.task_type,
            endpoint_deployment_id=obj.endpoint_deployment_id,
            model_id=obj.model_id,
        )
