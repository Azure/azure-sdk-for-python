# Azure Azure Digital Twins Core client library for Python

This package contains an SDK for Azure Digital Twins API to provide access to the Azure Digital Twins service for managing twins, models, relationships, etc.

## Getting started

### Introduction

Azure Digital Twins is a developer platform for next-generation IoT solutions that lets you create, run, and manage digital representations of your business environment, securely and efficiently in the cloud. With Azure Digital Twins, creating live operational state representations is quick and cost-effective, and digital representations stay current with real-time data from IoT and other data sources. If you are new to Azure Digital Twins and would like to learn more about the platform, please make sure you check out the Azure Digital Twins [official documentation page](https://docs.microsoft.com/azure/digital-twins/overview).

For an introduction on how to program against the Azure Digital Twins service, visit the [coding tutorial page](https://docs.microsoft.com/azure/digital-twins/tutorial-code) for an easy step-by-step guide. Visit [this tutorial](https://docs.microsoft.com/azure/digital-twins/tutorial-command-line-app) to learn how to interact with an Azure Digital Twin instance using a command-line client application. Finally, for a quick guide on how to build an end-to-end Azure Digital Twins solution that is driven by live data from your environment, make sure you check out [this helpful guide](https://docs.microsoft.com/azure/digital-twins/tutorial-end-to-end).

The guides mentioned above can help you get started with key elements of Azure Digital Twins, such as creating Azure Digital Twins instances, models, twin graphs, etc. Use this samples guide below to familiarize yourself with the various APIs that help you program against Azure Digital Twins.

### How to Install

Install [azure-digitaltwins-core][pypi_package_keys] and
[azure-identity][azure_identity_pypi] with [pip][pip]:
```Bash
pip install azure-digitaltwins-core azure-identity
```
[azure-identity][azure_identity] is used for Azure Active Directory
authentication as demonstrated below.

### How to use

#### Authentication, permission

To create a new digital twins client, you need the endpoint to an Azure Digital Twin instance and credentials.
For the samples below, the `AZURE_URL`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` environment variables have to be set.
The client requires an instance of [TokenCredential](https://docs.microsoft.com/dotnet/api/azure.core.tokencredential?view=azure-dotnet) or [ServiceClientCredentials](https://docs.microsoft.com/dotnet/api/microsoft.rest.serviceclientcredentials?view=azure-dotnet).
In this samples, we illustrate how to use one derived class: [DefaultAzureCredentials](https://docs.microsoft.com/dotnet/api/azure.identity.defaultazurecredential?view=azure-dotnet).

> Note: In order to access the data plane for the Digital Twins service, the entity must be given permissions.
> To do this, use the Azure CLI command: `az dt rbac assign-role --assignee '<user-email | application-id>' --role owner -n '<your-digital-twins-instance>'`

DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
It attempts to use multiple credential types in an order until it finds a working credential.

##### Sample code

```python Snippet:dt_create_digitaltwins_service_client.py
# DefaultAzureCredential supports different authentication mechanisms and determines the appropriate credential type based of the environment it is executing in.
# It attempts to use multiple credential types in an order until it finds a working credential.

# - AZURE_URL: The URL to the ADT in Azure
url = os.getenv("AZURE_URL")

# DefaultAzureCredential expects the following three environment variables:
# - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
# - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
# - AZURE_CLIENT_SECRET: The client secret for the registered application
credential = DefaultAzureCredential()
service_client = DigitalTwinsClient(url, credential)
```

## Key concepts

Azure Digital Twins is an Azure IoT service that creates comprehensive models of the physical environment. It can create spatial intelligence graphs to model the relationships and interactions between people, spaces, and devices.
You can learn more about Azure Digital Twins by visiting [Azure Digital Twins Documentation](https://docs.microsoft.com/azure/digital-twins/).

## Examples

You can explore the digital twins APIs (using the client library) using the samples project.

The samples project demonstrates the following:

- Instantiate the client
- Create, get, and decommission models
- Create, query, and delete a digital twin
- Get and update components for a digital twin
- Create, get, and delete relationships between digital twins
- Create, get, and delete event routes for digital twin
- Publish telemetry messages to a digital twin and digital twin component

### Create, list, decommission, and delete models

#### Create models

Let's create models using the code below. You need to pass an array containing list of models.

```Python Snippet:dt_models_lifecycle
temporary_component = {
    "@id": component_id,
    "@type": "Interface",
    "@context": "dtmi:dtdl:context;2",
    "displayName": "Component1",
    "contents": [
    {
        "@type": "Property",
        "name": "ComponentProp1",
        "schema": "string"
    },
    {
        "@type": "Telemetry",
        "name": "ComponentTelemetry1",
        "schema": "integer"
    }
    ]
}

temporary_model = {
    "@id": model_id,
    "@type": "Interface",
    "@context": "dtmi:dtdl:context;2",
    "displayName": "TempModel",
    "contents": [
    {
        "@type": "Property",
        "name": "Prop1",
        "schema": "string"
    },
    {
        "@type": "Component",
        "name": "Component1",
        "schema": component_id
    },
    {
        "@type": "Telemetry",
        "name": "Telemetry1",
        "schema": "integer"
    }
    ]
}

new_models = [temporary_component, temporary_model]
models = service_client.create_models(new_models)
print('Created Models:')
print(models)
```

### List models
Using `list_models` to retrieve all created models

```Python Snippet:dt_models_lifecycle
listed_models = service_client.list_models()
for model in listed_models:
    print(model)
```

### Get model
Use `get_model` with model's unique identifier to get a specific model.

```Python Snippet:dt_models_lifecycle
# Get a model
get_model = service_client.get_model(model_id)
print('Get Model:')
print(get_model)
```

### Decommission model
To decommision a model, pass in a model Id for the model you want to decommision.

```Python Snippet:dt_models_lifecycle
# Decommission a model
service_client.decommission_model(model_id)
```

### Delete model
To delete a model, pass in a model Id for the model you want to delete.

```Python Snippet:dt_models_lifecycle
# Delete a model
service_client.delete_model(model_id)
```

## Create and delete digital twins

### Create digital twins
For Creating Twin you will need to provide Id of a digital Twin such as `my_twin` and the application/json digital twin based on the model created earlier. You can look at sample application/json [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/digitaltwins/azure-digitaltwins-core/samples/dtdl/digital_twins).

```Python Snippet:dt_digitaltwins_lifecycle
digital_twin_id = 'digitalTwin-' + str(uuid.uuid4())
temporary_twin = {
    "$metadata": {
        "$model": model_id
    },
    "$dtId": digital_twin_id,
    "Prop1": 42
}

created_twin = service_client.upsert_digital_twin(digital_twin_id, temporary_twin)
print('Created Digital Twin:')
print(created_twin)
```

### Get a digital twin

Getting a digital twin is extremely easy.
```Python Snippet:dt_digitaltwins_lifecycle
get_twin = service_client.get_digital_twin(digital_twin_id)
print('Get Digital Twin:')
print(get_twin)
```

### Query digital twins

Query the Azure Digital Twins instance for digital twins using the [Azure Digital Twins Query Store lanaguage](https://docs.microsoft.com/azure/digital-twins/concepts-query-language). Query calls support paging. Here's an example of how to query for digital twins and how to iterate over the results.

Note that there may be a delay between before changes in your instance are reflected in queries.
For more details on query limitations, see (https://docs.microsoft.com/azure/digital-twins/how-to-query-graph#query-limitations)

```Python Snippet:dt_digitaltwins_query
query_expression = 'SELECT * FROM digitaltwins'
query_result = service_client.query_twins(query_expression)
print('DigitalTwins:')
for twin in query_result:
    print(twin)
```

### Delete digital twins

Delete a digital twin simply by providing Id of a digital twin as below.

```Python Snippet:dt_digitaltwins_lifecycle
service_client.delete_digital_twin(digital_twin_id)
```

## Get and update digital twin components

### Update digital twin components

To update a component or in other words to replace, remove and/or add a component property or subproperty within Digital Twin, you would need Id of a digital twin, component name and application/json-patch+json operations to be performed on the specified digital twin's component. Here is the sample code on how to do it.

```Python Snippet:dt_component_lifecycle
component_name = "Component1"
patch = [
    {
        "op": "replace",
        "path": "/ComponentProp1",
        "value": "value2"
    }
]
service_client.update_component(digital_twin_id, component_name, patch)
```

### Get digital twin components

Get a component by providing name of a component and Id of digital twin to which it belongs.

```Python Snippet:dt_component_lifecycle
get_component = service_client.get_component(digital_twin_id, component_name)
print('Get Component:')
print(get_component)
```

## Create and list digital twin relationships

### Create digital twin relationships

`upsert_relationship` creates a relationship on a digital twin provided with Id of a digital twin, name of relationship such as "contains", Id of an relationship such as "FloorContainsRoom" and an application/json relationship to be created. Must contain property with key "\$targetId" to specify the target of the relationship. Sample payloads for relationships can be found [here](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/digitaltwins/azure-digitaltwins-core/samples/dtdl/relationships/hospitalRelationships.json).

```Python Snippet:dt_scenario
hospital_relationships = [
    {
        "$relationshipId": "BuildingHasFloor",
        "$sourceId": building_twin_id,
        "$relationshipName": "has",
        "$targetId": floor_twin_id,
        "isAccessRestricted": False
    },
    {
        "$relationshipId": "BuildingIsEquippedWithHVAC",
        "$sourceId": building_twin_id,
        "$relationshipName": "isEquippedWith",
        "$targetId": hvac_twin_id
    },
    {
        "$relationshipId": "HVACCoolsFloor",
        "$sourceId": hvac_twin_id,
        "$relationshipName": "controlsTemperature",
        "$targetId": floor_twin_id
    },
    {
        "$relationshipId": "FloorContainsRoom",
        "$sourceId": floor_twin_id,
        "$relationshipName": "contains",
        "$targetId": room_twin_id
    }
]

for relationship in hospital_relationships:
    service_client.upsert_relationship(
        relationship["$sourceId"],
        relationship["$relationshipId"],
        relationship
    )
```

### List digital twin relationships

`list_relationships` and `list_incoming_relationships` lists all the relationships and all incoming relationships respectively of a digital twin.

```Python Snippet:dt_relationships_list
relationships = service_client.list_relationships(digital_twint_id)
for relationship in relationships:
    print(relationship)
```

```Python Snippet:dt_incoming_relationships_list
incoming_relationships = service_client.list_incoming_relationships(digital_twin_id)
for incoming_relationship in incoming_relationships:
    print(incoming_relationship)
```

## Create, list, and delete event routes of digital twins

### Create event routes

To create an event route, provide an Id of an event route such as "myEventRouteId" and event route data containing the endpoint and optional filter like the example shown below.

```Python Snippet:dt_scenario
event_route_id = 'eventRoute-' + str(uuid.uuid4())
event_filter = "$eventType = 'DigitalTwinTelemetryMessages' or $eventType = 'DigitalTwinLifecycleNotification'"
route = DigitalTwinsEventRoute(
    endpoint_name=event_hub_endpoint_name,
    filter=event_filter
)    
service_client.upsert_event_route(event_route_id, route)
```

For more information on the event route filter language, see the "how to manage routes" [filter events documentation](https://github.com/Azure/azure-digital-twins/blob/private-preview/Documentation/how-to-manage-routes.md#filter-events).

### List event routes

List a specific event route given event route Id or all event routes setting options with `list_event_routes`.

```Python Snippet:dt_event_routes_list
event_routes = service_client.list_event_routes()
for event_route in event_routes:
    print(event_route)
```

### Delete event routes

Delete an event route given event route Id.

```Python Snippet:dt_scenario
service_client.delete_event_route(event_route_id)
```

### Publish telemetry messages for a digital twin

To publish a telemetry message for a digital twin, you need to provide the digital twin Id, along with the payload on which telemetry that needs the update.

```Python Snippet:dt_publish_telemetry
digita_twin_id = "<DIGITAL TWIN ID>"
telemetry_payload = '{"Telemetry1": 5}'
service_client.publish_telemetry(
    digita_twin_id,
    telemetry_payload
)
```

You can also publish a telemetry message for a specific component in a digital twin. In addition to the digital twin Id and payload, you need to specify the target component Id.

```Python Snippet:dt_publish_component_telemetry
digita_twin_id = "<DIGITAL TWIN ID>"
component_name = "<COMPONENT_NAME>"
telemetry_payload = '{"Telemetry1": 5}'
service_client.publish_component_telemetry(
    digita_twin_id,
    component_name,
    telemetry_payload
)
```

## Troubleshooting

## Logging
This library uses the standard logging library for logging. Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO level.

Detailed DEBUG level logging, including request/response bodies and unredacted headers, can be enabled on a client with the logging_enable keyword argument:

### Client level logging
```python Snippet:dt_digitaltwins_get.py
import sys
import logging

# Create logger
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Create service client and enable logging for all operations
service_client = DigitalTwinsClient(url, credential, logging_enable=True)
```

### Per-operation level logging
```python Snippet:dt_models_get.py
import sys
import logging

# Create logger
logger = logging.getLogger('azure')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

# Get model with logging enabled
model = service_client.get_model(model_id, logging_enable=True)
```

### Optional Configuration
Optional keyword arguments can be passed in at the client and per-operation level. The azure-core [reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-core/latest/azure.core.html) describes available configurations for retries, logging, transport protocols, and more.

[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
[azure_identity_pypi]: https://pypi.org/project/azure-identity/
[default_cred_ref]: https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
[pip]: https://pypi.org/project/pip/


## Next steps

### Provide Feedback

If you encounter bugs or have suggestions, please
[open an issue](https://github.com/Azure/azure-sdk-for-python/issues).

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.