from mldesigner import command_component


@command_component(environment="azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:5")
def basic_module(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    return port1
