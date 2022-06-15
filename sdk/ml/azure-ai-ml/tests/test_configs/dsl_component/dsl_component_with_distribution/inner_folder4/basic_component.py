from mldesigner import command_component
from azure.ai.ml import MpiDistribution

distribution = MpiDistribution()
distribution.process_count_per_instance = 3

@command_component(distribution=distribution)
def basic_component(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
