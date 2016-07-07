# Intro

This project provides a Ruby gem for easy access to the Azure ARM Storage API. With this gem you can create/update/list/delete storage accounts. Usage operation aren't supported yet.

# Supported Ruby Versions

* Ruby 2+

Note: x64 Ruby for Windows is known to have some compatibility issues.

# Getting started

## Setting up the service principal

First of all to start interacting with the ARM resources you will need to setup a service principal. Service principal is an Azure application which allows you to authenticate to Azure and access Azure services. The detailed steps of how to setup a service principal can be found in this article: http://aka.ms/cli-service-principal. In the result of setting up service principal you will get tenant id, client id and client secret data.

## Installation

install the appropriate gem:

```
gem install azure_mgmt_storage
```

and reference it in your code:

```Ruby
require 'azure_mgmt_storage'
```

After that you should be ready to start using SDK!

## Authentication

```Ruby
# Create authentication objects
token_provider = MsRestAzure::ApplicationTokenProvider.new(tenant_id, client_id, secret)
credentials = MsRest::TokenCredentials.new(token_provider)
```

To get tenant_id, client_id and secret for your Azure application visit Azure portal or copy them from the powershell script from the article mentioned above.

## Creating storage account

```Ruby
# Create a client - a point of access to the API and set the subscription id
client = Azure::ARM::Storage::StorageManagementClient.new(credentials)
client.subscription_id = subscription_id

# Create a model for new storage account.
props = Models::StorageAccountPropertiesCreateParameters.new

params = Models::StorageAccountCreateParameters.new
params.properties = props
params.location = 'westus'
sku = Models::Sku.new
sku.name = 'Standard_LRS'
params.sku = sku
params.kind = Models::Kind::Storage

promise = client.storage_accounts.create('some_existing_resource_group', 'newstorageaccount', params)
```

The SDK method returns a promise which you can utilize depending on your needs. E.g. if you need to get result immediately via sync blocking call - do the following:

```Ruby
result = promise.value!
```

If you need to follow async flow - provide a block which will be executed in off main thread:

```Ruby
promise = promise.then do |result|
  # Handle the result
end
```

In both cases you're returned an instance of MsRestAzure::AzureOperationResponse which contains HTTP requests/response objects and response body. Response body is a deserialized object representing the received information. In case of code above - newly created storage account. To get data from it:

```Ruby
storage_account = result.body

p storage_account.location
p storage_account.sku.name
```

Congrats, you've create new storage account. We encourage you to try more stuff and let us know your feedback!
For advanced SDK usage please reference to the spec file storage_management_spec.rb.
