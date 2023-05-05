# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access,no-member,arguments-renamed,unidiomatic-typecheck

import logging
import os
import typing
from abc import abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import CodeConfiguration as RestCodeConfiguration
from azure.ai.ml._restclient.v2023_04_01_preview.models import EndpointComputeType
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    KubernetesOnlineDeployment as RestKubernetesOnlineDeployment,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import ManagedOnlineDeployment as RestManagedOnlineDeployment
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineDeployment as RestOnlineDeploymentData
from azure.ai.ml._restclient.v2023_04_01_preview.models import OnlineDeploymentProperties as RestOnlineDeploymentDetails
from azure.ai.ml._restclient.v2023_04_01_preview.models import Sku as RestSku
from azure.ai.ml._schema._deployment.online.online_deployment import (
    KubernetesOnlineDeploymentSchema,
    ManagedOnlineDeploymentSchema,
)
from azure.ai.ml._utils._arm_id_utils import _parse_endpoint_name_from_deployment_id
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY, TYPE, ArmConstants
from azure.ai.ml.constants._endpoint import EndpointYamlFields
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._assets._artifacts.model import Model
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._deployment.code_configuration import CodeConfiguration
from azure.ai.ml.entities._deployment.data_collector import DataCollector
from azure.ai.ml.entities._deployment.deployment_settings import OnlineRequestSettings, ProbeSettings
from azure.ai.ml.entities._deployment.resource_requirements_settings import ResourceRequirementsSettings
from azure.ai.ml.entities._deployment.scale_settings import (
    DefaultScaleSettings,
    OnlineScaleSettings,
    TargetUtilizationScaleSettings,
)
from azure.ai.ml.entities._endpoint._endpoint_helpers import validate_endpoint_or_deployment_name
from azure.ai.ml.entities._util import load_from_dict
from azure.ai.ml.exceptions import (
    DeploymentException,
    ErrorCategory,
    ErrorTarget,
    ValidationErrorType,
    ValidationException,
)

from .deployment import Deployment

