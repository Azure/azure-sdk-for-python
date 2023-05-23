# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental


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
    ):
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id
