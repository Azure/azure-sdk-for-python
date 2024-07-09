# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
import uuid
from os import PathLike
from pathlib import Path
from typing import IO, TYPE_CHECKING, Any, AnyStr, Callable, Dict, Iterable, Optional, Tuple, Union

from marshmallow import INCLUDE

from ..._restclient.v2024_01_01_preview.models import (
    ComponentContainer,
    ComponentContainerProperties,
    ComponentVersion,
    ComponentVersionProperties,
)
from ..._schema import PathAwareSchema
from ..._schema.component import ComponentSchema
from ..._utils.utils import dump_yaml_to_file, hash_dict
from ...constants._common import (
    ANONYMOUS_COMPONENT_NAME,
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    REGISTRY_URI_FORMAT,
    SOURCE_PATH_CONTEXT_KEY,
    CommonYamlFields,
    SchemaUrl,
)
from ...constants._component import ComponentSource, IOConstants, NodeType
from ...entities._assets.asset import Asset
from ...entities._inputs_outputs import Input, Output
from ...entities._mixins import LocalizableMixin, TelemetryMixin, YamlTranslatableMixin
from ...entities._system_data import SystemData
from ...entities._util import find_type_in_override
from ...entities._validation import MutableValidationResult, PathAwareSchemaValidatableMixin, RemoteValidatableMixin
from ...exceptions import ErrorCategory, ErrorTarget, ValidationException
from .._inputs_outputs import GroupInput

if TYPE_CHECKING:
    from ...entities.builders import BaseNode
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use id/type as argument name


COMPONENT_PLACEHOLDER = "COMPONENT_PLACEHOLDER"


