# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_02_01_preview.models import TritonInferencingServer as RestTritonInferencingServer


class TritonInferencingServer:
    def __init__(self, code_configuration: str = None):
        """TritonInferencingServer Variables are only populated by the server, and will be ignored when sending a request."""

        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestTritonInferencingServer) -> "RestTritonInferencingServer":
        return TritonInferencingServer(code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestTritonInferencingServer:
        return RestTritonInferencingServer(code_configuration=self.code_configuration)
