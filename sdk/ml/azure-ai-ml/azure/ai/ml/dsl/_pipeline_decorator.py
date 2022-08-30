# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
from collections import OrderedDict
from functools import wraps
from inspect import Parameter, signature
from typing import Any, Callable, Dict, TypeVar

from azure.ai.ml.dsl._pipeline_component_builder import PipelineComponentBuilder, _is_inside_dsl_pipeline_func
from azure.ai.ml.entities import PipelineJob, PipelineJobSettings
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.pipeline._exceptions import (
    MissingPositionalArgsError,
    MultipleValueError,
    TooManyPositionalArgsError,
    UnexpectedKeywordError,
    UnsupportedParameterKindError,
    UserErrorException,
)
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, PipelineOutputBase

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])

SUPPORTED_INPUT_TYPES = (
    PipelineInput,
    PipelineOutputBase,
    Input,
    str,
    bool,
    int,
    float,
)
module_logger = logging.getLogger(__name__)


def pipeline(
    *,
    name: str = None,
    version: str = None,
    display_name: str = None,
    description: str = None,
    experiment_name: str = None,
    tags: Dict[str, str] = None,
    continue_on_step_failure: bool = None,
    **kwargs,
):
    """Build a pipeline which contains all component nodes defined in this
    function. Currently only single layer pipeline is supported.

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

    :param name: The name of pipeline component, defaults to function name.
    :type name: str
    :param version: The version of pipeline component, defaults to "1".
    :type version: str
    :param display_name: The display name of pipeline component, defaults to function name.
    :type display_name: str
    :param description: The description of the built pipeline.
    :type description: str
    :param experiment_name: Name of the experiment the job will be created under, if None is provided, experiment will be set to current directory.
    :type experiment_name: str
    :param tags: The tags of pipeline component.
    :type tags: dict[str, str]
    :param continue_on_step_failure: Flag when set, continue pipeline execution if a step fails.
    :type continue_on_step_failure: bool
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def pipeline_decorator(func: _TFunc) -> _TFunc:
        # compute variable names changed from default_compute_targe -> compute -> default_compute -> none
        # to support legacy usage, we support them with priority.
        compute = kwargs.get("compute", None)
        default_compute_target = kwargs.get("default_compute_target", None)
        actual_compute = kwargs.get("default_compute", None) or compute or default_compute_target

        default_datastore = kwargs.get("default_datastore", None)
        force_rerun = kwargs.get("force_rerun", None)
        job_settings = {
            "default_datastore": default_datastore,
            "continue_on_step_failure": continue_on_step_failure,
            "force_rerun": force_rerun,
        }
        job_settings = {k: v for k, v in job_settings.items() if v is not None}
        pipeline_builder = PipelineComponentBuilder(
            func=func,
            name=name,
            version=version,
            display_name=display_name,
            description=description,
            compute=actual_compute,
            default_datastore=default_datastore,
            tags=tags,
        )

        @wraps(func)
        def wrapper(*args, **kwargs) -> PipelineJob:
            # Default args will be added here.
            provided_positional_args = _validate_args(func, args, kwargs)
            # Convert args to kwargs
            kwargs.update(provided_positional_args)

            # TODO: cache built pipeline component
            pipeline_component = pipeline_builder.build()

            # TODO: pass compute & default_compute separately?
            common_init_args = {
                "experiment_name": experiment_name,
                "component": pipeline_component,
                "inputs": kwargs,
                "tags": tags,
            }
            if _is_inside_dsl_pipeline_func():
                # Build pipeline node instead of pipeline job if inside dsl.
                built_pipeline = Pipeline(_from_component_func=True, **common_init_args)
                if job_settings:
                    module_logger.warning(
                        f"Job settings {job_settings} on pipeline function {func.__name__!r} are ignored when using inside PipelineJob."
                    )
            else:
                built_pipeline = PipelineJob(
                    jobs=pipeline_component.jobs,
                    compute=actual_compute,
                    settings=PipelineJobSettings(**job_settings),
                    **common_init_args,
                )

            return built_pipeline

        wrapper._is_dsl_func = True
        wrapper._job_settings = job_settings
        wrapper._pipeline_builder = pipeline_builder
        return wrapper

    return pipeline_decorator


def _validate_args(func, args, kwargs):
    """Validate customer function args and convert them to kwargs."""
    # Positional arguments validate
    all_parameters = [param for _, param in signature(func).parameters.items()]
    # Implicit parameter are *args and **kwargs
    if any(param.kind in {param.VAR_KEYWORD, param.VAR_POSITIONAL} for param in all_parameters):
        raise UnsupportedParameterKindError(func.__name__)

    all_parameter_keys = [param.name for param in all_parameters]
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

    for pipeline_input_name in provided_args:
        data = provided_args[pipeline_input_name]
        if data is not None and not isinstance(data, SUPPORTED_INPUT_TYPES):
            msg = (
                "Pipeline input expected an azure.ai.ml.Input or primitive types (str, bool, int or float), "
                "but got type {}."
            )
            raise UserErrorException(
                message=msg.format(type(data)),
                no_personal_data_message=msg.format("[type(pipeline_input_name)]"),
            )

    return provided_args
