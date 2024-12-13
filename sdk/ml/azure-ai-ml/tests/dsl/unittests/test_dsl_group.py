import sys
from enum import Enum as PyEnum
from io import StringIO

import pytest
from test_utilities.utils import omit_with_wildcard

from azure.ai.ml import Input, load_component
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.dsl._group_decorator import group
from azure.ai.ml.entities._inputs_outputs import GroupInput, Output, is_group
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, _GroupAttrDict
from azure.ai.ml.exceptions import UserErrorException

from .._util import _DSL_TIMEOUT_SECOND


@pytest.mark.usefixtures("enable_pipeline_private_preview_features", "enable_private_preview_schema_features")
@pytest.mark.timeout(_DSL_TIMEOUT_SECOND)
@pytest.mark.unittest
@pytest.mark.pipeline_test
class TestDSLGroup:
    def test_validate_conflict_key(self) -> None:
        def validator(keys, assert_valid=True):
            if assert_valid:
                GroupInput.validate_conflict_keys(keys)
                return
            with pytest.raises(Exception):
                GroupInput.validate_conflict_keys(keys)

        validator(["a", "b", "a.b"], assert_valid=False)
        validator(["a.b", "a.b.c"], assert_valid=False)
        validator(["a", "b", "ab"])
        validator(["aa", "a.c"])
        validator(["a.b", "a.c"])
        validator(["a.bc.de", "bc.de"])
        validator(["a.b", "a.bc", "a.c", "aa", "abc", "ac", "a.ac.b", "ab.c"])

    def test_restore_flattened_inputs(self) -> None:
        keys = ["a.b", "a.bc", "a.c", "aa", "abc", "ac", "a.ac.b", "ab.c"]
        definitions = {k: Input(type="string") for k in keys}
        result = GroupInput.restore_flattened_inputs(definitions)
        assert result.keys() == set({"aa", "abc", "ac", "a", "ab"})
        assert isinstance(result["a"], GroupInput)
        assert result["a"].values.keys() == set({"b", "bc", "ac", "c"})
        assert isinstance(result["a"].values["ac"], GroupInput)
        assert result["a"].values["ac"].values.keys() == set({"b"})
        assert isinstance(result["ab"], GroupInput)
        assert result["ab"].values.keys() == set({"c"})
        inputs = {k: PipelineInput(name=k, meta=None) for k in keys}
        result = _GroupAttrDict(GroupInput.restore_flattened_inputs(inputs))
        assert isinstance(result.a, _GroupAttrDict)
        assert isinstance(result.a.ac, _GroupAttrDict)
        assert isinstance(result.a.b, PipelineInput)
        assert isinstance(result.a.bc, PipelineInput)
        assert isinstance(result.a.c, PipelineInput)
        assert isinstance(result.ab, _GroupAttrDict)
        assert isinstance(result.ab.c, PipelineInput)

    def test_auto_generated_functions(self) -> None:
        class EnumOps(PyEnum):
            Option1 = "Option1"
            Option2 = "Option2"

        @group
        class MixedGroup:
            int_param: int
            str_param: str
            enum_param: EnumOps
            str_default_param: Input(type="string") = "test"
            optional_int_param: Input(type="integer", optional=True) = 5

        # __init__ func test
        assert hasattr(MixedGroup, "__init__") is True
        original_out = sys.stdout
        sys.stdout = stdout_str_IO = StringIO()
        help(MixedGroup.__init__)
        assert (
            "__init__(self,*,int_param:int=None,str_param:str=None,enum_param:str=None,"
            "str_default_param:str='test',optional_int_param:int=5)->None" in stdout_str_IO.getvalue().replace(" ", "")
        )
        sys.stdout = original_out

        # __repr__ func test
        var = MixedGroup(
            int_param=1, str_param="test-str", enum_param=EnumOps.Option1, str_default_param="op2", optional_int_param=4
        )
        assert (
            "MixedGroup(int_param=1,str_param='test-str',enum_param=<EnumOps.Option1:'Option1'>,"
            "str_default_param='op2',optional_int_param=4)".replace(" ", "") in var.__repr__().replace(" ", "")
        )

        # __set_attribute__ func test
        var.int_param = 2
        assert var.int_param == 2

    def test_group_items(self):
        @group
        class MixedGroup:
            int_param0: Input(type="integer")
            int_param1: int
            int_param2: Input(type="integer", min=1, max=5)
            int_param3 = 3
            int_param4: Input(type="integer", optional=True) = None

        values = list(getattr(MixedGroup, IOConstants.GROUP_ATTR_NAME).values.values())
        assert len(values) == 5
        values = sorted(values, key=lambda item: item["_port_name"])
        for idx, val in enumerate(values):
            assert val.type == "integer"
            if idx < 4:
                assert val.optional is not True
        assert values[2].min == 1
        assert values[2].max == 5
        assert values[4].optional is True
        assert values[1].default is None

        val = MixedGroup(int_param0=0, int_param1=1, int_param2=2)
        assert val.__dict__ == {"int_param0": 0, "int_param1": 1, "int_param2": 2, "int_param4": None, "int_param3": 3}
        val = MixedGroup(int_param0=0, int_param1=1, int_param2=2, int_param3=9, int_param4=9)
        assert val.__dict__ == {"int_param0": 0, "int_param1": 1, "int_param2": 2, "int_param4": 9, "int_param3": 9}

    def test_create_nested_group(self):
        @group
        class SubGroup:
            param: int = 1

        with pytest.raises(ValueError) as e:

            @group
            class ItemGroup:
                group_param: SubGroup = "str"

            ItemGroup()
        assert "Default value must be instance of parameter group" in str(e)

        @group
        class ItemGroup:
            group_param: SubGroup = SubGroup(param=2)

        assert hasattr(ItemGroup, IOConstants.GROUP_ATTR_NAME) is True
        assert isinstance(getattr(ItemGroup, IOConstants.GROUP_ATTR_NAME).values["group_param"], GroupInput)
        assert is_group(ItemGroup.group_param) is True
        var = ItemGroup()
        assert isinstance(var.group_param.param, PipelineInput)
        assert var.group_param.param._data == 2

    def test_group_supported_types(self):
        # Input Output are supported now
        @group
        class Group:
            param: Input(type="uri_folder")

        with pytest.raises(UserErrorException) as e:

            @pipeline
            def my_pipeline(param: Group):
                pass

        assert "Only primitive types can be used as input of group, got uri_folder" in str(e.value)

        @group
        class Group:
            param: Output

        with pytest.raises(UserErrorException) as e:

            @pipeline
            def my_pipeline(param: Group):
                pass

        assert "Output annotation cannot be used in @pipeline." in str(e.value)

        class CustomizedObj:
            pass

        with pytest.raises(UserErrorException) as e:

            @group
            class Group:
                param: CustomizedObj

        assert "Unsupported annotation type" in str(e.value)

    def test_group_inherit(self):
        @group
        class SubGroup:
            int_param0: int
            int_param1: int = 1

        @group
        class Group(SubGroup):
            int_param3: int
            int_param1: int

        test_group = Group(int_param0=0, int_param1=1, int_param3=3)
        assert test_group.int_param0 == 0
        assert test_group.int_param1 == 1
        assert test_group.int_param3 == 3

    def test_group_inherit_parameter_order(self):
        @group
        class SubGroup0:
            int_param0: int
            int_param1: int
            int_param2: int
            int_param3: int = 3

        @group
        class SubGroup1:
            int_param3: int
            int_param4: int
            int_param1: int = 1
            int_param6: int = 6

        # Merge 0 with 1, order should be:
        # [int_param0, int_param2, int_param3, int_param4], [int_param1=1, int_param6=6]

        @group
        class Group(SubGroup1, SubGroup0):
            int_param1: int
            int_param5: int
            int_param2: int = 2
            int_param7: int = 7

        # Merge Group with (merge 0 with 1), order should be:
        # [int_param0, int_param3, int_param4, int_param1, int_param5], [int_param6=6, int_param2=2, int_param7=7]

        params = getattr(Group, IOConstants.GROUP_ATTR_NAME).values
        assert len(params) == 8
        expected_keys = [
            "int_param0",
            "int_param3",
            "int_param4",
            "int_param1",
            "int_param5",
            "int_param6",
            "int_param2",
            "int_param7",
        ]
        for _id, (expected_key, value) in enumerate(zip(expected_keys, list(params.values()))):
            assert value._port_name == expected_key
            if _id > 4:
                assert value.default is not None
                assert value._port_name == f"int_param{value.default}"

    def test_pipeline_with_group(self):
        class EnumOps(PyEnum):
            Option1 = "option1"
            Option2 = "option2"
            Option3 = "option3"

        @group
        class SubParamClass:
            int_param: Input(min=1.0, max=5.0, type="integer")

        @group
        class ParamClass:
            enum_param: EnumOps
            sub: SubParamClass = SubParamClass(int_param=1)

        default_param = ParamClass(enum_param=EnumOps.Option1)

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @pipeline()
        def pipeline_with_group(group: ParamClass, data: int):
            hello_world_component_func(component_in_path=group.enum_param, component_in_number=group.sub.int_param)

        # Create with parameter group
        pipeline_job = pipeline_with_group(default_param, 1)
        job_dict = pipeline_job._to_dict()
        assert job_dict["inputs"] == {"data": 1, "group.enum_param": "option1", "group.sub.int_param": 1}
        assert job_dict["jobs"]["microsoftsamples_command_component_basic"]["inputs"] == {
            "component_in_number": {"path": "${{parent.inputs.group.sub.int_param}}"},
            "component_in_path": {"path": "${{parent.inputs.group.enum_param}}"},
        }

        # Assign new values one by one
        pipeline_job.inputs.group.sub.int_param = 2
        pipeline_job.inputs.group.enum_param = EnumOps.Option2
        job_dict = pipeline_job._to_dict()
        assert job_dict["inputs"] == {"group.sub.int_param": 2, "group.enum_param": "option2", "data": 1}

        # Assign new group values
        assign_param = ParamClass(enum_param=EnumOps.Option3, sub=SubParamClass(int_param=3))
        pipeline_job.inputs.group = assign_param
        job_dict = pipeline_job._to_dict()
        assert job_dict["inputs"] == {"data": 1, "group.enum_param": "option3", "group.sub.int_param": 3}

        # Assign new sub group values
        pipeline_job.inputs.group.sub = SubParamClass(int_param=5)
        job_dict = pipeline_job._to_dict()
        assert job_dict["inputs"] == {"data": 1, "group.enum_param": "option3", "group.sub.int_param": 5}

    def test_pipeline_with_default_group_value(self):
        @group
        class SubParamClass:
            int_param: Input(min=1.0, max=5.0, type="integer") = 1

        @group
        class ParamClass:
            str_param: str = "string_by_default"
            sub: SubParamClass = SubParamClass()

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(hello_world_component_yaml)

        @pipeline()
        def pipeline_with_group_default(group: ParamClass = ParamClass()):
            hello_world_component_func(component_in_path=group.str_param, component_in_number=group.sub.int_param)

        pipeline_job = pipeline_with_group_default()
        job_dict = pipeline_job._to_dict()
        assert job_dict["inputs"] == {"group.str_param": "string_by_default", "group.sub.int_param": 1}
        assert job_dict["jobs"]["microsoftsamples_command_component_basic"]["inputs"] == {
            "component_in_number": {"path": "${{parent.inputs.group.sub.int_param}}"},
            "component_in_path": {"path": "${{parent.inputs.group.str_param}}"},
        }

    def test_assign_group_invalid(self):
        @group
        class ParamClass:
            str_param: str = "string_by_default"

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(hello_world_component_yaml)

        @pipeline()
        def str_param_pipeline(str_param, group: ParamClass):
            hello_world_component_func(component_in_path=str_param, component_in_number=1)

        with pytest.raises(Exception) as e:
            str_param_pipeline(str_param=ParamClass(), group=None)
        assert "'str_param' is defined as a parameter but got a parameter group as input" in str(e)

        with pytest.raises(Exception) as e:
            str_param_pipeline(str_param="test", group="test")
        assert "'group' is defined as a parameter group but got input 'test' with type '<class 'str'>" in str(e)

        pipeline_job = str_param_pipeline(str_param="test", group=None)
        pipeline_job.inputs.str_param = ParamClass()
        # Note: this is the expected behavior.
        assert (
            pipeline_job._to_dict()["inputs"]["str_param"]
            == "TestDSLGroup.test_assign_group_invalid.<locals>.ParamClass(str_param='string_by_default')"
        )

        pipeline_job.inputs.str_param = "test"
        with pytest.raises(Exception) as e:
            pipeline_job.inputs.group = "test"
        assert "'group' is expected to be a parameter group, but got <class 'str'>." in str(e)

    def test_group_outputs(self):
        # can define group outputs object, but can not use in @pipeline
        @group
        class PortOutputs:
            # TODO(2097468): automatically change it to Input when used in input annotation
            output1: Output(type="uri_file")
            output2: Output(type="uri_folder")

        with pytest.raises(UserErrorException) as e:

            @pipeline
            def my_pipeline(my_inputs: PortOutputs):
                pass

        assert "Output annotation cannot be used in @pipeline." in str(e.value)

        @group
        class PrimitiveOutputs:
            output1: Output(type="string")
            output2: Output(type="integer")
            output3: Output(type="number")
            output4: Output(type="boolean", is_control=True)

        with pytest.raises(UserErrorException) as e:

            @pipeline
            def my_pipeline(my_inputs: PrimitiveOutputs):
                pass

        assert "Output annotation cannot be used in @pipeline." in str(e.value)

    def test_group_port_inputs(self):
        @group
        class PortInputs:
            input1: Input(type="uri_file")
            input2: Input(type="uri_folder")

        with pytest.raises(UserErrorException) as e:
            # TODO(2097478): support port type groups
            @pipeline
            def my_pipeline(my_inputs: PortInputs):
                pass

        assert "Only primitive types can be used as input of group, got uri_file" in str(e.value)

    def test_group_defaults_with_outputs(self):
        @group
        class MixedGroup:
            int_param: int
            str_default_param: Input(type="string") = "test"
            str_param: str
            input_folder: Input(type="uri_folder")
            optional_int_param: Input(type="integer", optional=True) = 5
            output_folder: Output(type="uri_folder")

        assert hasattr(MixedGroup, "__init__") is True
        original_out = sys.stdout
        sys.stdout = stdout_str_IO = StringIO()
        help(MixedGroup.__init__)
        assert (
            "__init__(self,*,"
            "int_param:int=None,"
            "str_default_param:str='test',"
            "str_param:str=None,"
            "input_folder:{'type':'uri_folder'}=None,"
            "optional_int_param:int=5,"
            "output_folder:{'type':'uri_folder'}=None)"
            "->None" in stdout_str_IO.getvalue().replace(" ", "")
        )
        sys.stdout = original_out

        # __repr__ func test
        var = MixedGroup(
            int_param=1, str_param="test-str", input_folder=Input(path="input"), output_folder=Output(path="output")
        )
        assert (
            "MixedGroup("
            "int_param=1,"
            "str_default_param='test',"
            "str_param='test-str',"
            "input_folder={'type':'uri_folder','path':'input'},"
            "optional_int_param=5,"
            "output_folder={'type':'uri_folder','path':'output'})" in var.__repr__().replace(" ", "")
        )

        # __set_attribute__ func test
        var.input_folder = Input(path="new_input")
        assert var.input_folder.path == "new_input"

    def test_group_port_defaults(self):
        # input
        with pytest.raises(UserErrorException) as e:

            @group
            class SubGroup:
                int_param0: Input
                int_param1: Input = Input(path="in1")

        assert "Default value of Input 'int_param1' cannot be set" in str(e.value)

        with pytest.raises(UserErrorException) as e:

            @group
            class SubGroup:
                out_param0: Output
                out_param1: Output = Output(path="out2")

        assert "Default value of Output 'out_param1' cannot be set" in str(e.value)

    @pytest.mark.skip(reason="Input group item .result() is not supported currently.")
    def test_input_group_result(self):
        @group
        class SubParamClass:
            int_param: Input(min=1.0, max=5.0, type="integer") = 1

        @group
        class ParamClass:
            str_param: str
            sub: SubParamClass = SubParamClass()

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(hello_world_component_yaml)

        @pipeline()
        def pipeline_with_group(group: ParamClass, int_param: int):
            assert isinstance(group.str_param.result(), str)
            assert isinstance(group.sub.int_param.result(), int)
            assert isinstance(int_param.result(), int)
            node1 = hello_world_component_func(
                component_in_path=group.str_param, component_in_number=group.sub.int_param.result()
            )
            node2 = hello_world_component_func(
                component_in_path=group.str_param.result(), component_in_number=int_param.result()
            )

            return {"output1": node1.outputs.component_out_path, "output2": node2.outputs.component_out_path}

        pipeline_job1 = pipeline_with_group(group=ParamClass(str_param="str_1"), int_param=1)

        common_omit_fields = [
            "jobs.*.componentId",
            "jobs.*._source",
            "jobs.*.properties",
        ]

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job1._to_rest_object().properties.as_dict(), *common_omit_fields
        )

        expected_pipeline_job1 = {}
        assert rest_pipeline_job == expected_pipeline_job1

        pipeline_job2 = pipeline_with_group(group=ParamClass(str_param="str_2"), int_param=1)

        rest_pipeline_job = omit_with_wildcard(
            pipeline_job2._to_rest_object().properties.as_dict(), *common_omit_fields
        )
        expected_pipeline_job2 = {}
        assert rest_pipeline_job == expected_pipeline_job2

    def test_group_outputs_return(self):
        @group
        class PortOutputs:
            output1: Output(type="uri_folder")
            output2: Output(type="uri_folder")

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @pipeline
        def my_pipeline_dict_return() -> PortOutputs:
            node1 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            node2 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            return {"output1": node1.outputs.component_out_path, "output2": node2.outputs.component_out_path}

        pipeline_job1 = my_pipeline_dict_return()

        @pipeline
        def my_pipeline() -> PortOutputs:
            node1 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            node2 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            return PortOutputs(output1=node1.outputs.component_out_path, output2=node2.outputs.component_out_path)

        pipeline_job2 = my_pipeline()

        assert pipeline_job1._to_dict()["outputs"] == pipeline_job2._to_dict()["outputs"]

    def test_group_outputs_validation(self):
        # test raise validation error if mismatch
        @group
        class PortOutputs:
            output1: Output(type="uri_folder")
            output2: Output(type="uri_folder")

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @pipeline
        def pipeline_count_mismatch() -> PortOutputs:
            node1 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            return PortOutputs(output1=node1.outputs.component_out_path)

        with pytest.raises(UserErrorException) as e:
            pipeline_count_mismatch()
        assert "Unmatched outputs between actual pipeline output and output in annotation" in str(e.value)

        @group
        class SinglePortOutput:
            output1: Output(type="mltable")

        @pipeline
        def pipeline_type_mismatch() -> SinglePortOutput:
            node1 = hello_world_component_func(component_in_number=1, component_in_path=Input(path="/a/path/on/ds"))
            return SinglePortOutput(output1=node1.outputs.component_out_path)

        with pytest.raises(UserErrorException) as e:
            pipeline_type_mismatch()

        assert "{'type': 'uri_folder'} != annotation output {'type': 'mltable'}" in str(e.value)

        basic_component = load_component(
            source="./tests/test_configs/components/component_with_conditional_output/spec.yaml"
        )

        @group
        class PrimitiveOutputs1:
            output1: Output(type="boolean", is_control=True)
            output2: Output(type="boolean", is_control=True)
            output3: Output(type="boolean")
            output: Output(type="boolean")

        @pipeline
        def pipeline_is_control_mismatch() -> PrimitiveOutputs1:
            node1 = basic_component()
            return PrimitiveOutputs1(
                output1=node1.outputs.output1,
                output2=node1.outputs.output2,
                output3=node1.outputs.output3,
                output=node1.outputs.output,
            )

        pipeline_is_control_mismatch()

    def test_group_outputs_unsupported_annotation(self):
        @group
        class SubOutputs:
            output1: Output(type="uri_folder")
            output2: Output(type="uri_folder")

        @group
        class ParentOutputs:
            output1: SubOutputs

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        with pytest.raises(UserErrorException) as e:

            @pipeline
            def my_pipeline() -> ParentOutputs:
                node1 = hello_world_component_func(component_in_number=1)
                return {
                    "output1": node1.outputs.component_out_path,
                }

        assert "Nested group annotation is not supported in pipeline output." in str(e.value)

        with pytest.raises(UserErrorException) as e:

            @group
            class GroupOutputs:
                output1: PipelineInput

        assert "Unsupported annotation type" in str(e.value)

    def test_input_in_output_group(self):
        @group
        class Outputs:
            output1: Input(type="uri_folder")

        hello_world_component_yaml = "./tests/test_configs/components/helloworld_component.yml"
        hello_world_component_func = load_component(source=hello_world_component_yaml)

        @pipeline
        def my_pipeline() -> Outputs:
            node1 = hello_world_component_func(component_in_number=1)
            return Outputs(
                output1=node1.outputs.component_out_path,
            )

        pipeline_job = my_pipeline()
        assert pipeline_job._to_dict()["outputs"] == {"output1": {"type": "uri_folder"}}
