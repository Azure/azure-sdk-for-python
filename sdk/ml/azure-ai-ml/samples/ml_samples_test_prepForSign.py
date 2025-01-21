from azure.identity import (
    DefaultAzureCredential,
    AzureCliCredential,
    InteractiveBrowserCredential,
)
from azure.ai.ml import MLClient, load_job
from azure.ai.ml.entities import Data, ManagedOnlineEndpoint, Job, CommandComponent
from azure.ai.ml.sweep import SweepJob, GridSamplingAlgorithm, Choice, Objective
from azure.ai.ml import command
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities._load_functions import load_component

subscription_id = "2d385bf4-0756-4a76-aa95-28bf9ed3b625"
resource_group = "sdkv2-20240925-rg"
workspace_name = "sdkv2-20240925-ws"


credential = DefaultAzureCredential()

print(credential)
ml_client = MLClient(
    credential=credential,
    subscription_id=subscription_id,
    resource_group_name=resource_group,
    workspace_name=workspace_name,
)

component = load_component(
    "C:\\Projects\\azure-sdk-for-python\\sdk\\ml\\azure-ai-ml\\azure\\ai\\ml\\YAMLsigning\\sum1.yaml"
)
ml_client.components.prepare_for_sign(component)
