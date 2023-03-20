# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    AzureMLBatchInferencingServer as RestAzureMLBatchInferencingServer,
)


class AzureMLBatchInferencingServer:
    def __init__(self, type: str = None, code_configuration: str = None):
        """AzureMLBatchInferencingServer Variables are only populated by the server, and will be ignored when sending a
        request."""
        self.type = type
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAzureMLBatchInferencingServer) -> "RestAzureMLBatchInferencingServer":
        return AzureMLBatchInferencingServer(code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestAzureMLBatchInferencingServer:
        return RestAzureMLBatchInferencingServer(server_type=self.type, code_configuration=self.code_configuration)
