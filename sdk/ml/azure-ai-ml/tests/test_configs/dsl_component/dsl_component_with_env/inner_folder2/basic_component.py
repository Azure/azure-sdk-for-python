from mldesigner import command_component
from azure.ai.ml.entities._assets import Environment

my_env = Environment.load(path="../conda.yaml")


@command_component(environment=my_env)
def basic_module(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
