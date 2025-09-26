# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional, Union

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.entities._assets import Environment
from azure.ai.ml.entities._deployment.deployment_template_settings import OnlineRequestSettings, ProbeSettings
from azure.ai.ml.entities._resource import Resource
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml._schema._deployment.template.deployment_template import DeploymentTemplateSchema

def seconds_to_hhmmss(seconds: int) -> str:
    """Convert seconds to HH:MM:SS format for backend."""
    try:
        if seconds is None:
            return "00:01:30"  # 90 seconds default
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError):
        return "00:01:30"  # Safe default


def hhmmss_to_seconds(hhmmss_str: str) -> int:
    """Convert HH:MM:SS format from backend to seconds for user."""
    try:
        if not hhmmss_str:
            return 90  # 90 seconds default
        
        parts = hhmmss_str.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        return 90  # Safe default
    except (ValueError, TypeError):
        return 90  # Safe default


def convert_probe_durations_from_backend(probe_dict: dict) -> dict:
    """Convert probe duration fields from HH:MM:SS (backend) to seconds (user)."""
    converted = probe_dict.copy()
    duration_fields = ["initialDelay", "period", "timeout"]
    
    for field in duration_fields:
        if field in converted and converted[field]:
            converted[field] = hhmmss_to_seconds(converted[field])
    
    return converted


def convert_probe_durations_to_backend(probe_dict: dict) -> dict:
    """Convert probe duration fields from seconds (user) to HH:MM:SS (backend)."""
    converted = probe_dict.copy()
    # Map user-facing field names to backend field names
    field_mappings = {
        "initial_delay": "initialDelay",
        "period": "period", 
        "timeout": "timeout"
    }
    
    for user_field, backend_field in field_mappings.items():
        if user_field in converted and converted[user_field] is not None:
            # Convert seconds to HH:MM:SS
            seconds_value = int(converted[user_field])
            hhmmss_value = seconds_to_hhmmss(seconds_value)
            # Remove the old field and add the new one
            del converted[user_field]
            converted[backend_field] = hhmmss_value
        elif backend_field in converted and converted[backend_field] is not None:
            # Already in backend format, convert from seconds to HH:MM:SS
            if isinstance(converted[backend_field], int):
                converted[backend_field] = seconds_to_hhmmss(int(converted[backend_field]))
    
    return converted


