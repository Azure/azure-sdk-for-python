import re

import pytest

from azure.ai.ml import Input, load_component
from azure.ai.ml.dsl._mldesigner import ParallelFor
from azure.ai.ml.entities import CommandComponent, Component, PipelineComponent, ValidationResult
from azure.ai.ml.entities._builders.base_node import BaseNode
from azure.ai.ml.entities._inputs_outputs import GroupInput
from azure.ai.ml.entities._job.pipeline._io import NodeInput, NodeOutput, PipelineInput


# mldesigner use this function to check if a component is an internal component
def is_internal_component(component):
    """Check if the component is internal component.

    Use class name to check to avoid import InternalComponent in mldesigner.
    """
    if not isinstance(component, Component):
        return False
    if re.match(r"Internal.*Component", component.__class__.__name__):
        return True
    return False


@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestMldesignerImports:
    """
    The assertions are NOT SUPPOSED TO BE CHANGED once they are added.

    The attributes are needed for a certain version of mldesigner package, modifying or deleting any of them will cause
    compatibility issues. If there are new dependencies for mldesigner package, add new assertions in this file.
    """

    def test_necessay_attributes(self):
        assert hasattr(Component, "_customized_validate")
        assert hasattr(Component, "_source_path")
        assert hasattr(CommandComponent, "_to_dict")
        assert hasattr(CommandComponent, "_source_path")
        assert hasattr(PipelineComponent, "_to_dict")
        assert hasattr(PipelineComponent, "_source_path")
        assert hasattr(PipelineComponent, "jobs")
        assert hasattr(ValidationResult, "passed")
        assert hasattr(ValidationResult, "error_messages")
        assert hasattr(ParallelFor, "_to_rest_items")

    @pytest.mark.usefixtures("enable_internal_components")
    def test_additional_includes_of_internal_component(self):
        yaml_path = (
            "./tests/test_configs/internal/component_with_additional_includes/helloworld_additional_includes.yml"
        )
        internal_component = load_component(yaml_path)
        assert hasattr(internal_component, "_to_dict")
        assert hasattr(internal_component, "_source_path")
        assert hasattr(internal_component, "_additional_includes")
        obj = internal_component._additional_includes
        assert hasattr(obj, "with_includes")
        assert hasattr(obj, "code_path")
        assert hasattr(obj, "includes")
        assert is_internal_component(internal_component)

    def test_necessary_attributes_for_input(self):
        input_obj = Input()
        assert hasattr(input_obj, "type")
        assert hasattr(input_obj, "_is_enum")
        assert hasattr(input_obj, "default")
        assert hasattr(input_obj, "min")
        assert hasattr(input_obj, "max")
        assert hasattr(input_obj, "optional")
        assert hasattr(input_obj, "_is_literal")
        assert hasattr(input_obj, "_get_python_builtin_type_str")
        assert hasattr(input_obj, "_get_param_with_standard_annotation")

        node_input_obj = NodeInput(port_name="sdk", meta=input_obj)
        assert hasattr(node_input_obj, "_meta")
        assert hasattr(node_input_obj, "_data")

    def test_class_names(self):
        """These class are undirectly used in mldesigner by their class names"""
        assert BaseNode.__name__ == "BaseNode"
        assert GroupInput.__name__ == "GroupInput"
        assert PipelineInput.__name__ == "PipelineInput"
        assert NodeInput.__name__ == "NodeInput"
        assert NodeOutput.__name__ == "NodeOutput"
