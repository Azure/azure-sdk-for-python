from mldesigner import command_component
from azure.ai.ml.entities._job.resource_configuration import ResourceConfiguration

resources = ResourceConfiguration()
resources.instance_count = 2

@command_component(resources = resources)
def basic_component(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
