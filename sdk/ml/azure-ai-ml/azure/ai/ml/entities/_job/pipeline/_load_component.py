# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from typing import Any, Callable, Dict, List, Mapping, Union

from marshmallow import INCLUDE

from azure.ai.ml import Output
from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.pipeline.component_job import SweepSchema
from azure.ai.ml.constants import BASE_PATH_CONTEXT_KEY, CommonYamlFields, NodeType
from azure.ai.ml.dsl._component_func import to_component_func
from azure.ai.ml.dsl._overrides_definition import OverrideDefinition
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._builders import BaseNode, Command, Parallel, Sweep
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob


class _PipelineNodeFactory:
    """A class to create pipeline node instances from yaml dict or rest objects
    without hard-coded type check."""

    def __init__(self):
        self._create_instance_funcs = {}
        self._load_from_rest_object_funcs = {}

        self.register_type(
            _type=NodeType.COMMAND,
            create_instance_func=lambda: Command.__new__(Command),
            load_from_rest_object_func=Command._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=NodeType.PARALLEL,
            create_instance_func=lambda: Parallel.__new__(Parallel),
            load_from_rest_object_func=Parallel._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=NodeType.PIPELINE,
            create_instance_func=lambda: Pipeline.__new__(Pipeline),
            load_from_rest_object_func=Pipeline._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=NodeType.SWEEP,
            create_instance_func=None,
            load_from_rest_object_func=Sweep._from_rest_object,
            nested_schema=NestedField(SweepSchema, unknown=INCLUDE),
        )
        self.register_type(
            _type=NodeType.AUTOML,
            create_instance_func=None,
            load_from_rest_object_func=self._automl_from_rest_object,
            nested_schema=None,
        )

    @classmethod
    def _get_func(cls, _type: str, funcs):
        if _type not in funcs:
            msg = f"Unsupported component type: {_type}."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.COMPONENT,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return funcs[_type]

    def get_create_instance_func(self, _type: str) -> Callable[..., BaseNode]:
        """Get the function to create a new instance of the node.

        param _type: The type of the node. type _type: str
        """
        return self._get_func(_type, self._create_instance_funcs)

    def get_load_from_rest_object_func(self, _type: str) -> Callable[[Any], BaseNode]:
        """Get the function to load a node from a rest object.

        param _type: The type of the node. type _type: str
        """
        return self._get_func(_type, self._load_from_rest_object_funcs)

    def register_type(
        self,
        _type: str,
        *,
        create_instance_func: Callable[..., Union[BaseNode, AutoMLJob]] = None,
        load_from_rest_object_func: Callable[[Any], Union[BaseNode, AutoMLJob]] = None,
        nested_schema: Union[NestedField, List[NestedField]] = None,
    ):
        """Register a type of node.

        param _type: The type of the node. type _type: str param
        create_instance_func: A function to create a new instance of the
        node. type create_instance_func: Callable[..., BaseNode] param
        load_from_rest_object_func: A function to load a node from a
        rest object. type load_from_rest_object_func: Callable[[Any],
        BaseNode] param nested_schema: schema/schemas of corresponding
        nested field, will be used in PipelineJobSchema.jobs.value. type
        nested_schema: Union[NestedField, List[NestedField]]
        """
        if create_instance_func is not None:
            self._create_instance_funcs[_type] = create_instance_func
        if load_from_rest_object_func is not None:
            self._load_from_rest_object_funcs[_type] = load_from_rest_object_func
        if nested_schema is not None:
            from azure.ai.ml._schema.core.fields import TypeSensitiveUnionField
            from azure.ai.ml._schema.pipeline import PipelineJobSchema
            from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentSchema

            for declared_fields in [
                PipelineJobSchema._declared_fields,
                PipelineComponentSchema._declared_fields,
            ]:
                jobs_value_field: TypeSensitiveUnionField = declared_fields["jobs"].value_field
                if not isinstance(nested_schema, list):
                    nested_schema = [nested_schema]
                for nested_field in nested_schema:
                    jobs_value_field.insert_type_sensitive_field(type_name=_type, field=nested_field)

    def load_from_dict(self, *, data: dict, _type: str = None) -> Union[BaseNode, AutoMLJob]:
        """Load a node from a dict.

        param data: A dict containing the node's data. type data: dict
        param _type: The type of the node. If not specified, it will be
        inferred from the data. type _type: str
        """
        if _type is None:
            _type = data[CommonYamlFields.TYPE] if CommonYamlFields.TYPE in data else NodeType.COMMAND
        else:
            data[CommonYamlFields.TYPE] = _type

        new_instance = self.get_create_instance_func(_type)()
        new_instance.__init__(**data)
        return new_instance

    def load_from_rest_object(self, *, obj: dict, _type: str = None) -> Union[BaseNode, AutoMLJob]:
        """Load a node from a rest object.

        param obj: A rest object containing the node's data. type obj:
        dict param _type: The type of the node. If not specified, it
        will be inferred from the data. type _type: str
        """
        if _type is None:
            _type = obj[CommonYamlFields.TYPE] if CommonYamlFields.TYPE in obj else NodeType.COMMAND
        else:
            obj[CommonYamlFields.TYPE] = _type

        return self.get_load_from_rest_object_func(_type)(obj)

    @classmethod
    def _automl_from_rest_object(cls, node: Dict) -> AutoMLJob:
        # rest dict outputs -> Output objects
        outputs = AutoMLJob._from_rest_outputs(node.get("outputs"))
        # Output objects -> yaml dict outputs
        parsed_outputs = {}
        for key, val in outputs.items():
            if isinstance(val, Output):
                val = val._to_dict()
            parsed_outputs[key] = val
        node["outputs"] = parsed_outputs
        return AutoMLJob._load_from_dict(
            node,
            context={BASE_PATH_CONTEXT_KEY: "./"},
            additional_message="Failed to load automl task from backend.",
            inside_pipeline=True,
        )


def _generate_component_function(
    component_entity: Component,
    override_definitions: Mapping[str, OverrideDefinition] = None,
) -> Callable[..., Union[Command, Parallel]]:
    # Generate a function which returns a component node.
    def create_component_func(**kwargs):
        return pipeline_node_factory.load_from_dict(
            data=dict(component=component_entity, inputs=kwargs, _from_component_func=True),
            _type=component_entity.type,
        )

    return to_component_func(component_entity, create_component_func)


pipeline_node_factory = _PipelineNodeFactory()
