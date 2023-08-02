# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._restclient.v2023_06_01_preview.models import MonitoringTarget as RestMonitoringTarget

@experimental
class MonitoringTarget:
    """Monitoring target

    :param endpoint_deployment_id: ARM ID of the target deployment id. Exclusive with
        model_id
    :type endpoint_deployment_id: str
    :param model_id: ARM ID of the target model id. Exclusive with
        endpoint_deployment_id
    :type model_id: str
    """

    def __init__(
        self,
        *,
        endpoint_deployment_id: str = None,
        model_id: str = None,
        ml_task: str = None,
    ):
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id
        self.ml_task = ml_task

    def _to_rest_object(self) -> RestMonitoringTarget:
        return RestMonitoringTarget(
            deployment_id=self.endpoint_deployment_id,
            model_id=self.model_id,
            task_type=self.ml_task,
        )
    
    def _from_rest_object(cls, obj: RestMonitoringTarget) -> "MonitoringTarget":
        return cls(
            endpoint_deployment_id=obj.endpoint_deployment_id,
            model_id=obj.model_id,
            task_type=obj.task_type,
        )
