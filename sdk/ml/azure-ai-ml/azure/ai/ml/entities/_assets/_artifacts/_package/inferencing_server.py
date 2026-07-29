# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,unused-argument

from typing import Any, Dict, Optional

from azure.ai.ml._utils._experimental import experimental

from ...._deployment.code_configuration import CodeConfiguration


def _code_configuration_to_wire(code_configuration: Any) -> Optional[Dict[str, Any]]:
    """Serialize a code configuration (entity, dict, or None) into the model-package wire shape.

    :param code_configuration: The code configuration to serialize.
    :type code_configuration: Any
    :return: The camelCase wire dict, or None.
    :rtype: Optional[Dict[str, Any]]
    """
    if code_configuration is None:
        return None
    if isinstance(code_configuration, dict):
        return code_configuration
    code_id = getattr(code_configuration, "code_id", None)
    if code_id is None:
        code_id = getattr(code_configuration, "code", None)
    scoring_script = getattr(code_configuration, "scoring_script", None)
    wire: Dict[str, Any] = {}
    if code_id is not None:
        wire["codeId"] = code_id
    if scoring_script is not None:
        wire["scoringScript"] = scoring_script
    return wire


@experimental
class AzureMLOnlineInferencingServer:
    """Azure ML online inferencing configurations.

    :param code_configuration: The code configuration of the inferencing server.
    :type code_configuration: str
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, code_configuration: Optional[CodeConfiguration] = None, **kwargs: Any):
        self.type = "azureml_online"
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "AzureMLOnlineInferencingServer":
        code = (
            rest_obj.get("codeConfiguration")
            if isinstance(rest_obj, dict)
            else getattr(rest_obj, "code_configuration", None)
        )
        return AzureMLOnlineInferencingServer(code_configuration=code)

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"serverType": "AzureMLOnline"}
        code = _code_configuration_to_wire(self.code_configuration)
        if code is not None:
            rest["codeConfiguration"] = code
        return rest


@experimental
class AzureMLBatchInferencingServer:
    """Azure ML batch inferencing configurations.

    :param code_configuration: The code configuration of the inferencing server.
    :type code_configuration: azure.ai.ml.entities.CodeConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, code_configuration: Optional[CodeConfiguration] = None, **kwargs: Any):
        self.type = "azureml_batch"
        self.code_configuration = code_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "AzureMLBatchInferencingServer":
        code = (
            rest_obj.get("codeConfiguration")
            if isinstance(rest_obj, dict)
            else getattr(rest_obj, "code_configuration", None)
        )
        return AzureMLBatchInferencingServer(code_configuration=code)

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"serverType": "AzureMLBatch"}
        code = _code_configuration_to_wire(self.code_configuration)
        if code is not None:
            rest["codeConfiguration"] = code
        return rest


@experimental
class TritonInferencingServer:
    """Azure ML triton inferencing configurations.

    :param inference_configuration: The inference configuration of the inferencing server.
    :type inference_configuration: azure.ai.ml.entities.CodeConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, inference_configuration: Optional[CodeConfiguration] = None, **kwargs: Any):
        self.type = "triton"
        self.inference_configuration = inference_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "CustomInferencingServer":
        ic = (
            rest_obj.get("inferenceConfiguration")
            if isinstance(rest_obj, dict)
            else getattr(rest_obj, "inference_configuration", None)
        )
        return CustomInferencingServer(inference_configuration=ic)

    def _to_rest_object(self) -> Dict[str, Any]:
        # NOTE: preserves the legacy wire shape exactly — the original built a ``CustomInferencingServer``
        # (server discriminator "Custom") from a Triton entity, so this path emits ``serverType: Custom``.
        rest: Dict[str, Any] = {"serverType": "Custom"}
        if self.inference_configuration is not None:
            ic = self.inference_configuration
            rest["inferenceConfiguration"] = ic._to_rest_object() if hasattr(ic, "_to_rest_object") else ic
        return rest


@experimental
class Route:
    """Route.

    :param port: The port of the route.
    :type port: str
    :param path: The path of the route.
    :type path: str
    """

    def __init__(self, *, port: Optional[str] = None, path: Optional[str] = None):
        self.port = port
        self.path = path

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "Route":
        if isinstance(rest_obj, dict):
            return Route(port=rest_obj.get("port"), path=rest_obj.get("path"))
        return Route(port=rest_obj.port, path=rest_obj.path)

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {}
        if self.port is not None:
            rest["port"] = int(self.port)
        if self.path is not None:
            rest["path"] = self.path
        return rest


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
        liveness_route: Optional[Route] = None,
        readiness_route: Optional[Route] = None,
        scoring_route: Optional[Route] = None,
        entry_script: Optional[str] = None,
        configuration: Optional[dict] = None,
    ):
        self.liveness_route = liveness_route
        self.readiness_route = readiness_route
        self.scoring_route = scoring_route
        self.entry_script = entry_script
        self.configuration = configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "OnlineInferenceConfiguration":
        def _get(obj: Any, key: str, attr: str) -> Any:
            return obj.get(key) if isinstance(obj, dict) else getattr(obj, attr, None)

        return OnlineInferenceConfiguration(
            liveness_route=Route._from_rest_object(_get(rest_obj, "livenessRoute", "liveness_route")),
            readiness_route=Route._from_rest_object(_get(rest_obj, "readinessRoute", "readiness_route")),
            scoring_route=Route._from_rest_object(_get(rest_obj, "scoringRoute", "scoring_route")),
            entry_script=_get(rest_obj, "entryScript", "entry_script"),
            configuration=_get(rest_obj, "configuration", "configuration"),
        )

    def _to_rest_object(self) -> Dict[str, Any]:
        # NOTE: ``configuration`` is intentionally omitted — the legacy msrest
        # ``OnlineInferenceConfiguration`` model had no such field and dropped it on the wire.
        rest: Dict[str, Any] = {}
        if self.liveness_route is not None:
            rest["livenessRoute"] = self.liveness_route._to_rest_object()
        if self.readiness_route is not None:
            rest["readinessRoute"] = self.readiness_route._to_rest_object()
        if self.scoring_route is not None:
            rest["scoringRoute"] = self.scoring_route._to_rest_object()
        if self.entry_script is not None:
            rest["entryScript"] = self.entry_script
        return rest


@experimental
class CustomInferencingServer:
    """Custom inferencing configurations.

    :param inference_configuration: The inference configuration of the inferencing server.
    :type inference_configuration: OnlineInferenceConfiguration
    :ivar type: The type of the inferencing server.
    """

    def __init__(self, *, inference_configuration: Optional[OnlineInferenceConfiguration] = None, **kwargs: Any):
        self.type = "custom"
        self.inference_configuration = inference_configuration

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "CustomInferencingServer":
        ic = (
            rest_obj.get("inferenceConfiguration")
            if isinstance(rest_obj, dict)
            else getattr(rest_obj, "inference_configuration", None)
        )
        return CustomInferencingServer(inference_configuration=ic)

    def _to_rest_object(self) -> Dict[str, Any]:
        rest: Dict[str, Any] = {"serverType": "Custom"}
        if self.inference_configuration is not None:
            rest["inferenceConfiguration"] = self.inference_configuration._to_rest_object()
        return rest
