# Quickstart: Azure Cosmos → Fabric Mirror Mapper (Python)

This quickstart shows how the mapper package is intended to be installed and used, and how it integrates with the Cosmos SDK via a minimal hook.

## Install

- Install the mapper (optional dependency):
  - `pip install azure-cosmos-fabric-mapper`

## Configure Mirror Serving

You will need:
- A Fabric Warehouse endpoint that exposes the mirrored Cosmos data via a SQL-driver-compatible interface.
- A credential source suitable for the driver.

## Use With Cosmos SDK (conceptual)

1. Enable mirror serving in your Cosmos client configuration (defaults to OFF).
2. Provide mirror endpoint + credential configuration.
3. Run existing Cosmos queries as normal.

If the mapper is not installed and mirror serving is enabled, you should receive a clear error explaining how to install the mapper.

## Use Mapper Directly (conceptual)

1. Build a CosmosQueryRequest: query text + parameters.
2. Translate to a MirrorQueryRequest.
3. Execute via a driver client.
4. Map results back into Cosmos-like documents.

## Limitations

- Only a defined Cosmos SQL subset is supported initially; unsupported constructs fail fast with targeted errors.
- Continuation token behavior may be best-effort depending on mirror capabilities.
