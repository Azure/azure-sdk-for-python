# # Copyright (c) Microsoft. All rights reserved.
# # Licensed under the MIT license. See LICENSE file in the project root for full license information.

# { DefaultAzureCredential } = require("@azure/identity")
# { DigitalTwinsClient } = require("@azure/digitaltwins")
# { inspect } = require("util")

# # Simple example of how to:
# # - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# # - list all models using the paginated API
# #
# # Preconditions:
# # - Environment variables have to be set
# # - DigitalTwins enabled device must exist on the ADT hub
# async function main() {
#   # - AZURE_URL: The tenant ID in Azure Active Directory
#   url = os.getenv.AZURE_URL

#   # DefaultAzureCredential expects the following three environment variables:
#   # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
#   # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
#   # - AZURE_CLIENT_SECRET: The client secret for the registered application
#   credential = DefaultAzureCredential()
#   serviceClient = DigitalTwinsClient(url, credential)

#   # List models
#   models = serviceClient.listModels()
#   for await (model of models) {
#     print(`Model:`)
#     print(inspect(model))
#   }
# }

# main().catch((err) => {
#   print("error code: ", err.code)
#   print("error message: ", err.message)
#   print("error stack: ", err.stack)
# })
