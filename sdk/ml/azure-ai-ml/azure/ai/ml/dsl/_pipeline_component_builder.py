# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
import copy
import sys
import typing
from collections import OrderedDict
from contextlib import contextmanager
from inspect import Parameter, signature
from typing import Callable, Union

from azure.ai.ml._utils.utils import (
    get_all_enum_values_iter,
    is_private_preview_enabled,
    is_valid_node_name,
    parse_args_description_from_docstring,
)
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import ComponentSource, IOConstants
from azure.ai.ml.dsl._utils import _sanitize_python_variable_name
from azure.ai.ml.entities import PipelineJob
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml.entities._builders.control_flow_node import ControlFlowNode
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._inputs_outputs import GroupInput, Output, _get_param_with_standard_annotation, Input
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput, PipelineOutput, _GroupAttrDict
from azure.ai.ml.entities._inputs_outputs.utils import _get_annotation_by_value

# We need to limit the depth of pipeline to avoid the built graph goes too deep and prevent potential
# stack overflow in dsl.pipeline.
from azure.ai.ml.exceptions import UserErrorException

_BUILDER_STACK_MAX_DEPTH = 100


class _PipelineComponentBuilderStack:
    def __init__(self):
        self.items = []

    def top(self) -> "PipelineComponentBuilder":
        if self.is_empty():
            return None
        return self.items[-1]

    def pop(self) -> "PipelineComponentBuilder":
        if self.is_empty():
            return None
        return self.items.pop()

    def push(self, item):
        error_msg = f"{self.__class__.__name__} only " f"allows pushing `{PipelineComponentBuilder.__name__}` element"
        assert isinstance(item, PipelineComponentBuilder), error_msg

        # TODO: validate cycle
        self.items.append(item)
        if not is_private_preview_enabled() and self.size() >= 2:
            current_pipelines = [p.name for p in self.items]
            # clear current pipeline stack
            self.items = []
            msg = "Currently only single layer pipeline is supported. Got: {}"
            raise UserErrorException(
                message=msg.format(current_pipelines),
                no_personal_data_message=msg.format("[current_pipeline]"),
            )
        if self.size() >= _BUILDER_STACK_MAX_DEPTH:
            current_pipeline = self.items[0].name
            # clear current pipeline stack
            self.items = []
            msg = "Pipeline {} depth exceeds limitation. Max depth: {}"
            raise UserErrorException(
                message=msg.format(current_pipeline, _BUILDER_STACK_MAX_DEPTH),
                no_personal_data_message=msg.format("[current_pipeline]", _BUILDER_STACK_MAX_DEPTH),
            )

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)


# This collection is used to record pipeline component builders in current call stack
_definition_builder_stack = _PipelineComponentBuilderStack()


def _is_inside_dsl_pipeline_func() -> bool:
    """Returns true if is inside DSL pipeline func."""
    return _definition_builder_stack.size() > 0


def _add_component_to_current_definition_builder(component):
    if _is_inside_dsl_pipeline_func():
        builder = _definition_builder_stack.top()
        builder.add_node(component)


def get_func_variable_tracer(_locals_data, func_code):
    """Get a tracer to trace variable names in dsl.pipeline function.

    :param _locals_data: A dict to save locals data.
    :type _locals_data: dict
    :param func_code: An code object to compare if current frame is inside user function.
    :type func_code: CodeType
    """

    def tracer(frame, event, arg):  # pylint: disable=unused-argument
        if frame.f_code == func_code and event == "return":
            # Copy the locals of user's dsl function when it returns.
            _locals_data.update(frame.f_locals.copy())

    return tracer


@contextmanager
def replace_sys_profiler(profiler):
    """A context manager which replaces sys profiler to given profiler."""
    original_profiler = sys.getprofile()
    sys.setprofile(profiler)
    try:
        yield
    finally:
        sys.setprofile(original_profiler)


