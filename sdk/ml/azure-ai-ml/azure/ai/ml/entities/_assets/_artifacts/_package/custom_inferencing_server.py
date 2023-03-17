# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_02_01_preview.models import CustomInferencingServer as RestCustomInferencingServer


class CustomInferencingServer:
    def __init__(self, code_configuration: str = None):
        """CustomInferencingServer Variables are only populated by the server, and will be ignored when sending a request."""

        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestCustomInferencingServer) -> "RestCustomInferencingServer":
        return CustomInferencingServer(code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestCustomInferencingServer:
        return RestCustomInferencingServer(code_configuration=self.code_configuration)
