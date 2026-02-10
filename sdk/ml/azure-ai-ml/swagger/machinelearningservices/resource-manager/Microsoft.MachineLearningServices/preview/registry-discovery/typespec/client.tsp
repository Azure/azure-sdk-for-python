import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

namespace Azure.AI.MachineLearning.RegistryDiscovery;

/** Client customizations for the Registry Discovery service. */
@@clientName(AsyncOperations.getAsyncOperation, "GetAsyncOperation");
@@clientName(RegistryManagementNonWorkspace.getRegistryDiscovery, "GetRegistryDiscovery");
