# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access



module_logger = logging.getLogger(__name__)

# This should be the implementation of what's used in the spec here: https://github.com/Azure/azureml_run_specification/blob/aims/flspec/specs/federated-learning/examples/sdk/1_preprocessing.py#L189
# General idea, this decorator will be used to warp a code snippet that would be used to in a scatter gather loop
# for FL learning. 
#
# Here's some example pseudocode usage. The resulting variable "pipeline_fl_component" will be a sub pipeline job(?) that performs 
# a scatter/gather loop across the inputted silos, with the actual per-silo code being the contents of the original user_func: 
# @this_decorator(silo configs, scatter/gather configs)
# user_func(ml_input):
#   ~do per-silo-based learning step.
# ...
# pipeline_fl_component = user_func(ml_input=input_location)
#
#
# We can hopefully leverage a lot of code from the STCA project to achieve this: https://github.com/Azure/DesignerPrivatePreviewFeatures/tree/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native
# At a high level, I believe we just want to turn the following code into it's own decorator, with a few changes: https://github.com/Azure/DesignerPrivatePreviewFeatures/blob/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native/main.py#L87
#  Changes include: 
#  - Expand inputs to match spec
#  - Possibly encapsulate entire scatter/gather loop with a do-while loop (). See https://github.com/Azure/DesignerPrivatePreviewFeatures/blob/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native/main.py#L151
#  - change output to be... whatever the standard output of a model training step is.
# 
# QUESTION: do we need another decorator that's a level 'above' this?
# I'm unsure if there's a market for a new decorator that would be similar in scope to the @pipeline decorator, but specialized
# for FL experiements, if it's assumed that users would just plug this component into larger experiments.
def fl_scatter_gather(
    func=None,
    *, 
    # Todo determine inputs
    # We'll probably want to reinstante most of the generic inputs from the pipeline decorator.
    # Known FL-specific inputs include all the fields of the hypothetical scatter_gather_loop object
    # defined in the spec here: https://github.com/Azure/azureml_run_specification/blob/aims/flspec/specs/federated-learning/examples/sdk/2_model_evaluation.py#L256
    # Determining how we want to represent that from a user's perspective will probably be a long discussion.
    #
    **kwargs,
):
    """ Build a pipeline that encapsulates the scatter/gather graph that is central
    to performing federated learning (TODO: add public/wiki link to explain what FL is)

    TODO: example
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    """

    def fl_scatter_gather_decorator(func: _TFunc) -> _TFunc:
        if not isinstance(func, Callable):  # pylint: disable=isinstance-second-argument-not-valid-type
            raise UserErrorException(f"Dsl fl scatter gather decorator accept only function type, got {type(func)}.")

        # Todo process kwargs

        # Todo understand this - seems like some sort of alternative file input, but it's inclear when/why this executes.
        func_entry_path = _resolve_source_file()
        if not func_entry_path:
            func_path = Path(inspect.getfile(func))
            # in notebook, func_path may be a fake path and will raise error when trying to resolve this fake path
            if func_path.exists():
                func_entry_path = func_path.resolve().absolute()

        job_settings = {k: v for k, v in job_settings.items() if v is not None}
        # TODO: At the end of the day, we're still just producing a pipeline, so I'm not sure how much
        # This will need to be changed, if at all.
        # This might depend partially on if we decide to make a unique FL entity of any sort, like
        # a child class of pipeline or otherwise. For now, I don't think we want to do that, yet.
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

        # See https://docs.python.org/3/library/functools.html#functools.wraps for what this is doing
        # See this for why: https://stackoverflow.com/questions/308999/what-does-functools-wraps-do
        @wraps(func)
        def wrapper(*args, **kwargs) -> PipelineJob:
            # TOdo implement this - I need to spend more than 5 minutes staring at the pipeline equivalent of this function,
            # since that wasn't enough for me to make heads or tails of this.

        wrapper._is_dsl_func = True
        wrapper._job_settings = job_settings
        wrapper._pipeline_builder = pipeline_builder
        return wrapper

    # enable use decorator without "()" if all arguments are default values
    if func is not None:
        return pipeline_decorator(func)
    return pipeline_decorator


def _validate_args(func, args, kwargs, non_pipeline_inputs):
    pass
   # TODO see corresponding function in _pipeline_deecorator and adapt accordingly