class PipelineComponentBuilder:
    # map from python built-in type to component type
    # pylint: disable=too-many-instance-attributes
    DEFAULT_DATA_TYPE_MAPPING = {
        "float": "number",
        "int": "integer",
        "bool": "boolean",
        "str": "string",
    }

    def __init__(
        self,
        func: Callable,
        name=None,
        version=None,
        display_name=None,
        description=None,
        default_datastore=None,
        tags=None,
        source_path=None,
        non_pipeline_inputs=None
    ):
        self.func = func
        name = name if name else func.__name__
        display_name = display_name if display_name else name
        description = description if description else func.__doc__
        self._args_description = parse_args_description_from_docstring(func.__doc__)
        if name is None:
            name = func.__name__
        # List of nodes, order by it's creation order in pipeline.
        self.nodes = []
        self.non_pipeline_parameter_names = non_pipeline_inputs or []
        # A dict of inputs name to InputDefinition.
        # TODO: infer pipeline component input meta from assignment
        self.inputs = self._build_inputs(func)
        self._name = name
        self.version = version
        self.display_name = display_name
        self.description = description
        self.default_datastore = default_datastore
        self.tags = tags
        self.source_path = source_path

    @property
    def name(self):
        """Name of pipeline builder, it's name will be same as the pipeline
        definition it builds."""
        return self._name

    def add_node(self, node: Union[BaseNode, AutoMLJob]):
        """Add node to pipeline builder.

        :param node: A pipeline node.
        :type node: Union[BaseNode, AutoMLJob]
        """
        self.nodes.append(node)

    def build(self, *, user_provided_kwargs=None,
              non_pipeline_inputs_dict=None, non_pipeline_inputs=None) -> PipelineComponent:
        """
        Build a pipeline component from current pipeline builder.
        :param user_provided_kwargs: The kwargs user provided to dsl pipeline function. None if not provided.
        :param non_pipeline_inputs_dict: The non-pipeline input provided key-value. None if not exist.
        :param non_pipeline_inputs: List of non-pipeline input name. None if not exist.
        """
        if user_provided_kwargs is None:
            user_provided_kwargs = {}
        # Clear nodes as we may call build multiple times.
        self.nodes = []

        kwargs = _build_pipeline_parameter(
            func=self.func,
            user_provided_kwargs=user_provided_kwargs,
            # TODO: support result() for pipeline input inside parameter group
            group_default_kwargs=self._get_group_parameter_defaults(),
            non_pipeline_inputs=non_pipeline_inputs
        )
        kwargs.update(non_pipeline_inputs_dict or {})
        # We use this stack to store the dsl pipeline definition hierarchy
        _definition_builder_stack.push(self)

        # Use a dict to store all variables in self.func
        _locals = {}
        func_variable_profiler = get_func_variable_tracer(_locals, self.func.__code__)
        try:
            with replace_sys_profiler(func_variable_profiler):
                outputs = self.func(**kwargs)
        finally:
            _definition_builder_stack.pop()

        if outputs is None:
            outputs = {}

        jobs = self._update_nodes_variable_names(_locals)
        pipeline_component = PipelineComponent(
            name=self.name,
            version=self.version,
            display_name=self.display_name,
            description=self.description,
            inputs=self.inputs,
            jobs=jobs,
            tags=self.tags,
            source_path=self.source_path,
            _source=ComponentSource.DSL,
        )
        # TODO: Refine here. The output can not be built first then pass into pipeline component creation,
        # exception will be raised in component.build_validate_io().
        pipeline_component._outputs = self._build_pipeline_outputs(outputs)
        return pipeline_component

    def _validate_group_annotation(self, name:str, val:GroupInput):
        for k, v in val.values.items():
            if isinstance(v, GroupInput):
                self._validate_group_annotation(k, v)
            elif isinstance(v, Output):
                # TODO(2097468): automatically change it to Input when used in input annotation
                raise UserErrorException("Output annotation cannot be used in @pipeline.")
            elif isinstance(v, Input):
                if v.type not in IOConstants.PRIMITIVE_STR_2_TYPE:
                    # TODO(2097478): support port type groups
                    raise UserErrorException(f"Only primitive types can be used as input of group, got {v.type}")
            else:
                raise UserErrorException(f"Unsupported annotation type {type(v)} for group field {name}.{k}")

    def _build_inputs(self, func):
        inputs = _get_param_with_standard_annotation(func, is_func=True, skip_params=self.non_pipeline_parameter_names)
        for k, v in inputs.items():
            if isinstance(v, GroupInput):
                self._validate_group_annotation(name=k, val=v)
            # add arg description
            if k in self._args_description:
                v["description"] = self._args_description[k]
        return inputs

    def _build_pipeline_outputs(self, outputs: typing.Dict[str, NodeOutput]):
        """Validate if dsl.pipeline returns valid outputs and set output
        binding. Create PipelineOutput as pipeline's output definition based on
        node outputs from return.

        :param outputs: Outputs of pipeline
        :type outputs: Mapping[str, azure.ai.ml.Output]
        """
        error_msg = (
            "The return type of dsl.pipeline decorated function should be a mapping from output name to "
            "azure.ai.ml.Output with owner."
        )

        if not isinstance(outputs, dict):
            raise UserErrorException(message=error_msg, no_personal_data_message=error_msg)
        output_dict = {}
        for key, value in outputs.items():
            if not isinstance(key, str) or not isinstance(value, NodeOutput) or value._owner is None:
                raise UserErrorException(message=error_msg, no_personal_data_message=error_msg)
            if value._meta is not None:
                meta = value._meta
            else:
                meta = Output(
                    type=value.type, path=value.path, mode=value.mode,
                    description=value.description, is_control=value.is_control
                )

            # hack: map component output type to valid pipeline output type
            def _map_type(_meta):
                if type(_meta).__name__ != "InternalOutput":
                    return _meta.type
                if _meta.type in list(get_all_enum_values_iter(AssetTypes)):
                    return _meta.type
                if _meta.type in ["AnyFile"]:
                    return AssetTypes.URI_FILE
                return AssetTypes.URI_FOLDER

            # Note: Here we set PipelineOutput as Pipeline's output definition as we need output binding.
            pipeline_output = PipelineOutput(
                name=key,
                data=None,
                meta=Output(
                    type=_map_type(meta), description=meta.description, mode=meta.mode, is_control=meta.is_control
                ),
                owner="pipeline",
                description=self._args_description.get(key, None),
            )
            value._owner.outputs[value._name]._data = PipelineOutput(
                name=key,
                data=value._data,
                meta=None,
                owner="pipeline",
                description=self._args_description.get(key, None),
            )
            output_dict[key] = pipeline_output
        return output_dict

    def _get_group_parameter_defaults(self):
        group_defaults = {}
        for key, val in self.inputs.items():
            if not isinstance(val, GroupInput):
                continue
            # Copy and insert top-level parameter name into group names for all items
            group_defaults[key] = copy.deepcopy(val.default)
            group_defaults[key].insert_group_name_for_items(key)
        return group_defaults

    def _update_nodes_variable_names(self, func_variables: dict):
        """Update nodes list to ordered dict with variable name key and
        component object value.

        Variable naming priority:
             1. Specified by using xxx.name.
                 e.g.
                 module1 = module_func()
                 module1.name = "node1"     # final node name is "node1"

             2. Variable name
                 e.g.
                 my_node = module_func()     # final node name is "my_node"

             3. Anonymous node, but another node with same component.name has user-defined name
                 e.g.
                 my_node = module_func()     # final node name is "my_node"
                 module_fun()                # final node name is "my_node_1"
                 module_fun()                # final node name is "my_node_2"

             4. Anonymous node
                 e.g.
                 my_node = module_func()     # final node name is "my_node"
                 module_func_1()             # final node name is its component name
        """

        def _get_name_or_component_name(node: Union[BaseNode, AutoMLJob]):
            # TODO(1979547): refactor this
            if isinstance(node, AutoMLJob):
                return node.name or _sanitize_python_variable_name(node.__class__.__name__)
            if isinstance(node, ControlFlowNode):
                return _sanitize_python_variable_name(node.__class__.__name__)
            return node.name or node._get_component_name()

        valid_component_ids = set(item._instance_id for item in self.nodes)
        id_name_dict = {}
        name_count_dict = {}
        compname_udfname_dict = {}
        local_names = set()
        result = OrderedDict()

        for k, v in func_variables.items():
            # TODO(1979547): refactor this
            if not isinstance(v, (BaseNode, AutoMLJob, PipelineJob, ControlFlowNode)):
                continue
            if getattr(v, "_instance_id", None) not in valid_component_ids:
                continue
            name = getattr(v, "name", None) or k
            if name is not None:
                name = name.lower()

            # User defined name must be valid python identifier
            if not is_valid_node_name(name):
                raise UserErrorException(
                    f"Invalid node name found: {name!r}. Node name must start with a lower letter or underscore, "
                    "and can only contain lower letters, numbers and underscore."
                )

            # Raise error when setting a name that already exists, likely conflict with a variable name
            if name in local_names:
                raise UserErrorException(
                    f"Duplicate node name found in pipeline: {self.name!r}, "
                    f"node name: {name!r}. Duplicate check is case-insensitive."
                )
            local_names.add(name)
            id_name_dict[v._instance_id] = name
            name_count_dict[name] = 1

        # Find the last user-defined name for the same type of components
        for node in self.nodes:
            _id = node._instance_id
            if _id in id_name_dict:
                compname_udfname_dict[_get_name_or_component_name(node)] = id_name_dict[_id]

        # Refine and fill default name
        # If component name is same, append '_{count}' suffix
        for node in self.nodes:
            _id = node._instance_id
            if _id not in id_name_dict:
                target_name = _get_name_or_component_name(node)
                if node.name is None and target_name in compname_udfname_dict:
                    target_name = compname_udfname_dict[target_name]
                if target_name not in name_count_dict:
                    name_count_dict[target_name] = 0
                name_count_dict[target_name] += 1
                suffix = "" if name_count_dict[target_name] == 1 else f"_{name_count_dict[target_name] - 1}"
                id_name_dict[_id] = f"{_sanitize_python_variable_name(target_name)}{suffix}"
            final_name = id_name_dict[_id]
            node.name = final_name
            result[final_name] = node
        return result

    def _update_inputs(self, pipeline_inputs):
        """Update the pipeline inputs by the dict."""
        for input_name, value in pipeline_inputs.items():
            if input_name not in self.inputs:
                if isinstance(value, PipelineInput):
                    value = value._data
                if isinstance(value, Input):
                    anno = copy.copy(value)
                else:
                    anno = _get_annotation_by_value(value)
                anno.name = input_name
                anno.description = self._args_description.get(input_name)
                self.inputs[input_name] = anno


