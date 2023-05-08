# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,redefined-builtin,unused-argument

from azure.ai.ml._restclient.v2023_02_01_preview.models import (
    AzureMLOnlineInferencingServer as RestAzureMLOnlineInferencingServer,
    AzureMLBatchInferencingServer as RestAzureMLBatchInferencingServer,
    CustomInferencingServer as RestCustomInferencingServer,
    TritonInferencingServer as RestTritonInferencingServer,
    OnlineInferenceConfiguration as RestOnlineInferenceConfiguration,
    Route as RestRoute,
)
from azure.ai.ml._utils._experimental import experimental

from ...._deployment.code_configuration import CodeConfiguration


@experimental
class AzureMLOnlineInferencingServer:
    """Azure ML online inferencing configurations.

    :param code_configuration: The code configuration of the inferencing server.
    :type code_configuration: str
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, code_configuration: CodeConfiguration = None, **kwargs):
        self.type = "azureml_online"
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAzureMLOnlineInferencingServer) -> "RestAzureMLOnlineInferencingServer":
        return AzureMLOnlineInferencingServer(type=rest_obj.server_type, code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestAzureMLOnlineInferencingServer:
        return RestAzureMLOnlineInferencingServer(server_type=self.type, code_configuration=self.code_configuration)


@experimental
class AzureMLBatchInferencingServer:
    """Azure ML batch inferencing configurations.

    :param code_configuration: The code configuration of the inferencing server.
    :type code_configuration: azure.ai.ml.entities.CodeConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, code_configuration: CodeConfiguration = None, **kwargs):
        self.type = "azureml_batch"
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestAzureMLBatchInferencingServer) -> "RestAzureMLBatchInferencingServer":
        return AzureMLBatchInferencingServer(code_configuration=rest_obj.code_configuration)

    def _to_rest_object(self) -> RestAzureMLBatchInferencingServer:
        return RestAzureMLBatchInferencingServer(server_type=self.type, code_configuration=self.code_configuration)


@experimental
class TritonInferencingServer:
    """Azure ML triton inferencing configurations.

    :param inference_configuration: The inference configuration of the inferencing server.
    :type inference_configuration: azure.ai.ml.entities.CodeConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, inference_configuration: CodeConfiguration = None, **kwargs):
        self.type = "triton"
        self.inference_configuration = inference_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestTritonInferencingServer) -> "RestTritonInferencingServer":
        return CustomInferencingServer(
            type=rest_obj.server_type, inference_configuration=rest_obj.inference_configuration
        )

    def _to_rest_object(self) -> RestTritonInferencingServer:
        return RestCustomInferencingServer(server_type=self.type, inference_configuration=self.inference_configuration)


@experimental
class Route:
    """Route.

    :param port: The port of the route.
    :type port: str
    :param path: The path of the route.
    :type path: str
    """

    def __init__(self, *, port: str = None, path: str = None):
        self.port = port
        self.path = path

    @classmethod
    def _from_rest_object(cls, rest_obj: RestRoute) -> "RestRoute":
        return Route(port=rest_obj.port, path=rest_obj.path)

    def _to_rest_object(self) -> RestRoute:
        return RestRoute(port=self.port, path=self.path)


@experimental
class OnlineInferenceConfiguration:
    """Online inference configurations.

    :param liveness_route: The liveness route of the online inference configuration.
    :type liveness_route: Route
    :param readiness_route: The readiness route of the online inference configuration.
    :type readiness_route: Route
    :param scoring_route: The scoring route of the online inference configuration.
    :type scoring_route: Route
    :param entry_script: The entry script of the online inference configuration.
    :type entry_script: str
    :param configuration: The configuration of the online inference configuration.
    :type configuration: dict
    """

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


@experimental
class CustomInferencingServer:
    """Custom inferencing configurations.

    :param inference_configuration: The inference configuration of the inferencing server.
    :type inference_configuration: OnlineInferenceConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, inference_configuration: OnlineInferenceConfiguration = None, **kwargs):
        self.type = "custom"
        self.inference_configuration = inference_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: RestCustomInferencingServer) -> "RestCustomInferencingServer":
        return CustomInferencingServer(
            type=rest_obj.server_type, inference_configuration=rest_obj.inference_configuration
        )

    def _to_rest_object(self) -> RestCustomInferencingServer:
        return RestCustomInferencingServer(server_type=self.type, inference_configuration=self.inference_configuration)
