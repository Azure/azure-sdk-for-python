# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import json
import pytest
from testcase import AppConfigTestCase
from consts import APPCONFIGURATION_ENDPOINT_STRING
from devtools_testutils import EnvironmentVariableLoader, recorded_by_proxy, set_custom_default_matcher
from azure.appconfiguration import (
    ConfigurationSetting,
    ConfigurationSettingsFilter,
    ConfigurationSnapshot,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
    FILTER_PERCENTAGE,
)
from azure.appconfiguration._generated.models import (
    KeyValue,
    KeyValueFilter,
    Snapshot as GeneratedSnapshot,
)

AppConfigPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
)


class TestAppConfigurationConsistency(AppConfigTestCase):
    @AppConfigPreparer()
    @recorded_by_proxy
    def test_update_json_by_value(self, appconfiguration_endpoint_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = json.dumps(
            {
                "conditions": {
                    "client_filters": [
                        {
                            "name": "Microsoft.Targeting",
                            "parameters": {
                                "name": "Microsoft.Targeting",
                                "parameters": {"Audience": {"DefaultRolloutPercentage": 50, "Groups": [], "Users": []}},
                            },
                        }
                    ]
                },
                "description": "",
                "enabled": False,
                "id": key,
            }
        )

        set_flag = client.set_configuration_setting(set_flag)
        assert isinstance(set_flag, FeatureFlagConfigurationSetting)
        assert set_flag.enabled == False
        assert set_flag.key.endswith(key)

        client.delete_configuration_setting(set_flag)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_invalid_json(self, appconfiguration_endpoint_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        with pytest.raises(TypeError):
            set_flag.value = []
            client.set_configuration_setting(set_flag)

        client.delete_configuration_setting(feature_flag)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_invalid_json_string(self, appconfiguration_endpoint_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        received = client.set_configuration_setting(set_flag)

        assert isinstance(received, FeatureFlagConfigurationSetting)
        client.delete_configuration_setting(set_flag)

    @AppConfigPreparer()
    @recorded_by_proxy
    def test_feature_flag_invalid_json_access_properties(self, appconfiguration_endpoint_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_endpoint_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        assert set_flag.enabled == False
        assert set_flag.filters == None
        client.delete_configuration_setting(feature_flag)


class TestAppConfigurationConsistencyUnitTest(AppConfigTestCase):
    def test_feature_flag_set_value(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        feature_flag.value = json.dumps({"conditions": {"client_filters": []}, "enabled": False})

        assert feature_flag.enabled == False

    def test_feature_flag_set_enabled(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        feature_flag.enabled = False

        temp = json.loads(feature_flag.value)
        assert temp["enabled"] == False

    def test_feature_flag_prefix(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        assert feature_flag.key.startswith(".appconfig.featureflag/")

    def test_feature_flag_different_key_and_id(self):
        key = f'.appconfig.featureflag/{self.get_resource_name("key")}'
        feature_id = self.get_resource_name("id")
        feature_flag = FeatureFlagConfigurationSetting(feature_id, enabled=True, key=key)

        assert feature_flag.feature_id == feature_id
        assert feature_flag.key == key

    def test_configuration_setting_description_defaults_to_none(self):
        setting = ConfigurationSetting(key="k", label="l", value="v")
        assert setting.description is None

        secret_ref = SecretReferenceConfigurationSetting(key="k", secret_id="https://vault.example/secrets/s")
        assert secret_ref.description is None

        snapshot = ConfigurationSnapshot(filters=[ConfigurationSettingsFilter(key="k")])
        assert snapshot.description is None

    def test_configuration_setting_description_round_trip(self):
        setting = ConfigurationSetting(key="k", label="l", value="v", description="kv-desc")
        assert setting.description == "kv-desc"

        generated = setting._to_generated()
        assert generated.description == "kv-desc"

        round_tripped = ConfigurationSetting._from_generated(generated)
        assert isinstance(round_tripped, ConfigurationSetting)
        assert not isinstance(round_tripped, FeatureFlagConfigurationSetting)
        assert not isinstance(round_tripped, SecretReferenceConfigurationSetting)
        assert round_tripped.description == "kv-desc"

    def test_secret_reference_configuration_setting_description_round_trip(self):
        secret_ref = SecretReferenceConfigurationSetting(
            key="k",
            secret_id="https://vault.example/secrets/s",
            description="sr-desc",
        )
        assert secret_ref.description == "sr-desc"

        generated = secret_ref._to_generated()
        assert generated.description == "sr-desc"

        round_tripped = ConfigurationSetting._from_generated(generated)
        assert isinstance(round_tripped, SecretReferenceConfigurationSetting)
        assert round_tripped.description == "sr-desc"

    def test_feature_flag_description_remains_feature_flag_json_description(self):
        # FeatureFlagConfigurationSetting intentionally keeps `description` as the
        # feature-flag JSON description; the KV-level description is not exposed on FF.
        kv_value = json.dumps({"id": "Beta", "enabled": True, "description": "ff-json-desc"})
        kv = KeyValue(
            key=".appconfig.featureflag/Beta",
            content_type="application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            value=kv_value,
            description="kv-level-desc-should-be-ignored-on-ff",
        )
        ff = ConfigurationSetting._from_generated(kv)
        assert isinstance(ff, FeatureFlagConfigurationSetting)
        assert ff.description == "ff-json-desc"

        ff.description = "updated-ff-json-desc"
        generated = ff._to_generated()
        # The KV-level description is not populated from FF; the FF JSON description
        # is serialized inside `value`.
        assert generated.description is None
        assert json.loads(generated.value)["description"] == "updated-ff-json-desc"

    def test_configuration_snapshot_description_round_trip(self):
        snapshot = ConfigurationSnapshot(
            filters=[ConfigurationSettingsFilter(key="k")],
            description="snap-desc",
        )
        assert snapshot.description == "snap-desc"

        generated = snapshot._to_generated()
        assert generated.description == "snap-desc"

        round_tripped = ConfigurationSnapshot._from_generated(generated)
        assert round_tripped.description == "snap-desc"

    def test_configuration_snapshot_description_from_deserialized(self):
        generated = GeneratedSnapshot(
            filters=[KeyValueFilter(key="k")],
            description="snap-from-deserialized",
        )
        snapshot = ConfigurationSnapshot._from_deserialized(response=None, deserialized=generated, response_headers={})
        assert snapshot.description == "snap-from-deserialized"
