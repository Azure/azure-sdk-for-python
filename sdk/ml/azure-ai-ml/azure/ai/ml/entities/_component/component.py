# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
import uuid
from contextlib import contextmanager
from os import PathLike
from pathlib import Path
from typing import IO, AnyStr, Dict, Optional, Tuple, Union

from marshmallow import INCLUDE

from ..._restclient.v2022_10_01.models import (
    ComponentContainer,
    ComponentContainerProperties,
    ComponentVersion,
    ComponentVersionProperties,
)
from ..._schema import PathAwareSchema
from ..._schema.component import ComponentSchema
from ..._utils._arm_id_utils import is_ARM_id_for_resource, is_registry_id_for_resource
from ..._utils.utils import dump_yaml_to_file, hash_dict, is_private_preview_enabled
from ...constants._common import (
    ANONYMOUS_COMPONENT_NAME,
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    REGISTRY_URI_FORMAT,
    SOURCE_PATH_CONTEXT_KEY,
    AzureMLResourceType,
    CommonYamlFields,
)
from ...constants._component import ComponentSource, IOConstants, NodeType
from ...entities._assets import Code
from ...entities._assets.asset import Asset
from ...entities._inputs_outputs import Input, Output
from ...entities._mixins import TelemetryMixin, YamlTranslatableMixin
from ...entities._system_data import SystemData
from ...entities._util import find_type_in_override
from ...entities._validation import MutableValidationResult, RemoteValidatableMixin, SchemaValidatableMixin
from ...exceptions import ErrorCategory, ErrorTarget, ValidationException
from .code import ComponentIgnoreFile

# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use id/type as argument name


COMPONENT_PLACEHOLDER = "COMPONENT_PLACEHOLDER"


