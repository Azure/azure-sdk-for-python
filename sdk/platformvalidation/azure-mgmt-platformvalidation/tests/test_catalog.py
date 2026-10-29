# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from functools import partial

from azure.mgmt.platformvalidation import PlatformValidationMgmtClient
from azure.mgmt.platformvalidation.aio import PlatformValidationMgmtClient as AsyncPlatformValidationMgmtClient
from devtools_testutils import (
    EnvironmentVariableLoader,
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    recorded_by_proxy,
)
from devtools_testutils.aio import recorded_by_proxy_async

from _cloud_validation_testcase import CloudValidationTestCase


CatalogPreparer = partial(
    EnvironmentVariableLoader,
    "platformvalidation",
    platformvalidation_catalog_endpoint="https://management.azure.com",
    platformvalidation_catalog_test="compute-vmimagevalidation-vm-boot-test",
)


def sanitize_catalog():
    # Canary uses a regional ARM host; playback uses the public ARM placeholder.
    add_general_regex_sanitizer(
        regex=r"(?i)https://[a-z0-9-]+\.management\.azure\.com",
        value="https://management.azure.com",
        function_scoped=True,
    )
    add_body_key_sanitizer(json_path="$..owners[*]", value="Sanitized", function_scoped=True)


class TestCatalog(CloudValidationTestCase):
    def public_entries(self, entries):
        public = [entry for entry in entries if entry.properties and entry.properties.audience == "Public"]
        assert public, "The approved public catalog must not be empty."
        return public

    def assert_entry(self, entry, resource_id, name):
        assert entry.name == name
        actual_id = entry.id
        assert (
            actual_id and actual_id.lower() == resource_id.lower()
        ), "Catalog ID differs from the canonical subscription-scoped identity."
        is_public = bool(entry.properties and entry.properties.audience == "Public")
        assert is_public, "The selected catalog entry must have Public audience."

    def catalog_id(self, name):
        subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
        return f"/subscriptions/{subscription_id}/providers/Microsoft.PlatformValidation/{name}"

    @CatalogPreparer()
    @recorded_by_proxy
    def test_public_catalog(self, platformvalidation_catalog_endpoint, platformvalidation_catalog_test):
        sanitize_catalog()
        name = platformvalidation_catalog_test
        test_id = self.catalog_id(f"validationTests/{name}")
        with self.create_mgmt_client(
            PlatformValidationMgmtClient, base_url=platformvalidation_catalog_endpoint
        ) as client:
            test = client.validation_tests.get(name)
            tests = self.public_entries(list(client.validation_tests.list_by_subscription()))
            assert sum(test.name == name for test in tests) == 1

            versions = self.public_entries(list(client.validation_test_versions.list(name)))
            version = versions[0].name
            test_version = client.validation_test_versions.get(name, version)

            categories = self.public_entries(list(client.validation_test_categories.list_by_subscription()))
            category = categories[0].name
            test_category = client.validation_test_categories.get(category)
            self.assert_entry(test, test_id, name)
            self.assert_entry(test_version, f"{test_id}/versions/{version}", version)
            self.assert_entry(test_category, self.catalog_id(f"validationTestCategories/{category}"), category)

    @CatalogPreparer()
    @recorded_by_proxy_async
    async def test_public_catalog_async(self, platformvalidation_catalog_endpoint, platformvalidation_catalog_test):
        sanitize_catalog()
        name = platformvalidation_catalog_test
        test_id = self.catalog_id(f"validationTests/{name}")
        credential = self.get_credential(AsyncPlatformValidationMgmtClient, is_async=True)
        try:
            async with self.create_client_from_credential(
                AsyncPlatformValidationMgmtClient,
                credential,
                subscription_id=self.get_settings_value("SUBSCRIPTION_ID"),
                base_url=platformvalidation_catalog_endpoint,
            ) as client:
                test = await client.validation_tests.get(name)
                tests = self.public_entries([test async for test in client.validation_tests.list_by_subscription()])
                assert sum(test.name == name for test in tests) == 1

                versions = self.public_entries(
                    [version async for version in client.validation_test_versions.list(name)]
                )
                version = versions[0].name
                test_version = await client.validation_test_versions.get(name, version)

                categories = self.public_entries(
                    [category async for category in client.validation_test_categories.list_by_subscription()]
                )
                category = categories[0].name
                test_category = await client.validation_test_categories.get(category)
                self.assert_entry(test, test_id, name)
                self.assert_entry(test_version, f"{test_id}/versions/{version}", version)
                self.assert_entry(test_category, self.catalog_id(f"validationTestCategories/{category}"), category)
        finally:
            await credential.close()
