import "@typespec/http";
import "@typespec/rest";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Azure.AI.MachineLearning.RegistryDiscovery;

/** Operations for checking async operation status. */
interface AsyncOperations {
  /** Get the status of an async operation. */
  #suppress "@azure-tools/typespec-azure-core/operation-missing-api-version" "This API does not use api-version parameter"
  #suppress "@azure-tools/typespec-azure-core/use-standard-operations" "This is a non-standard custom operation"
  #suppress "@azure-tools/typespec-azure-core/no-response-body" "Original swagger returns 200 with no body"
  @route("operations/{operationId}")
  @get
  getAsyncOperation(
    /** The operation ID. */
    @path operationId: string,
  ): OkResponse;
}

/** Operations for registry discovery. */
interface RegistryManagementNonWorkspace {
  /** Discover registry information by registry name. */
  #suppress "@azure-tools/typespec-azure-core/operation-missing-api-version" "This API does not use api-version parameter"
  #suppress "@azure-tools/typespec-azure-core/use-standard-operations" "This is a non-standard custom operation"
  @route("registries/{registryName}/discovery")
  @get
  getRegistryDiscovery(
    /** The registry name. */
    @path registryName: string,
  ): OkResponse & Body<RegistryDiscoveryDto>;
}
