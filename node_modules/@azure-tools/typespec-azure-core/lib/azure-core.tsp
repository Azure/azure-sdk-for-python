import "@typespec/http";
import "@typespec/rest";
import "@typespec/versioning";

import "./auth.tsp";
import "./traits.tsp";
import "./foundations.tsp";
import "./models.tsp";
import "./operations.tsp";
import "./decorators.tsp";
import "../dist/src/index.js";

using TypeSpec.Versioning;

@versioned(Versions)
namespace Azure.Core;

/**
 * Supported versions of Azure.Core TypeSpec building blocks.
 */
enum Versions {
  @doc("Version 1.0-preview.1")
  v1_0_Preview_1: "1.0-preview.1",

  @doc("Version 1.0-preview.2")
  v1_0_Preview_2: "1.0-preview.2",
}
