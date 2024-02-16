# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Iterable
from azure.core.polling import LROPoller

class AzureOpenAIDeploymentOperations():
    def __init__(self):
        pass

    def begin_create_or_update(self, deployment: "AzureOpenAIDeployment") -> LROPoller["AzureOpenAIDeployment"]:
        pass

    def get(self, deployment_name: str, connection_name: str = None):
        pass

    def list(self, include_connections: str = None) -> Iterable["AzureOpenAIDeployment"]:
        pass

    def begin_delete(self, deployment_name: str) -> LROPoller[None]:
        pass