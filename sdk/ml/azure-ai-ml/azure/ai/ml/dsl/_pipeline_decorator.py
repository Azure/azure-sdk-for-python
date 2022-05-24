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
    default_compute: str = None,
    default_datastore: str = None,
    tags: Dict[str, str] = None,
    continue_on_step_failure: bool = None,
    **kwargs,
):
    """Build a pipeline which contains all component nodes defined in this function. Currently only single layer pipeline is supported.

    .. note::

        The following pseudo-code shows how to create a pipeline using this decorator.

    .. code-block:: python

                # A pipeline defined with decorator
                @dsl.pipeline(name='sample pipeline', description='pipeline description')
                def pipeline(pipeline_parameter1, pipeline_parameter2):
                        # component1 and component2 will be added into the current sub pipeline
                        component1 = component1_func(input1=xxx, param1=xxx)
                        component2 = component2_func(input1=xxx, param1=xxx)
                        # A decorated pipeline function needs to return outputs.
                        # In this case, the sub_pipeline has two outputs: component1's output1 and component2's output1, and
                        # let's rename them to 'renamed_output1' and 'renamed_output2'
                        return {'renamed_output1': component1.outputs.output1, 'renamed_output2': component2.outputs.output1}

                # E.g.: This call returns a pipeline with nodes=[component1, component2],
                # outputs={'renamed_output1': component1.outputs.output1, 'renamed_output2': component2.outputs.output1}
                pipeline1 = pipeline(pipeline_parameter1=param1, pipeline_parameter2=param2)
                pipeline1.submit(parameters={"pipeline_parameter1": changed_param})

    .. remarks::

        Parameters in pipeline decorator functions will be stored as a substitutable part of the pipeline,
        which means you can change them directly in the re-submit or other operations in the future without
        re-construct a new pipeline.
        E.g.: change pipeline_parameter1 of pipeline when submit it.

    :param name: The name of pipeline component, defaults to None
    :type name: str, optional
    :param version: The version of pipeline component, defaults to None
    :type version: str, optional
    :param display_name: The display name of pipeline component, defaults to None
    :type display_name: str, optional
    :param description: The description of the built pipeline, defaults to None
    :type description: str, optional
    :param experiment_name: Name of the experiment the job will be created under, if None is provided, experiment will be set to current directory, defaults to None
    :type experiment_name: str, optional
    :param default_compute: The compute target of the built pipeline, defaults to None
    :type default_compute: str, optional
    :param default_datastore: The default datastore of pipeline, defaults to None
    :type default_datastore: str, optional
    :param tags: The tags of pipeline component, defaults to None
    :type tags: Dict[str, str], optional
    :param continue_on_step_failure: Flag when set, continue pipeline execution if a step fails, defaults to None
    :type continue_on_step_failure: bool, optional
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def pipeline_decorator(func: _TFunc) -> _TFunc:
        # Support both compute and default_compute target, but compute will have higher priority
        compute = kwargs.get("compute", None)
        default_compute_target = kwargs.get("default_compute_target", None)
        actual_compute = default_compute or compute or default_compute_target
        force_rerun = kwargs.get("force_rerun", False)

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
                display_name=display_name if display_name else func.__name__,
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
