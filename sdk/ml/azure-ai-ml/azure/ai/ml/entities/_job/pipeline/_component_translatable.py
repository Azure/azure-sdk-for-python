# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use input as argument name
import re
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

from pydash import get

from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutput
from azure.ai.ml.entities._job.sweep.search_space import Choice, Randint, SweepDistribution
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, JobException

# avoid circular import error
if TYPE_CHECKING:
    from azure.ai.ml.entities._builders import BaseNode
    from azure.ai.ml.entities._component.component import Component


class ComponentTranslatableMixin:
    _PYTHON_SDK_TYPE_MAPPING = {
        float: "number",
        int: "integer",
        bool: "boolean",
        str: "string",
    }

    @classmethod
    def _find_source_from_parent_inputs(cls, input: str, pipeline_job_inputs: dict) -> Tuple[str, Optional[str]]:
        """Find source type and mode of input/output from parent input.

        :param input: The input name
        :type input: str
        :param pipeline_job_inputs: The pipeline job inputs
        :type pipeline_job_inputs: dict
        :return: A 2-tuple of the type and the mode
        :rtype: Tuple[str, Optional[str]]
        """
        _input_name = input.split(".")[2][:-2]
        if _input_name not in pipeline_job_inputs.keys():
            msg = "Failed to find top level definition for input binding {}."
            raise JobException(
                message=msg.format(input),
                no_personal_data_message=msg.format("[input]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        input_data = pipeline_job_inputs[_input_name]
        input_type = type(input_data)
        if input_type in cls._PYTHON_SDK_TYPE_MAPPING:
            return cls._PYTHON_SDK_TYPE_MAPPING[input_type], None
        return getattr(input_data, "type", AssetTypes.URI_FOLDER), getattr(input_data, "mode", None)

    @classmethod
    def _find_source_from_parent_outputs(cls, input: str, pipeline_job_outputs: dict) -> Tuple[str, Optional[str]]:
        """Find source type and mode of input/output from parent output.

        :param input: The input name
        :type input: str
        :param pipeline_job_outputs: The pipeline job outputs
        :type pipeline_job_outputs: dict
        :return: A 2-tuple of the type and the mode
        :rtype: Tuple[str, Optional[str]]
        """
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
        if output_type in cls._PYTHON_SDK_TYPE_MAPPING:
            return cls._PYTHON_SDK_TYPE_MAPPING[output_type], None
        if isinstance(output_data, dict):
            if "type" in output_data:
                output_data_type = output_data["type"]
            else:
                output_data_type = AssetTypes.URI_FOLDER
            if "mode" in output_data:
                output_data_mode = output_data["mode"]
            else:
                output_data_mode = None
            return output_data_type, output_data_mode
        return getattr(output_data, "type", AssetTypes.URI_FOLDER), getattr(output_data, "mode", None)

    @classmethod
    def _find_source_from_other_jobs(
        cls, input: str, jobs_dict: dict, pipeline_job_dict: dict
    ) -> Tuple[str, Optional[str]]:
        """Find source type and mode of input/output from other job.

        :param input: The input name
        :type input: str
        :param jobs_dict: The job dict
        :type jobs_dict:
        :param pipeline_job_dict: The pipeline job dict
        :type pipeline_job_dict: dict
        :return: A 2-tuple of the type and the mode
        :rtype: Tuple[str, Optional[str]]
        """
        from azure.ai.ml.entities import CommandJob
        from azure.ai.ml.entities._builders import BaseNode
        from azure.ai.ml.entities._job.automl.automl_job import AutoMLJob
        from azure.ai.ml.parallel import ParallelJob

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

        # we only support input of one job is from output of another output, but input mode should be decoupled with
        # output mode, so we always return None source_mode
        source_mode = None
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
                        source_type, _ = cls._find_source_input_output_type(_source._data, pipeline_job_dict)
                return source_type, source_mode
            except AttributeError as e:
                msg = "Failed to get referenced component type {}."
                raise JobException(
                    message=msg.format(_input_regex),
                    no_personal_data_message=msg.format("[_input_regex]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                ) from e
        if isinstance(_input_job, (CommandJob, ParallelJob)):
            # If source has not parsed to Command yet, infer type
            _source = get(_input_job, f"{_io_type}.{_name}")
            if isinstance(_source, str):
                source_type, _ = cls._find_source_input_output_type(_source, pipeline_job_dict)
                return source_type, source_mode
            return getattr(_source, "type", AssetTypes.URI_FOLDER), source_mode
        if isinstance(_input_job, AutoMLJob):
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
            return AssetTypes.MLTABLE, source_mode
        msg = f"Unknown referenced source job type: {type(_input_job)}."
        raise JobException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.PIPELINE,
            error_category=ErrorCategory.USER_ERROR,
        )

    @classmethod
    def _find_source_input_output_type(cls, input: str, pipeline_job_dict: dict) -> Tuple[str, Optional[str]]:
        """Find source type and mode of input/output.

        :param input: The input binding
        :type input: str
        :param pipeline_job_dict: The pipeline job dict
        :type pipeline_job_dict: dict
        :return: A 2-tuple of the type and the mode
        :rtype: Tuple[str, Optional[str]]
        """
        pipeline_job_inputs = pipeline_job_dict.get("inputs", {})
        pipeline_job_outputs = pipeline_job_dict.get("outputs", {})
        jobs_dict = pipeline_job_dict.get("jobs", {})
        if is_data_binding_expression(input, ["parent", "inputs"]):
            return cls._find_source_from_parent_inputs(input, pipeline_job_inputs)
        if is_data_binding_expression(input, ["parent", "outputs"]):
            return cls._find_source_from_parent_outputs(input, pipeline_job_outputs)
        if is_data_binding_expression(input, ["parent", "jobs"]):
            try:
                return cls._find_source_from_other_jobs(input, jobs_dict, pipeline_job_dict)
            except JobException as e:
                raise e
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
        cls,  # pylint: disable=unused-argument
        input: Union[Input, str, bool, int, float],
        pipeline_job_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> Input:
        """Convert a single job input value to component input.

        :param input: The input
        :type input: Union[Input, str, bool, int, float]
        :param pipeline_job_dict: The pipeline job dict
        :type pipeline_job_dict: Optional[dict]
        :return: The Component Input
        :rtype: Input
        """
        pipeline_job_dict = pipeline_job_dict or {}
        input_variable: Dict = {}

        if isinstance(input, str) and bool(re.search(ComponentJobConstants.INPUT_PATTERN, input)):
            # handle input bindings
            input_variable["type"], input_variable["mode"] = cls._find_source_input_output_type(
                input, pipeline_job_dict
            )

        elif isinstance(input, Input):
            input_variable = input._to_dict()
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                if input.values is not None:
                    input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["optional"] = False
        elif type(input) in cls._PYTHON_SDK_TYPE_MAPPING:
            input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
        elif isinstance(input, PipelineInput):
            # Infer input type from input data
            input_variable = input._to_input()._to_dict()
        else:
            msg = "'{}' is not supported as component input, supported types are '{}'.".format(
                type(input), cls._PYTHON_SDK_TYPE_MAPPING.keys()
            )
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return Input(**input_variable)

    @classmethod
    def _to_input_builder_function(cls, input: Union[Dict, SweepDistribution, Input, str, bool, int, float]) -> Input:
        input_variable = {}

        if isinstance(input, Input):
            input_variable = input._to_dict()
        elif isinstance(input, SweepDistribution):
            if isinstance(input, Choice):
                if input.values is not None:
                    input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[type(input.values[0])]
            elif isinstance(input, Randint):
                input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[int]
            else:
                input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[float]

            input_variable["optional"] = False
        else:
            input_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[type(input)]
            input_variable["default"] = input
        return Input(**input_variable)

    @classmethod
    def _to_output(
        cls,  # pylint: disable=unused-argument
        output: Optional[Union[Output, Dict, str, bool, int, float]],
        pipeline_job_dict: Optional[dict] = None,
        **kwargs: Any,
    ) -> Output:
        """Translate output value to Output and infer component output type
        from linked pipeline output, its original type or default type.

        :param output: The output
        :type output: Union[Output, str, bool, int, float]
        :param pipeline_job_dict: The pipeline job dict
        :type pipeline_job_dict: Optional[dict]
        :return: The output object
        :rtype: Output
        """
        pipeline_job_dict = pipeline_job_dict or {}
        output_type = None
        if not pipeline_job_dict or output is None:
            try:
                output_type = output.type  # type: ignore
            except AttributeError:
                # default to url_folder if failed to get type
                output_type = AssetTypes.URI_FOLDER
            output_variable = {"type": output_type}
            return Output(**output_variable)
        output_variable = {}

        if isinstance(output, str) and bool(re.search(ComponentJobConstants.OUTPUT_PATTERN, output)):
            # handle output bindings
            output_variable["type"], output_variable["mode"] = cls._find_source_input_output_type(
                output, pipeline_job_dict
            )

        elif isinstance(output, Output):
            output_variable = output._to_dict()

        elif isinstance(output, PipelineOutput):
            output_variable = output._to_output()._to_dict()

        elif type(output) in cls._PYTHON_SDK_TYPE_MAPPING:
            output_variable["type"] = cls._PYTHON_SDK_TYPE_MAPPING[type(output)]
            output_variable["default"] = output
        else:
            msg = "'{}' is not supported as component output, supported types are '{}'.".format(
                type(output), cls._PYTHON_SDK_TYPE_MAPPING.keys()
            )
            raise JobException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return Output(**output_variable)

    def _to_inputs(self, inputs: Optional[Dict], **kwargs: Any) -> Dict:
        """Translate inputs to Inputs.

        :param inputs: mapping from input name to input object.
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        :return: mapping from input name to translated component input.
        :rtype: Dict[str, Input]
        """
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_inputs = {}
        if inputs is not None:
            for io_name, io_value in inputs.items():
                translated_component_inputs[io_name] = self._to_input(io_value, pipeline_job_dict)
        return translated_component_inputs

    def _to_outputs(self, outputs: Optional[Dict], **kwargs: Any) -> Dict:
        """Translate outputs to Outputs.

        :param outputs: mapping from output name to output object.
        :type outputs: Dict[str, Output]
        :return: mapping from output name to translated component output.
        :rtype: Dict[str, Output]
        """
        # Translate outputs to Outputs.
        pipeline_job_dict = kwargs.get("pipeline_job_dict", {})
        translated_component_outputs = {}
        if outputs is not None:
            for output_name, output_value in outputs.items():
                translated_component_outputs[output_name] = self._to_output(output_value, pipeline_job_dict)
        return translated_component_outputs

    def _to_component(self, context: Optional[Dict] = None, **kwargs: Any) -> Union["Component", str]:
        """Translate to Component.

        :param context: The context
        :type context: Optional[context]
        :return: Translated Component.
        :rtype: Component
        """
        # Note: Source of translated component should be same with Job
        # And should be set after called _to_component/_to_node as job has no _source now.
        raise NotImplementedError()

    def _to_node(self, context: Optional[Dict] = None, **kwargs: Any) -> "BaseNode":
        """Translate to pipeline node.

        :param context: The context
        :type context: Optional[context]
        :return: Translated node.
        :rtype: BaseNode
        """
        # Note: Source of translated component should be same with Job
        # And should be set after called _to_component/_to_node as job has no _source now.
        raise NotImplementedError()
