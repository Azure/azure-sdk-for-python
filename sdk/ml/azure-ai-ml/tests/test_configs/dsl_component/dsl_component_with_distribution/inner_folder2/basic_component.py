from mldesigner import command_component
from azure.ai.ml import TensorFlowDistribution


distribution = TensorFlowDistribution()
distribution.worker_count = 2

@command_component(distribution=distribution)
def basic_component(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
