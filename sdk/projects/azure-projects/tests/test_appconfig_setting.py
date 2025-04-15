from typing import Optional
from uuid import uuid4

import pytest

from azure.projects.resources.storage.blobs import BlobStorage
from azure.projects.resources.appconfig import ConfigStore
from azure.projects.resources.appconfig.setting import ConfigSetting
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, ResourceGroup as DefaultResourceGroup
from azure.projects import Parameter, AzureInfrastructure, export, field, AzureApp

TEST_SUB = "6e441d6a-23ce-4450-a4a6-78f8d4f45ce9"
RG = ResourceSymbol("resourcegroup")
IDENTITY = {"type": "UserAssigned", "userAssignedIdentities": {"identity": {}}}


def test_appconfig_setting_properties():
    r = ConfigSetting(name="foo", value="one")
    assert r.properties == {"name": "foo", "properties": {"value": "one"}}
    assert r.extensions == {}
    assert r.identifier == ResourceIdentifiers.config_setting
    assert r.parent == ConfigStore()
    assert r._existing == False
    assert r.resource == "Microsoft.AppConfiguration/configurationStores/keyValues"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert len(symbols) == 2
    assert list(fields.keys()) == [
        "configurationstore",
        "configurationstore.keyvalue_foo",
    ]
    assert (
        fields["configurationstore.keyvalue_foo"].resource == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore.keyvalue_foo"].properties == {
        "name": "foo",
        "properties": {"value": "one"},
        "parent": ResourceSymbol("configurationstore"),
    }
    assert fields["configurationstore.keyvalue_foo"].outputs == {}
    assert fields["configurationstore.keyvalue_foo"].extensions == {}
    assert fields["configurationstore.keyvalue_foo"].existing == False
    assert fields["configurationstore.keyvalue_foo"].version
    assert fields["configurationstore.keyvalue_foo"].symbol == symbols[0]
    assert fields["configurationstore.keyvalue_foo"].resource_group == None
    assert fields["configurationstore.keyvalue_foo"].name == "foo"
    assert fields["configurationstore.keyvalue_foo"].defaults

    r2 = ConfigSetting(name="foo", value="one", content_type="content-type")
    assert r2.properties == {"name": "foo", "properties": {"value": "one", "contentType": "content-type"}}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "configurationstore",
        "configurationstore.keyvalue_foo",
    ]
    assert (
        fields["configurationstore.keyvalue_foo"].resource == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore.keyvalue_foo"].properties == {
        "name": "foo",
        "properties": {"value": "one", "contentType": "content-type"},
        "parent": ResourceSymbol("configurationstore"),
    }
    assert fields["configurationstore.keyvalue_foo"].outputs == {}
    assert fields["configurationstore.keyvalue_foo"].extensions == {}
    assert fields["configurationstore.keyvalue_foo"].existing == False
    assert fields["configurationstore.keyvalue_foo"].version
    assert fields["configurationstore.keyvalue_foo"].symbol == symbols[0]
    assert fields["configurationstore.keyvalue_foo"].resource_group == None
    assert fields["configurationstore.keyvalue_foo"].name == "foo"
    assert fields["configurationstore.keyvalue_foo"].defaults

    r3 = ConfigSetting(name="foo", value="foo")
    assert r3.properties == {"name": "foo", "properties": {"value": "foo"}}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = ConfigSetting(name="bar", value="two")
    assert r4.properties == {"name": "bar", "properties": {"value": "two"}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "configurationstore",
        "configurationstore.keyvalue_foo",
        "configurationstore.keyvalue_bar",
    ]
    assert (
        fields["configurationstore.keyvalue_bar"].resource == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore.keyvalue_bar"].properties == {
        "parent": ResourceSymbol("configurationstore"),
        "name": "bar",
        "properties": {"value": "two"},
    }
    assert fields["configurationstore.keyvalue_bar"].outputs == {}
    assert fields["configurationstore.keyvalue_bar"].extensions == {}
    assert fields["configurationstore.keyvalue_bar"].existing == False
    assert fields["configurationstore.keyvalue_bar"].version
    assert fields["configurationstore.keyvalue_bar"].symbol == symbols[0]
    assert fields["configurationstore.keyvalue_bar"].resource_group == None
    assert fields["configurationstore.keyvalue_bar"].name == "bar"
    assert fields["configurationstore.keyvalue_bar"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    param3 = Parameter("testC")
    r5 = ConfigSetting(store=param1, name=param2, value=param3)
    assert r5.properties == {"name": param2, "properties": {"value": param3}}
    assert r5.parent == ConfigStore(name=param1)
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == [
        "configurationstore_testa",
        "configurationstore_testa.keyvalue_testa_testb",
    ]
    assert (
        fields["configurationstore_testa.keyvalue_testa_testb"].resource
        == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore_testa.keyvalue_testa_testb"].properties == {
        "parent": ResourceSymbol("configurationstore_testa"),
        "properties": {"value": param3},
        "name": param2,
    }
    assert fields["configurationstore_testa.keyvalue_testa_testb"].outputs == {}
    assert fields["configurationstore_testa.keyvalue_testa_testb"].extensions == {}
    assert fields["configurationstore_testa.keyvalue_testa_testb"].existing == False
    assert fields["configurationstore_testa.keyvalue_testa_testb"].version
    assert fields["configurationstore_testa.keyvalue_testa_testb"].symbol == symbols[0]
    assert fields["configurationstore_testa.keyvalue_testa_testb"].resource_group == None
    assert fields["configurationstore_testa.keyvalue_testa_testb"].name == param2
    assert fields["configurationstore_testa.keyvalue_testa_testb"].defaults
    assert params.get("testA") == param1
    assert params.get("testB") == param2
    assert params.get("testC") == param3


def test_appconfig_setting_reference():
    r = ConfigSetting.reference(name="foo", store="bar")
    assert r.properties == {"name": "foo"}
    assert r._existing == True
    assert r.parent == ConfigStore.reference(name="bar")
    assert r.extensions == {}
    assert r._settings["name"]() == "foo"
    with pytest.raises(RuntimeError):
        r._settings["resource_group"]()
    with pytest.raises(RuntimeError):
        r._settings["subscription"]()
    with pytest.raises(RuntimeError):
        r._settings["resource_id"]()
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "configurationstore_bar",
        "configurationstore_bar.keyvalue_bar_foo",
    ]
    assert (
        fields["configurationstore_bar.keyvalue_bar_foo"].resource
        == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore_bar.keyvalue_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("configurationstore_bar"),
    }
    assert fields["configurationstore_bar.keyvalue_bar_foo"].outputs == {}
    assert fields["configurationstore_bar.keyvalue_bar_foo"].extensions == {}
    assert fields["configurationstore_bar.keyvalue_bar_foo"].existing == True
    assert fields["configurationstore_bar.keyvalue_bar_foo"].version
    assert fields["configurationstore_bar.keyvalue_bar_foo"].symbol == symbols[0]
    assert fields["configurationstore_bar.keyvalue_bar_foo"].resource_group == None
    assert fields["configurationstore_bar.keyvalue_bar_foo"].name == "foo"
    assert not fields["configurationstore_bar.keyvalue_bar_foo"].defaults

    rg = ResourceSymbol("resourcegroup_baz")
    r = ConfigSetting.reference(name="foo", store="bar", resource_group="baz")
    assert r.properties == {"name": "foo"}
    assert r._settings["resource_group"]() == "baz"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == [
        "resourcegroup_baz",
        "configurationstore_bar",
        "configurationstore_bar.keyvalue_bar_foo",
    ]
    assert (
        fields["configurationstore_bar.keyvalue_bar_foo"].resource
        == "Microsoft.AppConfiguration/configurationStores/keyValues"
    )
    assert fields["configurationstore_bar.keyvalue_bar_foo"].properties == {
        "name": "foo",
        "parent": ResourceSymbol("configurationstore_bar"),
    }
    assert fields["configurationstore_bar.keyvalue_bar_foo"].outputs == {}
    assert fields["configurationstore_bar.keyvalue_bar_foo"].extensions == {}
    assert fields["configurationstore_bar.keyvalue_bar_foo"].existing == True
    assert fields["configurationstore_bar.keyvalue_bar_foo"].version
    assert fields["configurationstore_bar.keyvalue_bar_foo"].symbol == symbols[0]
    assert fields["configurationstore_bar.keyvalue_bar_foo"].resource_group == None
    assert fields["configurationstore_bar.keyvalue_bar_foo"].name == "foo"
    assert not fields["configurationstore_bar.keyvalue_bar_foo"].defaults

    account = ConfigStore.reference(
        name="foo", resource_group=ResourceGroup.reference(name="bar", subscription=TEST_SUB)
    )
    assert account._settings["subscription"]() == TEST_SUB
    r = ConfigSetting.reference(name="foo", store=account)
    assert r.properties == {"name": "foo"}
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/bar/providers/Microsoft.AppConfiguration/configurationStores/foo/keyValues/foo"
    )


