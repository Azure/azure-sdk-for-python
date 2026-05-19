# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

"""Sample: use the hedging-detection API to inspect cross-region hedging behavior.

This sample shows how, AFTER an operation completes, you can ask the response
wrapper or exception whether the SDK dispatched the operation to a hedge region,
which regions it was dispatched to (with reasons), and which regions responded.

The accessors are available on:
    * azure.cosmos.CosmosDict             (point reads / writes / patch)
    * azure.cosmos.CosmosList             (batch / read_all_items pages)
    * azure.cosmos.CosmosItemPaged        (query / change feed)
    * azure.cosmos.exceptions.CosmosHttpResponseError
    * azure.cosmos.exceptions.CosmosBatchOperationError
    * azure.cosmos.exceptions.CosmosClientTimeoutError

For paged operations the accessors reflect the most recently fetched page.

``RequestedRegionReason`` is non-exhaustive — handle ``UNKNOWN`` defensively:
calling ``RequestedRegionReason("future_value_42")`` returns
``RequestedRegionReason.UNKNOWN`` rather than raising ``ValueError``.
"""

from azure.cosmos import CosmosClient, RequestedRegion, RequestedRegionReason
from azure.cosmos.exceptions import CosmosHttpResponseError


def inspect_response_hedging(client: CosmosClient) -> None:
    container = (
        client.get_database_client("my-db").get_container_client("my-container")
    )

    try:
        response = container.read_item(item="abc", partition_key="pk1")
    except CosmosHttpResponseError as exc:
        # Error-path consumers also see the per-operation timeline.
        if exc.is_hedging_started():
            print(
                "Operation was hedged before failing across:",
                [r.region_name for r in exc.get_requested_regions()],
            )
        raise

    if response.is_hedging_started():
        print("Operation was hedged.")
    else:
        print("Operation was NOT hedged (primary returned under the threshold).")

    print("Dispatched regions (in observed dispatch order):")
    for entry in response.get_requested_regions():
        assert isinstance(entry, RequestedRegion)
        # Handle UNKNOWN / unknown reasons defensively.
        if entry.reason is RequestedRegionReason.UNKNOWN:
            print(f"  - {entry.region_name}  (unrecognized reason)")
        else:
            print(f"  - {entry.region_name}  ({entry.reason.value})")

    print("Responded regions (duplicates allowed — see docstring):")
    print("  raw:", list(response.get_responded_regions()))
    print("  unique-by-first-appearance:",
          list(dict.fromkeys(response.get_responded_regions())))


if __name__ == "__main__":
    import os

    endpoint = os.environ["COSMOS_ENDPOINT"]
    key = os.environ["COSMOS_KEY"]
    with CosmosClient(endpoint, credential=key) as client:
        inspect_response_hedging(client)
