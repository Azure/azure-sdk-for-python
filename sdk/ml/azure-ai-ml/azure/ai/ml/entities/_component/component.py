# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from os import PathLike
from pathlib import Path
from typing import Dict, Union
from abc import abstractmethod
from marshmallow import Schema
from marshmallow.exceptions import ValidationError

from azure.ai.ml._schema import PathAwareSchema
from azure.ai.ml.entities import Asset
from azure.ai.ml.entities._component.utils import build_validate_input, build_validate_output
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData, SystemData
from azure.ai.ml.constants import (
    CommonYamlFields,
    BASE_PATH_CONTEXT_KEY,
    PARAMS_OVERRIDE_KEY,
    ComponentSource,
    ANONYMOUS_COMPONENT_NAME,
)
from azure.ai.ml.constants import NodeType
from azure.ai.ml.entities._mixins import RestTranslatableMixin, YamlTranslatableMixin, TelemetryMixin
from azure.ai.ml._utils.utils import load_yaml, dump_yaml_to_file, hash_dict
from azure.ai.ml.entities._util import find_type_in_override
from azure.ai.ml._ml_exceptions import ComponentException, ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.entities._validation import ValidationResult, SchemaValidatableMixin


class Component(Asset, RestTranslatableMixin, TelemetryMixin, YamlTranslatableMixin, SchemaValidatableMixin):
    """Base class for component version, used to define a component. Can't be instantiated directly.

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
        # TODO: check why do we dropped kwargs

        inputs = inputs if inputs else {}
        outputs = outputs if outputs else {}

        self._schema = _schema
        self._type = type
        self._display_name = display_name
        self._is_deterministic = is_deterministic
        self._inputs = build_validate_input(inputs)
        self._outputs = build_validate_output(outputs)
        self._source = kwargs.pop("_source", ComponentSource.SDK)
        # Store original yaml
        self._yaml_str = yaml_str
        self._other_parameter = kwargs
        from azure.ai.ml.entities._job.pipeline._load_component import _generate_component_function

        self._func = _generate_component_function(self)

    @property
    def type(self) -> str:
        """Type of the component, default is 'command'.

        :return: Type of the component.
        :rtype: str
        """
        return self._type

    def _set_is_anonymous(self, is_anonymous: bool):
        """Mark this component as anonymous and overwrite component name to ANONYMOUS_COMPONENT_NAME."""
        if is_anonymous is True:
            self._is_anonymous = True
            self.name = ANONYMOUS_COMPONENT_NAME
        else:
            self._is_anonymous = False

    def _update_anonymous_hash(self):
        """For anonymous component, we use code hash + yaml hash as component version
        so the same anonymous component(same interface and same code) won't be created again.
        Should be called before _to_rest_object.
        """
        if self._is_anonymous:
            self.version = self._get_anonymous_hash()

    def _get_anonymous_hash(self) -> str:
        """Return the name of anonymous component.

        same anonymous component(same code and interface) will have same name.
        """
        component_interface_dict = self._to_dict()
        # omit version since anonymous component's version is random guid
        # omit name since name doesn't impact component's uniqueness
        return hash_dict(component_interface_dict, keys_to_omit=["name", "id", "version"])

    @property
    def display_name(self) -> str:
        """Display name of the component.

        :return: Display name of the component.
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, custom_display_name):
        """Set display_name of the component"""
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
    def _get_validation_error_target(cls) -> ErrorTarget:
        return ErrorTarget.COMPONENT

    def _schema_validate(self) -> ValidationResult:
        """Validate the component.

        :raises: ValidationException
        """
        origin_name = self.name
        if hasattr(self, "_is_anonymous") and getattr(self, "_is_anonymous"):
            # The name of an anonymous component is an uuid generated based on its hash.
            # Can't change naming logic to avoid breaking previous component reuse, so hack here.
            self.name = "dummy_" + self.name.replace("-", "_")
        result = SchemaValidatableMixin._schema_validate(self)
        self.name = origin_name
        return result

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

        from azure.ai.ml.entities import CommandComponent, ParallelComponent

        component_type = None
        type_in_override = find_type_in_override(params_override)
        # override takes the priority
        customized_component_type = type_in_override or data.get(CommonYamlFields.TYPE, NodeType.COMMAND)
        if customized_component_type == NodeType.COMMAND:
            component_type = CommandComponent
        elif customized_component_type == NodeType.PARALLEL:
            component_type = ParallelComponent
        else:
            msg = f"Unsupported component type: {customized_component_type}."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        # Load yaml content
        if yaml_path and Path(yaml_path).is_file():
            with open(yaml_path, "r") as f:
                kwargs["yaml_str"] = f.read()

        return component_type._load_from_dict(data=data, context=context, **kwargs)

    @classmethod
    def _from_rest_object(cls, component_rest_object: ComponentVersionData) -> "Component":
        from azure.ai.ml.entities import CommandComponent, ParallelComponent

        # TODO: should be RestComponentType.CommandComponent, but it did not get generated
        component_type = component_rest_object.properties.component_spec["type"]
        if component_type == NodeType.COMMAND:
            return CommandComponent._load_from_rest(component_rest_object)
        elif component_type == NodeType.PARALLEL:
            return ParallelComponent._load_from_rest(component_rest_object)
        else:
            msg = f"Unsupported component type {component_type}."
            raise ComponentException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.SYSTEM_ERROR,
            )

    @classmethod
    @abstractmethod
    def _load_from_dict(cls, data: Dict, context: Dict, **kwargs) -> "Component":
        pass

    def _get_telemetry_values(self):
        return {"type": self.type, "source": self._source, "is_anonymous": self._is_anonymous}

    def __call__(self, *args, **kwargs) -> [..., Union["Command", "Parallel"]]:
        """Call ComponentVersion as a function and get a Component object."""
        return self._func(*args, **kwargs)
