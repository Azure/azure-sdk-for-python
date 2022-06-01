from mldesigner import command_component
from azure.ai.ml.entities._inputs_outputs import Input, Output

@command_component(
    name="microsoftsamples_command_component_basic",
    version="0.0.1",
    display_name="CommandComponentBasic",
    tags={"tag": "tagvalue", "owner": "sdkteam"},
    environment="azureml:AzureML-sklearn-0.24-ubuntu18.04-py37-cpu:1",
    distribution= {"type": "Tensorflow", "parameter_server_count": 1, "worker_count": 2, "added_property": 7}
)
def hello_world(
        component_in_number: Input(type="number", description="A number", default=10.99),
        component_in_path: Input(description="A path"),
        component_out_path: Output()
):
    """This is the basic command component"""
    print("Hello World!")


@command_component(
    name="microsoftsamples_command_component_tensorflow",
    display_name="CommandComponentTensorFlow",
    distribution= {"type": "Tensorflow", "parameter_server_count": 1, "worker_count": 2, "added_property": 7}
)
def hello_world_tensorflow():
    """This is the TensorFlow command component"""
    print("Hello World!")

