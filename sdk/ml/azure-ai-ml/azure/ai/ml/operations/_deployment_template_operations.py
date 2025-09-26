# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Iterable, Optional, Union, cast
from os import PathLike

from azure.ai.ml._scope_dependent_operations import OperationScope, OperationConfig, _ScopeDependentOperations
from azure.ai.ml._telemetry import ActivityType, monitor_with_telemetry_mixin
from azure.ai.ml._utils._logger_utils import OpsLogger
from azure.ai.ml.entities import DeploymentTemplate
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import ResourceNotFoundError

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
        service_client_04_2024_dataplanepreview,
        **kwargs: Dict[str, Any],
    ):
        super(DeploymentTemplateOperations, self).__init__(operation_scope, operation_config)
        # ops_logger.update_info(kwargs)
        self._operation_scope = operation_scope
        self._operation_config = operation_config
        self._service_client = service_client_04_2024_dataplanepreview
        self._init_kwargs = kwargs

    def _get_registry_endpoint(self) -> str:
        """Dynamically determine the registry endpoint based on registry region.
        
        :return: The API endpoint URL for the registry
        :rtype: str
        """
        try:
            # Import here to avoid circular dependencies
            from azure.ai.ml.operations import RegistryOperations
            from azure.ai.ml._restclient.v2022_10_01_preview import AzureMachineLearningWorkspaces as ServiceClient102022
            # Try to get credential from service client or operation config
            credential = None
            if hasattr(self._service_client, '_config') and hasattr(self._service_client._config, 'credential'):
                credential = self._service_client._config.credential
            elif hasattr(self._operation_config, 'credential'):
                credential = self._operation_config.credential
            
            if credential and self._operation_scope.registry_name:
                # Get registry information to determine the region
                registry_operations = RegistryOperations(
                    operation_scope=self._operation_scope,
                    service_client=ServiceClient102022(
                        credential=credential,
                        subscription_id=self._operation_scope.subscription_id,
                        resource_group_name=self._operation_scope.resource_group_name
                    ),
                    all_operations=None,
                    credentials=credential
                )
                
                registry = registry_operations.get(self._operation_scope.registry_name)
                
                # Extract region from registry location or replication locations
                region = None
                if registry.location:
                    region = registry.location
                elif registry.replication_locations and len(registry.replication_locations) > 0:
                    region = registry.replication_locations[0].location
                
                if region:
                    # import pdb;pdb.set_trace()
                    # Format the endpoint using the detected region
                    return f"https://{region}.api.azureml.ms"
                    
        except Exception as e:
            module_logger.warning("Could not determine registry region dynamically: %s. Using default.", e)
        
        # Fallback to default region if unable to determine dynamically
        return "https://int.api.azureml.ms"

    def _convert_dict_to_deployment_template(self, dict_data: Dict[str, Any]) -> DeploymentTemplate:
        """Convert dictionary format to DeploymentTemplate object.
        
        This helper method handles the field name conversion from snake_case/user-friendly
        format to the camelCase format expected by the REST API.
        
        :param dict_data: Dictionary containing deployment template data
        :type dict_data: Dict[str, Any]
        :return: DeploymentTemplate object
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        """
        # Create a copy to avoid modifying the original
        fixed_data = dict_data.copy()
        
        # Field name mappings from user-friendly format to API format
        field_mappings = {
            'allowed_instance_types': 'allowedInstanceType',
            'deployment_template_type': 'deploymentTemplateType', 
            'model_mount_path': 'modelMountPath',
            'scoring_path': 'scoringPath',
            'scoring_port': 'scoringPort',
            'default_instance_type': 'defaultInstanceType',
            'instance_count': 'instanceCount',
            'environment_variables': 'environmentVariables',
            'request_settings': 'requestSettings',
            'liveness_probe': 'livenessProbe',
            'readiness_probe': 'readinessProbe'
        }
        
        # Apply field name mappings
        for old_name, new_name in field_mappings.items():
            if old_name in fixed_data:
                fixed_data[new_name] = fixed_data[old_name]
                del fixed_data[old_name]
        
        # Convert string to list for allowed instance types
        if 'allowedInstanceType' in fixed_data and isinstance(fixed_data['allowedInstanceType'], str):
            fixed_data['allowedInstanceType'] = fixed_data['allowedInstanceType'].split()
        
        # Fix request settings field names
        if 'requestSettings' in fixed_data:
            rs = fixed_data['requestSettings']
            if 'request_timeout_ms' in rs:
                rs['requestTimeout'] = rs['request_timeout_ms']
                del rs['request_timeout_ms']
            if 'max_concurrent_requests_per_instance' in rs:
                rs['maxConcurrentRequestsPerInstance'] = rs['max_concurrent_requests_per_instance']
                del rs['max_concurrent_requests_per_instance']
        
        # Fix probe settings field names
        for probe_field in ['livenessProbe', 'readinessProbe']:
            if probe_field in fixed_data:
                probe = fixed_data[probe_field]
                probe_mappings = {
                    'initial_delay': 'initialDelay',
                    'failure_threshold': 'failureThreshold',
                    'success_threshold': 'successThreshold',
                    'method': 'httpMethod'
                }
                for old, new in probe_mappings.items():
                    if old in probe:
                        probe[new] = probe[old]
                        del probe[old]
        
        # Create DeploymentTemplate object using _from_rest_object
        rest_data = {"properties": fixed_data}
        return DeploymentTemplate._from_rest_object(rest_data)

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.List", ActivityType.PUBLICAPI)
    def list(
        self,
        name: Optional[str] = None,
        tags: Optional[str] = None,
        count: Optional[int] = None,
        stage: Optional[str] = None,
        list_view_type: str = "ActiveOnly",
        **kwargs: Any,
    ) -> Iterable[DeploymentTemplate]:
        """List deployment templates.
        
        :param name: Filter by deployment template name.
        :type name: Optional[str]
        :param tags: Comma-separated list of tag names (and optionally values). Example:
            tag1,tag2=value2.
        :type tags: Optional[str]
        :param count: Maximum number of items to return.
        :type count: Optional[int]
        :param stage: Filter by deployment template stage.
        :type stage: Optional[str]  
        :param list_view_type: View type for including/excluding (for example) archived entities.
        :type list_view_type: str
        :return: Iterator of deployment template objects.
        :rtype: ~azure.core.paging.ItemPaged[~azure.ai.ml.entities.DeploymentTemplate]
        """

        endpoint = self._get_registry_endpoint()
        return cast(
            Iterable[DeploymentTemplate],
            self._service_client.deployment_templates.list_deployment_templates(
                    endpoint=endpoint,
                    subscription_id=self._operation_scope.subscription_id,
                    resource_group_name=self._operation_scope.resource_group_name,
                    registry_name=self._operation_scope.registry_name,
                    name=name,
                    tags=tags,
                    count=count,
                    stage=stage,
                    list_view_type=list_view_type,
                    **kwargs
                )
        )
        # try:
        #     if hasattr(self._service_client, 'deployment_templates'):
        #         registry_name_to_use = self._operation_scope.registry_name or self._operation_scope.workspace_name
        #         endpoint = f"https://eastus2.api.azureml.ms"  # TODO: Hardcoded value of endpoint
                
        #         results = self._service_client.deployment_templates.list_deployment_templates(
        #             endpoint=endpoint,
        #             subscription_id=self._operation_scope.subscription_id,
        #             resource_group_name=self._operation_scope.resource_group_name,
        #             registry_name=registry_name_to_use,
        #             name=name,
        #             tags=tags,
        #             count=count,
        #             stage=stage,
        #             list_view_type=list_view_type,
        #             **kwargs
        #         )
        #         import pdb;pdb.set_trace()
        #         if results is None or isinstance(results, str):
        #             return []
                
        #         deployment_templates = []
                
        #         for paged_result in results:
        #             if isinstance(paged_result, str):
        #                 continue
                    
        #             # Handle PagedDeploymentTemplate with 'value' property
        #             if hasattr(paged_result, 'value') and paged_result.value:
        #                 for deployment_template_obj in paged_result.value:
        #                     if deployment_template_obj:
        #                         try:
        #                             dt = DeploymentTemplate._from_rest_object(deployment_template_obj)
        #                             deployment_templates.append(dt)
        #                         except Exception:
        #                             # Skip malformed objects
        #                             continue
        #             elif isinstance(paged_result, dict):
        #                 # Handle direct response dictionary
        #                 if 'value' in paged_result:
        #                     for deployment_template_obj in paged_result['value']:
        #                         try:
        #                             dt = DeploymentTemplate._from_rest_object(deployment_template_obj)
        #                             deployment_templates.append(dt)
        #                         except Exception:
        #                             # Skip malformed objects
        #                             continue
        #                 else:
        #                     # Direct DeploymentTemplate object
        #                     try:
        #                         dt = DeploymentTemplate._from_rest_object(paged_result)
        #                         deployment_templates.append(dt)
        #                     except Exception:
        #                         # Skip malformed objects
        #                         continue
        #             elif hasattr(paged_result, 'name') or hasattr(paged_result, 'properties'):
        #                 # Direct DeploymentTemplate object
        #                 try:
        #                     dt = DeploymentTemplate._from_rest_object(paged_result)
        #                     deployment_templates.append(dt)
        #                 except Exception:
        #                     # Skip malformed objects
        #                     continue
                
        #         return deployment_templates
        #     else:
        #         return []
        # except Exception as e:
        #     module_logger.warning("DeploymentTemplate list operation failed: %s", e)
        #     return []

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Get", ActivityType.PUBLICAPI)
    def get(self, name: str, version: Optional[str] = None) -> DeploymentTemplate:
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
            endpoint = self._get_registry_endpoint()

            result = self._service_client.deployment_templates.get(
                endpoint=endpoint,
                subscription_id=self._operation_scope.subscription_id,
                resource_group_name=self._operation_scope.resource_group_name,
                registry_name=self._operation_scope.registry_name,
                name=name,
                version=version,
                **self._init_kwargs
            )
            return DeploymentTemplate._from_rest_object(result)
        except Exception as e:
            module_logger.warning("DeploymentTemplate get operation failed: %s", e)
            raise ResourceNotFoundError(f"DeploymentTemplate {name}:{version} not found") from e

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.CreateOrUpdate", ActivityType.PUBLICAPI)
    def create_or_update(self, deployment_template: Union[DeploymentTemplate, Dict[str, Any], str, PathLike]) -> DeploymentTemplate:
        """Create or update a deployment template.

        :param deployment_template: DeploymentTemplate object to create or update, dictionary containing deployment 
            template definition, or path to a YAML file containing deployment template definition.
        :type deployment_template: Union[DeploymentTemplate, Dict[str, Any], str, PathLike]
        :return: DeploymentTemplate object representing the created or updated resource.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        
        .. admonition:: Example

            .. literalinclude:: ../samples/ml_samples_deployment_template.py
                :start-after: [START deployment_template_create_with_dict]
                :end-before: [END deployment_template_create_with_dict]
                :language: python
                :dedent: 8
                :caption: Creating a deployment template using a dictionary.
        """
        try:
            # Handle YAML file path input
            if isinstance(deployment_template, (str, PathLike)):
                from azure.ai.ml.entities._load_functions import load_deployment_template
                deployment_template = load_deployment_template(source=deployment_template)
            
            # Handle dictionary input
            elif isinstance(deployment_template, dict):
                deployment_template = self._convert_dict_to_deployment_template(deployment_template)
            
            # Ensure we have a DeploymentTemplate object
            if not isinstance(deployment_template, DeploymentTemplate):
                raise ValueError(
                    "deployment_template must be a DeploymentTemplate object, dictionary, or path to a YAML file"
                )
            
            if hasattr(self._service_client, 'deployment_templates'):
                endpoint = self._get_registry_endpoint()
                
                rest_object = deployment_template._to_rest_object()
                self._service_client.deployment_templates.create(
                    endpoint=endpoint,
                    subscription_id=self._operation_scope.subscription_id,
                    resource_group_name=self._operation_scope.resource_group_name,
                    registry_name=self._operation_scope.registry_name,
                    name=deployment_template.name,
                    version=deployment_template.version,
                    body=rest_object,
                    **self._init_kwargs
                )
                return deployment_template
            else:
                raise RuntimeError("DeploymentTemplate service not available")
        except Exception as e:
            module_logger.error("DeploymentTemplate create_or_update operation failed: %s", e)
            raise

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Delete", ActivityType.PUBLICAPI)
    def delete(self, name: str, version: Optional[str] = None) -> None:
        """Delete a deployment template.

        :param name: Name of the deployment template to delete.
        :type name: str
        :param version: Version of the deployment template to delete. If not provided, deletes the latest version.
        :type version: Optional[str]
        """
        version = version or "latest"
        
        try:
            if hasattr(self._service_client, 'deployment_templates'):
                endpoint = self._get_registry_endpoint()
                
                self._service_client.deployment_templates.delete_deployment_template(
                    endpoint=endpoint,
                    subscription_id=self._operation_scope.subscription_id,
                    resource_group_name=self._operation_scope.resource_group_name,
                    registry_name=self._operation_scope.registry_name,
                    name=name,
                    version=version,
                    **self._init_kwargs
                )
            else:
                raise RuntimeError("DeploymentTemplate service not available")
        except ResourceNotFoundError:
            raise
        except Exception as e:
            module_logger.error("DeploymentTemplate delete operation failed: %s", e)
            raise

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Archive", ActivityType.PUBLICAPI)
    def archive(self, name: str, version: Optional[str] = None) -> DeploymentTemplate:
        """Archive a deployment template by setting its stage to 'Archived'.

        :param name: Name of the deployment template to archive.
        :type name: str
        :param version: Version of the deployment template to archive. If not provided, archives the latest version.
        :type version: Optional[str]
        :return: DeploymentTemplate object representing the archived template.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        :raises: ~azure.core.exceptions.ResourceNotFoundError if deployment template not found.
        """
        try:
            # Get the existing template
            template = self.get(name=name, version=version)
            
            # Set stage to Archived
            template.stage = "Archived"
            
            # Update the template using create_or_update
            return self.create_or_update(template)
        except Exception as e:
            module_logger.error("DeploymentTemplate archive operation failed: %s", e)
            raise

    @distributed_trace
    @monitor_with_telemetry_mixin(ops_logger, "DeploymentTemplate.Restore", ActivityType.PUBLICAPI)
    def restore(self, name: str, version: Optional[str] = None) -> DeploymentTemplate:
        """Restore a deployment template by setting its stage to 'Development'.

        :param name: Name of the deployment template to restore.
        :type name: str
        :param version: Version of the deployment template to restore. If not provided, restores the latest version.
        :type version: Optional[str]
        :return: DeploymentTemplate object representing the restored template.
        :rtype: ~azure.ai.ml.entities.DeploymentTemplate
        :raises: ~azure.core.exceptions.ResourceNotFoundError if deployment template not found.
        """
        try:
            # Get the existing template
            template = self.get(name=name, version=version)

            # Set stage to Development
            template.stage = "Development"
            
            # Update the template using create_or_update
            return self.create_or_update(template)
        except Exception as e:
            module_logger.error("DeploymentTemplate restore operation failed: %s", e)
            raise
