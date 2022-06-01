from mldesigner import command_component

# Default environment when not set
@command_component()
def basic_module(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
