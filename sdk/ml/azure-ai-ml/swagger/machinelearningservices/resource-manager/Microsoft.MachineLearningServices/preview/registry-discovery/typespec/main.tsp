import "@typespec/http";
import "@typespec/rest";
import "@typespec/versioning";
import "@azure-tools/typespec-azure-core";

import "./models.tsp";
import "./routes.tsp";
import "./client.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;
using TypeSpec.Versioning;
using Azure.Core;

/** Feed Management Service APIs for registry discovery. */
@useAuth(OAuth2Auth<[{
  type: OAuth2FlowType.implicit,
  authorizationUrl: "https://login.microsoftonline.com/common/oauth2/authorize",
  scopes: ["https://management.azure.com/.default"],
}]>)
@service(#{
  title: "Feed Management Service APIs",
})
@server(
  "{endpoint}/registrymanagement/v1.0",
  "Feed Management Service",
  {
    /** The endpoint of the Feed Management Service. */
    endpoint: url,
  }
)
@versioned(Versions)
namespace Azure.AI.MachineLearning.RegistryDiscovery;

/** Service API versions. */
enum Versions {
  /** The v1.0 API version. */
  v1_0: "v1.0",
}