module_logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class OnlineDeployment(Deployment):
    """Online endpoint deployment entity.

    :param name: Name of the deployment resource.
    :type name: str
    :keyword endpoint_name: Name of the endpoint resource, defaults to None
    :paramtype endpoint_name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword description: Description of the resource, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword model: Model entity for the endpoint deployment, defaults to None
    :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
    :keyword data_collector: Data Collector entity for the endpoint deployment, defaults to None
    :paramtype data_collector: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.DataCollector]]
    :keyword code_configuration: Code Configuration, defaults to None
    :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
    :keyword environment: Environment entity for the endpoint deployment, defaults to None
    :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword app_insights_enabled: Is appinsights enabled, defaults to False
    :paramtype app_insights_enabled: typing.Optional[bool]
    :keyword scale_settings: How the online deployment will scale, defaults to None
    :paramtype scale_settings: typing.Optional[~azure.ai.ml.entities.OnlineScaleSettings]
    :keyword request_settings: Online Request Settings, defaults to None
    :paramtype request_settings: typing.Optional[~azure.ai.ml.entities.OnlineRequestSettings]
    :keyword liveness_probe: Liveness probe settings, defaults to None
    :paramtype liveness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword readiness_probe: Readiness probe settings, defaults to None
    :paramtype readiness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
    :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
    :keyword instance_count: The instance count used for this deployment, defaults to None
    :paramtype instance_count: typing.Optional[int]
    :keyword instance_type: Azure compute sku, defaults to None
    :paramtype instance_type: typing.Optional[str]
    :keyword model_mount_path: The path to mount the model in custom container, defaults to None
    :paramtype model_mount_path: typing.Optional[str]
    :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
        , defaults to None
    :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
    :keyword scoring_script: Equivalent to code_configuration.code.scoring_script.
        Will be ignored if code_configuration is present, defaults to None
    :paramtype scoring_script: typing.Optional[typing.Union[str, os.PathLike]]
    """

    def __init__(
        self,
        name: str,
        *,
        endpoint_name: Optional[str] = None,
        tags: Optional[Dict[str, typing.Any]] = None,
        properties: Optional[Dict[str, typing.Any]] = None,
        description: Optional[str] = None,
        model: Optional[Union[str, "Model"]] = None,
        data_collector: Optional[DataCollector] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        environment: Optional[Union[str, "Environment"]] = None,
        app_insights_enabled: Optional[bool] = False,
        scale_settings: Optional[OnlineScaleSettings] = None,
        request_settings: Optional[OnlineRequestSettings] = None,
        liveness_probe: Optional[ProbeSettings] = None,
        readiness_probe: Optional[ProbeSettings] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        instance_count: Optional[int] = None,
        instance_type: Optional[str] = None,
        model_mount_path: Optional[str] = None,
        code_path: Optional[Union[str, os.PathLike]] = None,  # promoted property from code_configuration.code
        scoring_script: Optional[Union[str, os.PathLike]] = None,  # promoted property code_configuration.scoring_script
        **kwargs: typing.Any,
    ):
        """Online endpoint deployment entity.

        Constructor for Online endpoint deployment entity

        :param name: Name of the deployment resource.
        :type name: str
        :keyword endpoint_name: Name of the endpoint resource, defaults to None
        :paramtype endpoint_name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated, defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword description: Description of the resource, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword model: Model entity for the endpoint deployment, defaults to None
        :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
        :keyword code_configuration: Code Configuration, defaults to None
        :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
        :keyword environment: Environment entity for the endpoint deployment, defaults to None
        :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
        :keyword app_insights_enabled: Is appinsights enabled, defaults to False
        :paramtype app_insights_enabled: typing.Optional[bool]
        :keyword scale_settings: How the online deployment will scale, defaults to None
        :paramtype scale_settings: typing.Optional[~azure.ai.ml.entities.OnlineScaleSettings]
        :keyword request_settings: Online Request Settings, defaults to None
        :paramtype request_settings: typing.Optional[OnlineRequestSettings]
        :keyword liveness_probe: Liveness probe settings, defaults to None
        :paramtype liveness_probe: typing.Optional[ProbeSettings]
        :keyword readiness_probe: Readiness probe settings, defaults to None
        :paramtype readiness_probe: typing.Optional[ProbeSettings]
        :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
        :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
        :keyword instance_count: The instance count used for this deployment, defaults to None
        :paramtype instance_count: typing.Optional[int]
        :keyword instance_type: Azure compute sku, defaults to None
        :paramtype instance_type: typing.Optional[str]
        :keyword model_mount_path: The path to mount the model in custom container, defaults to None
        :paramtype model_mount_path: typing.Optional[str]
        :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
            , defaults to None
        :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
        :keyword scoring_script: Equivalent to code_configuration.code.scoring_script.
            Will be ignored if code_configuration is present, defaults to None
        :paramtype scoring_script: typing.Optional[typing.Union[str, os.PathLike]]
        """
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
        self.data_collector = data_collector

    @property
    def provisioning_state(self) -> Optional[str]:
        """Deployment provisioning state, readonly.

        :return: Deployment provisioning state.
        :rtype: typing.Optional[str]
        """
        return self._provisioning_state

    def _generate_dependencies(self) -> typing.Any:
        """Convert dependencies into ARM id or REST wrapper."""
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

    def _to_arm_resource_param(self, **kwargs):
        pass

    @abstractmethod
    def _to_rest_object(self) -> RestOnlineDeploymentData:
        pass

    @classmethod
    def _from_rest_object(cls, deployment: RestOnlineDeploymentData) -> RestOnlineDeploymentDetails:
        if deployment.properties.endpoint_compute_type == EndpointComputeType.KUBERNETES:
            return KubernetesOnlineDeployment._from_rest_object(deployment)
        if deployment.properties.endpoint_compute_type == EndpointComputeType.MANAGED:
            return ManagedOnlineDeployment._from_rest_object(deployment)

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
                    error_type=ValidationErrorType.INVALID_VALUE,
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
    def _set_scale_settings(cls, data: dict):
        if not hasattr(data, EndpointYamlFields.SCALE_SETTINGS):
            return

        scale_settings = data[EndpointYamlFields.SCALE_SETTINGS]
        keyName = TYPE
        if scale_settings and scale_settings[keyName] == "default":
            scale_copy = scale_settings.copy()
            for key in scale_copy:
                if key != keyName:
                    scale_settings.pop(key, None)

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[os.PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "OnlineDeployment":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path.cwd(),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        deployment_type = data.get("type", None)

        if deployment_type == camel_to_snake(EndpointComputeType.KUBERNETES.value):
            return load_from_dict(KubernetesOnlineDeploymentSchema, data, context, **kwargs)

        return load_from_dict(ManagedOnlineDeploymentSchema, data, context, **kwargs)


class KubernetesOnlineDeployment(OnlineDeployment):
    """Kubernetes Online endpoint deployment entity.

    :keyword name: Name of the deployment resource.
    :paramtype name: str
    :keyword endpoint_name: Name of the endpoint resource, defaults to None
    :paramtype endpoint_name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated., defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword description: Description of the resource, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword model: Model entity for the endpoint deployment, defaults to None
    :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
    :keyword code_configuration: Code Configuration, defaults to None
    :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
    :keyword environment: Environment entity for the endpoint deployment, defaults to None
    :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword app_insights_enabled: Is appinsights enabled, defaults to False
    :paramtype app_insights_enabled: bool
    :keyword scale_settings: How the online deployment will scale, defaults to None
    :paramtype scale_settings: typing.Optional[typing.Union[~azure.ai.ml.entities.DefaultScaleSettings
        , ~azure.ai.ml.entities.TargetUtilizationScaleSettings]]
    :keyword request_settings: Online Request Settings, defaults to None
    :paramtype request_settings: typing.Optional[OnlineRequestSettings]
    :keyword liveness_probe: Liveness probe settings, defaults to None
    :paramtype liveness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword readiness_probe: Readiness probe settings, defaults to None
    :paramtype readiness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
    :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
    :keyword resources: Resource requirements settings, defaults to None
    :paramtype resources: typing.Optional[~azure.ai.ml.entities.ResourceRequirementsSettings]
    :keyword instance_count: The instance count used for this deployment, defaults to None
    :paramtype instance_count: typing.Optional[int]
    :keyword instance_type: The instance type defined by K8S cluster admin, defaults to None
    :paramtype instance_type: typing.Optional[str]
    :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
        , defaults to None
    :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
    :keyword scoring_script: Equivalent to code_configuration.code.scoring_script.
        Will be ignored if code_configuration is present, defaults to None
    :paramtype scoring_script: typing.Optional[typing.Union[str, os.PathLike]]
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: Optional[str] = None,
        tags: Optional[Dict[str, typing.Any]] = None,
        properties: Optional[Dict[str, typing.Any]] = None,
        description: Optional[str] = None,
        model: Optional[Union[str, "Model"]] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        environment: Optional[Union[str, "Environment"]] = None,
        app_insights_enabled: bool = False,
        scale_settings: Optional[Union[DefaultScaleSettings, TargetUtilizationScaleSettings]] = None,
        request_settings: Optional[OnlineRequestSettings] = None,
        liveness_probe: Optional[ProbeSettings] = None,
        readiness_probe: Optional[ProbeSettings] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        resources: Optional[ResourceRequirementsSettings] = None,
        instance_count: Optional[int] = None,
        instance_type: Optional[str] = None,
        code_path: Optional[Union[str, os.PathLike]] = None,  # promoted property from code_configuration.code
        scoring_script: Optional[
            Union[str, os.PathLike]
        ] = None,  # promoted property from code_configuration.scoring_script
        **kwargs,
    ):
        """Kubernetes Online endpoint deployment entity.

        Constructor for Kubernetes Online endpoint deployment entity.

        :keyword name: Name of the deployment resource.
        :paramtype name: str
        :keyword endpoint_name: Name of the endpoint resource, defaults to None
        :paramtype endpoint_name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated., defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword description: Description of the resource, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword model: Model entity for the endpoint deployment, defaults to None
        :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
        :keyword code_configuration: Code Configuration, defaults to None
        :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
        :keyword environment: Environment entity for the endpoint deployment, defaults to None
        :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
        :keyword app_insights_enabled: Is appinsights enabled, defaults to False
        :paramtype app_insights_enabled: bool
        :keyword scale_settings: How the online deployment will scale, defaults to None
        :paramtype scale_settings: typing.Optional[typing.Union[~azure.ai.ml.entities.DefaultScaleSettings
            , ~azure.ai.ml.entities.TargetUtilizationScaleSettings]]
        :keyword request_settings: Online Request Settings, defaults to None
        :paramtype request_settings: typing.Optional[~azure.ai.ml.entities.OnlineRequestSettings]
        :keyword liveness_probe: Liveness probe settings, defaults to None
        :paramtype liveness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
        :keyword readiness_probe: Readiness probe settings, defaults to None
        :paramtype readiness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
        :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
        :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
        :keyword resources: Resource requirements settings, defaults to None
        :paramtype resources: typing.Optional[~azure.ai.ml.entities.ResourceRequirementsSettings]
        :keyword instance_count: The instance count used for this deployment, defaults to None
        :paramtype instance_count: typing.Optional[int]
        :keyword instance_type: The instance type defined by K8S cluster admin, defaults to None
        :paramtype instance_type: typing.Optional[str]
        :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
            , defaults to None
        :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
        :keyword scoring_script: Equivalent to code_configuration.code.scoring_script.
            Will be ignored if code_configuration is present, defaults to None
        :paramtype scoring_script: typing.Optional[typing.Union[str, os.PathLike]]
        """

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

    def _to_rest_object(self, location: str) -> RestOnlineDeploymentData:  # pylint: disable=arguments-differ
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
            data_collector=self.data_collector._to_rest_object() if self.data_collector else None,
        )
        sku = RestSku(name="Default", capacity=self.instance_count)

        return RestOnlineDeploymentData(location=location, properties=properties, tags=self.tags, sku=sku)

    def _to_arm_resource_param(self, **kwargs):
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
    def _from_rest_object(cls, resource: RestOnlineDeploymentData) -> "KubernetesOnlineDeployment":
        deployment = resource.properties

        code_config = (
            CodeConfiguration(
                code=deployment.code_configuration.code_id,
                scoring_script=deployment.code_configuration.scoring_script,
            )
            if deployment.code_configuration
            else None
        )

        return KubernetesOnlineDeployment(
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
            data_collector=DataCollector._from_rest_object(deployment.data_collector)
            if hasattr(deployment, "data_collector") and deployment.data_collector
            else None,
        )


class ManagedOnlineDeployment(OnlineDeployment):
    """Managed Online endpoint deployment entity.

    :keyword name: Name of the deployment resource
    :paramtype name: str
    :keyword endpoint_name: Name of the endpoint resource, defaults to None
    :paramtype endpoint_name: typing.Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated., defaults to None
    :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword properties: The asset property dictionary, defaults to None
    :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
    :keyword description: Description of the resource, defaults to None
    :paramtype description: typing.Optional[str]
    :keyword model: Model entity for the endpoint deployment, defaults to None
    :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
    :keyword code_configuration: Code Configuration, defaults to None
    :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
    :keyword environment: Environment entity for the endpoint deployment, defaults to None
    :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword app_insights_enabled: Is appinsights enabled, defaults to False
    :paramtype app_insights_enabled: bool
    :keyword scale_settings: How the online deployment will scale, defaults to None
    :paramtype scale_settings: typing.Optional[typing.Union[~azure.ai.ml.entities.DefaultScaleSettings
        , ~azure.ai.ml.entities.TargetUtilizationScaleSettings]]
    :keyword request_settings: Online Request Settings, defaults to None
    :paramtype request_settings: typing.Optional[OnlineRequestSettings]
    :keyword liveness_probe: Liveness probe settings, defaults to None
    :paramtype liveness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword readiness_probe: Readiness probe settings, defaults to None
    :paramtype readiness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
    :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
    :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
    :keyword instance_type: Azure compute sku, defaults to None
    :paramtype instance_type: typing.Optional[str]
    :keyword instance_count: The instance count used for this deployment, defaults to None
    :paramtype instance_count: typing.Optional[int]
    :keyword egress_public_network_access: Whether to restrict communication between a deployment and the
         Azure resources used to by the deployment. Allowed values are: "enabled", "disabled", defaults to None
    :paramtype egress_public_network_access: typing.Optional[str]
    :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
        , defaults to None
    :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
    :keyword scoring_script_path: Equivalent to code_configuration.scoring_script, will be ignored if
        code_configuration is present, defaults to None
    :paramtype scoring_script_path: typing.Optional[typing.Union[str, os.PathLike]]
    :keyword data_collector: Data collector, defaults to None
    :paramtype data_collectors: typing.Optional[typing.List[~azure.ai.ml.entities.DataCollector]]
    """

    def __init__(
        self,
        *,
        name: str,
        endpoint_name: Optional[str] = None,
        tags: Optional[Dict[str, typing.Any]] = None,
        properties: Optional[Dict[str, typing.Any]] = None,
        description: Optional[str] = None,
        model: Optional[Union[str, "Model"]] = None,
        code_configuration: Optional[CodeConfiguration] = None,
        environment: Optional[Union[str, "Environment"]] = None,
        app_insights_enabled: bool = False,
        scale_settings: Optional[Union[DefaultScaleSettings, TargetUtilizationScaleSettings]] = None,
        request_settings: Optional[OnlineRequestSettings] = None,
        liveness_probe: Optional[ProbeSettings] = None,
        readiness_probe: Optional[ProbeSettings] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        instance_type: Optional[str] = None,
        instance_count: Optional[int] = None,
        egress_public_network_access: Optional[str] = None,
        code_path: Optional[Union[str, os.PathLike]] = None,  # promoted property from code_configuration.code
        scoring_script: Optional[
            Union[str, os.PathLike]
        ] = None,  # promoted property from code_configuration.scoring_script
        data_collector: Optional[DataCollector] = None,
        **kwargs,
    ):
        """Managed Online endpoint deployment entity.

        Constructor for Managed Online endpoint deployment entity.

        :keyword name: Name of the deployment resource
        :paramtype name: str
        :keyword endpoint_name: Name of the endpoint resource, defaults to None
        :paramtype endpoint_name: typing.Optional[str]
        :keyword tags: Tag dictionary. Tags can be added, removed, and updated., defaults to None
        :paramtype tags: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword properties: The asset property dictionary, defaults to None
        :paramtype properties: typing.Optional[typing.Dict[str, typing.Any]]
        :keyword description: Description of the resource, defaults to None
        :paramtype description: typing.Optional[str]
        :keyword model: Model entity for the endpoint deployment, defaults to None
        :paramtype model: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Model]]
        :keyword code_configuration: Code Configuration, defaults to None
        :paramtype code_configuration: typing.Optional[~azure.ai.ml.entities.CodeConfiguration]
        :keyword environment: Environment entity for the endpoint deployment, defaults to None
        :paramtype environment: typing.Optional[typing.Union[str, ~azure.ai.ml.entities.Environment]]
        :keyword app_insights_enabled: Is appinsights enabled, defaults to False
        :paramtype app_insights_enabled: bool
        :keyword scale_settings: How the online deployment will scale, defaults to None
        :paramtype scale_settings: typing.Optional[typing.Union[~azure.ai.ml.entities.DefaultScaleSettings
            , ~azure.ai.ml.entities.TargetUtilizationScaleSettings]]
        :keyword request_settings: Online Request Settings, defaults to None
        :paramtype request_settings: typing.Optional[~azure.ai.ml.entities.OnlineRequestSettings]
        :keyword liveness_probe: Liveness probe settings, defaults to None
        :paramtype liveness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
        :keyword readiness_probe: Readiness probe settings, defaults to None
        :paramtype readiness_probe: typing.Optional[~azure.ai.ml.entities.ProbeSettings]
        :keyword environment_variables: Environment variables that will be set in deployment, defaults to None
        :paramtype environment_variables: typing.Optional[typing.Dict[str, str]]
        :keyword instance_type: Azure compute sku, defaults to None
        :paramtype instance_type: typing.Optional[str]
        :keyword instance_count: The instance count used for this deployment, defaults to None
        :paramtype instance_count: typing.Optional[int]
        :keyword egress_public_network_access: Whether to restrict communication between a deployment and the
            Azure resources used to by the deployment. Allowed values are: "enabled", "disabled", defaults to None
        :paramtype egress_public_network_access: typing.Optional[str]
        :keyword code_path: Equivalent to code_configuration.code, will be ignored if code_configuration is present
            , defaults to None
        :paramtype code_path: typing.Optional[typing.Union[str, os.PathLike]]
        """
        kwargs["type"] = EndpointComputeType.MANAGED.value
        self.private_network_connection = kwargs.pop("private_network_connection", None)

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
            data_collector=data_collector,
            **kwargs,
        )

        self.readiness_probe = readiness_probe
        self.egress_public_network_access = egress_public_network_access

    def _to_dict(self) -> Dict:
        return ManagedOnlineDeploymentSchema(context={BASE_PATH_CONTEXT_KEY: "./"}).dump(self)

    def _to_rest_object(self, location: str) -> RestOnlineDeploymentData:  # pylint: disable=arguments-differ
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
            data_collector=self.data_collector._to_rest_object() if self.data_collector else None,
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
    def _from_rest_object(cls, resource: RestOnlineDeploymentData) -> "ManagedOnlineDeployment":
        deployment = resource.properties

        code_config = (
            CodeConfiguration(
                code=deployment.code_configuration.code_id,
                scoring_script=deployment.code_configuration.scoring_script,
            )
            if deployment.code_configuration
            else None
        )

        return ManagedOnlineDeployment(
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
            private_network_connection=deployment.private_network_connection
            if hasattr(deployment, "private_network_connection")
            else None,
            egress_public_network_access=deployment.egress_public_network_access,
            data_collector=DataCollector._from_rest_object(deployment.data_collector)
            if hasattr(deployment, "data_collector") and deployment.data_collector
            else None,
        )

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
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
