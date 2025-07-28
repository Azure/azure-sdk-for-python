project_name = "EmailAppEnglish"
deployment_name = "deployment1"
deployment_client = client.get_deployment(project_name, deployment_name)

# Prepare request body
body = ConversationAuthoringCreateDeploymentDetails(trained_model_label="ModelWithDG")

# Start deployment
poller = deployment_client.begin_deploy_project(body)
result = poller.result()  # Wait for completion

# Access operation-location for logging/debugging
operation_location = poller._polling_method._initial_response.http_response.headers.get("operation-location", "Not found")
status_code = poller._polling_method._initial_response.http_response.status_code

print(f"Operation-Location: {operation_location}")
print(f"Operation completed with status code: {status_code}")

assert result is None
assert poller.status() == "succeeded"