# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable, Dict, Tuple

from marshmallow import INCLUDE, Schema

from azure.ai.ml._utils.utils import is_internal_components_enabled
from azure.ai.ml.constants._common import (
    AZUREML_INTERNAL_COMPONENTS_ENV_VAR,
    AZUREML_INTERNAL_COMPONENTS_SCHEMA_PREFIX,
    CommonYamlFields,
)
from azure.ai.ml.constants._component import ComponentSource, NodeType
from azure.ai.ml.entities._component.automl_component import AutoMLComponent
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.import_component import ImportComponent
from azure.ai.ml.entities._component.parallel_component import ParallelComponent
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._component.spark_component import SparkComponent
from azure.ai.ml.entities._util import extract_label
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class _ComponentFactory:
    """A class to create component instances from yaml dict or rest objects
    without hard-coded type check."""

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
        self.register_type(
            _type=NodeType.IMPORT,
            create_instance_func=lambda: ImportComponent.__new__(ImportComponent),
            create_schema_func=ImportComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.PIPELINE,
            create_instance_func=lambda: PipelineComponent.__new__(PipelineComponent),
            create_schema_func=PipelineComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.AUTOML,
            create_instance_func=lambda: AutoMLComponent.__new__(AutoMLComponent),
            create_schema_func=AutoMLComponent._create_schema_for_validation,
        )
        self.register_type(
            _type=NodeType.SPARK,
            create_instance_func=lambda: SparkComponent.__new__(SparkComponent),
            create_schema_func=SparkComponent._create_schema_for_validation,
        )

    def get_create_funcs(
        self, _type: str, *, schema: str = None
    ) -> Tuple[Callable[..., Component], Callable[[Any], Schema]]:
        """Get registered functions to create instance & its corresponding
        schema for the given type."""

        from azure.ai.ml._utils.utils import try_enable_internal_components

        try_enable_internal_components()

        _type, _ = extract_label(_type)
        if _type not in self._create_instance_funcs:
            if (
                schema
                and not is_internal_components_enabled()
                and schema.startswith(AZUREML_INTERNAL_COMPONENTS_SCHEMA_PREFIX)
            ):
                msg = (
                    f"Internal components is a private feature in v2, please set environment variable "
                    f"{AZUREML_INTERNAL_COMPONENTS_ENV_VAR} to true to use it."
                )
            else:
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
        self,
        _type: str,
        create_instance_func: Callable[..., Component],
        create_schema_func: Callable[[Any], Schema],
    ):
        """Register a new component type.

        param _type: the type name of the component. type _type: str
        param create_instance_func: a function to create an instance of
        the component. type create_instance_func: Callable[...,
        Component] param create_schema_func: a function to create a
        schema for the component. type create_schema_func:
        Callable[[Any], Schema]
        """
        self._create_instance_funcs[_type] = create_instance_func
        self._create_schema_funcs[_type] = create_schema_func

    def load_from_dict(self, *, data: Dict, context: Dict, _type: str = None, **kwargs) -> Component:
        """Load a component from a yaml dict.

        param data: the yaml dict. type data: Dict param context: the
        context of the yaml dict. type context: Dict param _type: the
        type name of the component. When None, it will be inferred from
        the yaml dict. type _type: str
        """
        if _type is None:
            _type = data.get(CommonYamlFields.TYPE, NodeType.COMMAND)
        else:
            data[CommonYamlFields.TYPE] = _type

        create_instance_func, create_schema_func = self.get_create_funcs(
            _type,
            schema=data.get(CommonYamlFields.SCHEMA) if CommonYamlFields.SCHEMA in data else None,
        )
        new_instance = create_instance_func()
        new_instance.__init__(
            yaml_str=kwargs.pop("yaml_str", None),
            _source=kwargs.pop("_source", ComponentSource.YAML_COMPONENT),
            **(create_schema_func(context).load(data, unknown=INCLUDE, **kwargs)),
        )
        return new_instance


component_factory = _ComponentFactory()
