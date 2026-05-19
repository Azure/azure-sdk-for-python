# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

"""Async twin of ``hedging_detection.py``. See that file for the narrative."""

import asyncio
import os

from azure.cosmos import RequestedRegion, RequestedRegionReason
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError


async def inspect_response_hedging(client: CosmosClient) -> None:
    container = (
        client.get_database_client("my-db").get_container_client("my-container")
    )

    try:
        response = await container.read_item(item="abc", partition_key="pk1")
    except CosmosHttpResponseError as exc:
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

    for entry in response.get_requested_regions():
        assert isinstance(entry, RequestedRegion)
        if entry.reason is RequestedRegionReason.UNKNOWN:
            print(f"  - {entry.region_name}  (unrecognized reason)")
        else:
            print(f"  - {entry.region_name}  ({entry.reason.value})")

    print("Responded regions:", list(response.get_responded_regions()))


async def main() -> None:
    endpoint = os.environ["COSMOS_ENDPOINT"]
    key = os.environ["COSMOS_KEY"]
    async with CosmosClient(endpoint, credential=key) as client:
        await inspect_response_hedging(client)


if __name__ == "__main__":
    asyncio.run(main())
