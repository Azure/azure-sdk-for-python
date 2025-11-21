"""
Example demonstrating how to use the defaultDeploymentTemplate field in Model.

This shows both JSON and Python object creation methods, as well as 
creating models in Azure ML using MLClient.
"""

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.ai.ml.entities._assets.default_deployment_template import DefaultDeploymentTemplate
from azure.identity import DefaultAzureCredential

# Example 1: Create a model with default deployment template using Python objects
default_template = DefaultDeploymentTemplate(
    asset_id="azureml://registries/registry1/deploymenttemplates/tfs-dt1-full-unsecuretest-contosoint/versions/2"
)

model = Model(
    name="my-model",
    version="1",
    path="./samples/model-artifacts/model.pkl",
    type="custom_model",
    description="Model with default deployment template",
    default_deployment_template=default_template,
    tags={"framework": "pytorch", "task": "classification"}
)

print(f"Model created: {model.name} v{model.version}")
print(f"Default deployment template: {model.default_deployment_template.asset_id if model.default_deployment_template else None}")

# Example 2: Create a model with default deployment template using dict
model2 = Model(
    name="my-model-2",
    version="1",
    path="./samples/model-artifacts/model.pkl",
    type="custom_model",
    description="Model with default deployment template from dict",
    default_deployment_template={
        "asset_id": "azureml://registries/unsecuretest-contosoint/deploymenttemplates/tfs-dt2-full-unsecuretest-contosoint/versions/6"
    },
    tags={"framework": "tensorflow"}
)

print(f"\nModel 2 created: {model2.name} v{model2.version}")
print(f"Default deployment template: {model2.default_deployment_template.asset_id if model2.default_deployment_template else None}")

# Example 3: JSON representation of the defaultDeploymentTemplate field
# When serialized, the structure will be:
# {
#     "name": "my-model",
#     "version": "1",
#     "type": "mlflow_model",
#     "path": "./samples/model-artifacts/model.pkl",
#     "description": "Model with default deployment template",
#     "defaultDeploymentTemplate": {
#         "assetId": "azureml://registries/registry1/deploymenttemplates/tfs-dt1-full-unsecuretest-contosoint/versions/2"
#     }
# }

print("\n" + "="*80)
print("MLClient Examples - Creating Models in Azure ML")
print("="*80)

# Example 4: Create a model in Azure ML workspace using MLClient
# try:
    # Initialize MLClient with DefaultAzureCredential
    # Replace with your subscription_id, resource_group, and workspace_name
ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id="2d385bf4-0756-4a76-aa95-28bf9ed3b625",
    resource_group_name="kchawla-rg",
    # workspace_name="kchawla-ws-region",
    registry_name="UnsecureTest-kchawla-reg",
)
    
    # Create a model with default deployment template
model_with_template = Model(
    name="sdk-model-with-template",
    version="12",
    path="./samples/model-artifacts/model.pkl",
    type="custom_model",
    description="Model created via MLClient with default deployment template",
    # default_deployment_template=DefaultDeploymentTemplate(
    #     asset_id="azureml://registries/UnsecureTest-kchawla-reg/deploymenttemplates/DT01/versions/1"
    # ),
    tags={
        "framework": "pytorch",
        "task": "classification",
        "created_by": "sdk-example"
    }
)
# print(f"Model before submit: {model_with_template}\n\n")
# # Register the model in Azure ML
# print("\n[Example 4] Creating model in Azure ML workspace...")
registered_model = ml_client.models.create_or_update(model_with_template)

# print(f"✓ Model registered successfully!")
# print(f"  Model: {registered_model}\n\n")
# print(f"  Version: {registered_model.version}")
# print(f"  ID: {registered_model.id}")

# if registered_model.default_deployment_template:
#     print(f"  Default Deployment Template: {registered_model.default_deployment_template.asset_id}")
# else:
#     print(f"  No Default Deployment Template configured")
print(ml_client.models.get(name="sdk-model-with-template", version="12"))
    # import pdb;pdb.set_trace()
# except Exception as e:
#     print(f"Note: To run this example, update the MLClient configuration with your Azure ML details.")
#     print(f"Error: {e}")

# # Example 5: Create model from YAML file using MLClient
# print("\n[Example 5] Creating model from YAML file...")
# try:
#     # Load and create model from YAML file
#     # The YAML file should contain the defaultDeploymentTemplate field
#     model_from_yaml = ml_client.models.create_or_update(
#         model="./model-with-deployment-template.yaml"
#     )
    
#     print(f"✓ Model created from YAML!")
#     print(f"  Name: {model_from_yaml.name}")
#     print(f"  Version: {model_from_yaml.version}")
#     if model_from_yaml.default_deployment_template:
#         print(f"  Default Deployment Template: {model_from_yaml.default_deployment_template.asset_id}")
    
# except Exception as e:
#     print(f"Note: Ensure 'model-with-deployment-template.yaml' exists in the current directory.")
#     print(f"Error: {e}")

# # Example 6: Get an existing model and check its default deployment template
# print("\n[Example 6] Retrieving existing model...")
# try:
#     # Get a model by name and version
#     retrieved_model = ml_client.models.get(
#         name="sdk-model-with-template",
#         version="1"
#     )
    
#     print(f"✓ Model retrieved successfully!")
#     print(f"  Name: {retrieved_model.name}")
#     print(f"  Version: {retrieved_model.version}")
#     print(f"  Type: {retrieved_model.type}")
    
#     # Check if it has a default deployment template
#     if retrieved_model.default_deployment_template:
#         print(f"  Default Deployment Template:")
#         print(f"    Asset ID: {retrieved_model.default_deployment_template.asset_id}")
#     else:
#         print(f"  No default deployment template configured")
    
# except Exception as e:
#     print(f"Note: Model must exist in the workspace to be retrieved.")
#     print(f"Error: {e}")

# # Example 7: Update an existing model's default deployment template
# print("\n[Example 7] Updating model's default deployment template...")
# try:
#     # Get existing model
#     model_to_update = ml_client.models.get(name="sdk-model-with-template", version="1")
    
#     # Update the default deployment template
#     model_to_update.default_deployment_template = DefaultDeploymentTemplate(
#         asset_id="azureml://registries/kchawla-reg/deploymenttemplates/DT01/versions/1"
#     )
    
#     # Update the model in Azure ML
#     updated_model = ml_client.models.create_or_update(model_to_update)
    
#     print(f"✓ Model updated successfully!")
#     print(f"  New Default Deployment Template: {updated_model.default_deployment_template.asset_id}")
    
# except Exception as e:
#     print(f"Note: Model must exist in the workspace to be updated.")
#     print(f"Error: {e}")

# print("\n" + "="*80)
# print("Examples completed!")
# print("="*80)
