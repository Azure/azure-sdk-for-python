# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import re
from typing import Dict, Union

from pydash import get

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, JobException
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes, ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutput
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
        from azure.ai.ml.entities import CommandJob
        from azure.ai.ml.parallel import ParallelJob
        from azure.ai.ml.entities._builders import BaseNode
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob

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
                    error_category=ErrorCategory.USER_ERROR,
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
                    error_category=ErrorCategory.USER_ERROR,
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
                        error_category=ErrorCategory.USER_ERROR,
                    )
                _input_job_name, _io_type, _name = m.groups()
                _input_job = jobs_dict[_input_job_name]
                if isinstance(_input_job, BaseNode):
                    # If source is base node, get type from io builder
                    _source = _input_job[_io_type][_name]
                    try:
                        source_type = _source.type
                        # Todo: get component type for registered component, and no need following codes
                        # source_type is None means _input_job's component is registered component which results in its
                        # input/output type is None.
                        if source_type is None:
                            if _source._data is None:
                                # return default type if _input_job's output data is None
                                source_type = AssetTypes.URI_FOLDER
                            elif isinstance(_source._data, Output):
                                # if _input_job data is a Output object and we return its type.
                                source_type = _source._data.type
                            else:
                                #  otherwise _input_job's input/output is bound to pipeline input/output, we continue
                                #  infer the type according to _source._data. Will return corresponding pipeline
                                #  input/output type because we didn't get the component.
                                source_type = cls._find_source_input_output_type(_source._data, pipeline_job_dict)
                        return source_type
                    except AttributeError:
                        msg = "Failed to get referenced component type {}."
                        raise JobException(
                            message=msg.format(_input_regex),
                            no_personal_data_message=msg.format("[_input_regex]"),
                            target=ErrorTarget.PIPELINE,
                            error_category=ErrorCategory.USER_ERROR,
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
                        raise JobException(
                            message=msg,
                            no_personal_data_message=msg,
                            target=ErrorTarget.PIPELINE,
                            error_category=ErrorCategory.USER_ERROR,
                        )
                    # AutoMLJob's output type can only be MLTABLE
                    return AssetTypes.MLTABLE
                else:
                    msg = f"Unknown referenced source job type: {type(_input_job)}."
                    raise JobException(
                        message=msg,
                        no_personal_data_message=msg,
                        target=ErrorTarget.PIPELINE,
                        error_category=ErrorCategory.USER_ERROR,
                    )
            except JobException as e:
                raise JobException(
                    message=e.message,
                    no_personal_data_message=e.no_personal_data_message,
                    target=e.target,
                    error_category=e.error_category,
                )
            except Exception as e:
                msg = "Failed to find referenced source for input binding {}"
                raise JobException(
                    message=msg.format(input),
                    no_personal_data_message=msg.format("[input]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                ) from e
        else:
            msg = "Job input in a pipeline can bind only to a job output or a pipeline input"
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    @classmethod
    def _to_input(
        cls,
        input: Union[Input, str, bool, int, float],
        pipeline_job_dict=None,
        **kwargs,
    ) -> Input:
        """Convert a single job input value to component input."""
        pipeline_job_dict = pipeline_job_dict or {}
        input_variable = {}

        if isinstance(input, str) and bool(re.search(ComponentJobConstants.INPUT_PATTERN, input)):
            # handle input bindings
            input_variable["type"] = cls._find_source_input_output_type(input, pipeline_job_dict)

        elif isinstance(input, Input):
            input_variable = input._to_dict()
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["optional"] = False
        elif type(input) in cls.PYTHON_SDK_TYPE_MAPPING.keys():
            input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
        elif isinstance(input, PipelineInput):
            # Infer input type from input data
            input_variable = input._to_input()._to_dict()
        else:
            msg = "'{}' is not supported as component input, supported types are '{}'.".format(
                type(input), cls.PYTHON_SDK_TYPE_MAPPING.keys()
            )
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return Input(**input_variable)

    @classmethod
    def _to_input_builder_function(cls, input: Union[Input, str, bool, int, float]) -> Input:
        input_variable = {}

        if isinstance(input, Input):
            input_variable = input._to_dict()
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["optional"] = False
        else:
            input_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
        return Input(**input_variable)

    @classmethod
    def _to_output(
        cls,
        output: Union[Output, str, bool, int, float],
        pipeline_job_dict=None,
        **kwargs,
    ) -> Output:
        """Translate output value to Output and infer component output type
        from linked pipeline output, its original type or default type."""
        pipeline_job_dict = pipeline_job_dict or {}
        if not pipeline_job_dict or output is None:
            try:
                output_type = output.type
            except Exception:
                # default to url_folder if failed to get type
                output_type = AssetTypes.URI_FOLDER
            output_variable = {"type": output_type}
            return Output(**output_variable)
        else:
            output_variable = {}

            if isinstance(output, str) and bool(re.search(ComponentJobConstants.OUTPUT_PATTERN, output)):
                # handle output bindings
                output_variable["type"] = cls._find_source_input_output_type(output, pipeline_job_dict)

            elif isinstance(output, Output):
                output_variable = output._to_dict()

            elif isinstance(output, PipelineOutput):
                output_variable = output._to_output()._to_dict()

            elif type(output) in cls.PYTHON_SDK_TYPE_MAPPING.keys():
                output_variable["type"] = cls.PYTHON_SDK_TYPE_MAPPING[type(output)]
                output_variable["default"] = output
            else:
                msg = "'{}' is not supported as component output, supported types are '{}'.".format(
                    type(output), cls.PYTHON_SDK_TYPE_MAPPING.keys()
                )
                raise JobException(
                    message=msg,
                    no_personal_data_message=msg,
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return Output(**output_variable)

    def _to_inputs(self, inputs: Dict[str, Union[Input, str, bool, int, float]], **kwargs) -> Dict[str, Input]:
        """Translate inputs to Inputs.

        :param inputs: mapping from input name to input object.
        :return: mapping from input name to translated component input.
        """
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_inputs = {}
        for io_name, io_value in inputs.items():
            translated_component_inputs[io_name] = self._to_input(io_value, pipeline_job_dict)
        return translated_component_inputs

    def _to_outputs(self, outputs: Dict[str, Output], **kwargs) -> Dict[str, Output]:
        """Translate outputs to Outputs.

        :param outputs: mapping from output name to output object.
        :return: mapping from output name to translated component output.
        """
        # Translate outputs to Outputs.
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_outputs = {}
        for output_name, output_value in outputs.items():
            translated_component_outputs[output_name] = self._to_output(output_value, pipeline_job_dict)
        return translated_component_outputs

    def _to_component(self, **kwargs) -> "Component":
        """Translate to Component.

        :return: Translated Component.
        """
        # Note: Source of translated component should be same with Job
        # And should be set after called _to_component/_to_node as job has no _source now.
        raise NotImplementedError()

    def _to_node(self, **kwargs) -> "BaseNode":
        """Translate to pipeline node.

        :param kwargs:
        :return: Translated node.
        """
        # Note: Source of translated component should be same with Job
        # And should be set after called _to_component/_to_node as job has no _source now.
        raise NotImplementedError()
