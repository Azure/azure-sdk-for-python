# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather

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
#  - Possibly encapsulate entire scatter/gather loop with a do-while loop (individual scatters will be managed by a parallel-for loop). 
#     - See https://github.com/Azure/DesignerPrivatePreviewFeatures/blob/d8732de8f3f201aebeac2f079f8f89e3592be2ba/azure-ai-ml/samples/control-flow/federated-learning/native/main.py#L151
#     - And for p-for: https://azureml-pipelines-doc-1p.azurewebsites.net/features/control_flow/parallel_for.html
#  - change output to be... whatever the standard output of a model training step is.
# 
# QUESTION: do we need another decorator that's a level 'above' this?
# I'm unsure if there's a market for a new decorator that would be similar in scope to the @pipeline decorator, but specialized
# for FL experiements, if it's assumed that users would just plug this component into larger experiments.
def fl_scatter_gather(
    *, 
    model,
    silo_configs,
    learning_func,
    aggregation_func,
    max_iterations,
    **kwargs,
):
    fl_scatter_gather_node = FLScatterGather(
        
    )