def _build_pipeline_parameter(
        func, *, user_provided_kwargs, group_default_kwargs=None, non_pipeline_inputs=None):
    # Pass group defaults into kwargs to support group.item can be used even if no default on function.
    # example:
    # @group
    # class Group:
    #   key = 'val'
    #
    # @pipeline
    # def pipeline_func(param: Group):
    #   component_func(input=param.key)  <--- param.key should be val.

    # transform kwargs
    transformed_kwargs, non_pipeline_inputs = {}, non_pipeline_inputs or []
    if group_default_kwargs:
        transformed_kwargs.update(
            {
                key: _wrap_pipeline_parameter(
                    key, default_value=value, actual_value=value
                ) for key, value in group_default_kwargs.items()
                if key not in non_pipeline_inputs
            }
        )

    def all_params(parameters):
        for value in parameters.values():
            yield value

    if func is None:
        return transformed_kwargs

    parameters = all_params(signature(func).parameters)
    # transform default values
    for left_args in parameters:
        if left_args.name not in transformed_kwargs.keys() and left_args.kind != Parameter.VAR_KEYWORD and \
                left_args.name not in non_pipeline_inputs:
            default_value = left_args.default if left_args.default is not Parameter.empty else None
            actual_value = user_provided_kwargs.get(left_args.name)
            transformed_kwargs[left_args.name] = _wrap_pipeline_parameter(
                key=left_args.name, default_value=default_value, actual_value=actual_value
            )
    # Add variable kwargs to transformed_kwargs.
    for key, value in user_provided_kwargs.items():
        if key not in transformed_kwargs:
            transformed_kwargs[key] = _wrap_pipeline_parameter(key=key, default_value=None, actual_value=value)
    return transformed_kwargs


def _wrap_pipeline_parameter(key, default_value, actual_value, group_names=None):
    # Append parameter path in group
    group_names = [*group_names] if group_names else []
    if isinstance(default_value, _GroupAttrDict):
        group_names.append(key)
        return _GroupAttrDict({
            k: _wrap_pipeline_parameter(
                k, default_value=v, actual_value=v, group_names=group_names
            ) for k, v in default_value.items()
        })
    # Note: this PipelineInput object is built to mark input as a data binding.
    # It only exists in dsl.pipeline function execution time and won't store in pipeline job or pipeline component.
    return PipelineInput(name=key, meta=None, default_data=default_value, data=actual_value, group_names=group_names)
