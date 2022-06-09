# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import abstractmethod
import logging
from typing import Any, Dict, Union, Optional

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    CodeConfiguration as RestCodeConfiguration,
    OnlineDeploymentDetails as RestOnlineDeploymentDetails,
    OnlineDeploymentData as RestOnlineDeploymentData,
    KubernetesOnlineDeployment as RestKubernetesOnlineDeployment,
    ManagedOnlineDeployment as RestManagedOnlineDeployment,
    Sku as RestSku,
    EndpointComputeType,
)
from azure.ai.ml._utils.utils import camel_to_snake, load_yaml
from azure.ai.ml.entities import CodeConfiguration, Environment, Model
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._deployment.deployment_settings import ProbeSettings, OnlineRequestSettings

from azure.ai.ml.entities._deployment.scale_settings import (
    OnlineScaleSettings,
    TargetUtilizationScaleSettings,
    DefaultScaleSettings,
)
from azure.ai.ml.entities._deployment.resource_requirements_settings import ResourceRequirementsSettings
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml.entities._endpoint._endpoint_helpers import validate_endpoint_or_deployment_name
from azure.ai.ml.constants import (
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    ArmConstants,
)
from os import PathLike
from pathlib import Path
from azure.ai.ml.entities._util import load_from_dict
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema._deployment.online.online_deployment import (
    KubernetesOnlineDeploymentSchema,
    ManagedOnlineDeploymentSchema,
)
from .deployment import Deployment
from azure.ai.ml._ml_exceptions import DeploymentException, ErrorCategory, ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


