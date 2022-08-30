# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import tempfile
import typing
from abc import abstractmethod
from os import PathLike
from pathlib import Path
from typing import Dict, Union

from marshmallow import Schema

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData, ComponentVersionDetails, SystemData
from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml._utils.utils import dump_yaml_to_file, hash_dict, is_private_preview_enabled
from azure.ai.ml.constants import (
    ANONYMOUS_COMPONENT_NAME,
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    REGISTRY_URI_FORMAT,
    ComponentSource,
)
from azure.ai.ml.entities._assets.asset import Asset
from azure.ai.ml.entities._assets import Code
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._mixins import RestTranslatableMixin, TelemetryMixin, YamlTranslatableMixin
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml.entities._validation import SchemaValidatableMixin, ValidationResult

COMPONENT_PLACEHOLDER = "COMPONENT_PLACEHOLDER"
COMPONENT_CODE_PLACEHOLDER = "command_component: code_placeholder"


class Component(
    Asset,
    RestTranslatableMixin,
    TelemetryMixin,
    YamlTranslatableMixin,
    SchemaValidatableMixin,
):
    """Base class for component version, used to define a component. Can't be
    instantiated directly.

    :param name: Name of the resource.
    :type name: str
    :param version: Version of the resource.
    :type version: str
    :param id:  Global id of the resource, Azure Resource Manager ID.
    :type id: str
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
    :type creation_context: SystemData
    """

    def __init__(
        self,
        *,
        name: str = None,
        version: str = None,
        id: str = None,
        type: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        display_name: str = None,
        is_deterministic: bool = True,
        inputs: Dict = None,
        outputs: Dict = None,
        yaml_str: str = None,
        _schema: str = None,
        creation_context: SystemData = None,
        **kwargs,
    ):
        # Setting this before super init because when asset init version, _auto_increment_version's value may change
        self._auto_increment_version = kwargs.pop("auto_increment", False)
        # Get source from id first, then kwargs.
        self._source = (
            self._resolve_component_source_from_id(id) if id else kwargs.pop("_source", ComponentSource.CLASS)
        )

        super().__init__(
            name=name,
            version=version,
            id=id,
            description=description,
            tags=tags,
            properties=properties,
            creation_context=creation_context,
            is_anonymous=kwargs.pop("is_anonymous", False),
            base_path=kwargs.pop("base_path", None),
        )
        # store kwargs to self._other_parameter instead of pop to super class to allow component have extra
        # fields not defined in current schema.

        # update component name to ANONYMOUS_COMPONENT_NAME if it is anonymous
        if hasattr(self, "_is_anonymous"):
            self._set_is_anonymous(self._is_anonymous)

        inputs = inputs if inputs else {}
        outputs = outputs if outputs else {}

        self._schema = _schema
        self._type = type
        self._display_name = display_name
        self._is_deterministic = is_deterministic
        self._inputs = self.build_validate_io(inputs, is_input=True)
        self._outputs = self.build_validate_io(outputs, is_input=False)
        # Store original yaml
        self._yaml_str = yaml_str
        self._other_parameter = kwargs
        from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

        self._func = _generate_component_function(self)

    @classmethod
    def build_validate_io(cls, io_dict: Union[Dict, Input, Output], is_input: bool):
        component_io = {}
        for name, port in io_dict.items():
            if not name.isidentifier():
                msg = "{!r} is not a valid parameter name"
                raise ValidationException(
                    message=msg.format(name),
                    no_personal_data_message=msg.format("[name]"),
                    target=ErrorTarget.COMPONENT,
                )
            else:
                if is_input:
                    component_io[name] = port if isinstance(port, Input) else Input(**port)
                else:
                    component_io[name] = port if isinstance(port, Output) else Output(**port)
        return component_io

    @property
    def type(self) -> str:
        """Type of the component, default is 'command'.

        :return: Type of the component.
        :rtype: str
        """
        return self._type

    def _set_is_anonymous(self, is_anonymous: bool):
        """Mark this component as anonymous and overwrite component name to
        ANONYMOUS_COMPONENT_NAME."""
        if is_anonymous is True:
            self._is_anonymous = True
            self.name = ANONYMOUS_COMPONENT_NAME
        else:
            self._is_anonymous = False

    def _update_anonymous_hash(self):
        """For anonymous component, we use code hash + yaml hash as component
        version so the same anonymous component(same interface and same code)
        won't be created again.

        Should be called before _to_rest_object.
        """
        if self._is_anonymous:
            self.version = self._get_anonymous_hash()

    def _get_anonymous_hash(self) -> str:
        """Return the name of anonymous component.

        same anonymous component(same code and interface) will have same
        name.
        """
        component_interface_dict = self._to_dict()
        # omit version since anonymous component's version is random guid
        # omit name since name doesn't impact component's uniqueness
        return hash_dict(component_interface_dict, keys_to_omit=["name", "id", "version"])

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

    def dump(self, path: Union[PathLike, str]) -> None:
        """Dump the component content into a file in yaml format.

        :param path: Path to a local file as the target, new file will be created, raises exception if the file exists.
        :type path: str
        """

        yaml_serialized = self._to_dict()
        dump_yaml_to_file(path, yaml_serialized, default_flow_style=False)

    @classmethod
    @abstractmethod
    def _create_schema_for_validation(cls, context) -> typing.Union[PathAwareSchema, Schema]:
        pass

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.COMPONENT

    def _customized_validate(self) -> ValidationResult:
        validation_result = super(Component, self)._customized_validate()
        # If private features are enable and component has code value of type str we need to check
        # that it is a valid git path case. Otherwise we should throw a ValidationError
        # saying that the code value is not valid
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
        return validation_result

    @classmethod
    def _load(
        cls,
        data: Dict = None,
        yaml_path: Union[PathLike, str] = None,
        params_override: list = None,
        **kwargs,
    ) -> "Component":
        data = data or {}
        params_override = params_override or []
        context = {
            BASE_PATH_CONTEXT_KEY: Path(yaml_path).parent if yaml_path else Path("./"),
            PARAMS_OVERRIDE_KEY: params_override,
        }

        type_in_override = find_type_in_override(params_override)
        from azure.ai.ml.entities._component.component_factory import component_factory

        component = component_factory.load_from_dict(_type=type_in_override, data=data, context=context, **kwargs)
        if yaml_path:
            component._source_path = yaml_path
        return component

    @classmethod
    def _from_rest_object(cls, component_rest_object: ComponentVersionData) -> "Component":
        from azure.ai.ml.entities._component.component_factory import component_factory

        # Object got from rest data contain _source, we delete it.
        if "_source" in component_rest_object.properties.component_spec:
            del component_rest_object.properties.component_spec["_source"]
        return component_factory.load_from_rest(obj=component_rest_object)

    def _to_rest_object(self) -> ComponentVersionData:
        component = self._to_dict()
        # add source type to component rest object
        component["_source"] = self._source
        properties = ComponentVersionDetails(
            component_spec=component,
            description=self.description,
            is_anonymous=self._is_anonymous,
            properties=self.properties,
            tags=self.tags,
        )
        result = ComponentVersionData(properties=properties)
        result.name = self.name
        return result

    def _to_dict(self) -> Dict:
        """Dump the command component content into a dictionary."""

        # Distribution inherits from autorest generated class, use as_dist() to dump to json
        # Replace the name of $schema to schema.
        component_schema_dict = self._dump_for_validation()
        component_schema_dict.pop("base_path", None)

        # TODO: handle other_parameters and remove override from subclass
        return component_schema_dict

    def _resolve_local_code(self, get_code_arm_id_and_fill_back) -> None:
        tmp_dir = None
        if hasattr(self, "code") and self.code is None:
            # Hack: when code not specified, we generated a file which contains COMPONENT_PLACEHOLDER as code
            # This hack was introduced because job does not allow running component without a code, and we need to
            # make sure when component updated some field(eg: description), the code remains the same.
            # Benefit of using a constant code for all components without code is this will generate same code for
            # anonymous components which enables component reuse
            tmp_dir = tempfile.TemporaryDirectory()
            code_file_path = Path(tmp_dir.name) / COMPONENT_PLACEHOLDER
            with open(code_file_path, "w") as f:
                f.write(COMPONENT_CODE_PLACEHOLDER)
            self.code = code_file_path

        self.code = get_code_arm_id_and_fill_back(Code(base_path=self._base_path, path=self.code))

        if tmp_dir is not None:
            tmp_dir.cleanup()

    def _get_telemetry_values(self):
        # Note: the is_anonymous is not reliable here, create_or_update will log is_anonymous from parameter.
        is_anonymous = self.name is None or ANONYMOUS_COMPONENT_NAME in self.name
        return {"type": self.type, "source": self._source, "is_anonymous": is_anonymous}

    def __call__(self, *args, **kwargs) -> [..., Union["Command", "Parallel"]]:
        """Call ComponentVersion as a function and get a Component object."""
        return self._func(*args, **kwargs)
