# Microsoft Azure SDK for Python

This is the Microsoft Azure Communication Management Client Library.
This package has been tested with Python 2.7, 3.5, 3.6, 3.7 and 3.8.
For a more complete view of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).

# Usage

For additional code examples, see [Communication Service Management](https://docs.microsoft.com/python/api/overview/azure/)
on docs.microsoft.com.

## Prerequisites

See the [Python developer
guide](https://docs.microsoft.com/azure/developer/python/configure-local-development-environment?tabs=cmd)
to configure your dev environment and set the needed environment variables.

## Examples

### Authentication

This example authenticates to Azure using a service principal. Documentation on creating and managing a
service principal in AAD can be found
[here](https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal).

```python
def __create_communication_management_client(credentials):
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID");
    if subscription_id is None:
        return None

    return CommunicationServiceManagementClient(credentials, subscription_id)

def __create_service_principal_credentials():
    # service principal's app id; `<your-app-id>`
    app_id = os.environ.get("AZURE_CLIENT_ID");
    # one of the service principal's client secrets; `<your-password>`
    client_secret = os.environ.get("AZURE_CLIENT_SECRET");
    # id of the principal's Azure Active Directory tenant; `<your-tenant-id>`
    tenant_id = os.environ.get("AZURE_TENANT_ID");

    if app_id is None or client_secret is None or tenant_id is None:
        return None

    return ServicePrincipalCredentials(client_id=app_id, secret=client_secret, tenant=tenant_id)
```

### Create a communication service resource

```python
def __create_communication_service(mgmt_client, resourceGroupName, resourceName):
    resource = CommunicationServiceResource(location="global", data_location = "UnitedStates")
    mgmt_client.communication_service.create_or_update(resourceGroupName, resourceName, resource)
```

### List all communication services

```python
def __list_communication_service(mgmt_client):
    resources = mgmt_client.communication_service.list_by_subscription();
    for resource in resources:
        print(resource)
```

### Delete a communication service

```python
def __delete_communication_service(mgmt_client, resourceGroupName, resourceName):
    mgmt_client.communication_service.delete(resourceGroupName, resourceName)
```

# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.
