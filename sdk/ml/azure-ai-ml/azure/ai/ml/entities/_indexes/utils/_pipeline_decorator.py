# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import inspect
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union, overload

from typing_extensions import ParamSpec

from azure.ai.ml.entities import Data, Model, PipelineJob, PipelineJobSettings
from azure.ai.ml.entities._builders.pipeline import Pipeline
from azure.ai.ml.entities._inputs_outputs import Input
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput, _GroupAttrDict
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.exceptions import UserErrorException

from azure.ai.ml.dsl._pipeline_component_builder import PipelineComponentBuilder, _is_inside_dsl_pipeline_func
from azure.ai.ml.dsl._pipeline_decorator import _validate_args
from azure.ai.ml.dsl._settings import _dsl_settings_stack
from azure.ai.ml.dsl._utils import _resolve_source_file

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

T = TypeVar("T")
P = ParamSpec("P")


# Overload the returns a decorator when func is None
@overload
def pipeline(
    func: None,
    *,
    name: Optional[str] = None,
    version: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    experiment_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Callable[[Callable[P, T]], Callable[P, PipelineJob]]: ...


# Overload the returns a decorated function when func isn't None
@overload
def pipeline(
    func: Callable[P, T],
    *,
    name: Optional[str] = None,
    version: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    experiment_name: Optional[str] = None,
    tags: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Callable[P, PipelineJob]: ...


def pipeline(
    func: Optional[Callable[P, T]] = None,
    *,
    name: Optional[str] = None,
    version: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    experiment_name: Optional[str] = None,
    tags: Optional[Union[Dict[str, str], str]] = None,
    **kwargs: Any,
) -> Union[Callable[[Callable[P, T]], Callable[P, PipelineJob]], Callable[P, PipelineJob]]:
    """Build a pipeline which contains all component nodes defined in this function.

    :param func: The user pipeline function to be decorated.
    :type func: types.FunctionType
    :keyword name: The name of pipeline component, defaults to function name.
    :paramtype name: str
    :keyword version: The version of pipeline component, defaults to "1".
    :paramtype version: str
    :keyword display_name: The display name of pipeline component, defaults to function name.
    :paramtype display_name: str
    :keyword description: The description of the built pipeline.
    :paramtype description: str
    :keyword experiment_name: Name of the experiment the job will be created under, \
        if None is provided, experiment will be set to current directory.
    :paramtype experiment_name: str
    :keyword tags: The tags of pipeline component.
    :paramtype tags: dict[str, str]
    :return: Either
      * A decorator, if `func` is None
      * The decorated `func`

    :rtype: Union[
        Callable[[Callable], Callable[..., ~azure.ai.ml.entities.PipelineJob]],
        Callable[P, ~azure.ai.ml.entities.PipelineJob]

      ]

    .. admonition:: Example:

        .. literalinclude:: ../../../../samples/ml_samples_pipeline_job_configurations.py
            :start-after: [START configure_pipeline]
            :end-before: [END configure_pipeline]
            :language: python
            :dedent: 8
            :caption: Shows how to create a pipeline using this decorator.
    """

    # get_component force pipeline to return Pipeline instead of PipelineJob so we can set optional argument
    # need to remove get_component and rely on azure.ai.ml.dsl.pipeline
    get_component = kwargs.get("get_component", False)

    def pipeline_decorator(func: Callable[P, T]) -> Callable:
        # pylint: disable=isinstance-second-argument-not-valid-type
        if not isinstance(func, Callable):  # type: ignore
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
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[Pipeline, PipelineJob]:
            # Default args will be added here.
            # pylint: disable=abstract-class-instantiated
            # Node: push/pop stack here instead of put it inside build()
            # Because we only want to enable dsl settings on top level pipeline
            _dsl_settings_stack.push()  # use this stack to track on_init/on_finalize settings
            try:
                # Convert args to kwargs
                provided_positional_kwargs = _validate_args(func, args, kwargs, non_pipeline_inputs)

                # When pipeline supports variable params, update pipeline component to support the inputs in **kwargs.
                pipeline_parameters = {
                    k: v for k, v in provided_positional_kwargs.items() if k not in non_pipeline_inputs
                }
                pipeline_builder._update_inputs(pipeline_parameters)

                non_pipeline_params_dict = {
                    k: v for k, v in provided_positional_kwargs.items() if k in non_pipeline_inputs
                }

                # TODO: cache built pipeline component
                pipeline_component = pipeline_builder.build(
                    user_provided_kwargs=provided_positional_kwargs,
                    non_pipeline_inputs_dict=non_pipeline_params_dict,
                    non_pipeline_inputs=non_pipeline_inputs,
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
            common_init_args: Any = {
                "experiment_name": experiment_name,
                "component": pipeline_component,
                "inputs": pipeline_parameters,
                "tags": tags,
            }
            built_pipeline: Any = None
            if _is_inside_dsl_pipeline_func() or get_component:
                # on_init/on_finalize is not supported for pipeline component
                if job_settings.get("on_init") is not None or job_settings.get("on_finalize") is not None:
                    raise UserErrorException("On_init/on_finalize is not supported for pipeline component.")
                # Build pipeline node instead of pipeline job if inside dsl.
                built_pipeline = Pipeline(_from_component_func=True, **common_init_args)
                if job_settings:
                    module_logger.warning(
                        ("Job settings %s on pipeline function %r are ignored when using inside PipelineJob."),
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

        # Bug Item number: 2883169
        wrapper._is_dsl_func = True  # type: ignore
        wrapper._job_settings = job_settings  # type: ignore
        wrapper._pipeline_builder = pipeline_builder  # type: ignore
        return wrapper

    # enable use decorator without "()" if all arguments are default values
    if func is not None:
        return pipeline_decorator(func)
    return pipeline_decorator
