# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.administration import ApiVersion
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultSettingsClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

only_7_4 = get_decorator(api_versions=[ApiVersion.V7_4_PREVIEW_1])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_list_settings(self, client, **kwargs):
        default_settings = [setting async for setting in await client.list_settings()]
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.type and setting.value

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_update_settings(self, client, **kwargs):
        setting = await client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.type and setting.value

        # Note: the value provided to `update_setting` *is* case-sensitive, so passing str(True) fails
        opposite_value = "false" if setting.value.lower() == "true" else "true"
        updated = await client.update_setting("AllowKeyManagementOperationsThroughARM", opposite_value)
        assert updated.name == setting.name
        assert updated.value != setting.value
