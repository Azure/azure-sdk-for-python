from azure.ai.ml import MLClient
from azure.ai.ml.entities import Workspace, WorkspaceConnection
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities import ApiKeyConfiguration


credentials = ApiKeyConfiguration(
    key="***"
)

# get a handle to the subscription
ml_client = MLClient(
    credential=DefaultAzureCredential(),
    subscription_id="<SUBSCRIPTION_ID>",
    resource_group_name="<RESOURCE_GROUP_NAME>"
)

connection = WorkspaceConnection(
    name="e2etestConn",
    type="AzureOpenAI",
    credentials=credentials,
    target="https://open-hanchi.openai.azure.com/",
    metadata = {'Kind': 'dummy', 'ApiVersion': 'dummy', 'ApiType': 'dummy'}
)

# get the workspace hub through the ml_client
hub = ml_client.connections.create_or_update(connection)


print("Created workspace:\n{}".format(result))