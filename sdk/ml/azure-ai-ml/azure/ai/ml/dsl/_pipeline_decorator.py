# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import OrderedDict
from functools import wraps
from inspect import signature, Parameter
from typing import TypeVar, Callable, Any, Dict
from azure.ai.ml.entities._inputs_outputs import Input

from azure.ai.ml.entities._job.pipeline._exceptions import (
    UnsupportedParameterKindError,
    TooManyPositionalArgsError,
    UnexpectedKeywordError,
    MultipleValueError,
    MissingPositionalArgsError,
    UserErrorException,
)
from azure.ai.ml.dsl._pipeline_component_builder import PipelineComponentBuilder
from azure.ai.ml.entities import PipelineJob, PipelineJobSettings
from azure.ai.ml.entities._job.pipeline._io import PipelineInput
from azure.ai.ml.constants import ComponentSource

_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])

SUPPORTED_INPUT_TYPES = (
    PipelineInput,
    Input,
    str,
    bool,
    int,
    float,
)


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
    """Build a pipeline which contains all component nodes defined in this function. Currently only single layer pipeline is supported.

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

        @wraps(func)
        def wrapper(*args, **kwargs) -> PipelineJob:
            # Default args will be added here.
            provided_positional_args = _validate_args(func, args, kwargs)
            # Convert args to kwargs
            kwargs.update(provided_positional_args)

            # TODO: cache built pipeline component
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
            pipeline_component = pipeline_builder.build(_build_pipeline_parameter(func))

            # TODO: pass compute & default_compute separately?
            built_pipeline = PipelineJob(
                jobs=pipeline_component.components,
                component=pipeline_component,
                experiment_name=experiment_name,
                compute=actual_compute,
                tags=tags,
                settings=PipelineJobSettings(
                    default_datastore=default_datastore,
                    default_compute=None,
                    continue_on_step_failure=continue_on_step_failure,
                    force_rerun=force_rerun,
                ),
                inputs=kwargs,
            )

            return built_pipeline

        wrapper._is_dsl_func = True
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


def _build_pipeline_parameter(func):
    # transform kwargs
    transformed_kwargs = {}

    def all_params(parameters):
        for value in parameters.values():
            yield value

    if func is None:
        return transformed_kwargs

    parameters = all_params(signature(func).parameters)
    # transform default values
    for left_args in parameters:
        if left_args.name not in transformed_kwargs.keys():
            default = left_args.default if left_args.default is not Parameter.empty else None
            transformed_kwargs[left_args.name] = _wrap_pipeline_parameter(left_args.name, default)
    return transformed_kwargs


def _wrap_pipeline_parameter(key, value):
    # Note: here we build PipelineInput to mark this input as a data binding.
    return PipelineInput(name=key, meta=None, data=value)