class DeploymentTemplate(Resource, RestTranslatableMixin):
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

    def __init__(
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
        scoring_port: Optional[int] = None,
        scoring_path: Optional[str] = None,
        model_mount_path: Optional[str] = None,
        type: Optional[str] = None,
        deployment_template_type: Optional[str] = None,
        stage: Optional[str] = None,
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        
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
        self.scoring_port = scoring_port
        self.scoring_path = scoring_path
        self.model_mount_path = model_mount_path
        self.type = type
        self.deployment_template_type = deployment_template_type
        self.stage = stage
        
        # Private flag to track if this template came from the service (and thus should exclude immutable fields on update)
        self._from_service = False
        
        # Store original immutable field values when template comes from service
        self._original_immutable_fields = {}

    @property
    def request_timeout_seconds(self) -> Optional[int]:
        """Get request timeout in seconds (user-friendly format)."""
        if self.request_settings and hasattr(self.request_settings, 'request_timeout_ms'):
            if isinstance(self.request_settings.request_timeout_ms, str):
                # Convert HH:MM:SS format to seconds
                return hhmmss_to_seconds(self.request_settings.request_timeout_ms)
            else:
                # Convert milliseconds to seconds
                return self.request_settings.request_timeout_ms // 1000 if self.request_settings.request_timeout_ms else None
        return None

    @request_timeout_seconds.setter
    def request_timeout_seconds(self, value: int):
        """Set request timeout in seconds (user-friendly format)."""
        if not self.request_settings:
            self.request_settings = OnlineRequestSettings(request_timeout_ms=value * 1000)
        else:
            self.request_settings.request_timeout_ms = value * 1000

    @property
    def liveness_probe_initial_delay_seconds(self) -> Optional[int]:
        """Get liveness probe initial delay in seconds (user-friendly format)."""
        if self.liveness_probe and hasattr(self.liveness_probe, 'initial_delay'):
            return self.liveness_probe.initial_delay
        return None

    @liveness_probe_initial_delay_seconds.setter
    def liveness_probe_initial_delay_seconds(self, value: int):
        """Set liveness probe initial delay in seconds (user-friendly format)."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(initial_delay=value)
        else:
            self.liveness_probe.initial_delay = value

    @property
    def liveness_probe_period_seconds(self) -> Optional[int]:
        """Get liveness probe period in seconds (user-friendly format)."""
        if self.liveness_probe and hasattr(self.liveness_probe, 'period'):
            return self.liveness_probe.period
        return None

    @liveness_probe_period_seconds.setter
    def liveness_probe_period_seconds(self, value: int):
        """Set liveness probe period in seconds (user-friendly format)."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(period=value)
        else:
            self.liveness_probe.period = value

    @property
    def liveness_probe_timeout_seconds(self) -> Optional[int]:
        """Get liveness probe timeout in seconds (user-friendly format)."""
        if self.liveness_probe and hasattr(self.liveness_probe, 'timeout'):
            return self.liveness_probe.timeout
        return None

    @liveness_probe_timeout_seconds.setter
    def liveness_probe_timeout_seconds(self, value: int):
        """Set liveness probe timeout in seconds (user-friendly format)."""
        if not self.liveness_probe:
            self.liveness_probe = ProbeSettings(timeout=value)
        else:
            self.liveness_probe.timeout = value

    # Readiness probe convenience properties
    @property
    def readiness_probe_initial_delay_seconds(self) -> Optional[int]:
        """Get readiness probe initial delay in seconds (user-friendly format)."""
        if self.readiness_probe and hasattr(self.readiness_probe, 'initial_delay'):
            return self.readiness_probe.initial_delay
        return None

    @readiness_probe_initial_delay_seconds.setter
    def readiness_probe_initial_delay_seconds(self, value: int):
        """Set readiness probe initial delay in seconds (user-friendly format)."""
        if not self.readiness_probe:
            self.readiness_probe = ProbeSettings(initial_delay=value)
        else:
            self.readiness_probe.initial_delay = value

    @property
    def readiness_probe_period_seconds(self) -> Optional[int]:
        """Get readiness probe period in seconds (user-friendly format)."""
        if self.readiness_probe and hasattr(self.readiness_probe, 'period'):
            return self.readiness_probe.period
        return None

    @readiness_probe_period_seconds.setter
    def readiness_probe_period_seconds(self, value: int):
        """Set readiness probe period in seconds (user-friendly format)."""
        if not self.readiness_probe:
            self.readiness_probe = ProbeSettings(period=value)
        else:
            self.readiness_probe.period = value

    @property
    def readiness_probe_timeout_seconds(self) -> Optional[int]:
        """Get readiness probe timeout in seconds (user-friendly format)."""
        if self.readiness_probe and hasattr(self.readiness_probe, 'timeout'):
            return self.readiness_probe.timeout
        return None

    @readiness_probe_timeout_seconds.setter
    def readiness_probe_timeout_seconds(self, value: int):
        """Set readiness probe timeout in seconds (user-friendly format)."""
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

    def dump(self, dest=None, **kwargs) -> Dict[str, Any]:
        """Dump the deployment template to a dictionary.
        
        :param dest: Destination path to write the deployment template to.
        :return: Dictionary representation of the deployment template.
        :rtype: dict
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
            elif hasattr(self.environment, 'id'):
                result["environment"] = self.environment.id
            elif hasattr(self.environment, 'name'):
                result["environment"] = self.environment.name
            else:
                result["environment"] = str(self.environment)
        if self.request_settings:
            result["request_settings"] = self.request_settings.__dict__
        if self.liveness_probe:
            result["liveness_probe"] = self.liveness_probe.__dict__
        if self.readiness_probe:
            result["readiness_probe"] = self.readiness_probe.__dict__
        if self.instance_count is not None:
            result["instance_count"] = self.instance_count
        if self.instance_type:
            result["instance_type"] = self.instance_type
        if self.model:
            result["model"] = self.model
        if self.code_configuration:
            result["code_configuration"] = self.code_configuration
        if self.environment_variables:
            result["environment_variables"] = self.environment_variables
        if self.app_insights_enabled is not None:
            result["app_insights_enabled"] = self.app_insights_enabled
            
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
        environment_id = (get_value(properties, "environmentId") or 
                         get_value(properties, "environment") or 
                         get_value(obj, "environment_id") or
                         get_value(obj, "environment"))
        environment_variables = get_value(properties, "environmentVariables") or get_value(obj, "environment_variables")
        request_settings = get_value(properties, "requestSettings") or get_value(obj, "request_settings")
        liveness_probe = get_value(properties, "livenessProbe") or get_value(obj, "liveness_probe")
        readiness_probe = get_value(properties, "readinessProbe") or get_value(obj, "readiness_probe")
        instance_count = get_value(properties, "instanceCount") or get_value(obj, "instance_count")
        default_instance_type = get_value(properties, "defaultInstanceType") or get_value(obj, "default_instance_type")
        deployment_template_type = get_value(properties, "deploymentTemplateType") or get_value(obj, "deployment_template_type")
        
        # Extract additional fields
        allowed_instance_types = get_value(properties, "allowedInstanceType") or get_value(obj, "allowed_instance_types")
        scoring_port = get_value(properties, "scoringPort") or get_value(obj, "scoring_port")
        scoring_path = get_value(properties, "scoringPath") or get_value(obj, "scoring_path")
        model_mount_path = get_value(properties, "modelMountPath") or get_value(obj, "model_mount_path")
        stage = get_value(properties, "stage") or get_value(obj, "stage")
        
        # Handle string representations from properties - they come as JSON strings
        import json
        import ast
        
        # Parse tags if it's a string
        if isinstance(tags, str):
            try:
                tags = json.loads(tags) if tags and tags != '{}' else {}
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
        
        # Convert request_settings to OnlineRequestSettings object
        request_settings_obj = None
        if request_settings:
            try:
                if isinstance(request_settings, str):
                    # Parse the string representation from properties
                    request_settings_dict = ast.literal_eval(request_settings)
                    timeout_val = request_settings_dict.get("requestTimeout", "00:01:30")
                    max_concurrent = request_settings_dict.get("maxConcurrentRequestsPerInstance", 1)
                    
                    # Convert HH:MM:SS to seconds, then to milliseconds
                    timeout_seconds = hhmmss_to_seconds(timeout_val) if isinstance(timeout_val, str) else 90
                    
                    request_settings_obj = OnlineRequestSettings(
                        request_timeout_ms=timeout_seconds * 1000,
                        max_concurrent_requests_per_instance=max_concurrent
                    )
                elif hasattr(request_settings, '__dict__'):
                    # It's already a REST client object, convert to our object
                    timeout_ms = getattr(request_settings, 'request_timeout_ms', None)
                    max_concurrent = getattr(request_settings, 'max_concurrent_requests_per_instance', 1)
                    
                    request_settings_obj = OnlineRequestSettings(
                        request_timeout_ms=timeout_ms,
                        max_concurrent_requests_per_instance=max_concurrent
                    )
                elif isinstance(request_settings, dict):
                    # It's a dict, extract fields
                    timeout_val = request_settings.get("requestTimeout", "00:01:30")
                    max_concurrent = request_settings.get("maxConcurrentRequestsPerInstance", 1)
                    
                    # Convert HH:MM:SS to seconds, then to milliseconds
                    timeout_seconds = hhmmss_to_seconds(timeout_val) if isinstance(timeout_val, str) else 90
                    
                    request_settings_obj = OnlineRequestSettings(
                        request_timeout_ms=timeout_seconds * 1000,
                        max_concurrent_requests_per_instance=max_concurrent
                    )
            except (AttributeError, ValueError, TypeError, SyntaxError):
                request_settings_obj = None
        
        # Convert probe settings to ProbeSettings objects
        liveness_probe_obj = None
        if liveness_probe:
            try:
                if isinstance(liveness_probe, str):
                    # Parse the string representation from properties
                    liveness_probe_dict = ast.literal_eval(liveness_probe)
                    
                    # Convert from backend format
                    converted_liveness = convert_probe_durations_from_backend(liveness_probe_dict)
                    
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    liveness_probe_obj = ProbeSettings(
                        failure_threshold=converted_liveness.get('failureThreshold'),
                        success_threshold=converted_liveness.get('successThreshold'),
                        timeout=converted_liveness.get('timeout'),
                        period=converted_liveness.get('period'),
                        initial_delay=converted_liveness.get('initialDelay'),
                        scheme=liveness_probe_dict.get('scheme'),
                        method=liveness_probe_dict.get('httpMethod') or liveness_probe_dict.get('method'),
                        path=liveness_probe_dict.get('path'),
                        port=liveness_probe_dict.get('port')
                    )
                elif hasattr(liveness_probe, '__dict__'):
                    # It's already a REST client ProbeSettings object, create our version manually
                    # to avoid deserialization issues with duration formats
                    failure_threshold = getattr(liveness_probe, 'failure_threshold', None)
                    success_threshold = getattr(liveness_probe, 'success_threshold', None)
                    timeout_str = getattr(liveness_probe, 'timeout_seconds', None)
                    period_str = getattr(liveness_probe, 'period_seconds', None) 
                    initial_delay_str = getattr(liveness_probe, 'initial_delay_seconds', None)
                    
                    # Convert HH:MM:SS format to seconds for user-friendly interface
                    timeout_sec = hhmmss_to_seconds(timeout_str) if timeout_str else None
                    period_sec = hhmmss_to_seconds(period_str) if period_str else None
                    initial_delay_sec = hhmmss_to_seconds(initial_delay_str) if initial_delay_str else None
                    
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    liveness_probe_obj = ProbeSettings(
                        failure_threshold=failure_threshold,
                        success_threshold=success_threshold,
                        timeout=timeout_sec,
                        period=period_sec,
                        initial_delay=initial_delay_sec,
                        scheme=getattr(liveness_probe, 'scheme', None),
                        method=getattr(liveness_probe, 'method', None),
                        path=getattr(liveness_probe, 'path', None),
                        port=getattr(liveness_probe, 'port', None)
                    )
                elif isinstance(liveness_probe, dict):
                    # Convert duration fields from HH:MM:SS to seconds
                    converted_liveness = convert_probe_durations_from_backend(liveness_probe)
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    liveness_probe_obj = ProbeSettings(
                        failure_threshold=converted_liveness.get('failureThreshold'),
                        success_threshold=converted_liveness.get('successThreshold'),
                        timeout=converted_liveness.get('timeout'),
                        period=converted_liveness.get('period'),
                        initial_delay=converted_liveness.get('initialDelay'),
                        scheme=liveness_probe.get('scheme'),
                        method=liveness_probe.get('httpMethod') or liveness_probe.get('method'),
                        path=liveness_probe.get('path'),
                        port=liveness_probe.get('port')
                    )
            except (AttributeError, ValueError, TypeError, SyntaxError):
                liveness_probe_obj = None
            
        readiness_probe_obj = None
        if readiness_probe:
            try:
                if isinstance(readiness_probe, str):
                    # Parse the string representation from properties
                    readiness_probe_dict = ast.literal_eval(readiness_probe)
                    
                    # Convert from backend format
                    converted_readiness = convert_probe_durations_from_backend(readiness_probe_dict)
                    
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    readiness_probe_obj = ProbeSettings(
                        failure_threshold=converted_readiness.get('failureThreshold'),
                        success_threshold=converted_readiness.get('successThreshold'),
                        timeout=converted_readiness.get('timeout'),
                        period=converted_readiness.get('period'),
                        initial_delay=converted_readiness.get('initialDelay'),
                        scheme=readiness_probe_dict.get('scheme'),
                        method=readiness_probe_dict.get('httpMethod') or readiness_probe_dict.get('method'),
                        path=readiness_probe_dict.get('path'),
                        port=readiness_probe_dict.get('port')
                    )
                elif hasattr(readiness_probe, '__dict__'):
                    # It's already a REST client ProbeSettings object, create our version manually
                    # to avoid deserialization issues with duration formats
                    failure_threshold = getattr(readiness_probe, 'failure_threshold', None)
                    success_threshold = getattr(readiness_probe, 'success_threshold', None)
                    timeout_str = getattr(readiness_probe, 'timeout_seconds', None)
                    period_str = getattr(readiness_probe, 'period_seconds', None)
                    initial_delay_str = getattr(readiness_probe, 'initial_delay_seconds', None)
                    
                    # Convert HH:MM:SS format to seconds for user-friendly interface
                    timeout_sec = hhmmss_to_seconds(timeout_str) if timeout_str else None
                    period_sec = hhmmss_to_seconds(period_str) if period_str else None
                    initial_delay_sec = hhmmss_to_seconds(initial_delay_str) if initial_delay_str else None
                    
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    readiness_probe_obj = ProbeSettings(
                        failure_threshold=failure_threshold,
                        success_threshold=success_threshold,
                        timeout=timeout_sec,
                        period=period_sec,
                        initial_delay=initial_delay_sec,
                        scheme=getattr(readiness_probe, 'scheme', None),
                        method=getattr(readiness_probe, 'method', None),
                        path=getattr(readiness_probe, 'path', None),
                        port=getattr(readiness_probe, 'port', None)
                    )
                elif isinstance(readiness_probe, dict):
                    # Convert duration fields from HH:MM:SS to seconds
                    converted_readiness = convert_probe_durations_from_backend(readiness_probe)
                    from azure.ai.ml.entities._deployment.deployment_template_settings import ProbeSettings
                    readiness_probe_obj = ProbeSettings(
                        failure_threshold=converted_readiness.get('failureThreshold'),
                        success_threshold=converted_readiness.get('successThreshold'),
                        timeout=converted_readiness.get('timeout'),
                        period=converted_readiness.get('period'),
                        initial_delay=converted_readiness.get('initialDelay'),
                        scheme=readiness_probe.get('scheme'),
                        method=readiness_probe.get('httpMethod') or readiness_probe.get('method'),
                        path=readiness_probe.get('path'),
                        port=readiness_probe.get('port')
                    )
            except (AttributeError, ValueError, TypeError, SyntaxError):
                readiness_probe_obj = None
        
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
            instance_type=default_instance_type,  # Use default instance type
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
        )
        
        # Mark this template as coming from the service so it excludes immutable fields on updates
        template._from_service = True
        
        # Store additional fields from the REST response that may be needed
        template.environment_id = environment_id  # Store for retrieval
        template.template = get_value(obj, "template", deployment_template_type)  # Alternative name for deployment_template_type
        template.code_id = get_value(obj, "code_id")  # Store code_id if present
        
        # Store original values of immutable fields to preserve them during updates
        # IMPORTANT: Store the raw values from the API response, not the converted objects
        template._original_immutable_fields = {
            'environment_id': environment_id,
            'environment_variables': environment_variables,
            'request_settings': request_settings,  # Store original REST object, not converted
            'liveness_probe': liveness_probe,      # Store original REST object, not converted
            'readiness_probe': readiness_probe,    # Store original REST object, not converted
            'instance_count': instance_count,
            'default_instance_type': default_instance_type,
            'model': get_value(obj, "model"),
            'code_configuration': get_value(obj, "code_configuration"),
            'app_insights_enabled': get_value(obj, "app_insights_enabled"),
            'deployment_template_type': deployment_template_type,
            'allowed_instance_types': allowed_instance_types,
            'scoring_port': scoring_port,
            'scoring_path': scoring_path,
            'model_mount_path': model_mount_path,
            'stage': stage,  # Store stage for archive/restore functionality
        }
        
        return template

    def _to_rest_object(self, **kwargs) -> dict:
        """Convert to REST object format for API submission.
        
        :param exclude_immutable_fields: If True, excludes immutable fields that cannot be updated.
                                       If None, automatically determines based on whether template came from service.
        :type exclude_immutable_fields: bool
        """
        # Auto-detect if we should preserve original immutable fields (if template came from service)
        preserve_original_immutable = getattr(self, '_from_service', False)
        original_fields = getattr(self, '_original_immutable_fields', {})
            
        result = {
            "name": self.name,
            "version": self.version,
        }
        
        # Always include mutable fields (description and tags)
        if self.description:
            result["description"] = self.description
            
        if self.tags:
            result["tags"] = dict(self.tags)
            
        if self.properties:
            result["properties"] = dict(self.properties)
            
        # For templates from service, use original values for immutable fields
        # For new templates, use current values
        if preserve_original_immutable and original_fields:
            # Use original immutable field values to avoid modification errors
            environment_id = original_fields.get('environment_id')
            environment_variables = original_fields.get('environment_variables')
            
            # Use the original REST objects directly, not the converted SDK objects
            original_request_settings = original_fields.get('request_settings')
            original_liveness_probe = original_fields.get('liveness_probe')
            original_readiness_probe = original_fields.get('readiness_probe')
            
            instance_count = original_fields.get('instance_count')
            default_instance_type = original_fields.get('default_instance_type')
            model = original_fields.get('model')
            code_configuration = original_fields.get('code_configuration')
            app_insights_enabled = original_fields.get('app_insights_enabled')
            deployment_template_type = original_fields.get('deployment_template_type')
            allowed_instance_types = original_fields.get('allowed_instance_types')
            scoring_port = original_fields.get('scoring_port')
            scoring_path = original_fields.get('scoring_path')
            model_mount_path = original_fields.get('model_mount_path')
            stage = self.stage  # Always use current stage value for archive/restore functionality
        else:
            # Use current values for new templates
            environment_id = str(self.environment) if self.environment else None
            environment_variables = dict(self.environment_variables) if self.environment_variables else None
            original_request_settings = None  # Will be converted from SDK object
            original_liveness_probe = None    # Will be converted from SDK object
            original_readiness_probe = None   # Will be converted from SDK object
            instance_count = self.instance_count
            default_instance_type = self.instance_type
            model = self.model
            code_configuration = self.code_configuration
            app_insights_enabled = self.app_insights_enabled
            deployment_template_type = self.deployment_template_type
            allowed_instance_types = self.allowed_instance_types
            scoring_port = self.scoring_port
            scoring_path = self.scoring_path
            model_mount_path = self.model_mount_path
            stage = self.stage
            
        # Include immutable fields with appropriate values
        if environment_id:
            result["environmentId"] = environment_id  # Use environmentId for API (camelCase)
            
        if environment_variables:
            result["environmentVariables"] = environment_variables  # Use environmentVariables for API (camelCase)
            
        if instance_count is not None:
            result["instanceCount"] = instance_count  # Use instanceCount for API (camelCase)
            
        if default_instance_type:
            result["defaultInstanceType"] = default_instance_type  # Use defaultInstanceType for API (camelCase)
            result["allowedInstanceType"] = [default_instance_type]  # Also set allowedInstanceType (camelCase)
            
        # Convert request settings to backend format
        if preserve_original_immutable and original_request_settings:
            # Use the original REST object directly 
            if isinstance(original_request_settings, dict):
                # It's already a dict, use it as-is
                result["requestSettings"] = original_request_settings
            elif hasattr(original_request_settings, '__dict__'):
                # It's a REST object, need to extract the exact format that came from API
                # Check if it has the backend field names
                if hasattr(original_request_settings, 'request_timeout') or hasattr(original_request_settings, 'requestTimeout'):
                    # Use the exact field names from the original object
                    request_settings_dict = {}
                    
                    # Try different possible field name variations
                    timeout_val = (getattr(original_request_settings, 'request_timeout', None) or 
                                 getattr(original_request_settings, 'requestTimeout', None) or
                                 getattr(original_request_settings, 'request_timeout_ms', None))
                    
                    max_concurrent_val = (getattr(original_request_settings, 'max_concurrent_requests_per_instance', None) or
                                        getattr(original_request_settings, 'maxConcurrentRequestsPerInstance', None))
                    
                    if timeout_val is not None:
                        # If it's already in HH:MM:SS format, keep it
                        if isinstance(timeout_val, str) and ':' in timeout_val:
                            request_settings_dict["requestTimeout"] = timeout_val
                        elif isinstance(timeout_val, int):
                            # Convert from milliseconds to seconds to HH:MM:SS
                            timeout_seconds = timeout_val // 1000 if timeout_val > 1000 else timeout_val
                            request_settings_dict["requestTimeout"] = seconds_to_hhmmss(timeout_seconds)
                        
                    if max_concurrent_val is not None:
                        request_settings_dict["maxConcurrentRequestsPerInstance"] = max_concurrent_val
                        
                    result["requestSettings"] = request_settings_dict
                else:
                    # Fallback: convert from our SDK object format
                    request_settings_dict = {}
                    if hasattr(original_request_settings, 'request_timeout_ms'):
                        if isinstance(original_request_settings.request_timeout_ms, str):
                            # It's already in HH:MM:SS format, use as is
                            request_settings_dict["requestTimeout"] = original_request_settings.request_timeout_ms
                        else:
                            # Convert milliseconds to seconds, then to HH:MM:SS format
                            timeout_seconds = original_request_settings.request_timeout_ms // 1000
                            request_settings_dict["requestTimeout"] = seconds_to_hhmmss(timeout_seconds)
                    if hasattr(original_request_settings, 'max_concurrent_requests_per_instance'):
                        request_settings_dict["maxConcurrentRequestsPerInstance"] = original_request_settings.max_concurrent_requests_per_instance
                    result["requestSettings"] = request_settings_dict
        elif self.request_settings:
            # Convert current SDK object for new templates
            request_settings_dict = {}
            
            if hasattr(self.request_settings, 'request_timeout_ms') and self.request_settings.request_timeout_ms:
                # Handle both string (HH:MM:SS) and integer (milliseconds) formats
                if isinstance(self.request_settings.request_timeout_ms, str):
                    # It's already in HH:MM:SS format, use as is
                    request_settings_dict["requestTimeout"] = self.request_settings.request_timeout_ms
                else:
                    # Convert milliseconds to seconds, then to HH:MM:SS format for backend
                    timeout_seconds = self.request_settings.request_timeout_ms // 1000
                    request_settings_dict["requestTimeout"] = seconds_to_hhmmss(timeout_seconds)
                
            if hasattr(self.request_settings, 'max_concurrent_requests_per_instance'):
                request_settings_dict["maxConcurrentRequestsPerInstance"] = self.request_settings.max_concurrent_requests_per_instance
                
            result["requestSettings"] = request_settings_dict
            
        # Convert probe settings to backend format (seconds -> HH:MM:SS)
        if preserve_original_immutable and original_liveness_probe:
            # Use the original REST object directly
            if isinstance(original_liveness_probe, dict):
                result["livenessProbe"] = original_liveness_probe
            elif hasattr(original_liveness_probe, '__dict__'):
                # It's a REST object, preserve its exact structure
                liveness_dict = {}
                
                # Try to preserve the exact field names and values from the original object
                all_attrs = dir(original_liveness_probe)
                for attr in all_attrs:
                    if not attr.startswith('_') and not callable(getattr(original_liveness_probe, attr)):
                        value = getattr(original_liveness_probe, attr, None)
                        if value is not None:
                            # Convert snake_case to camelCase for API
                            if attr == 'initial_delay_seconds':
                                liveness_dict['initialDelay'] = value
                            elif attr == 'period_seconds':
                                liveness_dict['period'] = value
                            elif attr == 'timeout_seconds':
                                liveness_dict['timeout'] = value
                            elif attr == 'failure_threshold':
                                liveness_dict['failureThreshold'] = value
                            elif attr == 'success_threshold':
                                liveness_dict['successThreshold'] = value
                            else:
                                # Keep other fields as-is
                                liveness_dict[attr] = value
                                
                result["livenessProbe"] = liveness_dict
        elif self.liveness_probe:
            try:
                liveness_dict = convert_probe_durations_to_backend({
                    "initial_delay": getattr(self.liveness_probe, 'initial_delay', None),
                    "period": getattr(self.liveness_probe, 'period', None), 
                    "timeout": getattr(self.liveness_probe, 'timeout', None),
                    "failure_threshold": getattr(self.liveness_probe, 'failure_threshold', None),
                    "success_threshold": getattr(self.liveness_probe, 'success_threshold', None),
                    "scheme": getattr(self.liveness_probe, 'scheme', None),
                    "method": getattr(self.liveness_probe, 'method', None),
                    "path": getattr(self.liveness_probe, 'path', None),
                    "port": getattr(self.liveness_probe, 'port', None), 
                })
                result["livenessProbe"] = liveness_dict
            except (AttributeError, TypeError):
                pass  # Skip if probe object is malformed
            
        if preserve_original_immutable and original_readiness_probe:
            # Use the original REST object directly
            if isinstance(original_readiness_probe, dict):
                result["readinessProbe"] = original_readiness_probe
            elif hasattr(original_readiness_probe, '__dict__'):
                # It's a REST object, preserve its exact structure
                readiness_dict = {}
                
                # Try to preserve the exact field names and values from the original object
                all_attrs = dir(original_readiness_probe)
                for attr in all_attrs:
                    if not attr.startswith('_') and not callable(getattr(original_readiness_probe, attr)):
                        value = getattr(original_readiness_probe, attr, None)
                        if value is not None:
                            # Convert snake_case to camelCase for API
                            if attr == 'initial_delay_seconds':
                                readiness_dict['initialDelay'] = value
                            elif attr == 'period_seconds':
                                readiness_dict['period'] = value
                            elif attr == 'timeout_seconds':
                                readiness_dict['timeout'] = value
                            elif attr == 'failure_threshold':
                                readiness_dict['failureThreshold'] = value
                            elif attr == 'success_threshold':
                                readiness_dict['successThreshold'] = value
                            else:
                                # Keep other fields as-is
                                readiness_dict[attr] = value
                                
                result["readinessProbe"] = readiness_dict
        elif self.readiness_probe:
            try:
                readiness_dict = convert_probe_durations_to_backend({
                    "initial_delay": getattr(self.readiness_probe, 'initial_delay', None),
                    "period": getattr(self.readiness_probe, 'period', None),
                    "timeout": getattr(self.readiness_probe, 'timeout', None), 
                    "failure_threshold": getattr(self.readiness_probe, 'failure_threshold', None),
                    "success_threshold": getattr(self.readiness_probe, 'success_threshold', None),
                    "scheme": getattr(self.readiness_probe, 'scheme', None),
                    "method": getattr(self.readiness_probe, 'method', None),
                    "path": getattr(self.readiness_probe, 'path', None),
                    "port": getattr(self.readiness_probe, 'port', None),
                })
                result["readinessProbe"] = readiness_dict
            except (AttributeError, TypeError):
                pass  # Skip if probe object is malformed
            
        # Add other optional fields
        if model:
            result["model"] = model
            
        if code_configuration:
            result["code_configuration"] = code_configuration
            
        if app_insights_enabled is not None:
            result["app_insights_enabled"] = app_insights_enabled
            
        if allowed_instance_types:
            result["allowed_instance_types"] = allowed_instance_types
            
        if scoring_port is not None:
            result["scoringPort"] = scoring_port  # Use camelCase for API
            
        if scoring_path:
            result["scoringPath"] = scoring_path  # Use camelCase for API
            
        if model_mount_path:
            result["modelMountPath"] = model_mount_path  # Use camelCase for API
            
        # NOTE: Do NOT include 'type' field - it's not supported by the REST API
        # The API only supports 'deployment_template_type' which maps to 'deploymentTemplateType' in JSON
        if deployment_template_type:
            result["deploymentTemplateType"] = deployment_template_type  # Use camelCase for API
            
        # Add stage for archive/restore functionality
        if stage:
            result["stage"] = stage
            
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
        if hasattr(self, 'environment_id') and self.environment_id:
            result["environmentId"] = self.environment_id
        elif self.environment:
            result["environmentId"] = str(self.environment)
        
        # Add metadata fields if available
        if hasattr(self, 'created_by') and self.created_by:
            result["createdBy"] = self.created_by
        if hasattr(self, 'created_time') and self.created_time:
            result["createdTime"] = self.created_time
        if hasattr(self, 'modified_time') and self.modified_time:
            result["modifiedTime"] = self.modified_time
        if hasattr(self, 'capabilities'):
            result["capabilities"] = self.capabilities or []
        
        # Add environment variables
        if self.environment_variables:
            result["environmentVariables"] = self.environment_variables
        
        # Add model mount path
        if self.model_mount_path:
            result["modelMountPath"] = self.model_mount_path
        
        # Add request settings
        if self.request_settings:
            request_dict = {}
            if hasattr(self.request_settings, 'request_timeout_ms') and self.request_settings.request_timeout_ms:
                # Convert to HH:MM:SS format
                if isinstance(self.request_settings.request_timeout_ms, str):
                    request_dict["requestTimeout"] = self.request_settings.request_timeout_ms
                else:
                    # Convert milliseconds to seconds, then to HH:MM:SS
                    timeout_seconds = self.request_settings.request_timeout_ms // 1000
                    hours = timeout_seconds // 3600
                    minutes = (timeout_seconds % 3600) // 60
                    seconds = timeout_seconds % 60
                    request_dict["requestTimeout"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            if hasattr(self.request_settings, 'max_concurrent_requests_per_instance') and self.request_settings.max_concurrent_requests_per_instance:
                request_dict["maxConcurrentRequestsPerInstance"] = self.request_settings.max_concurrent_requests_per_instance
            
            if request_dict:
                result["requestSettings"] = request_dict
        
        # Add liveness probe
        if self.liveness_probe:
            probe_dict = {}
            if hasattr(self.liveness_probe, 'initial_delay') and self.liveness_probe.initial_delay is not None:
                # Convert seconds to HH:MM:SS format
                seconds = self.liveness_probe.initial_delay
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["initialDelay"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.liveness_probe, 'period') and self.liveness_probe.period is not None:
                seconds = self.liveness_probe.period
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["period"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.liveness_probe, 'timeout') and self.liveness_probe.timeout is not None:
                seconds = self.liveness_probe.timeout
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["timeout"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.liveness_probe, 'failure_threshold') and self.liveness_probe.failure_threshold is not None:
                probe_dict["failureThreshold"] = self.liveness_probe.failure_threshold
            
            if hasattr(self.liveness_probe, 'success_threshold') and self.liveness_probe.success_threshold is not None:
                probe_dict["successThreshold"] = self.liveness_probe.success_threshold
            
            if hasattr(self.liveness_probe, 'path') and self.liveness_probe.path:
                probe_dict["path"] = self.liveness_probe.path
            
            if hasattr(self.liveness_probe, 'port') and self.liveness_probe.port is not None:
                probe_dict["port"] = self.liveness_probe.port
            
            if hasattr(self.liveness_probe, 'scheme') and self.liveness_probe.scheme:
                probe_dict["scheme"] = self.liveness_probe.scheme.lower()
            
            if hasattr(self.liveness_probe, 'method') and self.liveness_probe.method:
                probe_dict["httpMethod"] = self.liveness_probe.method
            
            if probe_dict:
                result["livenessProbe"] = probe_dict
        
        # Add readiness probe (similar to liveness probe)
        if self.readiness_probe:
            probe_dict = {}
            if hasattr(self.readiness_probe, 'initial_delay') and self.readiness_probe.initial_delay is not None:
                seconds = self.readiness_probe.initial_delay
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["initialDelay"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.readiness_probe, 'period') and self.readiness_probe.period is not None:
                seconds = self.readiness_probe.period
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["period"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.readiness_probe, 'timeout') and self.readiness_probe.timeout is not None:
                seconds = self.readiness_probe.timeout
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                secs = seconds % 60
                probe_dict["timeout"] = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            
            if hasattr(self.readiness_probe, 'failure_threshold') and self.readiness_probe.failure_threshold is not None:
                probe_dict["failureThreshold"] = self.readiness_probe.failure_threshold
            
            if hasattr(self.readiness_probe, 'success_threshold') and self.readiness_probe.success_threshold is not None:
                probe_dict["successThreshold"] = self.readiness_probe.success_threshold
            
            if hasattr(self.readiness_probe, 'path') and self.readiness_probe.path:
                probe_dict["path"] = self.readiness_probe.path
            
            if hasattr(self.readiness_probe, 'port') and self.readiness_probe.port is not None:
                probe_dict["port"] = self.readiness_probe.port
            
            if hasattr(self.readiness_probe, 'scheme') and self.readiness_probe.scheme:
                probe_dict["scheme"] = self.readiness_probe.scheme.lower()
            
            if hasattr(self.readiness_probe, 'method') and self.readiness_probe.method:
                probe_dict["httpMethod"] = self.readiness_probe.method
            
            if probe_dict:
                result["readinessProbe"] = probe_dict
        
        # Add instance configuration
        if hasattr(self, 'allowed_instance_types') and self.allowed_instance_types:
            result["allowedInstanceType"] = self.allowed_instance_types
        if self.instance_type:
            result["defaultInstanceType"] = self.instance_type
        if self.instance_count is not None:
            result["instanceCount"] = self.instance_count
        
        # Add scoring configuration
        if self.scoring_path:
            result["scoringPath"] = self.scoring_path
        if self.scoring_port is not None:
            result["scoringPort"] = self.scoring_port
        
        return result
    
    def __str__(self) -> str:
        """Return a JSON string representation of the deployment template."""
        import json
        return json.dumps(self._to_dict(), indent=2)
    
    def __repr__(self) -> str:
        """Return a JSON string representation of the deployment template."""
        return self.__str__()

