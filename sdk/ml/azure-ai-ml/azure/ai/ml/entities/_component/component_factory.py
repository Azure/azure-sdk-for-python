# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, Dict, Tuple, Any
from marshmallow import INCLUDE, Schema
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget, ErrorCategory
from azure.ai.ml._restclient.v2022_05_01.models import ComponentVersionData
from azure.ai.ml.constants import (
    NodeType,
    ComponentSource,
    BASE_PATH_CONTEXT_KEY,
    CommonYamlFields,
    ANONYMOUS_COMPONENT_NAME,
)
from azure.ai.ml.entities import ParallelComponent, CommandComponent, Component
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distribution import DistributionConfiguration


class _ComponentFactory:
    """A class to create component instances from yaml dict or rest objects without hard-coded type check."""

    def __init__(self):
        self._create_instance_funcs = {}
        self._create_schema_funcs = {}

        self.register_type(
            _type=NodeType.PARALLEL,
            create_instance_func=lambda: ParallelComponent.__new__(ParallelComponent),
            create_schema_func=ParallelComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.COMMAND,
            create_instance_func=lambda: CommandComponent.__new__(CommandComponent),
            create_schema_func=CommandComponent._create_schema_for_validation,
        )

    def get_create_funcs(self, _type: str) -> Tuple[Callable[..., Component], Callable[[Any], Schema]]:
        """Get registered functions to create instance & its corresponding schema for the given type."""
        _type = _type.lower()
        if _type not in self._create_instance_funcs:
            msg = f"Unsupported component type: {_type}."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        create_instance_func = self._create_instance_funcs[_type]
        create_schema_func = self._create_schema_funcs[_type]
        return create_instance_func, create_schema_func

    def register_type(
        self, _type: str, create_instance_func: Callable[..., Component], create_schema_func: Callable[[Any], Schema]
    ):
        """Register a new component type.

        param _type: the type name of the component.
        type _type: str
        param create_instance_func: a function to create an instance of the component.
        type create_instance_func: Callable[..., Component]
        param create_schema_func: a function to create a schema for the component.
        type create_schema_func: Callable[[Any], Schema]
        """
        self._create_instance_funcs[_type.lower()] = create_instance_func
        self._create_schema_funcs[_type.lower()] = create_schema_func

    def load_from_dict(self, *, data: Dict, context: Dict, _type: str = None, **kwargs) -> Component:
        """Load a component from a yaml dict.

        param data: the yaml dict.
        type data: Dict
        param context: the context of the yaml dict.
        type context: Dict
        param _type: the type name of the component. When None, it will be inferred from the yaml dict.
        type _type: str
        """
        if _type is None:
            _type = data.get(CommonYamlFields.TYPE, NodeType.COMMAND)
        else:
            data[CommonYamlFields.TYPE] = _type
        _type = _type.lower()
        create_instance_func, create_schema_func = self.get_create_funcs(_type)
        new_instance = create_instance_func()
        new_instance.__init__(
            yaml_str=kwargs.pop("yaml_str", None),
            _source=kwargs.pop("_source", ComponentSource.YAML),
            **(create_schema_func(context).load(data, unknown=INCLUDE, **kwargs)),
        )
        return new_instance

    def load_from_rest(self, *, obj: ComponentVersionData, _type: str = None) -> Component:
        """Load a component from a rest object.

        param obj: the rest object.
        type obj: ComponentVersionData
        param _type: the type name of the component. When None, it will be inferred from the rest object.
        type _type: str
        """
        rest_component_version = obj.properties
        # type name may be invalid?
        if _type is None:
            _type = rest_component_version.component_spec[CommonYamlFields.TYPE]
        else:
            rest_component_version.component_spec[CommonYamlFields.TYPE] = _type

        _type = _type.lower()
        inputs = {
            k: Input._from_rest_object(v) for k, v in rest_component_version.component_spec.pop("inputs", {}).items()
        }
        outputs = {
            k: Output._from_rest_object(v) for k, v in rest_component_version.component_spec.pop("outputs", {}).items()
        }

        distribution = rest_component_version.component_spec.pop("distribution", None)
        if distribution:
            distribution = DistributionConfiguration._from_rest_object(distribution)

        # shouldn't block serialization when name is not valid
        # maybe override serialization method for name field?
        create_instance_func, create_schema_func = self.get_create_funcs(_type)
        origin_name = rest_component_version.component_spec[CommonYamlFields.NAME]
        rest_component_version.component_spec[CommonYamlFields.NAME] = ANONYMOUS_COMPONENT_NAME

        new_instance = create_instance_func()
        new_instance.__init__(
            id=obj.id,
            is_anonymous=rest_component_version.is_anonymous,
            creation_context=obj.system_data,
            inputs=inputs,
            outputs=outputs,
            distribution=distribution,
            **(
                create_schema_func({BASE_PATH_CONTEXT_KEY: "./"}).load(
                    rest_component_version.component_spec, unknown=INCLUDE
                )
            ),
            _source=ComponentSource.REST,
        )
        new_instance.name = origin_name
        return new_instance


component_factory = _ComponentFactory()
