# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=broad-exception-caught,protected-access,f-string-without-interpolation
# pylint: disable=too-many-locals,docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=no-else-return,too-many-statements

from typing import Any, Dict, Iterable, Optional, cast

# cspell:disable-next-line
from azure.ai.ml._restclient.azure_ai_assets_v2024_04_01.azureaiassetsv20240401 import (
    MachineLearningServicesClient as AzureAiAssetsClient,
)
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_telemetry_mixin
from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import DeploymentTemplate
from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace

ops_logger = OpsLogger(__name__)
module_logger = ops_logger.module_logger


class DeploymentTemplateOperations(_ScopeDependentOperations):
    """DeploymentTemplateOperations.

    You should not instantiate this class directly. Instead, you should
    create an MLClient instance that instantiates it for you and
    attaches it as an attribute.
    """

    def __init__(
        self,
        operation_scope: OperationScope,
        operation_config: "OperationConfig",
        credential: TokenCredential,
        **kwargs: Dict[str, Any],
    ):
        super(DeploymentTemplateOperations, self).__init__(operation_scope, operation_config)
        self._operation_scope = operation_scope
        self._operation_config = operation_config
        self._credential = credential
        self._service_client_kwargs: Dict[str, Any] = kwargs.pop("_service_client_kwargs", {})
        self._init_kwargs = kwargs
        self.__service_client: Optional[AzureAiAssetsClient] = None

    @property
    def _service_client(self) -> AzureAiAssetsClient:
        """Lazily instantiated client for azure ai assets API.

        The client is created on first access since the endpoint depends on the registry region.
        """
        if self.__service_client is None:
            endpoint = self._get_registry_endpoint()
            # Only pass through kwargs that the TypeSpec-generated AzureAiAssetsClient
            # can handle. MLClient injects kwargs like 'cloud', 'credential_scopes',
            # 'client_request_id', 'request_id' which break the client's HTTP pipeline
            # when passed through to its policies.
            _allowed_kwargs = ("user_agent", "logging_enable")
            client_kwargs = {k: v for k, v in self._service_client_kwargs.items() if k in _allowed_kwargs}
            self.__service_client = AzureAiAssetsClient(
                endpoint=endpoint,
                subscription_id=self._operation_scope.subscription_id,
                resource_group_name=self._operation_scope.resource_group_name,
                credential=self._credential,
                **client_kwargs,
            )
        return self.__service_client

    def _get_registry_endpoint(self) -> str:
        """Dynamically determine the registry endpoint based on registry region.

        Uses the registry discovery API (which does not require ARM access to the
        registry's subscription) to resolve the primary region, then constructs the
        appropriate dataplane endpoint.

        :return: The API endpoint URL for the registry
        :rtype: str
        """
        try:
            from azure.ai.ml._azure_environments import (
                _get_default_cloud_name,
                _get_registry_discovery_endpoint_from_metadata,
            )
            from azure.ai.ml._restclient.registry_discovery import (
                RegistryDiscoveryClient as ServiceClientRegistryDiscovery,
            )

            if self._credential and self._operation_scope.registry_name:
                # Use registry discovery API to get the primary region
                discovery_base_url = _get_registry_discovery_endpoint_from_metadata(_get_default_cloud_name())
                discovery_client = ServiceClientRegistryDiscovery(
                    credential=self._credential, base_url=discovery_base_url
                )
                response = discovery_client.registry_management_non_workspace.get_registry_management_non_workspace(
                    self._operation_scope.registry_name
                )

                if response.primary_region:
                    return f"https://{response.primary_region}.api.azureml.ms"

        except Exception as e:
            module_logger.debug("Could not determine registry region dynamically: %s. Using default.", e)

        # Fallback to default region if unable to determine dynamically
        return "https://eastus.api.azureml.ms"

    def _convert_dict_to_deployment_template(self, dict_data: Dict[str, Any]) -> DeploymentTemplate:
        """Convert dictionary format to DeploymentTemplate object.

        This helper method converts a user-provided dictionary to a DeploymentTemplate object
        using the constructor directly. It handles field name variations and type conversions.

        :param dict_data: Dictionary containing deployment template data
        :type dict_data: Dict[str, Any]
        :return: DeploymentTemplate object
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        """
        # Create a copy to avoid modifying the original
        data = dict_data.copy()

        # Handle field name variations (both snake_case and camelCase should work)
        def get_field_value(data: dict, primary_name: str, alt_name: str = None, default=None):  # type: ignore
            """Get field value, trying both primary and alternative names."""
            if primary_name in data:
                return data[primary_name]
            elif alt_name and alt_name in data:
                return data[alt_name]
            return default

        # Extract constructor parameters with field name mappings
        name = data.get("name")
        version = data.get("version")
        description = data.get("description")
        tags = data.get("tags")

        # Validate required fields
        if not name:
            raise ValueError("name is required")
        if not version:
            raise ValueError("version is required")

        # Handle environment field - check multiple possible names
        environment = (
            data.get("environment") or data.get("environment_id") or data.get("environmentId")
        )  # Also check camelCase REST API format
        if not environment:
            raise ValueError("environment is required but was not found in the data")

        # Handle field name variations for constructor parameters
        allowed_instance_types = get_field_value(data, "allowed_instance_types", "allowedInstanceTypes")

        default_instance_type = get_field_value(data, "default_instance_type", "defaultInstanceType")
        deployment_template_type = get_field_value(data, "deployment_template_type", "deploymentTemplateType")
        model_mount_path = get_field_value(data, "model_mount_path", "modelMountPath")
        scoring_path = get_field_value(data, "scoring_path", "scoringPath")
        scoring_port = get_field_value(data, "scoring_port", "scoringPort")
        if scoring_port is not None and isinstance(scoring_port, str):
            try:
                scoring_port = int(scoring_port)
            except (ValueError, TypeError):
                scoring_port = None

        instance_count = get_field_value(data, "instance_count", "instanceCount")
        if instance_count is not None and isinstance(instance_count, str):
            try:
                instance_count = int(instance_count)
            except (ValueError, TypeError):
                instance_count = None

        environment_variables = get_field_value(data, "environment_variables", "environmentVariables")

        # Handle request settings
        request_settings_data = get_field_value(data, "request_settings", "requestSettings")
        request_settings = None
        if request_settings_data and isinstance(request_settings_data, dict):
            from azure.ai.ml.entities._deployment.deployment_template_settings import OnlineRequestSettings

            # Handle field name variations in request settings
            timeout = get_field_value(request_settings_data, "request_timeout_ms", "requestTimeout")
            # Also check for 'request_timeout' as an alternative name
            if timeout is None:
                timeout = request_settings_data.get("request_timeout")
            max_concurrent = get_field_value(
                request_settings_data, "max_concurrent_requests_per_instance", "maxConcurrentRequestsPerInstance"
            )

            # Convert string values to integers if needed
            if timeout is not None and isinstance(timeout, str):
                try:
                    timeout = int(timeout)
                except (ValueError, TypeError):
                    timeout = None

            if max_concurrent is not None and isinstance(max_concurrent, str):
                try:
                    max_concurrent = int(max_concurrent)
                except (ValueError, TypeError):
                    max_concurrent = None

            request_settings = OnlineRequestSettings(
                request_timeout_ms=timeout, max_concurrent_requests_per_instance=max_concurrent
            )

        # Handle probe settings
        def create_probe_settings(probe_data):
            if not probe_data or not isinstance(probe_data, dict):
                return None
            from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings

            # Helper function to convert string values to integers
            def convert_to_int(value):
                if value is not None and isinstance(value, str):
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None
                return value

            return ProbeSettings(
                initial_delay=convert_to_int(get_field_value(probe_data, "initial_delay", "initialDelay")),
                period=convert_to_int(probe_data.get("period")),
                timeout=convert_to_int(probe_data.get("timeout")),
                failure_threshold=convert_to_int(get_field_value(probe_data, "failure_threshold", "failureThreshold")),
                success_threshold=convert_to_int(get_field_value(probe_data, "success_threshold", "successThreshold")),
                scheme=probe_data.get("scheme"),
                path=probe_data.get("path"),
                port=convert_to_int(probe_data.get("port")),
                method=get_field_value(probe_data, "method", "httpMethod"),
            )

        liveness_probe_data = get_field_value(data, "liveness_probe", "livenessProbe")
        liveness_probe = create_probe_settings(liveness_probe_data)

        readiness_probe_data = get_field_value(data, "readiness_probe", "readinessProbe")
        readiness_probe = create_probe_settings(readiness_probe_data)

        # Get other fields
        model = data.get("model")
        code_configuration = data.get("code_configuration")
        app_insights_enabled = data.get("app_insights_enabled")
        stage = data.get("stage")
        type_field = data.get("type")

        # Create DeploymentTemplate object using constructor
        return DeploymentTemplate(
            name=name,
            version=version,
            description=description,
            tags=tags,
            environment=environment,
            request_settings=request_settings,
            liveness_probe=liveness_probe,
            readiness_probe=readiness_probe,
            instance_count=instance_count,
            instance_type=default_instance_type,
            model=model,
            code_configuration=code_configuration,
            environment_variables=environment_variables,
            app_insights_enabled=app_insights_enabled,
            allowed_instance_types=allowed_instance_types,
            default_instance_type=default_instance_type,
            scoring_port=scoring_port,
            scoring_path=scoring_path,
            model_mount_path=model_mount_path,
            type=type_field,
            deployment_template_type=deployment_template_type,
            stage=stage,
        )

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.List", ActivityType.PUBLICAPI)
    @experimental
    def list(
        self,
        *,
        name: Optional[str] = None,
        tags: Optional[str] = None,
        count: Optional[int] = None,
        stage: Optional[str] = None,
        list_view_type: str = "ActiveOnly",
        **kwargs: Any,
    ) -> Iterable[DeploymentTemplate]:
        """List deployment templates.

        :keyword name: Filter by deployment template name.
        :paramtype name: Optional[str]
        :keyword tags: Comma-separated list of tag names (and optionally values). Example:
            tag1,tag2=value2.
        :paramtype tags: Optional[str]
        :keyword count: Maximum number of items to return.
        :paramtype count: Optional[int]
        :keyword stage: Filter by deployment template stage.
        :paramtype stage: Optional[str]
        :keyword list_view_type: View type for including/excluding (for example) archived entities.
        :paramtype list_view_type: str
        :return: Iterator of deployment template objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.DeploymentTemplate]
        """

        return cast(
            Iterable[DeploymentTemplate],
            (
                DeploymentTemplate._from_rest_object(item)
                for item in self._service_client.deployment_templates.list(
                    registry_name=self._operation_scope.registry_name,
                    name=name,
                    tags=tags,
                    count=count,
                    stage=stage,
                    list_view_type=list_view_type,
                    **kwargs,
                )
            ),
        )

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Get", ActivityType.PUBLICAPI)
    @experimental
    def get(self, name: str, version: Optional[str] = None, **kwargs: Any) -> DeploymentTemplate:
        """Get a deployment template by name and version.

        :param name: Name of the deployment template.
        :type name: str
        :param version: Version of the deployment template. If not provided, gets the latest version.
        :type version: Optional[str]
        :return: DeploymentTemplate object.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        :raises: ~azure.core.exceptions.ResourceNotFoundError if deployment template not found.
        """
        version = version or "latest"

        try:
            result = self._service_client.deployment_templates.get(
                registry_name=self._operation_scope.registry_name,
                name=name,
                version=version,
                **kwargs,
            )
            return DeploymentTemplate._from_rest_object(result)
        except Exception as e:
            module_logger.debug("DeploymentTemplate get operation failed: %s", e)
            raise ResourceNotFoundError(f"DeploymentTemplate {name}:{version} not found") from e

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.CreateOrUpdate", ActivityType.PUBLICAPI)
    @experimental
    def create_or_update(self, deployment_template: DeploymentTemplate, **kwargs: Any) -> DeploymentTemplate:
        """Create or update a deployment template.

        :param deployment_template: DeploymentTemplate object to create or update, dictionary containing deployment
            template definition, or path to a YAML file containing deployment template definition.
        :type deployment_template: Union[DeploymentTemplate, Dict[str, Any], str, PathLike]
        :return: DeploymentTemplate object representing the created or updated resource.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        """
        # Ensure we have a DeploymentTemplate object
        if not isinstance(deployment_template, DeploymentTemplate):
            raise ValueError("deployment_template must be a DeploymentTemplate object")

        rest_object = deployment_template._to_rest_object()
        self._service_client.deployment_templates.begin_create(
            registry_name=self._operation_scope.registry_name,
            name=deployment_template.name,
            version=deployment_template.version,
            body=rest_object,
            polling=False,
            **kwargs,
        )
        # Fire the LRO but don't wait for polling — the asset is available immediately.
        # Fetch the created/updated resource to return the server-side state.
        try:
            return self.get(deployment_template.name, deployment_template.version)
        except Exception:
            return deployment_template

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Delete", ActivityType.PUBLICAPI)
    @experimental
    def delete(self, name: str, version: Optional[str] = None, **kwargs: Any) -> None:
        """Delete a deployment template.

        :param name: Name of the deployment template to delete.
        :type name: str
        :param version: Version of the deployment template to delete. If not provided, deletes the latest version.
        :type version: Optional[str]
        """
        version = version or "latest"

        try:
            self._service_client.deployment_templates.delete(
                registry_name=self._operation_scope.registry_name,
                name=name,
                version=version,
                **kwargs,
            )
        except ResourceNotFoundError:
            raise
        except Exception as e:
            module_logger.debug("DeploymentTemplate delete operation failed: %s", e)
            raise

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Archive", ActivityType.PUBLICAPI)
    @experimental
    def archive(self, name: str, version: Optional[str] = None, **kwargs: Any) -> DeploymentTemplate:
        """Archive a deployment template by setting its stage to 'Archived'.

        :param name: Name of the deployment template to archive.
        :type name: str
        :param version: Version of the deployment template to archive. If not provided, archives the latest version.
        :type version: Optional[str]
        :return: DeploymentTemplate object representing the archived template.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        :raises: ~azure.core.exceptions.ResourceNotFoundError if deployment template not found.
        """
        # Get the existing template
        template = self.get(name=name, version=version, **kwargs)

        # Set stage to Archived
        template.stage = "Archived"

        # Update the template using create_or_update
        return self.create_or_update(template, **kwargs)

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Restore", ActivityType.PUBLICAPI)
    @experimental
    def restore(self, name: str, version: Optional[str] = None, **kwargs: Any) -> DeploymentTemplate:
        """Restore a deployment template by setting its stage to 'Development'.

        :param name: Name of the deployment template to restore.
        :type name: str
        :param version: Version of the deployment template to restore. If not provided, restores the latest version.
        :type version: Optional[str]
        :return: DeploymentTemplate object representing the restored template.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        :raises: ~azure.core.exceptions.ResourceNotFoundError if deployment template not found.
        """
        # Get the existing template
        template = self.get(name=name, version=version, **kwargs)

        # Set stage to Development
        template.stage = "Development"

        # Update the template using create_or_update
        return self.create_or_update(template, **kwargs)
