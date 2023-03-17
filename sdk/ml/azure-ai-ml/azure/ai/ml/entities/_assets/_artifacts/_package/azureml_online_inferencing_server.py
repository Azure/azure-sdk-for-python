# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    AzureMLOnlineInferencingServer as RestAzureMLOnlineInferencingServer,
)


class AzureMLOnlineInferencingServer:
    def __init__(self, type: str = None, code_configuration: str = None):
        """AzureMLOnlineInferencingServer Variables are only populated by the server, and will be ignored when sending a
        request."""
        self.type = type
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAzureMLOnlineInferencingServer) -> "RestAzureMLOnlineInferencingServer":
        return AzureMLOnlineInferencingServer(type=rest_obj.server_type, code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestAzureMLOnlineInferencingServer:
        return RestAzureMLOnlineInferencingServer(server_type=self.type, code_configuration=self.code_configuration)