def test_appconfig_setting_defaults():
    contenttype = Parameter("ContentType", default="foobar")
    r = ConfigSetting(name="setting", value="value", content_type=contenttype)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field = fields.popitem()[1]
    assert field.properties == {
        "name": "setting",
        "parent": ResourceSymbol("configurationstore"),
        "properties": {
            "value": "value",
            "contentType": contenttype,
        },
    }


def test_appconfig_setting_export(export_dir):
    class test(AzureInfrastructure):
        r: ConfigSetting = ConfigSetting(name="setting", value="value")

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_existing(export_dir):
    class test(AzureInfrastructure):
        r: ConfigSetting = field(
            default=ConfigSetting.reference(name="test", store=ConfigStore.reference(name="configtest"))
        )

    infra = test(resource_group=ResourceGroup.reference(name="rgtest"), identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_existing_new_rg(export_dir):
    class test(AzureInfrastructure):
        r: ConfigSetting = field(
            default=ConfigSetting.reference(name="test", store="configtest", resource_group="rgtest")
        )

    infra = test(identity=None)
    export(infra, output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_properties(export_dir):
    with pytest.raises(ValueError):
        ConfigSetting()
    with pytest.raises(ValueError):
        ConfigSetting({"name": "foo"})

    class test(AzureInfrastructure):
        r: ConfigSetting = field(
            default=ConfigSetting(
                {"properties": {"value": "value"}, "name": "foo"},
                content_type="test",
                tags={"foo": "bar"},
            )
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_multiple_settings(export_dir):
    param_a = Parameter("ValueA")
    param_b = Parameter("ValueB")
    param_c = Parameter("ValueC")

    class test(AzureInfrastructure):
        a: ConfigSetting = ConfigSetting(name="setting_A", value=param_a)
        b: ConfigSetting = ConfigSetting(name="setting_B", value=param_b)
        c: ConfigSetting = ConfigSetting(name="setting_C", value=param_c)

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_field_reference_with_default_str(export_dir):
    class test(AzureInfrastructure):
        value: str = field(default="foo")
        r: ConfigSetting = ConfigSetting(name="setting", value=value)

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_field_reference_str_no_default(export_dir):
    class test(AzureInfrastructure):
        value: str = field()
        r: ConfigSetting = ConfigSetting(name="setting", value=value)

    export(test(value="foo"), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_field_reference_resource_no_default(export_dir):
    class test(AzureInfrastructure):
        config_store: ConfigStore = field()
        r: ConfigSetting = ConfigSetting(store=config_store, name="foo", value="bar")

    export(test(config_store=ConfigStore(name="testconfig")), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_export_with_other_resources(export_dir):
    class test(AzureInfrastructure):
        blobs: BlobStorage = BlobStorage()
        config_store: ConfigStore = field()
        r: ConfigSetting = ConfigSetting(store=config_store, name="foo", value="bar")

    export(test(config_store=ConfigStore(name="testconfig")), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_appconfig_setting_client():
    from azure.appconfiguration import AzureAppConfigurationClient

    r = ConfigSetting(name="foo", value="bar")
    with pytest.raises(TypeError):
        r.get_client(AzureAppConfigurationClient)


def test_appconfig_setting_infra():
    class TestInfra(AzureInfrastructure):
        data: ConfigSetting = ConfigSetting(name="setting", value="value")

    assert isinstance(TestInfra.data, ConfigSetting)
    infra = TestInfra()
    assert isinstance(infra.data, ConfigSetting)
    assert infra.data.properties == {"name": "setting", "properties": {"value": "value"}}

    infra = TestInfra(data=ConfigSetting(name="foo", value="bar", store="baz"))
    assert infra.data._settings["name"]() == "foo"
    assert infra.data.parent._settings["name"]() == "baz"

    class TestInfra(AzureInfrastructure):
        data: ConfigSetting = field(default=ConfigSetting.reference(name="testdata", store="testconfig"))

    infra = TestInfra()
    assert infra.data._settings["name"]() == "testdata"
    assert infra.data.parent._settings["name"]() == "testconfig"


def test_appconfig_setting_app():
    from azure.appconfiguration import AzureAppConfigurationClient

    r = ConfigSetting.reference(name="test", store="test", resource_group="test")

    class TestApp(AzureApp):
        client: AzureAppConfigurationClient

    with pytest.raises(TypeError):
        app = TestApp()

    with pytest.raises(TypeError):
        app = TestApp(client=r)

    app = TestApp.load(config_store={"AZURE_APPCONFIG_ENDPOINT": "test"})
