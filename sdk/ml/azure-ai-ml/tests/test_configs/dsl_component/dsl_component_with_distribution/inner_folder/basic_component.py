from mldesigner import command_component


@command_component(distribution={"type": "mpi"})
def basic_component(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
