# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import inspect
import logging
from collections import OrderedDict
from functools import wraps
from inspect import Parameter, signature
from pathlib import Path
from typing import Any, Callable, Dict, TypeVar, List

from azure.ai.ml.entities import Data, PipelineJob, PipelineJobSettings, Model
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._inputs_outputs import Input, is_parameter_group
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput, _GroupAttrDict
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.exceptions import (
    MissingPositionalArgsError,
    MultipleValueError,
    TooManyPositionalArgsError,
    UnexpectedKeywordError,
    UnsupportedParameterKindError,
    UserErrorException,
    ParamValueNotExistsError,
)

from ._pipeline_component_builder import PipelineComponentBuilder, _is_inside_dsl_pipeline_func
from ._settings import _dsl_settings_stack
from ._utils import _resolve_source_file

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])

SUPPORTED_INPUT_TYPES = (
    PipelineInput,
    NodeOutput,
    Input,
    Model,
    Data,  # For the case use a Data object as an input, we will convert it to Input object
    Pipeline,  # For the case use a pipeline node as the input, we use its only one output as the real input.
    str,
    bool,
    int,
    float,
    PipelineExpression,
    _GroupAttrDict,
)
module_logger = logging.getLogger(__name__)


def pipeline(
    func=None,
    *,
    name: str = None,
    version: str = None,
    display_name: str = None,
    description: str = None,
    experiment_name: str = None,
    tags: Dict[str, str] = None,
    **kwargs,
):
    """Build a pipeline which contains all component nodes defined in this
    function. Set AZURE_ML_CLI_PRIVATE_FEATURES_ENABLED to enable multi layer pipeline.

    .. note::

        The following pseudo-code shows how to create a pipeline using this decorator.

    .. code-block:: python

                # Define a pipeline with decorator
                @pipeline(name='sample_pipeline', description='pipeline description')
                def sample_pipeline_func(pipeline_input, pipeline_str_param):
                        # component1 and component2 will be added into the current pipeline
                        component1 = component1_func(input1=pipeline_input, param1='literal')
                        component2 = component2_func(input1=dataset, param1=pipeline_str_param)
                        # A decorated pipeline function needs to return outputs.
                        # In this case, the pipeline has two outputs: component1's output1 and component2's output1,
                        # and let's rename them to 'pipeline_output1' and 'pipeline_output2'
                        return {
                            'pipeline_output1': component1.outputs.output1,
                            'pipeline_output2': component2.outputs.output1
                        }

                # E.g.: This call returns a pipeline job with nodes=[component1, component2],
                pipeline_job = sample_pipeline_func(
                    pipeline_input=Input(type='uri_folder', path='./local-data'),
                    pipeline_str_param='literal'
                )
                ml_client.jobs.create_or_update(pipeline_job, experiment_name="pipeline_samples")

    :param func: The user pipeline function to be decorated.
    :param func: types.FunctionType
    :param name: The name of pipeline component, defaults to function name.
    :type name: str
    :param version: The version of pipeline component, defaults to "1".
    :type version: str
    :param display_name: The display name of pipeline component, defaults to function name.
    :type display_name: str
    :param description: The description of the built pipeline.
    :type description: str
    :param experiment_name: Name of the experiment the job will be created under, \
                if None is provided, experiment will be set to current directory.
    :type experiment_name: str
    :param tags: The tags of pipeline component.
    :type tags: dict[str, str]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def pipeline_decorator(func: _TFunc) -> _TFunc:
        if not isinstance(func, Callable): # pylint: disable=isinstance-second-argument-not-valid-type
            raise UserErrorException(f"Dsl pipeline decorator accept only function type, got {type(func)}.")

        non_pipeline_inputs = kwargs.get("non_pipeline_inputs", []) or kwargs.get("non_pipeline_parameters", [])
        # compute variable names changed from default_compute_targe -> compute -> default_compute -> none
        # to support legacy usage, we support them with priority.
        compute = kwargs.get("compute", None)
        default_compute_target = kwargs.get("default_compute_target", None)
        default_compute_target = kwargs.get("default_compute", None) or default_compute_target
        continue_on_step_failure = kwargs.get("continue_on_step_failure", None)
        on_init = kwargs.get("on_init", None)
        on_finalize = kwargs.get("on_finalize", None)

        default_datastore = kwargs.get("default_datastore", None)
        force_rerun = kwargs.get("force_rerun", None)
        job_settings = {
            "default_datastore": default_datastore,
            "continue_on_step_failure": continue_on_step_failure,
            "force_rerun": force_rerun,
            "default_compute": default_compute_target,
            "on_init": on_init,
            "on_finalize": on_finalize,
        }
        func_entry_path = _resolve_source_file()
        if not func_entry_path:
            func_path = Path(inspect.getfile(func))
            # in notebook, func_path may be a fake path and will raise error when trying to resolve this fake path
            if func_path.exists():
                func_entry_path = func_path.resolve().absolute()

        job_settings = {k: v for k, v in job_settings.items() if v is not None}
        pipeline_builder = PipelineComponentBuilder(
            func=func,
            name=name,
            version=version,
            display_name=display_name,
            description=description,
            default_datastore=default_datastore,
            tags=tags,
            source_path=str(func_entry_path),
            non_pipeline_inputs=non_pipeline_inputs,
        )

        @wraps(func)
        def wrapper(*args, **kwargs) -> PipelineJob:
            # Default args will be added here.
            # pylint: disable=abstract-class-instantiated
            # Node: push/pop stack here instead of put it inside build()
            # Because we only want to enable dsl settings on top level pipeline
            _dsl_settings_stack.push()  # use this stack to track on_init/on_finalize settings
            try:
                provided_positional_args = _validate_args(func, args, kwargs, non_pipeline_inputs)
                # Convert args to kwargs
                kwargs.update(provided_positional_args)
                non_pipeline_params_dict = {k: v for k, v in kwargs.items() if k in non_pipeline_inputs}

                # TODO: cache built pipeline component
                pipeline_component = pipeline_builder.build(
                    user_provided_kwargs=kwargs,
                    non_pipeline_params_dict=non_pipeline_params_dict
                )
            finally:
                # use `finally` to ensure pop operation from the stack
                dsl_settings = _dsl_settings_stack.pop()

            # update on_init/on_finalize settings if init/finalize job is set
            if dsl_settings.init_job_set:
                job_settings["on_init"] = dsl_settings.init_job_name(pipeline_component.jobs)
            if dsl_settings.finalize_job_set:
                job_settings["on_finalize"] = dsl_settings.finalize_job_name(pipeline_component.jobs)

            # TODO: pass compute & default_compute separately?
            common_init_args = {
                "experiment_name": experiment_name,
                "component": pipeline_component,
                "inputs": kwargs,
                "tags": tags,
            }
            if _is_inside_dsl_pipeline_func():
                # on_init/on_finalize is not supported for pipeline component
                if job_settings.get("on_init") is not None or job_settings.get("on_finalize") is not None:
                    raise UserErrorException("On_init/on_finalize is not supported for pipeline component.")
                # Build pipeline node instead of pipeline job if inside dsl.
                built_pipeline = Pipeline(_from_component_func=True, **common_init_args)
                if job_settings:
                    module_logger.warning(
                        ("Job settings %s on pipeline function %r are ignored " "when using inside PipelineJob."),
                        job_settings,
                        func.__name__,
                    )
            else:
                built_pipeline = PipelineJob(
                    jobs=pipeline_component.jobs,
                    compute=compute,
                    settings=PipelineJobSettings(**job_settings),
                    **common_init_args,
                )

            return built_pipeline

        wrapper._is_dsl_func = True
        wrapper._job_settings = job_settings
        wrapper._pipeline_builder = pipeline_builder
        return wrapper

    # enable use decorator without "()" if all arguments are default values
    if func is not None:
        return pipeline_decorator(func)
    return pipeline_decorator


def _validate_args(func, args, kwargs, non_pipeline_inputs):
    """Validate customer function args and convert them to kwargs."""
    if not isinstance(non_pipeline_inputs, List) or \
            any(not isinstance(param, str) for param in non_pipeline_inputs):
        msg = "Type of 'non_pipeline_parameter' in dsl.pipeline should be a list of string"
        raise UserErrorException(message=msg, no_personal_data_message=msg)
    # Positional arguments validate
    all_parameters = [param for _, param in signature(func).parameters.items()]
    # Implicit parameter are *args and **kwargs
    if any(param.kind in {param.VAR_KEYWORD, param.VAR_POSITIONAL} for param in all_parameters):
        raise UnsupportedParameterKindError(func.__name__)

    all_parameter_keys = [param.name for param in all_parameters]
    non_pipeline_inputs = non_pipeline_inputs or []
    unexpected_non_pipeline_inputs = [param for param in non_pipeline_inputs if param not in all_parameter_keys]
    if unexpected_non_pipeline_inputs:
        raise ParamValueNotExistsError(func.__name__, unexpected_non_pipeline_inputs)

    empty_parameters = {param.name: param for param in all_parameters if param.default is Parameter.empty}
    min_num = len(empty_parameters)
    max_num = len(all_parameters)
    if len(args) > max_num:
        raise TooManyPositionalArgsError(func.__name__, min_num, max_num, len(args))

    provided_args = OrderedDict({param.name: args[idx] for idx, param in enumerate(all_parameters) if idx < len(args)})
    for _k in kwargs.keys():
        if _k not in all_parameter_keys:
            raise UnexpectedKeywordError(func.__name__, _k, all_parameter_keys)
        if _k in provided_args.keys():
            raise MultipleValueError(func.__name__, _k)
        provided_args[_k] = kwargs[_k]

    if len(provided_args) < len(empty_parameters):
        missing_keys = empty_parameters.keys() - provided_args.keys()
        raise MissingPositionalArgsError(func.__name__, missing_keys)

    def _is_supported_data_type(_data):
        return (
            isinstance(_data, SUPPORTED_INPUT_TYPES)
            or is_parameter_group(_data)
        )

    for pipeline_input_name in provided_args:
        data = provided_args[pipeline_input_name]
        if data is not None and not _is_supported_data_type(data) and \
                pipeline_input_name not in non_pipeline_inputs:
            msg = (
                "Pipeline input expected an azure.ai.ml.Input or primitive types (str, bool, int or float), "
                "but got type {}."
            )
            raise UserErrorException(
                message=msg.format(type(data)),
                no_personal_data_message=msg.format("[type(pipeline_input_name)]"),
            )

    return provided_args
