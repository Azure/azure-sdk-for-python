# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import uuid
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

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

    # Create models from the sample dtdls
    with open(r"dtdl\models\building.json") as f:
        dtdl_model_building = json.load(f)

    with open(r"dtdl\models\floor.json") as f:
        dtdl_model_floor = json.load(f)

    with open(r"dtdl\models\hvac.json") as f:
        dtdl_model_hvac = json.load(f)

    with open(r"dtdl\models\room.json") as f:
        dtdl_model_room = json.load(f)

    new_model_list = []
    new_model_list.append(
        dtdl_model_building,
        dtdl_model_floor,
        dtdl_model_hvac,
        dtdl_model_room
    )
    models = service_client.create_models(new_model_list)
    print('Created Models:')
    print(models)

    # Create digital twins from the sample dtdls
    building_twin_id = 'BuildingTwin-' + str(uuid.uuid4())
    with open(r"dtdl\digital_twins\buildingTwin.json") as f:
        dtdl_digital_twins_building = json.load(f)
    created_building_twin = service_client.upsert_digital_twin(building_twin_id, dtdl_digital_twins_building)
    print('BuildingTwin:')
    print(created_building_twin)

    floor_twin_id = 'FloorTwin-' + str(uuid.uuid4())
    with open(r"dtdl\digital_twins\floorTwin.json") as f:
        dtdl_digital_twins_floor = json.load(f)
    created_floor_twin = service_client.upsert_digital_twin(floor_twin_id, dtdl_digital_twins_floor)
    print('FloorTwin:')
    print(created_floor_twin)

    hvac_twin_id = 'HVACTwin-' + str(uuid.uuid4())
    with open(r"dtdl\digital_twins\hvacTwin.json") as f:
        dtdl_digital_twins_hvac = json.load(f)
    created_hvac_twin = service_client.upsert_digital_twin(hvac_twin_id, dtdl_digital_twins_hvac)
    print('HVACTwin:')
    print(created_hvac_twin)

    room_twin_id = 'RoomTwin-' + str(uuid.uuid4())
    with open(r"dtdl\digital_twins\hvacTwin.json") as f:
        dtdl_digital_twins_room = json.load(f)
    created_room_twin = service_client.upsert_digital_twin(room_twin_id, dtdl_digital_twins_room)
    print('RoomTwin:')
    print(created_room_twin)

    # Create digital relationships from the sample dtdls
    with open(r"dtdl\relationships\hospitalRelationships.json") as f:
        dtdl_relationships = json.load(f)
    for relationship in dtdl_relationships:
        service_client.upsert_relationship(
            relationship["$sourceId"],
            relationship["$relationshipId"],
            relationship
        )

    # Create event route
    event_route_id = 'eventRoute-' + str(uuid.uuid4())
    event_filter = "$eventType = 'DigitalTwinTelemetryMessages' or $eventType = 'DigitalTwinLifecycleNotification'"
    service_client.upsert_event_route(
        event_route_id,
        event_hub_endpoint_name,
        **{"filter": event_filter}
    )

    # Get event route
    created_event_route = service_client.get_event_route(event_route_id)
    print('Created Event Route:')
    print(created_event_route)

    # Clean up
    service_client.delete_event_route(event_route_id)

    for relationship in dtdl_relationships:
        service_client.delete_relationship(
        relationship["$sourceId"],
        relationship["$relationshipId"]
    )

    service_client.delete_digital_twin(building_twin_id)
    service_client.delete_digital_twin(floor_twin_id)
    service_client.delete_digital_twin(hvac_twin_id)
    service_client.delete_digital_twin(room_twin_id)

    service_client.decommission_model(building_twin_id)
    service_client.decommission_model(floor_twin_id)
    service_client.decommission_model(hvac_twin_id)
    service_client.decommission_model(room_twin_id)

    service_client.delete_model(building_twin_id)
    service_client.delete_model(floor_twin_id)
    service_client.delete_model(hvac_twin_id)
    service_client.delete_model(room_twin_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
