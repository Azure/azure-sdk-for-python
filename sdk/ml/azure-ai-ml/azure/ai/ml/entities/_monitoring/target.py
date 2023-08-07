# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitoringTarget:
    """Monitoring target.

    :keyword endpoint_deployment_id: The ARM ID of the target deployment. Mutually exclusive with model_id.
    :type endpoint_deployment_id: Optional[str]
    :keyword model_id: ARM ID of the target model ID. Mutually exclusive with endpoint_deployment_id.
    :type model_id: Optional[str]

    .. admonition:: Example:


        .. literalinclude:: ../../../../../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_monitor_definition]
            :end-before: [END spark_monitor_definition]
            :language: python
            :dedent: 8
            :caption: Setting a monitoring target using endpoint_deployment_id.
    """

    def __init__(
        self,
        *,
        endpoint_deployment_id: str = None,
        model_id: str = None,
    ) -> None:
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id
