# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import re
from pydash import get
from typing import Dict, Union

from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._ml_exceptions import JobException, ErrorTarget
from azure.ai.ml.constants import ComponentJobConstants, AssetTypes
from azure.ai.ml.entities._component.input_output import ComponentInput, ComponentOutput
from azure.ai.ml.entities._job.sweep.search_space import Choice, Randint, SweepDistribution


class ComponentTranslatableMixin:
    PYTHON_SDK_TYPE_MAPPING = {
        float: "number",
        int: "integer",
        bool: "boolean",
        str: "string",
    }

    @classmethod
    def _find_source_input_output_type(cls, input: str, pipeline_job_dict: dict):
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.entities import CommandJob, ParallelJob
        from azure.ai.ml.entities._builders import Command, Parallel

        pipeline_job_inputs = pipeline_job_dict.get("inputs", {})
        pipeline_job_outputs = pipeline_job_dict.get("outputs", {})
        jobs_dict = pipeline_job_dict.get("jobs", {})
        if is_data_binding_expression(input, ["parent", "inputs"]):
            _input_name = input.split(".")[2][:-2]
            if _input_name not in pipeline_job_inputs.keys():
                msg = "Failed to find top level definition for input binding {}."
                raise JobException(
                    message=msg.format(input),
                    no_personal_data_message=msg.format("[input]"),
                    target=ErrorTarget.PIPELINE,
                )
            input_type = type(pipeline_job_inputs[_input_name])
            if input_type in cls.PYTHON_SDK_TYPE_MAPPING.keys():
                return cls.PYTHON_SDK_TYPE_MAPPING[input_type]
            else:
                return getattr(pipeline_job_inputs[_input_name], "type", AssetTypes.URI_FOLDER)
        elif is_data_binding_expression(input, ["parent", "outputs"]):
            _output_name = input.split(".")[2][:-2]
            if _output_name not in pipeline_job_outputs.keys():
                msg = "Failed to find top level definition for output binding {}."
                raise JobException(
                    message=msg.format(input),
                    no_personal_data_message=msg.format("[input]"),
                    target=ErrorTarget.PIPELINE,
                )
            output_data = pipeline_job_outputs[_output_name]
            output_type = type(output_data)
            if output_type in cls.PYTHON_SDK_TYPE_MAPPING.keys():
                return cls.PYTHON_SDK_TYPE_MAPPING[output_type]
            elif isinstance(output_data, dict):
                if "type" in output_data:
                    return output_data["type"]
                else:
                    return AssetTypes.URI_FOLDER
            else:
                return getattr(output_data, "type", AssetTypes.URI_FOLDER)
        elif is_data_binding_expression(input, ["parent", "jobs"]):
            try:
                _input_regex = r"\${{parent.jobs.([^.]+).([^.]+).([^.]+)}}"
                m = re.match(_input_regex, input)
                if m is None:
                    msg = "Failed to find top level definition for job binding {}."
                    raise JobException(
                        message=msg.format(input),
                        no_personal_data_message=msg.format("[input]"),
                        target=ErrorTarget.PIPELINE,
                    )
                _input_job_name, _io_type, _name = m.groups()
                _input_job = jobs_dict[_input_job_name]
                if isinstance(_input_job, (Command, Parallel)):
                    # If source is Command, get type from io builder
                    _source = _input_job[_io_type][_name]
                    try:
                        return _source.type
                    except AttributeError:
                        msg = "Failed to get referenced component type {}."
                        raise JobException(
                            message=msg.format(_input_regex),
                            no_personal_data_message=msg.format("[_input_regex]"),
                            target=ErrorTarget.PIPELINE,
                        )
                elif isinstance(_input_job, (CommandJob, ParallelJob)):
                    # If source has not parsed to Command yet, infer type
                    _source = get(_input_job, f"{_io_type}.{_name}")
                    if isinstance(_source, str):
                        return cls._find_source_input_output_type(_source, pipeline_job_dict)
                    else:
                        return getattr(_source, "type", AssetTypes.URI_FOLDER)
                elif isinstance(_input_job, AutoMLJob):
                    # If source is AutoMLJob, only outputs is supported
                    if _io_type != "outputs":
                        msg = f"Only binding to AutoMLJob output is supported, currently got {_io_type}"
                        raise JobException(message=msg, no_personal_data_message=msg, target=ErrorTarget.PIPELINE)
                    # AutoMLJob's output type can only be MLTABLE
                    return AssetTypes.MLTABLE
                else:
                    msg = f"Unknown referenced source job type: {type(_input_job)}."
                    raise JobException(
                        message=msg,
                        no_personal_data_message=msg,
                        target=ErrorTarget.PIPELINE,
                    )
            except Exception as e:
                msg = "Failed to find referenced source for input binding {}"
                raise JobException(
                    message=msg.format(input),
                    no_personal_data_message=msg.format("[input]"),
                    target=ErrorTarget.PIPELINE,
                ) from e
        else:
            msg = "Job input in a pipeline can bind only to a job output or a pipeline input"
            raise JobException(message=msg, no_personal_data_message=msg, target=ErrorTarget.PIPELINE)

    @classmethod
    def _to_component_input(
        cls, input: Union[Input, str, bool, int, float], pipeline_job_dict=None, **kwargs
    ) -> ComponentInput:
        pipeline_job_dict = pipeline_job_dict or {}
        input_variable = {}

        if isinstance(input, str) and bool(re.search(ComponentJobConstants.INPUT_PATTERN, input)):
            # handle input bindings
            input_variable["type"] = cls._find_source_input_output_type(input, pipeline_job_dict)

        elif isinstance(input, Input):
            input_variable["type"] = input.type
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["required"] = True
        elif type(input) in cls.PYTHON_SDK_TYPE_MAPPING.keys():
            input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
            input_variable["required"] = False
        else:
            msg = "'{}' is not supported as component input, supported types are '{}'.".format(
                type(input), cls.PYTHON_SDK_TYPE_MAPPING.keys()
            )
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
            )
        return ComponentInput(input_variable)

    @classmethod
    def _to_component_input_builder_function(cls, input: Union[Input, str, bool, int, float]) -> ComponentInput:
        input_variable = {}

        if isinstance(input, Input):
            input_variable["type"] = input.type
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["required"] = True
        else:
            input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
            input_variable["required"] = False
        return ComponentInput(input_variable)

    @classmethod
    def _to_component_output(
        cls, output: Union[Output, str, bool, int, float], pipeline_job_dict=None, **kwargs
    ) -> ComponentOutput:
        """
        Translate outputs to ComponentOutputs and infer component output type from linked pipeline output, its original
        type or default type
        """
        pipeline_job_dict = pipeline_job_dict or {}
        if not pipeline_job_dict or output is None:
            try:
                output_type = output.type
            except Exception:
                # default to url_folder if failed to get type
                output_type = AssetTypes.URI_FOLDER
            output_variable = {"type": output_type}
            return ComponentOutput(output_variable)
        else:
            output_variable = {}

            if isinstance(output, str) and bool(re.search(ComponentJobConstants.OUTPUT_PATTERN, output)):
                # handle output bindings
                output_variable["type"] = cls._find_source_input_output_type(output, pipeline_job_dict)

            elif isinstance(output, Output):
                output_variable["type"] = output.type

            elif type(output) in cls.PYTHON_SDK_TYPE_MAPPING.keys():
                output_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(output)]
                output_variable["default"] = output
                output_variable["required"] = False
            else:
                msg = "'{}' is not supported as component output, supported types are '{}'.".format(
                    type(output), cls.PYTHON_SDK_TYPE_MAPPING.keys()
                )
                raise JobException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.PIPELINE,
                )
            return ComponentOutput(output_variable)

    def _to_component_inputs(
        self, inputs: Dict[str, Union[Input, str, bool, int, float]], **kwargs
    ) -> Dict[str, ComponentInput]:
        """Translate inputs to ComponentInputs.

        :param inputs: mapping from input name to input object.
        :return: mapping from input name to translated component input.
        """
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_inputs = {}
        for io_name, io_value in inputs.items():
            translated_component_inputs[io_name] = self._to_component_input(io_value, pipeline_job_dict)
        return translated_component_inputs

    def _to_component_outputs(self, outputs: Dict[str, Output], **kwargs) -> Dict[str, ComponentOutput]:
        """Translate outputs to ComponentOutputs

        :param outputs: mapping from output name to output object.
        :return: mapping from output name to translated component output.
        """
        # Translate outputs to ComponentOutputs.
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_outputs = {}
        for output_name, output_value in outputs.items():
            translated_component_outputs[output_name] = self._to_component_output(output_value, pipeline_job_dict)
        return translated_component_outputs

    def _to_component(self, **kwargs) -> "Component":
        """Translate to Component.

        :return: Translated Component.
        """
        raise NotImplementedError()

    def _to_node(self, **kwargs) -> "BaseNode":
        """Translate to pipeline node.

        :param kwargs:
        :return: Translated node.
        """
        raise NotImplementedError()
