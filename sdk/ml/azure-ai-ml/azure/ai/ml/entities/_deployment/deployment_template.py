# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=docstring-missing-param,docstring-missing-rtype,docstring-missing-return,docstring-missing-type
# pylint: disable=docstring-should-be-keyword,no-else-return,too-many-locals,too-many-statements
# pylint: disable=too-many-branches,protected-access,redefined-outer-name,reimported
# pylint: disable=attribute-defined-outside-init,no-member

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union, IO, AnyStr

from azure.ai.ml._utils._experimental import experimental
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._assets import Environment

from azure.ai.ml.entities._deployment.deployment_template_settings import OnlineRequestSettings, ProbeSettings
from azure.ai.ml.entities._resource import Resource


@experimental
class DeploymentTemplate(Resource, RestTranslatableMixin):  # pylint: disable=too-many-instance-attributes
    """DeploymentTemplate entity for Azure ML deployments.

    :param name: Name of the deployment template.
    :type name: str
    :param version: Version of the deployment template.
    :type version: str
    :param description: Description of the deployment template.
    :type description: str
    :param environment: Environment for the deployment template.
    :type environment: ~azure.ai.ml.entities.Environment
    :param request_settings: Request settings for the deployment template.
    :type request_settings: ~azure.ai.ml.entities.OnlineRequestSettings
    :param liveness_probe: Liveness probe settings.
    :type liveness_probe: ~azure.ai.ml.entities.ProbeSettings
    :param readiness_probe: Readiness probe settings.
    :type readiness_probe: ~azure.ai.ml.entities.ProbeSettings
    :param instance_count: Number of instances for the deployment template.
    :type instance_count: int
    :param instance_type: Instance type for the deployment template.
    :type instance_type: str
    :param model: Model for the deployment template.
    :type model: str
    :param code_configuration: Code configuration for the deployment template.
    :type code_configuration: dict
    :param environment_variables: Environment variables for the deployment template.
    :type environment_variables: dict
    :param app_insights_enabled: Whether application insights is enabled.
    :type app_insights_enabled: bool
    :param stage: Stage of the deployment template. Can be "Active" or "Archived".
    :type stage: str
    """

    def __init__(  # pylint: disable=too-many-locals
        self,
        name: str,
        version: str,
        *,
        description: Optional[str] = None,
        environment: Optional[Union[Environment, str]] = None,
        request_settings: Optional[OnlineRequestSettings] = None,
        liveness_probe: Optional[ProbeSettings] = None,
        readiness_probe: Optional[ProbeSettings] = None,
        instance_count: Optional[int] = None,
        instance_type: Optional[str] = None,
        model: Optional[str] = None,
        code_configuration: Optional[Dict[str, Any]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        app_insights_enabled: Optional[bool] = None,
        allowed_instance_types: Optional[str] = None,
        default_instance_type: Optional[str] = None,  # Handle default instance type
        scoring_port: Optional[int] = None,
        scoring_path: Optional[str] = None,
        model_mount_path: Optional[str] = None,
        type: Optional[str] = None,
        deployment_template_type: Optional[str] = None,
        stage: Optional[str] = None,
        **kwargs,
    ):
        # Extract kwargs that should be passed to parent
        parent_kwargs = {}
        for key in ["description", "tags", "properties", "print_as_yaml", "id", "source_path", "creation_context"]:
            if key in kwargs:
                parent_kwargs[key] = kwargs.pop(key)

        super().__init__(name=name, **parent_kwargs)

        self.version = version
        self.description = description
        self.environment = environment
        self.request_settings = request_settings
        self.liveness_probe = liveness_probe
        self.readiness_probe = readiness_probe
        self.instance_count = instance_count
        self.instance_type = instance_type
        self.model = model
        self.code_configuration = code_configuration
        self.environment_variables = environment_variables
        self.app_insights_enabled = app_insights_enabled
        self.allowed_instance_types = allowed_instance_types
        self.default_instance_type = default_instance_type
        self.scoring_port = scoring_port
        self.scoring_path = scoring_path
        self.model_mount_path = model_mount_path
        self.type = type
        self.deployment_template_type = deployment_template_type
        self.stage = stage

        # Private flag to track if this template came from the service (and thus should exclude
        # immutable fields on update)
        self._from_service = False

        # Store original immutable field values when template comes from service
        self._original_immutable_fields = {}  # type: ignore[var-annotated]

    @property
    def request_timeout(self) -> Optional[int]:  # pylint: disable=docstring-missing-rtype
        """Get request timeout in seconds."""
        if self.request_settings and hasattr(self.request_settings, "request_timeout_ms"):
            if isinstance(self.request_settings.request_timeout_ms, str):
                # This shouldn't happen with proper OnlineRequestSettings, return a default
                return self.request_settings.request_timeout_ms
            else:  # pylint: disable=no-else-return
                # Convert milliseconds to seconds
                return (
                    self.request_settings.request_timeout_ms // 1000
                    if self.request_settings.request_timeout_ms
                    else None
                )
        return None

    @request_timeout.setter
    def request_timeout(self, value: int):  # pylint: disable=docstring-missing-param
        """Set request timeout in seconds."""
        if not self.request_settings:
            self.request_settings = OnlineRequestSettings(request_timeout_ms=value * 1000)
        else:
            self.request_settings.request_timeout_ms = value * 1000

    @property
    def liveness_probe_initial_delay(self) -> Optional[int]:  # pylint: disable=docstring-missing-rtype
        """Get liveness probe initial delay in seconds."""
        if self.liveness_probe and hasattr(self.liveness_probe, "initial_delay"):
            return self.liveness_probe.initial_delay
        return None

    @liveness_probe_initial_delay.setter
    def liveness_probe_initial_delay(self, value: int):  # pylint: disable=docstring-missing-param
        """Set liveness probe initial delay in seconds."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(initial_delay=value)
        else:
            self.liveness_probe.initial_delay = value

    @property
    def liveness_probe_period(self) -> Optional[int]:
        """Get liveness probe period in seconds."""
        if self.liveness_probe and hasattr(self.liveness_probe, "period"):
            return self.liveness_probe.period
        return None

    @liveness_probe_period.setter
    def liveness_probe_period(self, value: int):
        """Set liveness probe period in seconds."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(period=value)
        else:
            self.liveness_probe.period = value

    @property
    def liveness_probe_timeout(self) -> Optional[int]:
        """Get liveness probe timeout in seconds."""
        if self.liveness_probe and hasattr(self.liveness_probe, "timeout"):
            return self.liveness_probe.timeout
        return None

    @liveness_probe_timeout.setter
    def liveness_probe_timeout(self, value: int):
        """Set liveness probe timeout in seconds."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(timeout=value)
        else:
            self.liveness_probe.timeout = value

    # Readiness probe convenience properties
    @property
    def readiness_probe_initial_delay(self) -> Optional[int]:
        """Get readiness probe initial delay in seconds."""
        if self.readiness_probe and hasattr(self.readiness_probe, "initial_delay"):
            return self.readiness_probe.initial_delay
        return None

    @readiness_probe_initial_delay.setter
    def readiness_probe_initial_delay(self, value: int):
        """Set readiness probe initial delay in seconds."""
        if not self.readiness_probe:
            self.readiness_probe = ProbeSettings(initial_delay=value)
        else:
            self.readiness_probe.initial_delay = value

    @property
    def readiness_probe_period(self) -> Optional[int]:
        """Get readiness probe period in seconds."""
        if self.readiness_probe and hasattr(self.readiness_probe, "period"):
            return self.readiness_probe.period
        return None

    @readiness_probe_period.setter
    def readiness_probe_period(self, value: int):
        """Set readiness probe period in seconds."""
        if not self.readiness_probe:
            self.readiness_probe = ProbeSettings(period=value)
        else:
            self.readiness_probe.period = value

    @property
    def readiness_probe_timeout(self) -> Optional[int]:
        """Get readiness probe timeout in seconds."""
        if self.readiness_probe and hasattr(self.readiness_probe, "timeout"):
            return self.readiness_probe.timeout
        return None

    @readiness_probe_timeout.setter
    def readiness_probe_timeout(self, value: int):
        """Set readiness probe timeout in seconds."""
        if not self.readiness_probe:
            self.readiness_probe = ProbeSettings(timeout=value)
        else:
            self.readiness_probe.timeout = value

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "DeploymentTemplate":
        """Load a DeploymentTemplate object from a dictionary or YAML file.

        :param data: Data Dictionary, defaults to None
        :type data: Optional[Dict]
        :param yaml_path: YAML Path, defaults to None
        :type yaml_path: Optional[Union[PathLike, str]]
        :param params_override: Fields to overwrite on top of the yaml file.
            Format is [{"field1": "value1"}, {"field2": "value2"}], defaults to None
        :type params_override: Optional[list]
        :return: Loaded DeploymentTemplate object.
        :rtype: DeploymentTemplate
        """
        from azure.ai.ml._schema._deployment.template.deployment_template import DeploymentTemplateSchema
        from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, PARAMS_OVERRIDE_KEY
        from azure.ai.ml.entities._util import load_from_dict

        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        res: DeploymentTemplate = load_from_dict(DeploymentTemplateSchema, data, context, **kwargs)
        return res

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]] = None, **kwargs: Any) -> Dict[str, Any]:  # type: ignore
        """Dump the deployment template to a dictionary.

        :param dest: Destination path to write the deployment template to.
        :type dest: Optional[Union[str, PathLike]]
        :return: Dictionary representation of the deployment template.
        :rtype: Dict[str, Any]
        """
        result = {
            "name": self.name,
            "version": self.version,
        }

        if self.description:
            result["description"] = self.description
        if self.environment:
            if isinstance(self.environment, str):
                result["environment"] = self.environment
            elif hasattr(self.environment, "id"):
                result["environment"] = self.environment.id
            elif hasattr(self.environment, "name"):
                result["environment"] = self.environment.name
            else:
                result["environment"] = str(self.environment)
        if self.request_settings:
            result["request_settings"] = self.request_settings.__dict__  # type: ignore[assignment]
        if self.liveness_probe:
            result["liveness_probe"] = self.liveness_probe.__dict__  # type: ignore[assignment]
        if self.readiness_probe:
            result["readiness_probe"] = self.readiness_probe.__dict__  # type: ignore[assignment]
        if self.instance_count is not None:
            result["instance_count"] = self.instance_count  # type: ignore[assignment]
        if self.instance_type:
            result["instance_type"] = self.instance_type
        if self.model:
            result["model"] = self.model
        if self.code_configuration:
            result["code_configuration"] = self.code_configuration  # type: ignore[assignment]
        if self.environment_variables:
            result["environment_variables"] = self.environment_variables  # type: ignore[assignment]
        if self.app_insights_enabled is not None:
            result["app_insights_enabled"] = self.app_insights_enabled  # type: ignore[assignment]

        return result

    @classmethod
    def _from_rest_object(cls, obj) -> "DeploymentTemplate":
        """Create from REST object."""

        # Helper function to get values from either dict or object with attributes
        def get_value(source, key, default=None):
            if isinstance(source, dict):
                return source.get(key, default)
            else:
                return getattr(source, key, default)

        # Get the properties dictionary where the actual data is stored
        properties = get_value(obj, "properties", {})

        # Extract name and version from properties first, then fallback to top-level
        name = get_value(properties, "name") or get_value(obj, "name")
        if not name:
            additional_props = get_value(obj, "additional_properties", {})
            if isinstance(additional_props, dict):
                name = additional_props.get("name", "unknown")
            else:
                name = "unknown"

        version = get_value(properties, "version") or get_value(obj, "version")
        if not version:
            additional_props = get_value(obj, "additional_properties", {})
            if isinstance(additional_props, dict):
                version = additional_props.get("version", "1.0")
            else:
                version = "1.0"

        # Extract other fields from properties first, then fallback to top-level
        description = get_value(properties, "description") or get_value(obj, "description")
        tags = get_value(properties, "tags") or get_value(obj, "tags", {})

        # Extract from properties using the backend field names
        environment_id = (
            get_value(properties, "environmentId")
            or get_value(properties, "environment")
            or get_value(obj, "environment_id")
            or get_value(obj, "environment")
        )
        environment_variables = get_value(properties, "environmentVariables") or get_value(obj, "environment_variables")
        request_settings = get_value(properties, "requestSettings") or get_value(obj, "request_settings")
        liveness_probe = get_value(properties, "livenessProbe") or get_value(obj, "liveness_probe")
        readiness_probe = get_value(properties, "readinessProbe") or get_value(obj, "readiness_probe")
        instance_count = get_value(properties, "instanceCount") or get_value(obj, "instance_count")
        default_instance_type = get_value(properties, "defaultInstanceType") or get_value(obj, "default_instance_type")
        deployment_template_type = get_value(properties, "deploymentTemplateType") or get_value(
            obj, "deployment_template_type"
        )

        # Extract additional fields
        allowed_instance_types = get_value(properties, "allowedInstanceTypes") or get_value(obj, "allowed_instance_types")
        scoring_port = get_value(properties, "scoringPort") or get_value(obj, "scoring_port")
        scoring_path = get_value(properties, "scoringPath") or get_value(obj, "scoring_path")
        model_mount_path = get_value(properties, "modelMountPath") or get_value(obj, "model_mount_path")
        stage = get_value(properties, "stage") or get_value(obj, "stage")
        type_field = get_value(properties, "type") or get_value(obj, "type")

        # Handle string representations from properties - they come as JSON strings
        import json
        import ast

        # Parse tags if it's a string
        if isinstance(tags, str):
            try:
                tags = json.loads(tags) if tags and tags != "{}" else {}
            except (json.JSONDecodeError, ValueError):
                tags = {}

        # Parse environment_variables if it's a string
        if isinstance(environment_variables, str):
            try:
                environment_variables = ast.literal_eval(environment_variables)
            except (ValueError, SyntaxError):
                environment_variables = {}

        # Parse allowed_instance_types if it's a string
        if isinstance(allowed_instance_types, str):
            try:
                allowed_instance_types = ast.literal_eval(allowed_instance_types)
            except (ValueError, SyntaxError):
                allowed_instance_types = None

        # Convert request_settings to OnlineRequestSettings object using the built-in conversion method
        request_settings_obj = OnlineRequestSettings._from_rest_object(request_settings) if request_settings else None

        # Convert probe settings to ProbeSettings objects using the built-in conversion methods
        from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings

        liveness_probe_obj = ProbeSettings._from_rest_object(liveness_probe) if liveness_probe else None
        readiness_probe_obj = ProbeSettings._from_rest_object(readiness_probe) if readiness_probe else None

        # Convert string values to appropriate types
        if isinstance(instance_count, str):
            try:
                instance_count = int(instance_count)
            except (ValueError, TypeError):
                instance_count = None

        if isinstance(scoring_port, str):
            try:
                scoring_port = int(scoring_port)
            except (ValueError, TypeError):
                scoring_port = None

        template = cls(
            name=name or "unknown",
            version=version or "1.0",
            description=description,
            tags=tags,  # Include tags from REST response
            properties=properties,  # Include properties from REST response
            id=get_value(obj, "id"),  # Set the ID from the REST response
            environment=environment_id,  # Use the environment ID from API
            request_settings=request_settings_obj,  # Use proper OnlineRequestSettings object or None
            liveness_probe=liveness_probe_obj,  # Use proper ProbeSettings object or None
            readiness_probe=readiness_probe_obj,  # Use proper ProbeSettings object or None
            instance_count=instance_count,
            default_instance_type=default_instance_type,  # Use default instance type
            model=get_value(obj, "model"),  # May not be present in this API format
            code_configuration=get_value(obj, "code_configuration"),  # May not be present in this API format
            environment_variables=environment_variables,
            app_insights_enabled=get_value(obj, "app_insights_enabled"),  # May not be present in this API format
            deployment_template_type=deployment_template_type,  # Include deployment template type
            allowed_instance_types=allowed_instance_types,  # Include allowed instance types
            scoring_port=scoring_port,  # Include scoring port
            scoring_path=scoring_path,  # Include scoring path
            model_mount_path=model_mount_path,  # Include model mount path
            stage=stage,  # Include stage for archive/restore functionality
            type=type_field,  # Include type field from REST response
        )

        # Mark this template as coming from the service so it excludes immutable fields on
        # updates
        template._from_service = True

        # Store additional fields from the REST response that may be needed
        template.environment_id = environment_id  # type: ignore[attr-defined]
        # Alternative name for deployment_template_type
        template.template = get_value(obj, "template", deployment_template_type)  # type: ignore
        template.code_id = get_value(obj, "code_id")  # type: ignore

        # Store original values of immutable fields to preserve them during updates
        # IMPORTANT: Store the raw values from the API response, not the converted objects
        template._original_immutable_fields = {
            "environment_id": environment_id,
            "environment_variables": environment_variables,
            "request_settings": request_settings,  # Store original REST object, not converted
            "liveness_probe": liveness_probe,  # Store original REST object, not converted
            "readiness_probe": readiness_probe,  # Store original REST object, not converted
            "instance_count": instance_count,
            "default_instance_type": default_instance_type,
            "model": get_value(obj, "model"),
            "code_configuration": get_value(obj, "code_configuration"),
            "app_insights_enabled": get_value(obj, "app_insights_enabled"),
            "deployment_template_type": deployment_template_type,
            "allowed_instance_types": allowed_instance_types,
            "scoring_port": scoring_port,
            "scoring_path": scoring_path,
            "model_mount_path": model_mount_path,
            "stage": stage,  # Store stage for archive/restore functionality
            "type": type_field,  # Store type field from REST response
        }

        return template

    def _to_rest_object(self) -> dict:
        """Convert to REST object format for API submission.

        :param exclude_immutable_fields: If True, excludes immutable fields that cannot be updated.
                                       If None, automatically determines based on whether template came from service.
        :type exclude_immutable_fields: bool
        """
        result = {
            "name": self.name,
            "version": self.version,
        }

        # Always include type field
        if hasattr(self, "type") and self.type:
            result["type"] = self.type
        else:
            result["type"] = "deploymenttemplates"  # Default type if not specified

        # Add optional basic fields
        if self.description:
            result["description"] = self.description

        if hasattr(self, "stage") and self.stage:
            result["stage"] = self.stage

        if hasattr(self, "deployment_template_type") and self.deployment_template_type:
            result["deploymentTemplateType"] = self.deployment_template_type  # Use camelCase for API

        # Add tags if present
        if self.tags:
            result["tags"] = dict(self.tags)  # type: ignore[assignment]

        # Add environment information
        if hasattr(self, "environment_id") and self.environment_id:
            result["environmentId"] = self.environment_id
        elif self.environment:
            result["environmentId"] = str(self.environment)

        if self.environment_variables:
            result["environmentVariables"] = dict(self.environment_variables)  # type: ignore[assignment]

        if hasattr(self, "model_mount_path") and self.model_mount_path:
            result["modelMountPath"] = self.model_mount_path

        # Convert request settings to dictionary for API request body
        if self.request_settings:
            request_dict = self.request_settings._to_dict()
            if request_dict:
                result["requestSettings"] = request_dict  # type: ignore[assignment]

        # Convert probe settings to dictionaries for API request body
        if self.liveness_probe:
            liveness_dict = self.liveness_probe._to_dict()
            if liveness_dict:
                result["livenessProbe"] = liveness_dict  # type: ignore[assignment]

        if self.readiness_probe:
            readiness_dict = self.readiness_probe._to_dict()
            if readiness_dict:
                result["readinessProbe"] = readiness_dict  # type: ignore[assignment]

        # Add instance configuration
        if hasattr(self, "default_instance_type") and self.default_instance_type:
            result["defaultInstanceType"] = self.default_instance_type
        elif hasattr(self, "instance_type") and self.instance_type:
            result["defaultInstanceType"] = self.instance_type

        if hasattr(self, "instance_count") and self.instance_count is not None:
            result["instanceCount"] = self.instance_count  # type: ignore[assignment]

        # Add scoring configuration
        if hasattr(self, "scoring_path") and self.scoring_path:
            result["scoringPath"] = self.scoring_path

        if hasattr(self, "scoring_port") and self.scoring_port is not None:
            result["scoringPort"] = self.scoring_port  # type: ignore[assignment]

        # Add other optional fields
        if hasattr(self, "model") and self.model:
            result["model"] = self.model

        if hasattr(self, "code_configuration") and self.code_configuration:
            result["codeConfiguration"] = self.code_configuration  # type: ignore[assignment]

        if hasattr(self, "app_insights_enabled") and self.app_insights_enabled is not None:
            result["appInsightsEnabled"] = self.app_insights_enabled  # type: ignore

        # Handle allowed instance types - convert string to array format for API
        if hasattr(self, "allowed_instance_types") and self.allowed_instance_types:
            if isinstance(self.allowed_instance_types, str):
                # Convert space-separated string to array
                instance_types_array = self.allowed_instance_types.split()
            elif isinstance(self.allowed_instance_types, list):
                instance_types_array = self.allowed_instance_types
            else:
                instance_types_array = [str(self.allowed_instance_types)]
            result["allowedInstanceTypes"] = instance_types_array  # type: ignore[assignment]

        return result

    def _to_dict(self) -> Dict:
        """Convert the deployment template to a dictionary matching the expected API format."""
        result = {
            "type": "deploymenttemplates",
            "name": self.name,
            "version": self.version,
        }

        # Add optional basic fields
        if self.description:
            result["description"] = self.description
        if self.stage:
            result["stage"] = self.stage
        if self.deployment_template_type:
            result["deploymentTemplateType"] = self.deployment_template_type

        # Add tags if present
        if self.tags:
            result["tags"] = dict(self.tags)  # type: ignore[assignment]

        if hasattr(self, "environment_id") and self.environment_id:
            result["environmentId"] = self.environment_id
        elif self.environment:
            result["environmentId"] = str(self.environment)

        # Add metadata fields if available
        if hasattr(self, "created_by") and self.created_by:
            result["createdBy"] = self.created_by
        if hasattr(self, "created_time") and self.created_time:
            result["createdTime"] = self.created_time
        if hasattr(self, "modified_time") and self.modified_time:
            result["modifiedTime"] = self.modified_time
        if hasattr(self, "capabilities"):
            result["capabilities"] = self.capabilities or []  # type: ignore[assignment]

        # Add environment variables
        if self.environment_variables:
            result["environmentVariables"] = self.environment_variables  # type: ignore[assignment]

        # Add model mount path
        if self.model_mount_path:
            result["modelMountPath"] = self.model_mount_path

        # Add request settings using dictionary conversion for JSON serialization
        if self.request_settings:
            request_dict = self.request_settings._to_dict()
            if request_dict:
                result["requestSettings"] = request_dict  # type: ignore[assignment]

        # Add probe settings using dictionary conversion for JSON serialization
        if self.liveness_probe:
            liveness_dict = self.liveness_probe._to_dict()
            if liveness_dict:
                result["livenessProbe"] = liveness_dict  # type: ignore[assignment]

        if self.readiness_probe:
            readiness_dict = self.readiness_probe._to_dict()
            if readiness_dict:
                result["readinessProbe"] = readiness_dict  # type: ignore[assignment]

        # Add instance configuration
        if hasattr(self, "allowed_instance_types") and self.allowed_instance_types:
            result["allowedInstanceTypes"] = self.allowed_instance_types  # type: ignore[assignment]
        if self.default_instance_type:
            result["defaultInstanceType"] = self.default_instance_type
        elif self.instance_type:
            result["defaultInstanceType"] = self.instance_type
        if self.instance_count is not None:
            result["instanceCount"] = self.instance_count  # type: ignore[assignment]

        # Add scoring configuration
        if self.scoring_path:
            result["scoringPath"] = self.scoring_path
        if self.scoring_port is not None:
            result["scoringPort"] = self.scoring_port  # type: ignore[assignment]

        return result

    def __str__(self) -> str:
        """Return a JSON string representation of the deployment template."""
        import json

        return json.dumps(self._to_dict(), indent=2)

    def __repr__(self) -> str:
        """Return a JSON string representation of the deployment template."""
        return self.__str__()
