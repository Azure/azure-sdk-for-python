import "@typespec/http";

using TypeSpec.Http;

namespace Azure.AI.MachineLearning.RegistryDiscovery;

/** Debug information for error responses. */
model DebugInfoResponse {
  /** The exception type. */
  type?: string;

  /** The exception message. */
  message?: string;

  /** The stack trace. */
  stackTrace?: string;

  /** The inner exception. */
  innerException?: DebugInfoResponse;

  /** Additional untyped data about the exception. */
  data?: Record<string>;

  /** The error response. */
  errorResponse?: ErrorResponse;
}

/** The resource management error additional info. */
model ErrorAdditionalInfo {
  /** The additional info type. */
  type?: string;

  /** The additional info. */
  info?: Record<string>;
}

/** The error response. */
model ErrorResponse {
  /** The root error. */
  error?: RootError;

  /** Correlation information for the error. */
  correlation?: Record<string>;

  /** The hosting environment. */
  environment?: string;

  /** The error location. */
  location?: string;

  /** The error timestamp. */
  time?: utcDateTime;

  /** The component name. */
  componentName?: string;
}

/** A nested structure of errors. */
model InnerErrorResponse {
  /** The error code. */
  code?: string;

  /** The inner error. */
  innerError?: InnerErrorResponse;
}

/** Registry discovery information. */
model RegistryDiscoveryDto {
  /** The registry name. */
  registryName?: string;

  /** The tenant ID. */
  tenantId?: string;

  /** The primary region. */
  primaryRegion?: string;

  /** The list of regions. */
  regions?: string[];

  /** The subscription ID. */
  subscriptionId?: string;

  /** The resource group name. */
  resourceGroup?: string;

  /** The workspace name. */
  workspaceName?: string;

  /** The primary region resource provider URI. */
  primaryRegionResourceProviderUri?: url;
}

/** The root error. */
model RootError {
  /** The error code. */
  code?: string;

  /** The error severity. */
  severity?: int32;

  /** The error message. */
  message?: string;

  /** The error message format. */
  messageFormat?: string;

  /** The error message parameters. */
  messageParameters?: Record<string>;

  /** The error reference code. */
  referenceCode?: string;

  /** The URI for error details. */
  detailsUri?: url;

  /** The error target. */
  target?: string;

  /** The error details. */
  details?: RootError[];

  /** The inner error. */
  innerError?: InnerErrorResponse;

  /** Debug information for the error. */
  debugInfo?: DebugInfoResponse;

  /** The error additional info. */
  additionalInfo?: ErrorAdditionalInfo[];
}