class Component(
    Asset,
    RemoteValidatableMixin,
    TelemetryMixin,
    YamlTranslatableMixin,
    PathAwareSchemaValidatableMixin,
    LocalizableMixin,
):
    """Base class for component version, used to define a component. Can't be instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param id: Global ID of the resource, Azure Resource Manager ID.
    :type id: str
    :param type: Type of the command, supported is 'command'.
    :type type: str
    :param description: Description of the resource.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict
    :param properties: Internal use only.
    :type properties: dict
    :param display_name: Display name of the component.
    :type display_name: str
    :param is_deterministic: Whether the component is deterministic. Defaults to True.
    :type is_deterministic: bool
    :param inputs: Inputs of the component.
    :type inputs: dict
    :param outputs: Outputs of the component.
    :type outputs: dict
    :param yaml_str: The YAML string of the component.
    :type yaml_str: str
    :param _schema: Schema of the component.
    :type _schema: str
    :param creation_context: Creation metadata of the component.
    :type creation_context: ~azure.ai.ml.entities.SystemData
    :param kwargs: Additional parameters for the component.
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
        **kwargs: Any,
    ) -> None:
        self.latest_version = None
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
            base_path=kwargs.pop(BASE_PATH_CONTEXT_KEY, None),
            source_path=kwargs.pop(SOURCE_PATH_CONTEXT_KEY, None),
        )
        # store kwargs to self._other_parameter instead of pop to super class to allow component have extra
        # fields not defined in current schema.

        inputs = inputs if inputs else {}
        outputs = outputs if outputs else {}

        self.name = name
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
    def _func(self) -> Callable[..., "BaseNode"]:
        from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

        # validate input/output names before creating component function
        validation_result = self._validate_io_names(self.inputs)
        validation_result.merge_with(self._validate_io_names(self.outputs))
        self._try_raise(validation_result)

        res: Callable = _generate_component_function(self)
        return res

    @property
    def type(self) -> Optional[str]:
        """Type of the component, default is 'command'.

        :return: Type of the component.
        :rtype: str
        """
        return self._type

    @property
    def display_name(self) -> Optional[str]:
        """Display name of the component.

        :return: Display name of the component.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, custom_display_name: str) -> None:
        """Set display_name of the component.

        :param custom_display_name: The new display name
        :type custom_display_name: str
        """
        self._display_name = custom_display_name

    @property
    def is_deterministic(self) -> Optional[bool]:
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
        res: dict = self._inputs
        return res

    @property
    def outputs(self) -> Dict:
        """Outputs of the component.

        :return: Outputs of the component.
        :rtype: dict
        """
        return self._outputs

    @property
    def version(self) -> Optional[str]:
        """Version of the component.

        :return: Version of the component.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        """Set the version of the component.

        :param value: The version of the component.
        :type value: str
        """
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

    def dump(self, dest: Union[str, PathLike, IO[AnyStr]], **kwargs: Any) -> None:
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
    def _resolve_component_source_from_id(  # pylint: disable=docstring-type-do-not-use-class
        id: Optional[Union["Component", str]],
    ) -> Any:
        """Resolve the component source from id.

        :param id: The component ID
        :type id: Optional[str]
        :return: The component source
        :rtype: Literal[
            ComponentSource.CLASS,
            ComponentSource.REMOTE_REGISTRY,
            ComponentSource.REMOTE_WORKSPACE_COMPONENT

        ]
        """
        if id is None:
            return ComponentSource.CLASS
        # Consider default is workspace source, as
        # azureml: prefix will be removed for arm versioned id.
        return (
            ComponentSource.REMOTE_REGISTRY
            if not isinstance(id, Component) and id.startswith(REGISTRY_URI_FORMAT)
            else ComponentSource.REMOTE_WORKSPACE_COMPONENT
        )

    @classmethod
    def _validate_io_names(cls, io_names: Iterable[str], raise_error: bool = False) -> MutableValidationResult:
        """Validate input/output names, raise exception if invalid.

        :param io_names: The names to validate
        :type io_names: Iterable[str]
        :param raise_error: Whether to raise if validation fails. Defaults to False
        :type raise_error: bool
        :return: The validation result
        :rtype: MutableValidationResult
        """
        validation_result = cls._create_empty_validation_result()
        lower2original_kwargs: dict = {}

        for name in io_names:
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
        return cls._try_raise(validation_result, raise_error=raise_error)

    @classmethod
    def _build_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool) -> Dict:
        component_io: dict = {}
        for name, port in io_dict.items():
            if is_input:
                component_io[name] = port if isinstance(port, Input) else Input(**port)
            else:
                component_io[name] = port if isinstance(port, Output) else Output(**port)

        if is_input:
            # Restore flattened parameters to group
            res: dict = GroupInput.restore_flattened_inputs(component_io)
            return res
        return component_io

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> PathAwareSchema:
        return ComponentSchema(context=context)

    @classmethod
    def _create_validation_error(cls, message: str, no_personal_data_message: str) -> ValidationException:
        return ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.COMPONENT,
        )

    @classmethod
    def _is_flow(cls, data: Any) -> bool:
        _schema = data.get(CommonYamlFields.SCHEMA, None)

        if _schema and _schema in [SchemaUrl.PROMPTFLOW_FLOW, SchemaUrl.PROMPTFLOW_RUN]:
            return True
        return False

    @classmethod
    def _load(
        cls,
        data: Optional[Dict] = None,
        yaml_path: Optional[Union[PathLike, str]] = None,
        params_override: Optional[list] = None,
        **kwargs: Any,
    ) -> "Component":
        data = data or {}
        params_override = params_override or []
        base_path = Path(yaml_path).parent if yaml_path else Path("./")

        type_in_override = find_type_in_override(params_override)

        # type_in_override > type_in_yaml > default (command)
        if type_in_override is None:
            type_in_override = data.get(CommonYamlFields.TYPE, None)
        if type_in_override is None and cls._is_flow(data):
            type_in_override = NodeType.FLOW_PARALLEL
        if type_in_override is None:
            type_in_override = NodeType.COMMAND
        data[CommonYamlFields.TYPE] = type_in_override

        from azure.ai.ml.entities._component.component_factory import component_factory

        create_instance_func, _ = component_factory.get_create_funcs(
            data,
            for_load=True,
        )
        new_instance: Component = create_instance_func()
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
        # Set base path separately to avoid doing this in post load, as return types of post load are not unified,
        # could be object or dict.
        # base_path in context can be changed in loading, so we use original base_path here.
        init_kwargs[BASE_PATH_CONTEXT_KEY] = base_path.absolute()
        if yaml_path:
            init_kwargs[SOURCE_PATH_CONTEXT_KEY] = Path(yaml_path).absolute().as_posix()
        # TODO: Bug Item number: 2883415
        new_instance.__init__(  # type: ignore
            **init_kwargs,
        )
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
            is_deterministic=None,  # type: ignore[arg-type]
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

        instance: Component = create_instance_func()
        # TODO: Bug Item number: 2883415
        instance.__init__(**instance._from_rest_object_to_init_params(obj))  # type: ignore
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
        init_kwargs = cls._load_with_schema(
            rest_component_version.component_spec, context={BASE_PATH_CONTEXT_KEY: Path.cwd()}, unknown=INCLUDE
        )
        init_kwargs.update(
            {
                "id": obj.id,
                "is_anonymous": rest_component_version.is_anonymous,
                "creation_context": obj.system_data,
                "inputs": inputs,
                "outputs": outputs,
                "name": origin_name,
            }
        )

        # remove empty values, because some property only works for specific component, eg: distribution for command
        # note that there is an issue that environment == {} will always be true, so use isinstance here
        return {k: v for k, v in init_kwargs.items() if v is not None and not (isinstance(v, dict) and not v)}

    def _get_anonymous_hash(self) -> str:
        """Return the hash of anonymous component.

        Anonymous Components (same code and interface) will have same hash.

        :return: The component hash
        :rtype: str
        """
        # omit version since anonymous component's version is random guid
        # omit name since name doesn't impact component's uniqueness
        return self._get_component_hash(keys_to_omit=["name", "id", "version"])

    def _get_component_hash(self, keys_to_omit: Optional[Iterable[str]] = None) -> str:
        """Return the hash of component.

        :param keys_to_omit: An iterable of keys to omit when computing the component hash
        :type keys_to_omit: Optional[Iterable[str]]
        :return: The component hash
        :rtype: str
        """
        component_interface_dict = self._to_dict()
        res: str = hash_dict(component_interface_dict, keys_to_omit=keys_to_omit)
        return res

    @classmethod
    def _get_resource_type(cls) -> str:
        return "Microsoft.MachineLearningServices/workspaces/components/versions"

    def _get_resource_name_version(self) -> Tuple:
        version: Optional[str] = None
        if not self.version and not self._auto_increment_version:
            version = str(uuid.uuid4())
        else:
            version = self.version
        return self.name or ANONYMOUS_COMPONENT_NAME, version

    def _validate(self, raise_error: Optional[bool] = False) -> MutableValidationResult:
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

        # validate inputs names
        validation_result.merge_with(self._validate_io_names(self.inputs, raise_error=False))
        validation_result.merge_with(self._validate_io_names(self.outputs, raise_error=False))

        return validation_result

    def _get_anonymous_component_name_version(self) -> Tuple:
        return ANONYMOUS_COMPONENT_NAME, self._get_anonymous_hash()

    def _get_rest_name_version(self) -> Tuple:
        if self._is_anonymous:
            return self._get_anonymous_component_name_version()
        return self.name, self.version

    def _to_rest_object(self) -> ComponentVersion:
        component = self._to_dict()

        # TODO: Remove in PuP with native import job/component type support in MFE/Designer
        # Convert import component to command component private preview
        if component.get(CommonYamlFields.TYPE, None) == NodeType.IMPORT:
            component[CommonYamlFields.TYPE] = NodeType.COMMAND
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
            properties=dict(self.properties) if self.properties else {},
            tags=self.tags,
        )
        result = ComponentVersion(properties=properties)
        if self._is_anonymous:
            result.name = ANONYMOUS_COMPONENT_NAME
        else:
            result.name = self.name
            result.properties.properties["client_component_hash"] = self._get_component_hash(keys_to_omit=["version"])
        return result

    def _to_dict(self) -> Dict:
        # Replace the name of $schema to schema.
        component_schema_dict: dict = self._dump_for_validation()
        component_schema_dict.pop(BASE_PATH_CONTEXT_KEY, None)

        # TODO: handle other_parameters and remove override from subclass
        return component_schema_dict

    def _localize(self, base_path: str) -> None:
        """Called on an asset got from service to clean up remote attributes like id, creation_context, etc. and update
        base_path.

        :param base_path: The base_path
        :type base_path: str
        """
        if not getattr(self, "id", None):
            raise ValueError("Only remote asset can be localize but got a {} without id.".format(type(self)))
        self._id = None
        self._creation_context = None
        self._base_path = base_path

    def _get_telemetry_values(self, *args: Any, **kwargs: Any) -> Dict:  # pylint: disable=unused-argument
        # Note: the is_anonymous is not reliable here, create_or_update will log is_anonymous from parameter.
        is_anonymous = self.name is None or ANONYMOUS_COMPONENT_NAME in self.name
        return {"type": self.type, "source": self._source, "is_anonymous": is_anonymous}

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "BaseNode":
        """Call ComponentVersion as a function and get a Component object.

        :return: The component object
        :rtype: BaseNode
        """
        if args:
            # raise clear error message for unsupported positional args
            if self._func._has_parameters:  # type: ignore
                _error = f"got {args} for {self.name}"
                msg = (
                    f"Component function doesn't support positional arguments, {_error}. "  # type: ignore
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