class Component(
    Asset,
    RemoteValidatableMixin,
    TelemetryMixin,
    YamlTranslatableMixin,
    SchemaValidatableMixin,
):
    """Base class for component version, used to define a component. Can't be instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param id:  Global id of the resource, Azure Resource Manager ID.
    :type id: str
    :param type:  Type of the command, supported is 'command'.
    :param type:  Type of the command, supported is 'command'.
    :type type: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param properties: Internal use only.
    :type properties: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param is_deterministic: Whether the component is deterministic.
    :type is_deterministic: bool
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param yaml_str: The yaml string of the component.
    :type yaml_str: str
    :param _schema: Schema of the component.
    :type _schema: str
    :param creation_context: Creation metadata of the component.
    :type creation_context: ~azure.ai.ml.entities.SystemData
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Component cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        version: Optional[str] = None,
        id: Optional[str] = None,
        type: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        display_name: Optional[str] = None,
        is_deterministic: bool = True,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        yaml_str: Optional[str] = None,
        _schema: Optional[str] = None,
        creation_context: Optional[SystemData] = None,
        **kwargs,
    ):
        self._intellectual_property = kwargs.pop("intellectual_property", None)
        # Setting this before super init because when asset init version, _auto_increment_version's value may change
        self._auto_increment_version = kwargs.pop("auto_increment", False)
        # Get source from id first, then kwargs.
        self._source = (
            self._resolve_component_source_from_id(id) if id else kwargs.pop("_source", ComponentSource.CLASS)
        )
        # use ANONYMOUS_COMPONENT_NAME instead of guid
        is_anonymous = kwargs.pop("is_anonymous", False)
        if not name and version is None:
            name = ANONYMOUS_COMPONENT_NAME
            version = "1"
            is_anonymous = True

        super().__init__(
            name=name,
            version=version,
            id=id,
            description=description,
            tags=tags,
            properties=properties,
            creation_context=creation_context,
            is_anonymous=is_anonymous,
            base_path=kwargs.pop("base_path", None),
            source_path=kwargs.pop("source_path", None),
        )
        # store kwargs to self._other_parameter instead of pop to super class to allow component have extra
        # fields not defined in current schema.

        inputs = inputs if inputs else {}
        outputs = outputs if outputs else {}

        self._schema = _schema
        self._type = type
        self._display_name = display_name
        self._is_deterministic = is_deterministic
        self._inputs = self._build_io(inputs, is_input=True)
        self._outputs = self._build_io(outputs, is_input=False)
        # Store original yaml
        self._yaml_str = yaml_str
        self._other_parameter = kwargs

    @property
    def _func(self):
        from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

        # validate input/output names before creating component function
        validation_result = self._validate_io_names(self.inputs)
        validation_result.merge_with(self._validate_io_names(self.outputs))
        validation_result.try_raise(error_target=self._get_validation_error_target())

        return _generate_component_function(self)

    @property
    def type(self) -> str:
        """Type of the component, default is 'command'.

        :return: Type of the component.
        :rtype: str
        """
        return self._type

    @property
    def display_name(self) -> str:
        """Display name of the component.

        :return: Display name of the component.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, custom_display_name):
        """Set display_name of the component."""
        self._display_name = custom_display_name

    @property
    def is_deterministic(self) -> bool:
        """Whether the component is deterministic.

        :return: Whether the component is deterministic
        :rtype: bool
        """
        return self._is_deterministic

    @property
    def inputs(self) -> Dict:
        """Inputs of the component.

        :return: Inputs of the component.
        :rtype: dict
        """
        return self._inputs

    @property
    def outputs(self) -> Dict:
        """Outputs of the component.

        :return: Outputs of the component.
        :rtype: dict
        """
        return self._outputs

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        if value:
            if not isinstance(value, str):
                msg = f"Component version must be a string, not type {type(value)}."
                raise ValidationException(
                    message=msg,
                    target=ErrorTarget.COMPONENT,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.USER_ERROR,
                )
        self._version = value
        self._auto_increment_version = self.name and not self._version

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs) -> None:
        """Dump the component content into a file in yaml format.

        :param dest: The destination to receive this component's content.
            Must be either a path to a local file, or an already-open file stream.
            If dest is a file path, a new file will be created,
            and an exception is raised if the file exists.
            If dest is an open file, the file will be written to directly,
            and an exception will be raised if the file is not writable.
        :type dest: Union[PathLike, str, IO[AnyStr]]
        """
        path = kwargs.pop("path", None)
        yaml_serialized = self._to_dict()
        dump_yaml_to_file(dest, yaml_serialized, default_flow_style=False, path=path, **kwargs)

    @staticmethod
    def _resolve_component_source_from_id(id):
        """Resolve the component source from id."""
        if id is None:
            return ComponentSource.CLASS
        # Consider default is workspace source, as
        # azureml: prefix will be removed for arm versioned id.
        return (
            ComponentSource.REMOTE_REGISTRY
            if id.startswith(REGISTRY_URI_FORMAT)
            else ComponentSource.REMOTE_WORKSPACE_COMPONENT
        )

    @classmethod
    def _validate_io_names(cls, io_dict: Dict, raise_error=False) -> MutableValidationResult:
        """Validate input/output names, raise exception if invalid."""
        validation_result = cls._create_empty_validation_result()
        lower2original_kwargs = {}

        for name in io_dict.keys():
            if re.match(IOConstants.VALID_KEY_PATTERN, name) is None:
                msg = "{!r} is not a valid parameter name, must be composed letters, numbers, and underscores."
                validation_result.append_error(message=msg.format(name), yaml_path=f"inputs.{name}")
            # validate name conflict
            lower_key = name.lower()
            if lower_key in lower2original_kwargs:
                msg = "Invalid component input names {!r} and {!r}, which are equal ignore case."
                validation_result.append_error(
                    message=msg.format(name, lower2original_kwargs[lower_key]), yaml_path=f"inputs.{name}"
                )
            else:
                lower2original_kwargs[lower_key] = name
        return validation_result.try_raise(error_target=cls._get_validation_error_target(), raise_error=raise_error)

    @classmethod
    def _build_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool):
        component_io = {}
        for name, port in io_dict.items():
            if is_input:
                component_io[name] = port if isinstance(port, Input) else Input(**port)
            else:
                component_io[name] = port if isinstance(port, Output) else Output(**port)
        return component_io

    @classmethod
    def _create_schema_for_validation(cls, context) -> PathAwareSchema:
        return ComponentSchema(context=context)

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.COMPONENT

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs,
    ) -> "Component":
        data = data or {}
        params_override = params_override or []
        base_path = Path(yaml_path).parent if yaml_path else Path("./")

        type_in_override = find_type_in_override(params_override)

        # type_in_override > type_in_yaml > default (command)
        if type_in_override is None:
            type_in_override = data.get(CommonYamlFields.TYPE, NodeType.COMMAND)
        data[CommonYamlFields.TYPE] = type_in_override

        from azure.ai.ml.entities._component.component_factory import component_factory

        create_instance_func, _ = component_factory.get_create_funcs(
            data,
            for_load=True,
        )
        new_instance = create_instance_func()
        # specific keys must be popped before loading with schema using kwargs
        init_kwargs = {
            "yaml_str": kwargs.pop("yaml_str", None),
            "_source": kwargs.pop("_source", ComponentSource.YAML_COMPONENT),
        }
        init_kwargs.update(
            new_instance._load_with_schema(  # pylint: disable=protected-access
                data,
                context={
                    BASE_PATH_CONTEXT_KEY: base_path,
                    SOURCE_PATH_CONTEXT_KEY: yaml_path,
                    PARAMS_OVERRIDE_KEY: params_override,
                },
                unknown=INCLUDE,
                raise_original_exception=True,
                **kwargs,
            )
        )
        new_instance.__init__(
            **init_kwargs,
        )
        # Set base path separately to avoid doing this in post load, as return types of post load are not unified,
        # could be object or dict.
        # base_path in context can be changed in loading, so we use original base_path here.
        new_instance._base_path = base_path
        if yaml_path:
            new_instance._source_path = yaml_path
        return new_instance

    @classmethod
    def _from_container_rest_object(cls, component_container_rest_object: ComponentContainer) -> "Component":
        component_container_details: ComponentContainerProperties = component_container_rest_object.properties
        component = Component(
            id=component_container_rest_object.id,
            name=component_container_rest_object.name,
            description=component_container_details.description,
            creation_context=SystemData._from_rest_object(component_container_rest_object.system_data),
            tags=component_container_details.tags,
            properties=component_container_details.properties,
            type=NodeType._CONTAINER,
            # Set this field to None as it hold a default True in init.
            is_deterministic=None,
        )
        component.latest_version = component_container_details.latest_version
        return component

    @classmethod
    def _from_rest_object(cls, obj: ComponentVersion) -> "Component":
        # TODO: Remove in PuP with native import job/component type support in MFE/Designer
        # Convert command component back to import component private preview
        component_spec = obj.properties.component_spec
        if component_spec[CommonYamlFields.TYPE] == NodeType.COMMAND and component_spec["command"] == NodeType.IMPORT:
            component_spec[CommonYamlFields.TYPE] = NodeType.IMPORT
            component_spec["source"] = component_spec.pop("inputs")
            component_spec["output"] = component_spec.pop("outputs")["output"]

        # shouldn't block serialization when name is not valid
        # maybe override serialization method for name field?
        from azure.ai.ml.entities._component.component_factory import component_factory

        create_instance_func, _ = component_factory.get_create_funcs(obj.properties.component_spec, for_load=True)

        instance = create_instance_func()
        instance.__init__(**instance._from_rest_object_to_init_params(obj))
        return instance

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: ComponentVersion) -> Dict:
        # Object got from rest data contain _source, we delete it.
        if "_source" in obj.properties.component_spec:
            del obj.properties.component_spec["_source"]

        rest_component_version = obj.properties
        _type = rest_component_version.component_spec[CommonYamlFields.TYPE]

        # inputs/outputs will be parsed by instance._build_io in instance's __init__
        inputs = rest_component_version.component_spec.pop("inputs", {})
        # parse String -> string, Integer -> integer, etc
        for _input in inputs.values():
            _input["type"] = Input._map_from_rest_type(_input["type"])
        outputs = rest_component_version.component_spec.pop("outputs", {})

        origin_name = rest_component_version.component_spec[CommonYamlFields.NAME]
        rest_component_version.component_spec[CommonYamlFields.NAME] = ANONYMOUS_COMPONENT_NAME
        init_kwargs = cls._load_with_schema(rest_component_version.component_spec, unknown=INCLUDE)
        init_kwargs.update(
            dict(
                id=obj.id,
                is_anonymous=rest_component_version.is_anonymous,
                creation_context=obj.system_data,
                inputs=inputs,
                outputs=outputs,
                name=origin_name,
            )
        )

        # remove empty values, because some property only works for specific component, eg: distribution for command
        # note that there is an issue that environment == {} will always be true, so use isinstance here
        return {k: v for k, v in init_kwargs.items() if v is not None and not (isinstance(v, dict) and not v)}

    def _get_anonymous_hash(self) -> str:
        """Return the name of anonymous component.

        same anonymous component(same code and interface) will have same name.
        """
        component_interface_dict = self._to_dict()
        # omit version since anonymous component's version is random guid
        # omit name since name doesn't impact component's uniqueness
        return hash_dict(component_interface_dict, keys_to_omit=["name", "id", "version"])

    @classmethod
    def _get_resource_type(cls) -> str:
        return "Microsoft.MachineLearningServices/workspaces/components/versions"

    def _get_resource_name_version(self) -> Tuple[str, str]:
        if not self.version and not self._auto_increment_version:
            version = str(uuid.uuid4())
        else:
            version = self.version
        return self.name or ANONYMOUS_COMPONENT_NAME, version

    def _validate(self, raise_error=False) -> MutableValidationResult:
        origin_name = self.name
        # skip name validation for anonymous component as ANONYMOUS_COMPONENT_NAME will be used in component creation
        if self._is_anonymous:
            self.name = ANONYMOUS_COMPONENT_NAME
        try:
            return super()._validate(raise_error)
        finally:
            self.name = origin_name

    def _customized_validate(self) -> MutableValidationResult:
        validation_result = super(Component, self)._customized_validate()
        # If private features are enable and component has code value of type str we need to check
        # that it is a valid git path case. Otherwise we should throw a ValidationError
        # saying that the code value is not valid
        # pylint: disable=no-member
        if (
            hasattr(self, "code")
            and self.code is not None
            and isinstance(self.code, str)
            and self.code.startswith("git+")
            and not is_private_preview_enabled()
        ):
            validation_result.append_error(
                message="Not a valid code value: git paths are not supported.",
                yaml_path="code",
            )
        # validate inputs names
        validation_result.merge_with(self._validate_io_names(self.inputs, raise_error=False))
        validation_result.merge_with(self._validate_io_names(self.outputs, raise_error=False))

        return validation_result

    def _get_anonymous_component_name_version(self):
        return ANONYMOUS_COMPONENT_NAME, self._get_anonymous_hash()

    def _get_rest_name_version(self):
        if self._is_anonymous:
            return self._get_anonymous_component_name_version()
        return self.name, self.version

    def _to_rest_object(self) -> ComponentVersion:
        component = self._to_dict()

        # TODO: Remove in PuP with native import job/component type support in MFE/Designer
        # Convert import component to command component private preview
        if component["type"] == NodeType.IMPORT:
            component["type"] = NodeType.COMMAND
            component["inputs"] = component.pop("source")
            component["outputs"] = dict({"output": component.pop("output")})
            # method _to_dict() will remove empty keys
            if "tags" not in component:
                component["tags"] = {}
            component["tags"]["component_type_overwrite"] = NodeType.IMPORT
            component["command"] = NodeType.IMPORT

        # add source type to component rest object
        component["_source"] = self._source
        if self._intellectual_property:
            # hack while full pass through supported is worked on for IPP fields
            component.pop("intellectual_property")
            component["intellectualProperty"] = self._intellectual_property._to_rest_object().serialize()
        properties = ComponentVersionProperties(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersion(properties=properties)
        if self._is_anonymous:
            result.name = ANONYMOUS_COMPONENT_NAME
        else:
            result.name = self.name
        return result

    def _to_dict(self) -> Dict:
        """Dump the command component content into a dictionary."""

        # Replace the name of $schema to schema.
        component_schema_dict = self._dump_for_validation()
        component_schema_dict.pop("base_path", None)

        # TODO: handle other_parameters and remove override from subclass
        return component_schema_dict

    def _get_telemetry_values(self, *args, **kwargs):  # pylint: disable=unused-argument
        # Note: the is_anonymous is not reliable here, create_or_update will log is_anonymous from parameter.
        is_anonymous = self.name is None or ANONYMOUS_COMPONENT_NAME in self.name
        return {"type": self.type, "source": self._source, "is_anonymous": is_anonymous}

    def __call__(self, *args, **kwargs) -> [..., Union["Command", "Parallel"]]:
        """Call ComponentVersion as a function and get a Component object."""
        if args:
            # raise clear error message for unsupported positional args
            if self._func._has_parameters:
                msg = (
                    f"Component function doesn't support positional arguments, got {args} for {self.name}. "
                    f"Please use keyword arguments like: {self._func._func_calling_example}."
                )
            else:
                msg = (
                    "Component function doesn't has any parameters, "
                    f"please make sure component {self.name} has inputs. "
                )
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return self._func(*args, **kwargs)  # pylint: disable=not-callable

    @contextmanager
    def _resolve_local_code(self) -> Optional[Code]:
        """Try to create a Code object pointing to local code and yield it.

        If there is no local code to upload, yield None. Otherwise, yield a Code object pointing to the code.
        """
        if not hasattr(self, "code"):
            yield None
            return

        code = getattr(self, "code")

        if is_ARM_id_for_resource(code, AzureMLResourceType.CODE) or is_registry_id_for_resource(code):
            # arm id can be passed directly
            yield None
        elif isinstance(code, Code):
            # Code object & registry id need to be resolved into arm id
            # note that:
            # 1. Code & CodeOperation are not public for now
            # 2. AnonymousCodeSchema is not supported in Component for now
            # So isinstance(component.code, Code) will always be false, or an exception will be raised
            # in validation stage.
            yield code
        elif isinstance(code, str) and code.startswith("git+"):
            # git also need to be resolved into arm id
            yield Code(path=code, is_remote=True)
        elif code is None:
            # server-side will handle how to run component without a code.
            yield None
        else:
            yield Code(base_path=self._base_path, path=code, ignore_file=ComponentIgnoreFile(code))
