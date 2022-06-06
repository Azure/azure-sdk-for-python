# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from typing import Callable, Union
from collections import OrderedDict
from contextlib import contextmanager
from inspect import signature, Parameter

from azure.ai.ml.constants import ComponentSource
from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._job.pipeline._io import PipelineOutputBase, PipelineOutput
from azure.ai.ml.dsl._utils import _sanitize_python_variable_name
from azure.ai.ml.entities._component._pipeline_component import _PipelineComponent
from azure.ai.ml.entities._builders import BaseNode
from azure.ai.ml._utils.utils import is_valid_node_name

# Currently we only support single layer pipeline, we may increase this when we supports multiple layer pipeline(
# nested pipeline, aka sub graph).
# But we still need to limit the depth of pipeline to avoid the built graph goes too deep and prevent potential
# stack overflow in dsl.pipeline.

_BUILDER_STACK_MAX_DEPTH = 2


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
        if self.size() >= _BUILDER_STACK_MAX_DEPTH:
            current_pipelines = [p.name for p in self.items]
            # clear current pipeline stack
            self.items = []
            msg = "Currently only single layer pipeline is supported. Currently got: {}"
            raise UserErrorException(
                message=msg.format(current_pipelines), no_personal_data_message=msg.format("[current_pipeline]")
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

    def tracer(frame, event, arg):
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
        compute=None,
        default_datastore=None,
        tags=None,
    ):
        self.func = func
        if name is None:
            name = func.__name__
        if version is None:
            version = "1"
        # List of nodes, order by it's creation order in pipeline.
        self.nodes = []
        # A dict of inputs name to InputDefinition.
        # TODO: infer pipeline component input meta from assignment
        self.inputs = {}
        for p in signature(func).parameters.values():
            if p.default is Parameter.empty or p.default is None:
                self.inputs[p.name] = {"type": "unknown", "default": None}
            else:
                default_type = type(p.default).__name__
                self.inputs[p.name] = {
                    "type": self.DEFAULT_DATA_TYPE_MAPPING.get(default_type, default_type),
                    "default": p.default,
                }
        # A dict of outputs name to OutputDefinition.
        self.outputs = {}
        self.pipeline_component = _PipelineComponent(
            name=name,
            version=version,
            display_name=display_name,
            description=description,
            inputs=self.inputs,
            outputs=self.outputs,
            components={},
            _source=ComponentSource.DSL,
        )
        self._name = self.pipeline_component.name
        self.compute = compute
        self.default_datastore = default_datastore
        self.tags = tags

    @property
    def name(self):
        """Name of pipeline builder, it's name will be same as the pipeline definition it builds."""
        return self._name

    def add_node(self, node: Union[BaseNode, AutoMLJob]):
        """Add node to pipeline builder.

        :param node: dsl component object.
        :type node: azure.ai.ml.dsl.Component
        """
        self.nodes.append(node)

    def build(self, kwargs) -> _PipelineComponent:
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

        self._update_outputs(outputs)
        self._update_nodes_variable_names(_locals)
        return self.pipeline_component

    def _update_outputs(self, outputs):
        """Validate if dsl.pipeline returns valid outputs and set output binding.

        :param outputs: Outputs of pipeline
        :type outputs: Mapping[str, azure.ai.ml.dsl._component.Output]
        """
        error_msg = (
            "The return type of dsl.pipeline decorated function should be a mapping from output name to "
            "azure.ai.ml.dsl.component.Output with owner."
        )

        if not isinstance(outputs, dict):
            raise UserErrorException(message=error_msg, no_personal_data_message=error_msg)
        output_dict = {}
        for key, value in outputs.items():
            if not isinstance(key, str) or not isinstance(value, PipelineOutputBase) or value._owner is None:
                raise UserErrorException(message=error_msg, no_personal_data_message=error_msg)

            pipeline_output = PipelineOutput(name=key, data=None, meta=None, owner="pipeline")
            # set bound component's output to data binding
            value._owner.outputs[value._name]._data = pipeline_output
            output_dict[key] = pipeline_output
        self.pipeline_component._outputs = output_dict

    def _update_nodes_variable_names(self, func_variables: dict):
        """Update nodes list to ordered dict with variable name key and component object value.

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
            if isinstance(node, AutoMLJob):
                return node.name
            else:
                return node.name or node._get_component_name()

        valid_component_ids = set(item._instance_id for item in self.nodes)
        id_name_dict = {}
        name_count_dict = {}
        compname_udfname_dict = {}
        local_names = set()
        result = OrderedDict()

        for k, v in func_variables.items():
            if not isinstance(v, (BaseNode, AutoMLJob)):
                continue
            if getattr(v, "_instance_id", None) not in valid_component_ids:
                continue
            name = v.name or k
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
        self.pipeline_component._components = result
