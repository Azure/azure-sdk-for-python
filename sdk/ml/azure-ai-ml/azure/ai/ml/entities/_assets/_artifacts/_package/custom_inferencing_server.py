# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    OnlineInferenceConfiguration,
    CustomInferencingServer as RestCustomInferencingServer,
)


class CustomInferencingServer:
    def __init__(self, type: str = None, inference_configuration: OnlineInferenceConfiguration = None):
        """CustomInferencingServer Variables are only populated by the server, and will be ignored when sending a request."""
        self.type = type
        self.inference_configuration = inference_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestCustomInferencingServer) -> "RestCustomInferencingServer":
        return CustomInferencingServer(
            type=rest_obj.server_type, inference_configuration=rest_obj.inference_configuration
        )

    def _to_rest_object(self) -> RestCustomInferencingServer:
        return RestCustomInferencingServer(server_type=self.type, inference_configuration=self.inference_configuration)
