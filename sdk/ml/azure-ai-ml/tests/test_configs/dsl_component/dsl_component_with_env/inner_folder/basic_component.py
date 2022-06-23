from mldesigner import command_component


@command_component(environment="../conda.yaml")
def basic_module(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
