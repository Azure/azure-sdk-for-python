# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import Any, Callable, Dict, List, Mapping, Optional, Union

from marshmallow import INCLUDE

from azure.ai.ml import Output
from azure.ai.ml._schema import NestedField
from azure.ai.ml._schema.pipeline.component_job import SweepSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY, SOURCE_PATH_CONTEXT_KEY, CommonYamlFields
from azure.ai.ml.constants._component import ControlFlowType, NodeType, DataTransferTaskType
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.dsl._component_func import to_component_func
from azure.ai.ml.dsl._overrides_definition import OverrideDefinition
from azure.ai.ml.entities._builders import (
    BaseNode,
    Command,
    Import,
    Parallel,
    Spark,
    Sweep,
    DataTransferCopy,
    DataTransferImport,
    DataTransferExport,
)
from azure.ai.ml.entities._builders.condition_node import ConditionNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._builders.do_while import DoWhile
from azure.ai.ml.entities._builders.parallel_for import ParallelFor
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._util import get_type_from_spec
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationException


class _PipelineNodeFactory:
    """A class to create pipeline node instances from yaml dict or rest objects without hard-coded type check."""

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
            _type=NodeType.IMPORT,
            create_instance_func=lambda: Import.__new__(Import),
            load_from_rest_object_func=Import._from_rest_object,
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
            create_instance_func=lambda: Sweep.__new__(Sweep),
            load_from_rest_object_func=Sweep._from_rest_object,
            nested_schema=NestedField(SweepSchema, unknown=INCLUDE),
        )
        self.register_type(
            _type=NodeType.AUTOML,
            create_instance_func=None,
            load_from_rest_object_func=self._automl_from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=NodeType.SPARK,
            create_instance_func=lambda: Spark.__new__(Spark),
            load_from_rest_object_func=Spark._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=ControlFlowType.DO_WHILE,
            create_instance_func=None,
            load_from_rest_object_func=DoWhile._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=ControlFlowType.IF_ELSE,
            create_instance_func=None,
            load_from_rest_object_func=ConditionNode._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type=ControlFlowType.PARALLEL_FOR,
            create_instance_func=None,
            load_from_rest_object_func=ParallelFor._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.COPY_DATA]),
            create_instance_func=lambda: DataTransferCopy.__new__(DataTransferCopy),
            load_from_rest_object_func=DataTransferCopy._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.IMPORT_DATA]),
            create_instance_func=lambda: DataTransferImport.__new__(DataTransferImport),
            load_from_rest_object_func=DataTransferImport._from_rest_object,
            nested_schema=None,
        )
        self.register_type(
            _type="_".join([NodeType.DATA_TRANSFER, DataTransferTaskType.EXPORT_DATA]),
            create_instance_func=lambda: DataTransferExport.__new__(DataTransferExport),
            load_from_rest_object_func=DataTransferExport._from_rest_object,
            nested_schema=None,
        )

    @classmethod
    def _get_func(cls, _type: str, funcs: Dict[str, Callable]) -> Callable:
        if _type == NodeType._CONTAINER:
            msg = (
                "Component returned by 'list' is abbreviated and can not be used directly, "
                "please use result from 'get'."
            )
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.COMPONENT,
                error_category=ErrorCategory.USER_ERROR,
            )
        _type = get_type_from_spec({CommonYamlFields.TYPE: _type}, valid_keys=funcs)
        return funcs[_type]

    def get_create_instance_func(self, _type: str) -> Callable[..., BaseNode]:
        """Get the function to create a new instance of the node.

        param _type: The type of the node. type _type: str
        """
        return self._get_func(_type, self._create_instance_funcs)

    def get_load_from_rest_object_func(
        self, _type: str
    ) -> Callable[[Any], Union[BaseNode, AutoMLJob, ControlFlowNode]]:
        """Get the function to load a node from a rest object.

        param _type: The type of the node. type _type: str
        """
        return self._get_func(_type, self._load_from_rest_object_funcs)

    def register_type(
        self,
        _type: str,
        *,
        create_instance_func: Optional[Callable[..., Union[BaseNode, AutoMLJob]]] = None,
        load_from_rest_object_func: Optional[Callable[[Any], Union[BaseNode, AutoMLJob, ControlFlowNode]]] = None,
        nested_schema: Optional[Union[NestedField, List[NestedField]]] = None,
    ):
        """Register a type of node.

        :param _type: The type of the node.
        :type _type: str
        :param create_instance_func: A function to create a new instance of the node, defaults to None
        :type create_instance_func: typing.Optional[typing.Callable[..., typing.Union[BaseNode, AutoMLJob]]]
        :param load_from_rest_object_func: A function to load a node from a rest object, defaults to None
        :type load_from_rest_object_func: typing.Optional[typing.Callable[[Any], typing.Union[BaseNode, AutoMLJob\
            , ControlFlowNode]]]
        :param nested_schema: schema/schemas of corresponding nested field, will be used in \
            PipelineJobSchema.jobs.value, defaults to None
        :type nested_schema: typing.Optional[typing.Union[NestedField, List[NestedField]]]
        """
        # pylint: disable=no-member
        if create_instance_func is not None:
            self._create_instance_funcs[_type] = create_instance_func
        if load_from_rest_object_func is not None:
            self._load_from_rest_object_funcs[_type] = load_from_rest_object_func
        if nested_schema is not None:
            from azure.ai.ml._schema.core.fields import TypeSensitiveUnionField
            from azure.ai.ml._schema.pipeline.pipeline_component import PipelineComponentSchema
            from azure.ai.ml._schema.pipeline.pipeline_job import PipelineJobSchema

            for declared_fields in [
                PipelineJobSchema._declared_fields,
                PipelineComponentSchema._declared_fields,
            ]:
                jobs_value_field: TypeSensitiveUnionField = declared_fields["jobs"].value_field
                if not isinstance(nested_schema, list):
                    nested_schema = [nested_schema]
                for nested_field in nested_schema:
                    jobs_value_field.insert_type_sensitive_field(type_name=_type, field=nested_field)

    def load_from_dict(self, *, data: dict, _type: Optional[str] = None) -> Union[BaseNode, AutoMLJob]:
        """Load a node from a dict.

        :param data: A dict containing the node's data.
        :type data: dict
        :param _type: The type of the node. If not specified, it will be inferred from the data.
        :type _type: str
        """
        if _type is None:
            _type = data[CommonYamlFields.TYPE] if CommonYamlFields.TYPE in data else NodeType.COMMAND
            # todo: refine Hard code for now to support different task type for DataTransfer node
            if _type == NodeType.DATA_TRANSFER:
                _type = "_".join([NodeType.DATA_TRANSFER, data.get("task", " ")])
        else:
            data[CommonYamlFields.TYPE] = _type

        new_instance: Union[BaseNode, AutoMLJob] = self.get_create_instance_func(_type)()

        if isinstance(new_instance, BaseNode):
            # parse component
            component_key = new_instance._get_component_attr_name()
            if component_key in data and isinstance(data[component_key], dict):
                data[component_key] = Component._load(
                    data=data[component_key],
                    yaml_path=data[component_key].pop(SOURCE_PATH_CONTEXT_KEY, None),
                )

        new_instance.__init__(**data)
        return new_instance

    def load_from_rest_object(
        self, *, obj: dict, _type: Optional[str] = None, **kwargs
    ) -> Union[BaseNode, AutoMLJob, ControlFlowNode]:
        """Load a node from a rest object.

        :param obj: A rest object containing the node's data.
        :type obj: dict
        :param _type: The type of the node. If not specified, it will be inferred from the data.
        :type _type: str
        """

        # TODO: Remove in PuP with native import job/component type support in MFE/Designer
        if "computeId" in obj and obj["computeId"] and obj["computeId"].endswith("/" + ComputeType.ADF):
            _type = NodeType.IMPORT

        if _type is None:
            _type = obj[CommonYamlFields.TYPE] if CommonYamlFields.TYPE in obj else NodeType.COMMAND
            # todo: refine Hard code for now to support different task type for DataTransfer node
            if _type == NodeType.DATA_TRANSFER:
                _type = "_".join([NodeType.DATA_TRANSFER, obj.get("task", " ")])
        else:
            obj[CommonYamlFields.TYPE] = _type

        return self.get_load_from_rest_object_func(_type)(obj, **kwargs)

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
    override_definitions: Optional[Mapping[str, OverrideDefinition]] = None,  # pylint: disable=unused-argument
) -> Callable[..., Union[Command, Parallel]]:
    # Generate a function which returns a component node.
    def create_component_func(**kwargs):
        # todo: refine Hard code for now to support different task type for DataTransfer node
        _type = component_entity.type
        if _type == NodeType.DATA_TRANSFER:
            _type = "_".join([NodeType.DATA_TRANSFER, component_entity.task])
            if component_entity.task == DataTransferTaskType.IMPORT_DATA:
                return pipeline_node_factory.load_from_dict(
                    data=dict(component=component_entity, **kwargs, _from_component_func=True),
                    _type=_type,
                )
        return pipeline_node_factory.load_from_dict(
            data={"component": component_entity, "inputs": kwargs, "_from_component_func": True},
            _type=_type,
        )

    return to_component_func(component_entity, create_component_func)


pipeline_node_factory = _PipelineNodeFactory()
