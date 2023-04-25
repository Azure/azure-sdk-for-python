# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.keyvault.administration import ApiVersion, KeyVaultSetting, KeyVaultSettingsClient, KeyVaultSettingType

from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultSettingsClientPreparer, get_decorator

only_7_4 = get_decorator(api_versions=[ApiVersion.V7_4])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_list_settings(self, client: KeyVaultSettingsClient, **kwargs):
        default_settings = [setting for setting in client.list_settings()]
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.setting_type and setting.value is not None

    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_update_settings(self, client: KeyVaultSettingsClient, **kwargs):
        setting = client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.setting_type and setting.value

        # Set value by using a bool
        opposite_value = KeyVaultSetting(
            name=setting.name, value=not setting.getboolean(), setting_type=KeyVaultSettingType.BOOLEAN
        )
        updated = client.update_setting(opposite_value)
        assert updated.name == setting.name
        if setting.getboolean():
            assert not updated.getboolean()
        else:
            assert updated.getboolean()

        # Set value by using a string
        new_opposite = KeyVaultSetting(name=updated.name, value="false" if updated.getboolean() else "true")
        new_updated = client.update_setting(new_opposite)
        assert new_updated.name == updated.name
        assert new_updated.value != updated.value
