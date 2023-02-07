# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
from typing import List, Dict


from azure.ai.ml.entities._builders.fl_scatter_gather import FLScatterGather
from azure.ai.ml.entities._assets.federated_learning_silo import FederatedLearningSilo
from azure.ai.ml.entities._component.pipeline_component import PipelineComponent
from azure.ai.ml.entities._assets._artifacts.model import Model

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
    initial_model: Model,
    silo_configs: List[FederatedLearningSilo],
    aggregation_config: Dict,
    silo_component: PipelineComponent,
    aggregation_component: PipelineComponent,
    silo_to_aggregation_argument_map: Dict,
    max_iterations: int,
    shared_silo_kwargs: Dict = None,
    aggregation_kwargs: Dict = None,
    **kwargs,
):
    """
    param silo_configs: A list of FederatedLearningSilo objects, which contain the necessary data
        to find and locally use data spread out across different datastores, as well as the inputs
        located therein.
    type silo_configs: List[FederatedLearningSilo]
    param aggregation_config: A dictionary containing configuration values for the aggregation component.
    type aggregation_config: Dict
    param silo_component: The component that will be duplicated across silos to perform model training
        on local datasets. These components are run on separate computes from rest of the pipeline,
        as specified by each silo's FederatedLearningSilo. 
    type silo_component: PipelineComponent
    param aggregation_component: The component that receives trained models from each silo and aggregates
        them into single model. Run on the 'main' compute of this node's job.
    type aggregation_component: PipelineComponent
    param max_iterations: The maximum number of scatter gather iterations that should be performed.
    type max_iterations: int
    param shared_silo_kwargs: A dictionary of kwargs to be injected into each duplicated silo component.
    type shared_silo_kwargs: Dict
    param aggregation_kwargs: A dictionary of kwargs to be injected into the aggregation component.
    type aggregation_kwargs: Dict
    """
    # Like most nodes, this is just a wrapper around a node builder entity initializer.
    return FLScatterGather(
        silo_configs=silo_configs,
        aggregation_config=aggregation_config,
        silo_component=silo_component,
        aggregation_component=aggregation_component,
        silo_to_aggregation_argument_map=silo_to_aggregation_argument_map
        max_iterations=max_iterations,
        shared_silo_kwargs=shared_silo_kwargs,
        aggregation_kwargs=aggregation_kwargs,
    )
        