# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: check_configuration_settings_sample.py

DESCRIPTION:
    This sample demos how to check configuration settings using HEAD requests.
    HEAD requests return only headers (including ETags) without the response body,
    making them useful for efficiently detecting whether settings have changed.

USAGE: python check_configuration_settings_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.identity import DefaultAzureCredential


def main():
    ENDPOINT = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    credential = DefaultAzureCredential()

    # Create an app config client
    client = AzureAppConfigurationClient(base_url=ENDPOINT, credential=credential)

    # Set up sample configuration settings
    config_setting1 = ConfigurationSetting(
        key="CheckKey1", value="value1", content_type="my content type", tags={"env": "dev"}
    )
    config_setting2 = ConfigurationSetting(
        key="CheckKey2", value="value2", content_type="my content type", tags={"env": "dev"}
    )
    client.set_configuration_setting(config_setting1)
    client.set_configuration_setting(config_setting2)

    # [START check_configuration_settings]
    # Use check_configuration_settings to get page ETags via HEAD requests.
    # This returns only headers (no body), which is more efficient than listing all settings.
    print("Checking configuration settings (HEAD request)...")
    items = client.check_configuration_settings(key_filter="CheckKey*")
    iterator = items.by_page()
    etags = []
    for _ in iterator:
        print(f"  Page ETag: {iterator.etag}")
        etags.append(iterator.etag)

    # Later, use the collected ETags to check if any pages have changed.
    # Pages that haven't changed will be skipped (HTTP 304), so only changed pages are returned.
    print("\nChecking for changes using ETags...")
    items = client.check_configuration_settings(key_filter="CheckKey*")
    has_changes = False
    iterator = items.by_page(match_conditions=etags)
    for _ in iterator:
        has_changes = True
        print(f"  Page changed! New ETag: {iterator.etag}")

    if not has_changes:
        print("  No changes detected.")

    # Now modify a setting and check again
    print("\nModifying a setting...")
    client.set_configuration_setting(
        ConfigurationSetting(key="CheckKey1", value="updated value1", content_type="my content type")
    )

    print("Checking for changes after modification...")
    items = client.check_configuration_settings(key_filter="CheckKey*")
    has_changes = False
    iterator = items.by_page(match_conditions=etags)
    for _ in iterator:
        has_changes = True
        print(f"  Page changed! New ETag: {iterator.etag}")

    if not has_changes:
        print("  No changes detected.")
    # [END check_configuration_settings]

    # Clean up
    client.delete_configuration_setting(key="CheckKey1")
    client.delete_configuration_setting(key="CheckKey2")


if __name__ == "__main__":
    main()
