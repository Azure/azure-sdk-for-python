# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---


from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    OnlineInferenceConfiguration,
    CustomInferencingServer as RestCustomInferencingServer,
    Route as RestRoute,
    OnlineInferenceConfiguration as RestOnlineInferenceConfiguration,
)


class Route:
    def __init__(self, port: str = None, path: str = None):
        """Route Variables are only populated by the server, and will be ignored when sending a request."""
        self.port = port
        self.path = path

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRoute) -> "RestRoute":
        return Route(port=rest_obj.port, path=rest_obj.path)

    def _to_rest_object(self) -> RestRoute:
        return RestRoute(port=self.port, path=self.path)


class OnlineInferenceConfiguration:
    def __init__(
        self,
        liveness_route: Route = None,
        readiness_route: Route = None,
        scoring_route: Route = None,
        entry_script: str = None,
        configuration: dict = None,
    ):
        self.liveness_route = liveness_route
        self.readiness_route = readiness_route
        self.scoring_route = scoring_route
        self.entry_script = entry_script
        self.configuration = configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestOnlineInferenceConfiguration) -> "RestOnlineInferenceConfiguration":
        return OnlineInferenceConfiguration(
            liveness_route=Route._from_rest_object(rest_obj.liveness_route),
            readiness_route=Route._from_rest_object(rest_obj.readiness_route),
            scoring_route=Route._from_rest_object(rest_obj.scoring_route),
            entry_script=rest_obj.entry_script,
            configuration=rest_obj.configuration,
        )

    def _to_rest_object(self) -> RestOnlineInferenceConfiguration:
        return RestOnlineInferenceConfiguration(
            liveness_route=self.liveness_route._to_rest_object(),
            readiness_route=self.readiness_route._to_rest_object(),
            scoring_route=self.scoring_route._to_rest_object(),
            entry_script=self.entry_script,
            configuration=self.configuration,
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
