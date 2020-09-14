# # Copyright (c) Microsoft. All rights reserved.
# # Licensed under the MIT license. See LICENSE file in the project root for full license information.

# { DefaultAzureCredential } = require("@azure/identity")
# { DigitalTwinsClient } = require("@azure/digitaltwins")
# { v4 } = require("uuid")
# { buildingTwin } = require("../dtdl/digitalTwins/buildingTwin.ts")
# { building } = require("../dtdl/models/building.ts")
# { inspect } = require("util")

# # Scenario example of how to:
# # - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# # - create digital twin based on a model
# # - get digital twin
# # - update digital twin using JSON patch
# # - delete digital twin
# #
# # Preconditions:
# # - Environment variables have to be set
# # - DigitalTwins enabled device must exist on the ADT hub
# #
# # For the purpose of this example we will create temporary digital twin using random Ids.
# # We have to make sure these Ids are unique within the DT instance so we use generated UUIDs.
# async function main() {
#   # - AZURE_URL: The tenant ID in Azure Active Directory
#   url = os.getenv.AZURE_URL

#   # DefaultAzureCredential expects the following three environment variables:
#   # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
#   # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
#   # - AZURE_CLIENT_SECRET: The client secret for the registered application
#   credential = DefaultAzureCredential()
#   serviceClient = DigitalTwinsClient(url, credential)

#   # Create model first
#   newModels = [building]
#   model = await serviceClient.createModels(newModels)
#   print(`Created Model:`)
#   print(inspect(model))

#   # Create digital twin based on the created model
#   digitalTwinId = `digitalTwin-${v4()}`
#   newTwin = buildingTwin
#   createdTwin = await serviceClient.upsertDigitalTwin(digitalTwinId, newTwin, {
#     enableUpdate: true
#   })
#   print(`Created Digital Twin:`)
#   print(inspect(createdTwin))

#   # Get digital twin
#   getTwin = await serviceClient.getDigitalTwin(digitalTwinId)
#   print(`Get Digital Twin:`)
#   print(inspect(getTwin))

#   # Update digital twin
#   twinPatch = {
#     AverageTemperature: 42
#   }
#   updatedTwin = await serviceClient.updateDigitalTwin(digitalTwinId, twinPatch)
#   print(`Updated Digital Twin:`)
#   print(inspect(updatedTwin))

#   # Delete digital twin
#   response = await serviceClient.deleteDigitalTwin(digitalTwinId)
#   print(`Delete response:`)
#   print(inspect(response))
# }

# main().catch((err) => {
#   print("error code: ", err.code)
#   print("error message: ", err.message)
#   print("error stack: ", err.stack)
# })
