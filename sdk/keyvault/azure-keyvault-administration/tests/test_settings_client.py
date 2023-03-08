# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.keyvault.administration import ApiVersion, KeyVaultSetting, KeyVaultSettingsClient, KeyVaultSettingType

from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultSettingsClientPreparer, get_decorator

only_7_4 = get_decorator(api_versions=[ApiVersion.V7_4_PREVIEW_1])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_list_settings(self, client: KeyVaultSettingsClient, **kwargs):
        default_settings = [setting for setting in client.list_settings()]
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.type and setting.value is not None

    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_update_settings(self, client: KeyVaultSettingsClient, **kwargs):
        setting = client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.type and setting.value is not None

        # Set value by using a bool
        opposite_value = not setting.value
        updated = client.update_setting("AllowKeyManagementOperationsThroughARM", opposite_value)
        assert updated.name == setting.name
        assert updated.value != setting.value

        # Set value by using a string
        new_opposite = "false" if updated.value else "true"
        new_updated = client.update_setting("AllowKeyManagementOperationsThroughARM", new_opposite)
        assert new_updated.name == updated.name
        assert new_updated.value != updated.value

def test_setting_boolean_type_string_value():
    """Convert successfully when a KeyVaultSetting is given a KeyVaultSettingType.BOOLEAN `type` and boolean string `value`"""
    # Mimics what we get from KeyVaultSetting._from_generated when a service setting is True
    true_setting = KeyVaultSetting(name="test", type=KeyVaultSettingType.BOOLEAN, value="true")
    assert isinstance(true_setting.value, bool) and true_setting.value

    # If `value` is anything but "True" (case-insensitive), it should be converted to False
    false_setting = KeyVaultSetting(name="test", type=KeyVaultSettingType.BOOLEAN, value="not true")
    assert isinstance(false_setting.value, bool) and not false_setting.value
