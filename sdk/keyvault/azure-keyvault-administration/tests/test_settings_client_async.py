# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.administration import KeyVaultSetting, KeyVaultSettingType
from azure.keyvault.administration.aio import KeyVaultSettingsClient
from azure.keyvault.administration._internal.client_base import DEFAULT_VERSION
from devtools_testutils.aio import recorded_by_proxy_async

from _async_test_case import KeyVaultSettingsClientPreparer, get_decorator
from _shared.test_case_async import KeyVaultTestCase

only_latest = get_decorator(api_versions=[DEFAULT_VERSION])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_list_settings(self, client: KeyVaultSettingsClient, **kwargs):
        result = client.list_settings()
        default_settings = []
        async for setting in result:
            default_settings.append(setting)
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.setting_type and setting.value is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_version", only_latest)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy_async
    async def test_update_settings(self, client: KeyVaultSettingsClient, **kwargs):
        setting = await client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.setting_type and setting.value

        # Set value by using a bool
        opposite_value = KeyVaultSetting(
            name=setting.name, value=not setting.getboolean(), setting_type=KeyVaultSettingType.BOOLEAN
        )
        updated = await client.update_setting(opposite_value)
        assert updated.name == setting.name
        if setting.getboolean():
            assert not updated.getboolean()
        else:
            assert updated.getboolean()

        # Set value by using a string
        new_opposite = KeyVaultSetting(name=updated.name, value="false" if updated.getboolean() else "true")
        new_updated = await client.update_setting(new_opposite)
        assert new_updated.name == updated.name
        assert new_updated.value != updated.value
