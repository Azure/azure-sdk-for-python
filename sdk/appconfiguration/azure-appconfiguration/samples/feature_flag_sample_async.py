# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: feature_flag_sample_async.py

DESCRIPTION:
    This sample demos how to set, get, list, and delete feature flags using the
    dedicated feature flag endpoint methods asynchronously. It also shows how to build
    a fully populated FeatureFlag with conditions, variants, allocation, and telemetry.

USAGE: python feature_flag_sample_async.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.appconfiguration.aio import FeatureFlagClient
from azure.appconfiguration import (
    FeatureFlag,
    FeatureFlagConditions,
    FeatureFlagFilter,
    FeatureFlagVariantDefinition,
    FeatureFlagAllocation,
    FeatureFlagTelemetryConfiguration,
    PercentileAllocation,
    UserAllocation,
    GroupAllocation,
)


async def main():
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    credential = DefaultAzureCredential()
    client = FeatureFlagClient(base_url=endpoint, credential=credential)

    print("Set a simple feature flag")
    # [START set_feature_flag_async]
    flag = FeatureFlag(name="SampleFeature", enabled=True, description="A simple on/off feature flag")
    created = await client.set_feature_flag(flag)
    # [END set_feature_flag_async]
    print(f"  name={created.name}, enabled={created.enabled}")
    print("")

    print("Get a feature flag")
    # [START get_feature_flag_async]
    retrieved = await client.get_feature_flag("SampleFeature")
    # [END get_feature_flag_async]
    if retrieved is not None:
        print(f"  name={retrieved.name}, enabled={retrieved.enabled}, description={retrieved.description}")
    print("")

    print("Set a fully populated feature flag (conditions, variants, allocation, telemetry, tags)")
    rich_flag = FeatureFlag(
        name="RichFeature",
        enabled=True,
        description="A feature flag using every part of the model",
        # Conditions gate the feature with client filters.
        conditions=FeatureFlagConditions(
            requirement_type="All",
            client_filters=[
                FeatureFlagFilter(name="Microsoft.TimeWindow", parameters={"Start": "Mon, 01 Jan 2024 00:00:00 GMT"}),
                FeatureFlagFilter(name="Microsoft.Percentage", parameters={"Value": "50"}),
            ],
        ),
        # Variants describe the possible values the feature can resolve to.
        variants=[
            FeatureFlagVariantDefinition(name="Large", value="large", status_override="Enabled"),
            FeatureFlagVariantDefinition(name="Small", value="small"),
        ],
        # Allocation controls how users/groups/percentiles map to variants.
        allocation=FeatureFlagAllocation(
            default_when_enabled="Large",
            default_when_disabled="Small",
            seed="sample-seed",
            percentile=[
                PercentileAllocation(variant="Large", percentile_from=0, percentile_to=50),
                PercentileAllocation(variant="Small", percentile_from=50, percentile_to=100),
            ],
            user=[UserAllocation(variant="Large", users=["alice", "bob"])],
            group=[GroupAllocation(variant="Small", groups=["beta-testers"])],
        ),
        # Telemetry configuration and free-form metadata/tags.
        telemetry=FeatureFlagTelemetryConfiguration(enabled=True, metadata={"owner": "team-a"}),
        tags={"env": "prod", "team": "core"},
    )
    await client.set_feature_flag(rich_flag)
    fetched = await client.get_feature_flag("RichFeature")
    if fetched is not None:
        print(f"  name={fetched.name}")
        if fetched.conditions is not None:
            print(f"  requirement_type={fetched.conditions.requirement_type}")
        if fetched.variants is not None:
            print(f"  variants={[v.name for v in fetched.variants]}")
        if fetched.allocation is not None:
            print(f"  default_when_enabled={fetched.allocation.default_when_enabled}")
        if fetched.telemetry is not None:
            print(f"  telemetry_enabled={fetched.telemetry.enabled}")
        print(f"  tags={fetched.tags}")
    print("")

    print("List feature flags")
    # [START list_feature_flags_async]
    async for f in client.list_feature_flags():
        print(f"  {f.name}: enabled={f.enabled}")
    # [END list_feature_flags_async]
    print("")

    print("List revisions of a feature flag")
    # [START list_feature_flag_revisions_async]
    async for revision in client.list_feature_flag_revisions(name_filter="RichFeature"):
        print(f"  {revision.name}: last_modified={revision.last_modified}")
    # [END list_feature_flag_revisions_async]
    print("")

    print("Delete feature flags")
    # [START delete_feature_flag_async]
    await client.delete_feature_flag("SampleFeature")
    await client.delete_feature_flag("RichFeature")
    # [END delete_feature_flag_async]

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
