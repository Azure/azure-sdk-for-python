# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.administration import ApiVersion
from azure.keyvault.administration.aio import KeyVaultSettingsClient
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultSettingsClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

only_7_4 = get_decorator(api_versions=[ApiVersion.V7_4_PREVIEW_1])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_list_settings(self, client: KeyVaultSettingsClient, **kwargs):
        default_settings = [setting async for setting in await client.list_settings()]
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.type and setting.value is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_update_settings(self, client: KeyVaultSettingsClient, **kwargs):
        setting = await client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.type and setting.value is not None

        # Set value by using a bool
        opposite_value = not setting.value
        updated = await client.update_setting("AllowKeyManagementOperationsThroughARM", opposite_value)
        assert updated.name == setting.name
        assert updated.value != setting.value

        # Set value by using a string (providing in uppercase to make sure it's lowercased before being sent)
        new_opposite = "FALSE" if updated.value else "TRUE"
        new_updated = await client.update_setting("AllowKeyManagementOperationsThroughARM", new_opposite)
        assert new_updated.name == updated.name
        assert new_updated.value != updated.value
