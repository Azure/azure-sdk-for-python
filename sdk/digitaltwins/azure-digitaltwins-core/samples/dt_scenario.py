# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient, DigitalTwinsEventRoute

# <summary>
# This sample creates all the models in \DTDL\Models folder in the ADT service instance
# and creates the corresponding twins in \DTDL\DigitalTwins folder
# The Diagram for the Hospital model looks like this:
#
#     +------------+
#     |  Building  +-----isEquippedWith-----+
#     +------------+                        |
#           |                               v
#          has                           +-----+
#           |                            | HVAC|
#           v                            +-----+
#     +------------+                        |
#     |   Floor    +<--controlsTemperature--+
#     +------------+
#           |
#        contains
#           |
#           v
#     +------------+                 +-----------------+
#     |   Room     |-with component->| WifiAccessPoint |
#     +------------+                 +-----------------+
# </summary>

# Scenario example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - create models from file
# - get created models by modelIds one by one
# - get all models by listing them using the pagianted API
# - delete the created eventRoutes
# - delete the created relationships
# - delete the created digital twins
# - decomission the created models
# - delete the created models
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
#
# For the purpose of this example we will create temporary model and a temporay component model using random Ids.
# We have to make sure these model Ids are unique within the DT instance so we use generated UUIDs.
try:
    building_model_id = 'dtmi:samples:Building;1'
    building_model = {
        "@id": building_model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "Building",
        "contents": [
            {
                "@type": "Relationship",
                "name": "has",
                "target": "dtmi:samples:Floor;1",
                "properties": [
                    {
                    "@type": "Property",
                    "name": "isAccessRestricted",
                    "schema": "boolean"
                    }
                ]
            },
            {
                "@type": "Relationship",
                "name": "isEquippedWith",
                "target": "dtmi:samples:HVAC;1"
            },
            {
                "@type": "Property",
                "name": "AverageTemperature",
                "schema": "double"
            },
            {
                "@type": "Property",
                "name": "TemperatureUnit",
                "schema": "string"
            }
        ]
    }

    floor_model_id = 'dtmi:samples:Floor;1'
    floor_model = {
        "@id": floor_model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "Floor",
        "contents": [
            {
                "@type": "Relationship",
                "name": "contains",
                "target": "dtmi:samples:Room;1"
            },
            {
                "@type": "Property",
                "name": "AverageTemperature",
                "schema": "double"
            }
        ]
    }

    hvac_model_id = 'dtmi:samples:HVAC;1'
    hvac_model = {
        "@id": hvac_model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "HVAC",
        "contents": [
            {
                "@type": "Property",
                "name": "Efficiency",
                "schema": "double"
            },
            {
                "@type": "Property",
                "name": "TargetTemperature",
                "schema": "double"
            },
            {
                "@type": "Property",
                "name": "TargetHumidity",
                "schema": "double"
            },
            {
                "@type": "Relationship",
                "name": "controlsTemperature",
                "target": "dtmi:samples:Floor;1"
            }
        ]
    }

    room_model_id = 'dtmi:samples:Room;1'
    room_model = {
        "@id": room_model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "Room",
        "contents": [
            {
                "@type": "Property",
                "name": "Temperature",
                "schema": "double"
            },
            {
                "@type": "Property",
                "name": "Humidity",
                "schema": "double"
            },
            {
                "@type": "Property",
                "name": "IsOccupied",
                "schema": "boolean"
            },
            {
                "@type": "Property",
                "name": "EmployeeId",
                "schema": "string"
            },
            {
                "@type": "Component",
                "name": "wifiAccessPoint",
                "schema": "dtmi:samples:Wifi;1"
            }
        ]
    }

    wifi_model_id = 'dtmi:samples:Wifi;1'
    wifi_model = {
        "@id": wifi_model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "Wifi",
        "contents": [
            {
                "@type": "Property",
                "name": "RouterName",
                "schema": "string"
            },
            {
                "@type": "Property",
                "name": "Network",
                "schema": "string"
            }
        ]
    }

    building_twin_id = 'BuildingTwin-' + str(uuid.uuid4())
    building_twin = {
        "$metadata": {
            "$model": 'dtmi:samples:Building;1'
        },
        "$dtId": building_twin_id,
        "AverageTemperature": 68,
        "TemperatureUnit": "Celsius"
    }

    floor_twin_id = 'FloorTwin-' + str(uuid.uuid4())
    floor_twin = {
        "$metadata": {
            "$model": "dtmi:samples:Floor;1"
        },
        "AverageTemperature": 75
    }

    hvac_twin_id = 'HVACTwin-' + str(uuid.uuid4())
    hvac_twin = {
        "$metadata": {
            "$model": "dtmi:samples:HVAC;1"
        },
        "Efficiency": 94,
        "TargetTemperature": 72,
        "TargetHumidity": 30
    }

    room_twin_id = 'RoomTwin-' + str(uuid.uuid4())
    room_twin = {
        "$metadata": {
            "$model": "dtmi:samples:Room;1"
        },
        "Temperature": 80,
        "Humidity": 25,
        "IsOccupied": True,
        "EmployeeId": "Employee1",
        "wifiAccessPoint": {
            "$metadata": {},
            "RouterName": "Cisco1",
            "Network": "Room1"
        }
    }

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

    # DefaultAzureCredential supports different authentication mechanisms and determines
    # the appropriate credential type based of the environment it is executing in.
    # It attempts to use multiple credential types in an order until it finds a working credential.

    event_hub_endpoint_name = os.getenv("AZURE_EVENT_HUB_ENDPOINT_NAME")

    # - AZURE_URL: The tenant ID in Azure Active Directory
    url = os.getenv("AZURE_URL")

    # DefaultAzureCredential expects the following three environment variables:
    # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
    # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
    # - AZURE_CLIENT_SECRET: The client secret for the registered application
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)

    # Create models
    new_model_list = [building_model, floor_model, hvac_model, room_model, wifi_model]
    models = service_client.create_models(new_model_list)
    print('Created Models:')
    print(models)

    # Create digital twins
    created_building_twin = service_client.upsert_digital_twin(building_twin_id, building_twin)
    print('BuildingTwin:')
    print(created_building_twin)

    created_floor_twin = service_client.upsert_digital_twin(floor_twin_id, floor_twin)
    print('FloorTwin:')
    print(created_floor_twin)

    created_hvac_twin = service_client.upsert_digital_twin(hvac_twin_id, hvac_twin)
    print('HVACTwin:')
    print(created_hvac_twin)

    created_room_twin = service_client.upsert_digital_twin(room_twin_id, room_twin)
    print('RoomTwin:')
    print(created_room_twin)

    # Create digital relationships
    for relationship in hospital_relationships:
        service_client.upsert_relationship(
            relationship["$sourceId"],
            relationship["$relationshipId"],
            relationship
        )

    # Create event route
    event_route_id = 'eventRoute-' + str(uuid.uuid4())
    event_filter = "$eventType = 'DigitalTwinTelemetryMessages' or $eventType = 'DigitalTwinLifecycleNotification'"
    route = DigitalTwinsEventRoute(
        endpoint_name=event_hub_endpoint_name,
        filter=event_filter
    )    
    service_client.upsert_event_route(event_route_id, route)

    # Get event route
    created_event_route = service_client.get_event_route(event_route_id)
    print('Created Event Route:')
    print(created_event_route)

    # Clean up
    service_client.delete_event_route(event_route_id)

    for relationship in hospital_relationships:
        service_client.delete_relationship(
        relationship["$sourceId"],
        relationship["$relationshipId"]
    )

    service_client.delete_digital_twin(building_twin_id)
    service_client.delete_digital_twin(floor_twin_id)
    service_client.delete_digital_twin(hvac_twin_id)
    service_client.delete_digital_twin(room_twin_id)

    service_client.decommission_model(building_model_id)
    service_client.decommission_model(floor_model_id)
    service_client.decommission_model(hvac_model_id)
    service_client.decommission_model(room_model_id)
    service_client.decommission_model(wifi_model_id)

    service_client.delete_model(building_model_id)
    service_client.delete_model(floor_model_id)
    service_client.delete_model(hvac_model_id)
    service_client.delete_model(room_model_id)
    service_client.delete_model(wifi_model_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
