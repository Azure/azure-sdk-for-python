# # Copyright (c) Microsoft. All rights reserved.
# # Licensed under the MIT license. See LICENSE file in the project root for full license information.

# { DefaultAzureCredential } = require("@azure/identity")
# { DigitalTwinsClient } = require("@azure/digitaltwins")
# { v4 } = require("uuid")
# { inspect } = require("util")

# # Scenario example of how to:
# # - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# # - create model, component and twin
# # - create digital twin based on the model
# # - update component
# # - get component
# # - delete twin
# # - decomission and delete model, component
# #
# # Preconditions:
# # - Environment variables have to be set
# # - DigitalTwins enabled device must exist on the ADT hub
# #
# # For the purpose of this example we will create temporary digital twin using random Ids.
# # We have to make sure these model Ids are unique within the DT instance so we use generated UUIDs.
# async function main() {
#   modelId = `model-${v4()}`
#   componentId = `component-${v4()}`
#   digitalTwinId = `digitalTwin-${v4()}`

#   temporaryComponent = {
#     "@id": componentId,
#     "@type": "Interface",
#     "@context": "dtmi:dtdl:context2",
#     displayName: "Component1",
#     contents: [
#       {
#         "@type": "Property",
#         name: "ComponentProp1",
#         schema: "string"
#       }
#     ]
#   }

#   temporaryModel = {
#     "@id": modelId,
#     "@type": "Interface",
#     "@context": "dtmi:dtdl:context2",
#     displayName: "TempModel",
#     contents: [
#       {
#         "@type": "Property",
#         name: "Prop1",
#         schema: "double"
#       },
#       {
#         "@type": "Component",
#         name: "Component1",
#         schema: componentId
#       }
#     ]
#   }

#   temporaryTwin = {
#     "@id": digitalTwinId,
#     $metadata: {
#       "@model": modelId
#     },
#     Prop1: 42,
#     Component1: {
#       $metadata: {},
#       ComponentProp1: "value1"
#     }
#   }

#   # - AZURE_URL: The tenant ID in Azure Active Directory
#   url = os.getenv.AZURE_URL

#   # DefaultAzureCredential expects the following three environment variables:
#   # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
#   # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
#   # - AZURE_CLIENT_SECRET: The client secret for the registered application
#   credential = DefaultAzureCredential()
#   serviceClient = DigitalTwinsClient(url, credential)

#   # Create models
#   newModels = [temporaryComponent, temporaryModel]
#   models = await serviceClient.createModels(newModels)
#   print(`Created Models:`)
#   print(inspect(models))

#   # Create digital twin
#   createdTwin = await serviceClient.upsertDigitalTwin(digitalTwinId, temporaryTwin, {
#     enableUpdate: true
#   })
#   print(`Created Digital Twin:`)
#   print(inspect(createdTwin))

#   # Update component
#   componentPath = "Component1"
#   options = {
#     patchDocument: {
#       ComponentProp1: "value2"
#     }
#   }
#   response = await serviceClient.updateComponent(digitalTwinId, componentPath, options)
#   print(`Update Component response:`)
#   print(inspect(response))

#   # Get component
#   getComponent = await serviceClient.getComponent(digitalTwinId, componentPath)
#   print(`Get Component:`)
#   print(inspect(getComponent))

#   # Delete digital twin
#   response = await serviceClient.deleteDigitalTwin(digitalTwinId)
#   print(`Delete response:`)
#   print(inspect(response))

#   # Decomission models
#   response = await serviceClient.decomissionModel(modelId)
#   print(`Decomission Model response:`)
#   print(inspect(response))
#   response = await serviceClient.decomissionModel(componentId)
#   print(`Decomission Component Model response:`)
#   print(inspect(response))

#   # Delete models
#   response = await serviceClient.deleteModel(modelId)
#   print(`Delete Model response:`)
#   print(inspect(response))

#   response = await serviceClient.deleteModel(componentId)
#   print(`Delete Component Model response:`)
#   print(inspect(response))
# }

# main().catch((err) => {
#   print("error code: ", err.code)
#   print("error message: ", err.message)
#   print("error stack: ", err.stack)
# })
