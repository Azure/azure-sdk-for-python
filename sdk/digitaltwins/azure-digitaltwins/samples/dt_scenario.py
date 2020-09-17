# # Copyright (c) Microsoft. All rights reserved.
# # Licensed under the MIT license. See LICENSE file in the project root for full license information.

# { DefaultAzureCredential } = require("@azure/identity")
# { DigitalTwinsClient } = require("@azure/digitaltwins")
# { v4 } = require("uuid")

# { buildingTwin } = require("../dtdl/digitalTwins/buildingTwin.ts")
# { floorTwin } = require("../dtdl/digitalTwins/floorTwin.ts")
# { hvacTwin } = require("../dtdl/digitalTwins/hvacTwin.ts")
# { roomTwin } = require("../dtdl/digitalTwins/roomTwin.ts")

# { building } = require("../dtdl/models/building.ts")
# { floor } = require("../dtdl/models/floor.ts")
# { room } = require("../dtdl/models/room.ts")
# { wifi } = require("../dtdl/models/wifi.ts")

# { hospitalRelationships } = require("../dtdl/relationships/hospitalRelationships.ts")

# { inspect } = require("util")

# # <summary>
# # This sample creates all the models in \DTDL\Models folder in the ADT service instance
# # and creates the corresponding twins in \DTDL\DigitalTwins folder
# # The Diagram for the Hospital model looks like this:
# #
# #     +------------+
# #     |  Building  +-----isEquippedWith-----+
# #     +------------+                        |
# #           |                               v
# #          has                           +-----+
# #           |                            | HVAC|
# #           v                            +-----+
# #     +------------+                        |
# #     |   Floor    +<--controlsTemperature--+
# #     +------------+
# #           |
# #        contains
# #           |
# #           v
# #     +------------+                 +-----------------+
# #     |   Room     |-with component->| WifiAccessPoint |
# #     +------------+                 +-----------------+
# # </summary>

# # Scenario example of how to:
# # - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# # - create models from file
# # - get created models by modelIds one by one
# # - get all models by listing them using the pagianted API
# # - delete the created eventRoutes
# # - delete the created relationships
# # - delete the created digital twins
# # - decomission the created models
# # - delete the created models
# #
# # Preconditions:
# # - Environment variables have to be set
# # - DigitalTwins enabled device must exist on the ADT hub
# #
# # For the purpose of this example we will create temporary model and a temporay component model using random Ids.
# # We have to make sure these model Ids are unique within the DT instance so we use generated UUIDs.
# async function main() {
#   # - AZURE_URL: The tenant ID in Azure Active Directory
#   url = os.getenv.AZURE_URL

#   # - AZURE_EVENT_HUB_ENDPOINT_NAME
#   eventHubEndpointName = os.getenv.AZURE_EVENT_HUB_ENDPOINT_NAME

#   # DefaultAzureCredential expects the following three environment variables:
#   # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
#   # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
#   # - AZURE_CLIENT_SECRET: The client secret for the registered application
#   credential = DefaultAzureCredential()
#   serviceClient = DigitalTwinsClient(url, credential)

#   # Create models
#   # newModels = [wifi, room, floor, building]
#   # createdModels = await serviceClient.createModels(newModels)
#   # print(createdModels)

#   # # List models
#   # models = serviceClient.listModels()
#   # for await (model of models) {
#   #   print(`Model: ${model}`)
#   # }

#   # Create digital twins
#   buildingTwinId = "BuildingTwin"
#   floorTwinId = "FloorTwin"
#   hvacTwinId = "HVACTwin"
#   roomTwinId = "RoomTwin"

#   createdBuildingTwin = await serviceClient.upsertDigitalTwin(buildingTwinId, buildingTwin)
#   print(`BuildingTwin:`)
#   print(inspect(createdBuildingTwin))

#   createdFloorTwin = await serviceClient.upsertDigitalTwin(floorTwinId, floorTwin)
#   print(`FloorTwin:`)
#   print(inspect(createdFloorTwin))

#   createdHVACTwin = await serviceClient.upsertDigitalTwin(hvacTwinId, hvacTwin)
#   print(`HVACTwin:`)
#   print(inspect(createdHVACTwin))

#   createdRoomTwin = await serviceClient.upsertDigitalTwin(roomTwinId, roomTwin)
#   print(`RoomTwin:`)
#   print(inspect(createdRoomTwin))

#   # Create relationships
#   for (relationship of hospitalRelationships) {
#     await serviceClient.upsertRelationship(
#       relationship["$sourceId"],
#       relationship["$relationshipId"],
#       relationship
#     )
#   }

#   # Create event route
#   eventRouteId = `eventRoute-${v4()}`
#   eventFilter =
#     "$eventType = 'DigitalTwinTelemetryMessages' or $eventType = 'DigitalTwinLifecycleNotification'"
#   response = await serviceClient.upsertEventRoute(
#     eventRouteId,
#     eventHubEndpointName,
#     eventFilter
#   )
#   print(`Upsert Event Route response:`)
#   print(inspect(response))

#   # Get event route
#   createdEventRoute = await serviceClient.getEventRoute(eventRouteId)
#   print(`Created Event Route:`)
#   print(inspect(createdEventRoute))

#   # Clean up
#   await serviceClient.deleteEventRoute(eventRouteId)

#   for (relationship of hospitalRelationships) {
#     await serviceClient.deleteRelationship(
#       relationship["$sourceId"],
#       relationship["$relationshipId"]
#     )
#   }

#   await serviceClient.deleteDigitalTwin(buildingTwinId)
#   await serviceClient.deleteDigitalTwin(floorTwinId)
#   await serviceClient.deleteDigitalTwin(hvacTwinId)
#   await serviceClient.deleteDigitalTwin(roomTwinId)

#   await serviceClient.decomissionModel(building["@id"])
#   await serviceClient.decomissionModel(floor["@id"])
#   await serviceClient.decomissionModel(room["@id"])
#   await serviceClient.decomissionModel(wifi["@id"])

#   await serviceClient.deleteModel(building["@id"])
#   await serviceClient.deleteModel(floor["@id"])
#   await serviceClient.deleteModel(room["@id"])
#   await serviceClient.deleteModel(wifi["@id"])
# }

# main().catch((err) => {
#   print("error code: ", err.code)
#   print("error message: ", err.message)
#   print("error stack: ", err.stack)
# })
