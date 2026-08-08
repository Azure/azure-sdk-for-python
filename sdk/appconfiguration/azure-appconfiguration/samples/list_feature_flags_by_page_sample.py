# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_feature_flags_by_page_sample.py

DESCRIPTION:
    This sample demos how to detect feature flag changes using etag-based change detection.
    By collecting page ETags from list_feature_flags and passing them to by_page via the
    match_conditions parameter, unchanged pages are skipped (HTTP 304), making it efficient
    to detect whether feature flags have changed.

USAGE: python list_feature_flags_by_page_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""

import os
from azure.appconfiguration import FeatureFlagClient, FeatureFlag
from azure.identity import DefaultAzureCredential


def main():
    ENDPOINT = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    credential = DefaultAzureCredential()

    # Create a feature flag client
    client = FeatureFlagClient(base_url=ENDPOINT, credential=credential)

    # Set up sample feature flags
    client.set_feature_flag(FeatureFlag(name="ListFeature1", enabled=True, tags={"env": "dev"}))
    client.set_feature_flag(FeatureFlag(name="ListFeature2", enabled=False, tags={"env": "dev"}))

    # [START list_feature_flags]
    # Use list_feature_flags to get page ETags.
    # These ETags identify the current state of each page of feature flags.
    print("Collecting feature flag page ETags...")
    items = client.list_feature_flags(name_filter="ListFeature*")
    iterator = items.by_page()
    etags = []
    for _ in iterator:
        print(f"  Page ETag: {iterator.etag}")
        etags.append(iterator.etag)

    # Later, use the collected ETags to check if any pages have changed.
    # Pages that haven't changed will be skipped (HTTP 304), so only changed pages are returned.
    print("\nChecking for changes using ETags...")
    items = client.list_feature_flags(name_filter="ListFeature*")
    has_changes = False
    iterator = items.by_page(match_conditions=etags)
    for _ in iterator:
        has_changes = True
        print(f"  Page changed! New ETag: {iterator.etag}")

    if not has_changes:
        print("  No changes detected.")

    # Now modify a feature flag and check again
    print("\nModifying a feature flag...")
    client.set_feature_flag(FeatureFlag(name="ListFeature1", enabled=False, tags={"env": "dev"}))

    print("Checking for changes after modification...")
    items = client.list_feature_flags(name_filter="ListFeature*")
    has_changes = False
    iterator = items.by_page(match_conditions=etags)
    for _ in iterator:
        has_changes = True
        print(f"  Page changed! New ETag: {iterator.etag}")

    if not has_changes:
        print("  No changes detected.")
    # [END list_feature_flags]

    # Clean up
    client.delete_feature_flag("ListFeature1")
    client.delete_feature_flag("ListFeature2")


if __name__ == "__main__":
    main()
