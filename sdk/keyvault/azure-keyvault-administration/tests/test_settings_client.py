# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.keyvault.administration import ApiVersion
from devtools_testutils import recorded_by_proxy

from _shared.test_case import KeyVaultTestCase
from _test_case import KeyVaultSettingsClientPreparer, get_decorator

only_7_4 = get_decorator(api_versions=[ApiVersion.V7_4_PREVIEW_1])


class TestSettings(KeyVaultTestCase):
    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_list_settings(self, client, **kwargs):
        default_settings = [setting for setting in client.list_settings()]
        assert len(default_settings)
        for setting in default_settings:
            assert setting.name and setting.type and setting.value

    @pytest.mark.parametrize("api_version", only_7_4)
    @KeyVaultSettingsClientPreparer()
    @recorded_by_proxy
    def test_update_settings(self, client, **kwargs):
        setting = client.get_setting("AllowKeyManagementOperationsThroughARM")
        assert setting.name and setting.type and setting.value

        # Note: the value provided to `update_setting` *is* case-sensitive, so passing str(True) fails
        opposite_value = "false" if setting.value.lower() == "true" else "true"
        updated = client.update_setting("AllowKeyManagementOperationsThroughARM", opposite_value)
        assert updated.name == setting.name
        assert updated.value != setting.value
