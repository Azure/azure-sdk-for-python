# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from typing import Dict, Any, List, Tuple, Optional
from .arm_helper import get_template, deployment_message_mapping
from azure.ai.ml._utils.utils import snake_to_camel
from azure.ai.ml.entities import (
    OnlineDeployment,
    OnlineEndpoint,
)
from azure.ai.ml.entities._assets import Model, Code, Environment

from azure.ai.ml._restclient.v2021_10_01.models import (
    OnlineEndpointData,
    CodeVersionDetails,
    ModelVersionDetails,
    ResourceIdentity,
)
from azure.ai.ml._scope_dependent_operations import OperationsContainer, OperationScope
from azure.ai.ml.operations._operation_orchestrator import OperationOrchestrator
from azure.ai.ml.constants import ArmConstants, AzureMLResourceType
from azure.ai.ml._arm_deployments.online_endpoint_assets import OnlineEndpointAssets
from azure.ai.ml._utils.utils import initialize_logger_info

module_logger = logging.getLogger(__name__)


class OnlineDeploymentArmGenerator(object):
    def __init__(self, operation_container: OperationsContainer, operation_scope: OperationScope):
        self._all_operations = operation_container
        self._operation_scope = operation_scope
        self._orchestrator = OperationOrchestrator(
            operation_container=self._all_operations, operation_scope=self._operation_scope
        )

    def generate_online_deployment_template(
        self, workspace_name: str, location: str, deployment: OnlineDeployment
    ) -> Dict[str, Any]:
        # step1: Get base Template
        base_template = get_template(resource_type=ArmConstants.BASE_TYPE)

        resources_and_params = deployment._get_arm_resource_and_params(location=location)

        template_resources = []
        params = {}
        for resource, param in resources_and_params:
            template_resources.append(resource)
            self._add_param(param, params)

        template_params = self._get_template_params(params)

        self._add_common_params(template_params, location=location, workspaceName=workspace_name)

        template_params[ArmConstants.ENDPOINT_NAME_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type=ArmConstants.STRING, value=deployment.endpoint_name
        )

        base_template["parameters"] = template_params
        base_template["resources"] = template_resources

        return base_template, template_resources

    def _add_param(self, param, params):
        for pType, pValue in param.items():
            if pType in params.keys():
                params[pType] = params[pType].append(pValue)
            else:
                params[pType] = [pValue]

    def _get_template_params(self, params):
        template_params = {}
        for key, value in params.items():
            param = {"type": ArmConstants.ARRAY, "defaultValue": value}
            template_params[key] = param
        return template_params

    def _convert_to_template_param(self, params):
        template_param = {}
        for ptype, value in params.items():
            template_param[ptype] = {
                # TODO: How to identify if it should be array or object
                "type": ArmConstants.ARRAY,
                "defaultValue": value,
            }
        return template_param

    def _serialize_to_dict_code_versions(self, yaml_codes: List[Code]) -> List[Dict[str, Any]]:
        code_versions = []
        for code in yaml_codes:
            code_obj = {}
            code_obj[ArmConstants.NAME] = code.name
            code_obj[ArmConstants.VERSION] = code.version
            code_version = CodeVersionDetails(code_uri=code.path)
            code_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = code_version.serialize()
            if code_obj not in code_versions:
                code_versions.append(code_obj)
        return code_versions

    def _serialize_to_dict_model_versions(self, yaml_models: List[Model]) -> List[Dict[str, Any]]:
        model_versions = []
        for model in yaml_models:
            model_obj = {}
            model_obj[ArmConstants.NAME] = model.name
            model_obj[ArmConstants.VERSION] = model.version
            model_version = ModelVersionDetails(model_uri=model.path, properties=model.flavors)
            model_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = model_version.serialize()
            if model_obj not in model_versions:
                model_versions.append(model_obj)
        return model_versions

    def _serialize_to_dict_environments(self, yaml_environments: List[Environment]) -> List[Dict[str, Any]]:
        environments = []
        for environment in yaml_environments:
            environment_obj = {}
            environment_obj[ArmConstants.NAME] = environment.name
            environment_obj[ArmConstants.VERSION] = environment.version
            environment_rest_properties = environment._to_rest_object().properties
            env_properties = environment_rest_properties.serialize()
            environment_obj[ArmConstants.PROPERTIES_PARAMETER_NAME] = env_properties
            if environment_obj not in environments:
                environments.append(environment_obj)
        return environments

    def _serialize_online_endpoint_properties(self, endpoint: OnlineEndpoint, location: str) -> Dict[str, Any]:
        if endpoint:
            endpoint_rest = endpoint._to_rest_online_endpoint(location)
            if not endpoint_rest.properties.traffic:
                endpoint_rest.properties.traffic = {}
            return self._serialize_online_endpoint_rest_properties(endpoint_rest, endpoint.name)

    def _serialize_online_endpoint_properties_traffic_update(
        self, endpoint: OnlineEndpoint, location: str
    ) -> Optional[Dict[str, Any]]:
        if endpoint:
            endpoint_rest_traffic_update = endpoint._to_rest_online_endpoint_traffic_update(location)
            return self._serialize_online_endpoint_rest_properties(endpoint_rest_traffic_update, endpoint.name)

    def _serialize_online_endpoint_rest_properties(
        self, endpoint_resource: OnlineEndpointData, name: str
    ) -> Dict[str, Any]:
        return endpoint_resource.serialize()

    def _serialize_deployments(self, deployments: List[OnlineDeployment], location: str) -> List[Dict[str, Any]]:
        arm_deployments = []
        for deployment in deployments:
            deployment_rest = deployment._to_rest_object(location=location)
            deployment_arm_obj = deployment_rest.serialize()
            deployment_arm_obj[ArmConstants.NAME] = deployment.name
            arm_deployments.append(deployment_arm_obj)
        return arm_deployments

    def _serialize_to_dict_identity(self, identity: ResourceIdentity) -> Dict[str, Any]:
        if identity:
            if identity.type.lower() in ("system_assigned", "none"):
                identity = ResourceIdentity(type="SystemAssigned")
            else:
                if identity.user_assigned_identities:
                    ids = dict()
                    for id in identity.user_assigned_identities:
                        ids[id["resource_id"]] = {}
                    identity.user_assigned_identities = ids
                    identity.type = snake_to_camel(identity.type)
        else:
            identity = ResourceIdentity(type="SystemAssigned")  # If no identity provided this should be the default
        return identity.serialize()

    def _add_common_parameters(
        self, workspace_name: str, location: str, endpoint_assets: OnlineEndpointAssets, parameters: Dict[str, Any]
    ) -> None:
        parameters[ArmConstants.WORKSPACE_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type=ArmConstants.STRING, value=workspace_name
        )
        parameters[ArmConstants.LOCATION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type=ArmConstants.STRING, value=location
        )

        parameters[ArmConstants.ENDPOINT_NAME_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type=ArmConstants.STRING, value=endpoint_assets.endpoint_name
        )
        parameters[ArmConstants.ENDPOINT_CREATE_OR_UPDATE_PARAMETER_NAME] = self._serialize_to_dict_parameter(
            value_type=ArmConstants.STRING,
            value=ArmConstants.OPERATION_CREATE if endpoint_assets.is_create else ArmConstants.OPERATION_UPDATE,
        )

        if endpoint_assets.endpoint:
            identity = self._serialize_to_dict_identity(identity=endpoint_assets.endpoint.identity)
            parameters[ArmConstants.ENDPOINT_IDENTITY_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.OBJECT, value=identity
            )

            parameters[ArmConstants.ENDPOINT_TAGS_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.OBJECT, value=endpoint_assets.endpoint.tags
            )

    def _add_common_params(self, template_params, **kwargs):
        location = kwargs.pop(ArmConstants.LOCATION_PARAMETER_NAME, None)
        workspace = kwargs.pop(ArmConstants.WORKSPACE_PARAMETER_NAME, None)
        template_params.update(
            {
                ArmConstants.LOCATION_PARAMETER_NAME: {"defaultValue": location, "type": ArmConstants.STRING},
                ArmConstants.WORKSPACE_PARAMETER_NAME: {"defaultValue": workspace, "type": ArmConstants.STRING},
            }
        )

    def _generate_parameters(
        self, workspace_name: str, location: str, endpoint_assets: OnlineEndpointAssets
    ) -> Dict[str, Any]:
        parameters = {}
        self._add_common_parameters(
            workspace_name=workspace_name, location=location, endpoint_assets=endpoint_assets, parameters=parameters
        )

        code_versions = self._serialize_to_dict_code_versions(yaml_codes=endpoint_assets.codes)
        if code_versions:
            parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=code_versions
            )

        model_versions = self._serialize_to_dict_model_versions(yaml_models=endpoint_assets.models)
        if model_versions:
            parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=model_versions
            )

        environments = self._serialize_to_dict_environments(yaml_environments=endpoint_assets.environments)
        if environments:
            parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=environments
            )

        endpoint_properties = self._serialize_online_endpoint_properties(endpoint_assets.endpoint, location)
        if endpoint_properties:
            parameters[ArmConstants.ENDPOINT_PROPERTIES_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.OBJECT, value=endpoint_properties
            )

        endpoint = endpoint_assets.endpoint
        # There are two cases to generate the endpoint parameters.
        # 1. creation and endpoint exists and endpoint traffic exists.
        # 2. Update and endpoint exists.
        if endpoint and (not endpoint_assets.is_create or endpoint.traffic):
            endpoint_properties_traffic_update = self._serialize_online_endpoint_properties_traffic_update(
                endpoint_assets.endpoint, location
            )
            if endpoint_properties_traffic_update:
                parameters[
                    ArmConstants.ENDPOINT_PROPERTIES_TRAFFIC_UPDATE_PARAMETER_NAME
                ] = self._serialize_to_dict_parameter(
                    value_type=ArmConstants.OBJECT, value=endpoint_properties_traffic_update
                )

        deployments = self._serialize_deployments(endpoint_assets.deployments, location)
        if deployments:
            parameters[ArmConstants.DEPLOYMENTS_PARAMETER_NAME] = self._serialize_to_dict_parameter(
                value_type=ArmConstants.ARRAY, value=deployments
            )

        return parameters

    def _serialize_to_dict_parameter(self, value_type: str, value: Any) -> Dict[str, Any]:
        parameter = {}
        parameter["type"] = value_type
        parameter["defaultValue"] = value
        return parameter

    def _generate_resource(self, resource_data: List[Dict[str, Any]], resource_type: str) -> Dict[str, Any]:
        if resource_data:
            template = get_template(resource_type=resource_type)
            return template
        return {}

    def _generate_resources(
        self, parameters: Dict[str, Any], location: str, workspace_name: str
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        resources = []
        resources_being_deployed = {}

        # Add code version resource
        code_version_resource = None
        if ArmConstants.CODE_VERSION_PARAMETER_NAME in parameters:
            code_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME],
                resource_type=ArmConstants.CODE_VERSION_TYPE,
            )
            if code_version_resource:
                resources.append(code_version_resource)
                for item in parameters[ArmConstants.CODE_VERSION_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    code_name = item[ArmConstants.NAME]
                    code_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, code_name, code_version)] = (
                        deployment_message_mapping[ArmConstants.CODE_VERSION_TYPE].format(
                            f"{code_name}:{code_version}"
                        ),
                        None,
                    )

        # Add model resource
        model_resource = None
        if ArmConstants.MODEL_PARAMETER_NAME in parameters:
            model_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.MODEL_PARAMETER_NAME], resource_type=ArmConstants.MODEL_TYPE
            )
            if model_resource:
                resources.append(model_resource)
                for item in parameters[ArmConstants.MODEL_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    model_name = item[ArmConstants.NAME]
                    resources_being_deployed["{}/{}".format(workspace_name, model_name)] = (
                        deployment_message_mapping[ArmConstants.MODEL_TYPE].format(model_name),
                        None,
                    )

        # Add model version resource
        model_version_resource = None
        if ArmConstants.MODEL_VERSION_PARAMETER_NAME in parameters:
            model_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME],
                resource_type=ArmConstants.MODEL_VERSION_TYPE,
            )
            if model_version_resource:
                model_version_depends = []
                if model_resource:
                    model_version_depends.append(ArmConstants.MODEL_RESOURCE_NAME)
                model_version_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = model_version_depends
                resources.append(model_version_resource)
                for item in parameters[ArmConstants.MODEL_VERSION_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    model_name = item[ArmConstants.NAME]
                    model_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, model_name, model_version)] = (
                        deployment_message_mapping[ArmConstants.MODEL_VERSION_TYPE].format(
                            f"{model_name}:{model_version}"
                        ),
                        None,
                    )

        # Add environment resource
        environment_version_resource = None
        if ArmConstants.ENVIRONMENT_PARAMETER_NAME in parameters:
            environment_version_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME],
                resource_type=ArmConstants.ENVIRONMENT_VERSION_TYPE,
            )
            if environment_version_resource:
                resources.append(environment_version_resource)
                for item in parameters[ArmConstants.ENVIRONMENT_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    env_name = item[ArmConstants.NAME]
                    env_version = item[ArmConstants.VERSION]
                    resources_being_deployed["{}/{}/{}".format(workspace_name, env_name, env_version)] = (
                        deployment_message_mapping[ArmConstants.ENVIRONMENT_VERSION_TYPE].format(
                            f"{env_name}:{env_version}"
                        ),
                        None,
                    )

        # Add online endpoint resource
        endpoint_resource = None
        if ArmConstants.ENDPOINT_PROPERTIES_PARAMETER_NAME in parameters:
            endpoint_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.ENDPOINT_PROPERTIES_PARAMETER_NAME],
                resource_type=ArmConstants.ONLINE_ENDPOINT_TYPE,
            )
            if endpoint_resource:
                resources.append(endpoint_resource)
                endpoint_name = parameters[ArmConstants.ENDPOINT_NAME_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]
                resources_being_deployed["{}/{}".format(workspace_name, endpoint_name)] = (
                    deployment_message_mapping[ArmConstants.ONLINE_ENDPOINT_TYPE].format(endpoint_name),
                    None,
                )

        # Add online deployment resource
        deployment_resource = None
        if ArmConstants.DEPLOYMENTS_PARAMETER_NAME in parameters:
            deployment_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.DEPLOYMENTS_PARAMETER_NAME],
                resource_type=ArmConstants.ONLINE_DEPLOYMENT_TYPE,
            )
            if deployment_resource:
                deployment_depends = []
                if endpoint_resource:
                    deployment_depends.append(ArmConstants.ONLINE_ENDPOINT_RESOURCE_NAME)
                if code_version_resource:
                    deployment_depends.append(ArmConstants.CODE_VERSION_RESOURCE_NAME)
                if model_version_resource:
                    deployment_depends.append(ArmConstants.MODEL_VERSION_RESOURCE_NAME)
                if environment_version_resource:
                    deployment_depends.append(ArmConstants.ENVIRONMENT_VERSION_RESOURCE_NAME)
                deployment_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = deployment_depends
                resources.append(deployment_resource)
                endpoint_name = parameters[ArmConstants.ENDPOINT_NAME_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]
                for item in parameters[ArmConstants.DEPLOYMENTS_PARAMETER_NAME][ArmConstants.DEFAULT_VALUE]:
                    resources_being_deployed[
                        "{}/{}/{}".format(workspace_name, endpoint_name, item[ArmConstants.NAME])
                    ] = (
                        deployment_message_mapping[ArmConstants.ONLINE_DEPLOYMENT_TYPE].format(item[ArmConstants.NAME]),
                        None,
                    )

        # Update endpoint Traffic resource
        if ArmConstants.ENDPOINT_PROPERTIES_TRAFFIC_UPDATE_PARAMETER_NAME in parameters:
            update_traffic_resource = self._generate_resource(
                resource_data=parameters[ArmConstants.ENDPOINT_PROPERTIES_TRAFFIC_UPDATE_PARAMETER_NAME],
                resource_type=ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE,
            )
            if update_traffic_resource:
                update_depends = []
                if deployment_resource:
                    update_depends.append(ArmConstants.ONLINE_DEPLOYMENT_RESOURCE_NAME)
                update_traffic_resource[ArmConstants.DEPENDSON_PARAMETER_NAME] = update_depends
                resources.append(update_traffic_resource)
                update_traffic_resource_name = "{}{}{}".format(ArmConstants.UPDATE_RESOURCE_NAME, "-", endpoint_name)
                resources_being_deployed[update_traffic_resource_name] = (
                    deployment_message_mapping[ArmConstants.UPDATE_ONLINE_ENDPOINT_TYPE],
                    None,
                )

        return resources, resources_being_deployed

    def _get_settings(self, online_deployment: OnlineDeployment) -> OnlineEndpointAssets:
        # endpoint create/update. For creation, the old_endpoint is None
        all_assets = OnlineEndpointAssets()
        all_assets.add_online_deployment(online_deployment)
        return all_assets
