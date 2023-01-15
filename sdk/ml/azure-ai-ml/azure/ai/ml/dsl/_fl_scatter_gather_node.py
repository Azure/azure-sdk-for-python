# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather

# This should be the implementation of what's used in the spec here: https://github.com/Azure/azureml_run_specification/blob/aims/flspec/specs/federated-learning/examples/sdk/1_preprocessing.py#L189
# General idea, this node will be used to warp code snippets into in a scatter gather loop
# for FL learning. 
#
# Here's some example pseudocode usage. The output of FLScatterGather(inputs) is a node which,
# when included in the definition of a @pipeline function, will produce a subgraph that performs
# a scatter-gather loop in AML:
#  
# @pipeline(name = "example_fl_pipeline")
# pipeline_func():
#   fl_node = FLScatterGather(
#     model=get_initial_model(),
#     silo_configs=silo_config_list,
#     learning_func=train_model_func,
#     aggregation_func=gather_models_func,
#     max_iterations=100)
#   return {pipeline_output : fl_node.output}
# ...
# fl_pipeline = pipeline_func()
# ml_client.jobs.create_or_update(fl_pipeline, experiment_name="fl_pipeline")
#
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
def fl_scatter_gather(
    *, 
    model,
    silo_configs,
    learning_func,
    aggregation_func,
    max_iterations,
    **kwargs,
):
    return FLScatterGather(model=model, # TODO determine typehint of this
        silo_configs=silo_configs, # TODO determine (and probably create) typehint of this
        learning_func=learning_func, # TODO determine typehint of this
        aggregation_func=aggregation_func, # TODO determine typehint of this
        max_iterations=max_iterations: int,
        )