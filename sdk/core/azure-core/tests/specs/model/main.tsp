import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

namespace Test;

@usage(Usage.input)
/** A scratch model for testing purposes */
model Scratch {
    /** A string property */
    prop: string;
}
