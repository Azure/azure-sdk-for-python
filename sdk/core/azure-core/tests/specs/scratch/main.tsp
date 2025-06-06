import "@azure-tools/typespec-client-generator-core";

using Azure.ClientGenerator.Core;

namespace ModelTest;
/** A scratch model for testing purposes */
@usage(Usage.input)
model Scratch {
    /** A string property */
    prop: string;
}