class OnlineDeployment(Deployment):
    """Online endpoint deployment entity

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: Dict[str, Any], optional
    :param description: Description of the resource.
    :type description: str, optional
    :param model: Model entity for the endpoint deployment, defaults to None
    :type model: Union[str, Model], optional
    :param code_configuration: defaults to None
    :type code_configuration: CodeConfiguration, optional
    :param environment: Environment entity for the endpoint deployment, defaults to None
    :type environment: Union[str, Environment], optional
    :param app_insights_enabled: defaults to False
    :type app_insights_enabled: bool, optional
    :param scale_settings: How the online deployment will scale.
    :type scale_settings: OnlineScaleSettings, optional
    :param request_settings: defaults to RequestSettings()
    :type request_settings: OnlineRequestSettings, optional
    :param liveness_probe: Liveness probe settings.
    :type liveness_probe: ProbeSettings, optional
    :param readiness_probe: Readiness probe settings.
    :type readiness_probe: ProbeSettings, optional
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict, optional
    :param instance_count: The instance count used for this deployment.
    :type instance_count: int
    :param instance_type: Azure compute sku.
    :type instance_type: str
    :param model_mount_path: The path to mount the model in custom container..
    :type model_mount_path: str
    :param code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present.
    :type code_path: Union[str, PathLike], optional
    :param scoring_script: Equivalent to code_configuration.code.scoring_script, will be ignored if code_configuration is present.
    :type scoring_script: Union[str, PathLike], optional
    """

    def __init__(
        self,
        name: str,
        endpoint_name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        description: str = None,
        model: Union[str, "Model"] = None,
        code_configuration: CodeConfiguration = None,
        environment: Union[str, "Environment"] = None,
        app_insights_enabled: bool = False,
        scale_settings: OnlineScaleSettings = None,
        request_settings: OnlineRequestSettings = None,
        liveness_probe: ProbeSettings = None,
        readiness_probe: ProbeSettings = None,
        environment_variables: Dict[str, str] = None,
        instance_count: int = None,
        instance_type: str = None,
        model_mount_path: str = None,
        code_path: Union[str, PathLike] = None,  # promoted property from code_configuration.code
        scoring_script: Union[str, PathLike] = None,  # promoted property from code_configuration.scoring_script
        **kwargs,
    ):
        self._provisioning_state = kwargs.pop("provisioning_state", None)

        super(OnlineDeployment, self).__init__(
            name=name,
            endpoint_name=endpoint_name,
            tags=tags,
            properties=properties,
            description=description,
            model=model,
            code_configuration=code_configuration,
            environment=environment,
            environment_variables=environment_variables,
            code_path=code_path,
            scoring_script=scoring_script,
            **kwargs,
        )

        self.app_insights_enabled = app_insights_enabled
        self.scale_settings = scale_settings
        self.request_settings = request_settings
        self.liveness_probe = liveness_probe
        self.readiness_probe = readiness_probe
        self.instance_count = instance_count
        self._arm_type = ArmConstants.ONLINE_DEPLOYMENT_TYPE
        self.model_mount_path = model_mount_path
        self.instance_type = instance_type

    @property
    def provisioning_state(self) -> Optional[str]:
        """Deployment provisioning state, readonly

        :return: Deployment provisioning state.
        :rtype: Optional[str]
        """
        return self._provisioning_state

    def _generate_dependencies(self) -> Any:
        """Convert dependencies into ARM id or REST wrapper"""
        code = None

        if self.code_configuration:
            self.code_configuration._validate()
            code_id = (
                self.code_configuration.code
                if isinstance(self.code_configuration.code, str)
                else self.code_configuration.code.id
            )
            code = RestCodeConfiguration(code_id=code_id, scoring_script=self.code_configuration.scoring_script)

        model_id = None
        if self.model:
            model_id = self.model if isinstance(self.model, str) else self.model.id

        environment_id = None
        if self.environment:
            environment_id = self.environment if isinstance(self.environment, str) else self.environment.id

        return code, environment_id, model_id

    def _to_dict(self) -> Dict:
        pass

    @abstractmethod
    def _to_rest_object(self) -> RestOnlineDeploymentData:
        pass

    @classmethod
    def _from_rest_object(self, deployment: RestOnlineDeploymentData) -> RestOnlineDeploymentDetails:

        if deployment.properties.endpoint_compute_type == EndpointComputeType.KUBERNETES:
            return KubernetesOnlineDeployment._from_rest_object(deployment)
        elif deployment.properties.endpoint_compute_type == EndpointComputeType.MANAGED:
            return ManagedOnlineDeployment._from_rest_object(deployment)
        else:
            msg = f"Unsupported online endpoint type {deployment.properties.type}."
            raise DeploymentException(
                message=msg,
                target=ErrorTarget.ONLINE_DEPLOYMENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    def _get_arm_resource(self, **kwargs):
        resource = super(OnlineDeployment, self)._get_arm_resource(**kwargs)
        depends_on = []
        if self.environment and isinstance(self.environment, Environment):
            depends_on.append(f"{self.environment._arm_type}Deployment")
        if self.code_configuration and self.code_configuration.code and isinstance(self.code_configuration.code, Code):
            depends_on.append(f"{self.code_configuration.code._arm_type}Deployment")
        if self.model and isinstance(self.model, Model):
            depends_on.append(f"{self.model._arm_type}Deployment")
        resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = depends_on
        return resource

    def _get_arm_resource_and_params(self, **kwargs):
        resource_param_tuple_list = [(self._get_arm_resource(**kwargs), self._to_arm_resource_param(**kwargs))]
        if self.environment and isinstance(self.environment, Environment):
            resource_param_tuple_list.extend(self.environment._get_arm_resource_and_params())
        if self.code_configuration and self.code_configuration.code and isinstance(self.code_configuration.code, Code):
            resource_param_tuple_list.extend(self.code_configuration.code._get_arm_resource_and_params())
        if self.model and isinstance(self.model, Model):
            resource_param_tuple_list.extend(self.model._get_arm_resource_and_params())
        return resource_param_tuple_list

    def _validate_name(self) -> None:
        if self.name:
            validate_endpoint_or_deployment_name(self.name, is_deployment=True)

    def _merge_with(self, other: "OnlineDeployment") -> None:
        if other:
            if self.name != other.name:
                msg = "The deployment name: {} and {} are not matched when merging."
                raise ValidationException(
                    message=msg.format(self.name, other.name),
                    target=ErrorTarget.ONLINE_DEPLOYMENT,
                    no_personal_data_message=msg.format("[name1]", "[name2]"),
                    error_category=ErrorCategory.USER_ERROR,
                )
            super()._merge_with(other)
            self.app_insights_enabled = other.app_insights_enabled or self.app_insights_enabled
            # Adding noqa: Fix E721 do not compare types, use 'isinstance()'
            # isinstance will include checking for subclasses, which is explicitly undesired by a logic.
            if self.scale_settings and type(self.scale_settings) == type(other.scale_settings):  # noqa
                self.scale_settings._merge_with(other.scale_settings)
            else:
                self.scale_settings = other.scale_settings
            if self.request_settings:
                self.request_settings._merge_with(other.request_settings)
            else:
                self.request_settings = other.request_settings
            if self.liveness_probe:
                self.liveness_probe._merge_with(other.liveness_probe)
            else:
                self.liveness_probe = other.liveness_probe
            if self.readiness_probe:
                self.readiness_probe._merge_with(other.readiness_probe)
            else:
                self.readiness_probe = other.readiness_probe
            self.instance_count = other.instance_count or self.instance_count
            self.instance_type = other.instance_type or self.instance_type

    @classmethod
    def load(
        cls,
        path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "OnlineDeployment":
        params_override = params_override or []
        data = load_yaml(path)
        return OnlineDeployment.load_from_dict(data=data, path=path, params_override=params_override)

    @classmethod
    def load_from_dict(
        cls,
        data: dict,
        path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "OnlineDeployment":
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(path).parent if path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        deployment_type = data.get("type", None)

        if deployment_type == camel_to_snake(EndpointComputeType.KUBERNETES.value):
            return load_from_dict(KubernetesOnlineDeploymentSchema, data, context, **kwargs)

        return load_from_dict(ManagedOnlineDeploymentSchema, data, context, **kwargs)


class KubernetesOnlineDeployment(OnlineDeployment):
    """Kubernetes Online endpoint deployment entity

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: Dict[str, Any], optional
    :param description: Description of the resource.
    :type description: str, optional
    :param model: Model entity for the endpoint deployment, defaults to None
    :type model: Union[str, Model], optional
    :param code_configuration: defaults to None
    :type code_configuration: CodeConfiguration, optional
    :param environment: Environment entity for the endpoint deployment, defaults to None
    :type environment: Union[str, Environment], optional
    :param app_insights_enabled: defaults to False
    :type app_insights_enabled: bool, optional
    :param scale_settings: How the online deployment will scale.
    :type scale_settings: OnlineScaleSettings, optional
    :param request_settings: defaults to RequestSettings()
    :type request_settings: OnlineRequestSettings, optional
    :param liveness_probe: Liveness probe settings.
    :type liveness_probe: ProbeSettings, optional
    :param readiness_probe: Readiness probe settings.
    :type readiness_probe: ProbeSettings, optional
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict, optional
    :param resources: defaults to None
    :type resources: ResourceRequirementsSettings, optional
    :param instance_type: The instance type defined by K8S cluster admin.
    :type instance_type: str
    :param instance_count: The instance count used for this deployment.
    :type instance_count: int
    :param code_path: Folder path to local code assets. Equivalent to code_configuration.code.
    :type code_path: Union[str, PathLike], optional
    :param scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script.
    :type scoring_script: Union[str, PathLike], optional
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        description: str = None,
        model: Union[str, "Model"] = None,
        code_configuration: CodeConfiguration = None,
        environment: Union[str, "Environment"] = None,
        app_insights_enabled: bool = False,
        scale_settings: OnlineScaleSettings = None,
        request_settings: OnlineRequestSettings = None,
        liveness_probe: ProbeSettings = None,
        readiness_probe: ProbeSettings = None,
        environment_variables: Dict[str, str] = None,
        resources: ResourceRequirementsSettings = None,
        instance_count: int = None,
        instance_type: str = None,
        code_path: Union[str, PathLike] = None,  # promoted property from code_configuration.code
        scoring_script: Union[str, PathLike] = None,  # promoted property from code_configuration.scoring_script
        **kwargs,
    ):

        kwargs["type"] = EndpointComputeType.KUBERNETES.value
        super(KubernetesOnlineDeployment, self).__init__(
            name=name,
            endpoint_name=endpoint_name,
            tags=tags,
            properties=properties,
            description=description,
            model=model,
            code_configuration=code_configuration,
            environment=environment,
            environment_variables=environment_variables,
            instance_count=instance_count,
            instance_type=instance_type,
            app_insights_enabled=app_insights_enabled,
            scale_settings=scale_settings,
            request_settings=request_settings,
            liveness_probe=liveness_probe,
            readiness_probe=readiness_probe,
            code_path=code_path,
            scoring_script=scoring_script,
            **kwargs,
        )

        self.resources = resources

    def _to_dict(self) -> Dict:
        return KubernetesOnlineDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self, location: str) -> RestOnlineDeploymentData:
        self._validate()
        code, environment, model = self._generate_dependencies()

        properties = RestKubernetesOnlineDeployment(
            code_configuration=code,
            environment_id=environment,
            model=model,
            model_mount_path=self.model_mount_path,
            scale_settings=self.scale_settings._to_rest_object() if self.scale_settings else None,
            properties=self.properties,
            description=self.description,
            environment_variables=self.environment_variables,
            app_insights_enabled=self.app_insights_enabled,
            request_settings=self.request_settings._to_rest_object() if self.request_settings else None,
            liveness_probe=self.liveness_probe._to_rest_object() if self.liveness_probe else None,
            readiness_probe=self.readiness_probe._to_rest_object() if self.readiness_probe else None,
            container_resource_requirements=self.resources._to_rest_object() if self.resources else None,
            instance_type=self.instance_type if self.instance_type else None,
        )
        sku = RestSku(name="Default", capacity=self.instance_count)

        return RestOnlineDeploymentData(location=location, properties=properties, tags=self.tags, sku=sku)

    def _to_arm_resource_param(self, **kwargs):
        from azure.ai.ml.constants import ArmConstants

        rest_object = self._to_rest_object(**kwargs)
        properties = rest_object.properties
        sku = rest_object.sku
        tags = rest_object.tags

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "K8SOnlineDeployment"),
                ArmConstants.SKU: self._serialize.body(sku, "Sku"),
                ArmConstants.TAGS: tags,
            }
        }

    def _merge_with(self, other: "KubernetesOnlineDeployment") -> None:
        if other:
            super()._merge_with(other)
            if self.resources:
                self.resources._merge_with(other.resources)
            else:
                self.resources = other.resources

    def _validate(self) -> None:
        self._validate_name()

    @classmethod
    def _from_rest_object(self, resource: RestOnlineDeploymentData) -> "KubernetesOnlineDeployment":

        deployment = resource.properties

        code_config = (
            CodeConfiguration(
                code=deployment.code_configuration.code_id,
                scoring_script=deployment.code_configuration.scoring_script,
            )
            if deployment.code_configuration
            else None
        )

        entity = KubernetesOnlineDeployment(
            id=resource.id,
            name=resource.name,
            tags=resource.tags,
            properties=deployment.properties,
            description=deployment.description,
            request_settings=OnlineRequestSettings._from_rest_object(deployment.request_settings),
            model=deployment.model,
            code_configuration=code_config,
            environment=deployment.environment_id,
            resources=ResourceRequirementsSettings._from_rest_object(deployment.container_resource_requirements),
            app_insights_enabled=deployment.app_insights_enabled,
            scale_settings=OnlineScaleSettings._from_rest_object(deployment.scale_settings),
            liveness_probe=ProbeSettings._from_rest_object(deployment.liveness_probe),
            readiness_probe=ProbeSettings._from_rest_object(deployment.readiness_probe),
            environment_variables=deployment.environment_variables,
            endpoint_name=_parse_endpoint_name_from_deployment_id(resource.id),
            instance_count=resource.sku.capacity if resource.sku else None,
            instance_type=deployment.instance_type,
        )

        entity._provisioning_state = deployment.provisioning_state
        return entity


class ManagedOnlineDeployment(OnlineDeployment):
    """Managed Online endpoint deployment entity

    :param name: Name of the resource.
    :type name: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The asset property dictionary.
    :type properties: Dict[str, Any], optional
    :param description: Description of the resource.
    :type description: str, optional
    :param model: Model entity for the endpoint deployment, defaults to None
    :type model: Union[str, Model], optional
    :param code_configuration: defaults to None
    :type code_configuration: CodeConfiguration, optional
    :param environment: Environment entity for the endpoint deployment, defaults to None
    :type environment: Union[str, Environment], optional
    :param app_insights_enabled: defaults to False
    :type app_insights_enabled: bool, optional
    :param scale_settings: How the online deployment will scale.
    :type scale_settings: OnlineScaleSettings, optional
    :param request_settings: defaults to RequestSettings()
    :type request_settings: OnlineRequestSettings, optional
    :param liveness_probe: Liveness probe settings.
    :type liveness_probe: ProbeSettings, optional
    :param readiness_probe: Readiness probe settings.
    :type readiness_probe: ProbeSettings, optional
    :param environment_variables: Environment variables that will be set in deployment.
    :type environment_variables: dict, optional
    :param instance_type: Azure compute sku.
    :type instance_type: str
    :param instance_count: The instance count used for this deployment.
    :type instance_count: int
    :param code_path: Folder path to local code assets. Equivalent to code_configuration.code.
    :type code_path: Union[str, PathLike], optional
    :param scoring_script: Scoring script name. Equivalent to code_configuration.code.scoring_script.
    :type scoring_script: Union[str, PathLike], optional
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: str = None,
        tags: Dict[str, Any] = None,
        properties: Dict[str, Any] = None,
        description: str = None,
        model: Union[str, "Model"] = None,
        code_configuration: CodeConfiguration = None,
        environment: Union[str, "Environment"] = None,
        app_insights_enabled: bool = False,
        scale_settings: OnlineScaleSettings = None,
        request_settings: OnlineRequestSettings = None,
        liveness_probe: ProbeSettings = None,
        readiness_probe: ProbeSettings = None,
        environment_variables: Dict[str, str] = None,
        instance_type: str = None,
        instance_count: int = None,
        code_path: Union[str, PathLike] = None,  # promoted property from code_configuration.code
        scoring_script: Union[str, PathLike] = None,  # promoted property from code_configuration.scoring_script
        **kwargs,
    ):

        kwargs["type"] = EndpointComputeType.MANAGED.value

        self.private_network_connection = kwargs.pop("private_network_connection", None)
        self.egress_public_network_access = kwargs.pop("egress_public_network_access", None)

        super(ManagedOnlineDeployment, self).__init__(
            name=name,
            endpoint_name=endpoint_name,
            tags=tags,
            properties=properties,
            description=description,
            model=model,
            code_configuration=code_configuration,
            environment=environment,
            environment_variables=environment_variables,
            app_insights_enabled=app_insights_enabled,
            scale_settings=scale_settings,
            request_settings=request_settings,
            liveness_probe=liveness_probe,
            readiness_probe=readiness_probe,
            instance_count=instance_count,
            instance_type=instance_type,
            code_path=code_path,
            scoring_script=scoring_script,
            **kwargs,
        )

        self.readiness_probe = readiness_probe

    def _to_dict(self) -> Dict:
        return ManagedOnlineDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self, location: str) -> RestOnlineDeploymentData:
        self._validate()
        code, environment, model = self._generate_dependencies()

        properties = RestManagedOnlineDeployment(
            code_configuration=code,
            environment_id=environment,
            model=model,
            model_mount_path=self.model_mount_path,
            scale_settings=self.scale_settings._to_rest_object() if self.scale_settings else None,
            properties=self.properties,
            description=self.description,
            environment_variables=self.environment_variables,
            app_insights_enabled=self.app_insights_enabled,
            request_settings=self.request_settings._to_rest_object() if self.request_settings else None,
            liveness_probe=self.liveness_probe._to_rest_object() if self.liveness_probe else None,
            instance_type=self.instance_type,
            readiness_probe=self.readiness_probe._to_rest_object() if self.readiness_probe else None,
        )
        # TODO: SKU name is defaulted to value "Default" since service side requires it.
        #  Should be removed once service side defaults it.
        sku = RestSku(name="Default", capacity=self.instance_count)

        # mfe is expecting private network connection to be in both the attribute level
        # as well as in the properties dictionary.
        if hasattr(self, "private_network_connection") and self.private_network_connection:
            properties.private_network_connection = self.private_network_connection
            properties.properties["private-network-connection"] = self.private_network_connection
        if hasattr(self, "egress_public_network_access") and self.egress_public_network_access:
            properties.egress_public_network_access = self.egress_public_network_access
        return RestOnlineDeploymentData(location=location, properties=properties, tags=self.tags, sku=sku)

    def _to_arm_resource_param(self, **kwargs):
        from azure.ai.ml.constants import ArmConstants

        rest_object = self._to_rest_object(**kwargs)
        properties = rest_object.properties
        sku = rest_object.sku
        tags = rest_object.tags

        return {
            self._arm_type: {
                ArmConstants.NAME: self.name,
                ArmConstants.PROPERTIES_PARAMETER_NAME: self._serialize.body(properties, "ManagedOnlineDeployment"),
                ArmConstants.SKU: self._serialize.body(sku, "Sku"),
                ArmConstants.TAGS: tags,
            }
        }

    @classmethod
    def _from_rest_object(self, resource: RestOnlineDeploymentData) -> "ManagedOnlineDeployment":

        deployment = resource.properties

        code_config = (
            CodeConfiguration(
                code=deployment.code_configuration.code_id,
                scoring_script=deployment.code_configuration.scoring_script,
            )
            if deployment.code_configuration
            else None
        )

        entity = ManagedOnlineDeployment(
            id=resource.id,
            name=resource.name,
            tags=resource.tags,
            properties=deployment.properties,
            description=deployment.description,
            request_settings=OnlineRequestSettings._from_rest_object(deployment.request_settings),
            model=(deployment.model if deployment.model else None),
            code_configuration=code_config,
            environment=deployment.environment_id,
            app_insights_enabled=deployment.app_insights_enabled,
            scale_settings=OnlineScaleSettings._from_rest_object(deployment.scale_settings),
            liveness_probe=ProbeSettings._from_rest_object(deployment.liveness_probe),
            environment_variables=deployment.environment_variables,
            readiness_probe=ProbeSettings._from_rest_object(deployment.readiness_probe),
            instance_type=deployment.instance_type,
            endpoint_name=_parse_endpoint_name_from_deployment_id(resource.id),
            instance_count=resource.sku.capacity,
            private_network_connection=deployment.private_network_connection,
            egress_public_network_access=deployment.egress_public_network_access,
        )

        entity._provisioning_state = deployment.provisioning_state
        return entity

    def _merge_with(self, other: "ManagedOnlineDeployment") -> None:
        if other:
            super()._merge_with(other)
            self.instance_type = other.instance_type or self.instance_type

    def _validate(self) -> None:
        self._validate_name()
        self._validate_scale_settings()

    def _validate_scale_settings(self) -> None:
        if self.scale_settings:
            if not isinstance(self.scale_settings, DefaultScaleSettings):
                msg = "ManagedOnlineEndpoint supports DefaultScaleSettings only."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.ONLINE_DEPLOYMENT,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )
