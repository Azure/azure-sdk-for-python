# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._utils._experimental import experimental


@experimental
class MonitoringTarget:
    def __init__(
        self,
        *,
        endpoint_deployment_id: str = None,
        model_id: str = None,
    ):
        self.endpoint_deployment_id = endpoint_deployment_id
        self.model_id = model_id
