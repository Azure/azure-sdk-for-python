from azure.ai.ml import MLClient
from azure.identity import InteractiveBrowserCredential as Credential

from azure.ai.ml.entities._autogen_entities.models import ServerlessEndpoint

"""client = MLClient(
    Credential(tenant_id="7f292395-a08f-4cc0-b3d0-a400b023b0d2"),
    "75703df0-38f9-4e2e-8328-45f6fc810286",
    "rg-neduvvuraieu2",
    workspace_name="neduvvur-7714",
)"""

endpoint = ServerlessEndpoint(
    model_id="azureml://registries/azureml-mistral/models/Mistral-large",
    name="mistral-from-sdk",
    properties={},
)

endpoint._validate()

"""serverless_endpoint = client.serverless_endpoints.begin_create_or_update(
    endpoint=endpoint
).result()
print(serverless_endpoint.as_dict())"""