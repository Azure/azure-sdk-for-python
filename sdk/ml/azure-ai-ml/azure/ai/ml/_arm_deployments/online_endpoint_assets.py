# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging

from azure.ai.ml.entities import OnlineDeployment, OnlineEndpoint
from azure.ai.ml.entities._assets import Code, Model, Environment

module_logger = logging.getLogger(__name__)


class OnlineEndpointAssets(object):
    def __init__(self):
        self.codes = []
        self.models = []
        self.environments = []
        self.deployments = []
        self.endpoint = None
        self.endpoint_name = None
        self.is_create = False

    def add_online_deployment(self, deployment: OnlineDeployment) -> None:
        if (
            deployment.code_configuration
            and isinstance(deployment.code_configuration.code, Code)
            and deployment.code_configuration.code not in self.codes
        ):
            self.codes.append(deployment.code_configuration.code)
        if isinstance(deployment.model, Model):
            if deployment.model not in self.models:
                self.models.append(deployment.model)
        if isinstance(deployment.environment, Environment):
            if deployment.environment not in self.environments:
                self.environments.append(deployment.environment)
        self.endpoint_name = deployment.endpoint_name
        self.deployments += [deployment]

    def add_online_assets(self, old_endpoint: OnlineEndpoint, new_endpoint: OnlineEndpoint) -> None:
        self.endpoint_name = new_endpoint.name
        if not old_endpoint:
            # creation case: old_endpoint is None
            self.is_create = True
            if new_endpoint.deployments:
                for new_deployment in new_endpoint.deployments:
                    self.add_online_deployment(deployment=new_deployment)
            self.endpoint = new_endpoint
        else:
            # update case: old_endpoint is not None
            if new_endpoint != old_endpoint:
                self.endpoint = new_endpoint
            if new_endpoint.deployments:
                if not old_endpoint.deployments:
                    for deployment in new_endpoint.deployments:
                        self.add_online_deployment(deployment=deployment)
                else:
                    for deployment in new_endpoint.deployments:
                        old_deployment = next((d for d in old_endpoint.deployments if d.name == deployment.name), None)
                        if not old_deployment or old_deployment != deployment:
                            self.add_online_deployment(deployment=deployment)
