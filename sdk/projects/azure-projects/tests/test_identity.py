from uuid import uuid4

import pytest
from azure.projects._resource import FieldType
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._utils import add_defaults
from azure.projects.resources._identifiers import ResourceIdentifiers
from azure.projects._bicep.expressions import ResourceSymbol, Output
from azure.projects import Parameter, export, AzureInfrastructure, field

TEST_SUB = "6ceba549-5d9d-47da-a5bb-72816776ba40"


def test_identity_properties():
    r = UserAssignedIdentity()
    assert r.properties == {}
    assert r.extensions == {}
    assert r._existing == False
    assert not r.parent
    assert r.resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert r.version
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["userassignedidentity"]
    assert fields["userassignedidentity"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity"].properties == {}
    # assert fields['userassignedidentity'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity"].extensions == {}
    assert fields["userassignedidentity"].existing == False
    assert fields["userassignedidentity"].version
    assert fields["userassignedidentity"].symbol == symbols[0]
    assert fields["userassignedidentity"].resource_group == None
    assert not fields["userassignedidentity"].name
    assert fields["userassignedidentity"].defaults

    r2 = UserAssignedIdentity(location="westus")
    assert r2.properties == {"location": "westus"}
    r2.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["userassignedidentity"]
    assert fields["userassignedidentity"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity"].properties == {"location": "westus"}
    # assert fields['userassignedidentity'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity"].extensions == {}
    assert fields["userassignedidentity"].existing == False
    assert fields["userassignedidentity"].version
    assert fields["userassignedidentity"].symbol == symbols[0]
    assert fields["userassignedidentity"].resource_group == None
    assert not fields["userassignedidentity"].name
    assert fields["userassignedidentity"].defaults

    r3 = UserAssignedIdentity(location="eastus")
    assert r3.properties == {"location": "eastus"}
    with pytest.raises(ValueError):
        r3.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))

    r4 = UserAssignedIdentity(name="foo", tags={"test": "value"})
    assert r4.properties == {"name": "foo", "tags": {"test": "value"}}
    symbols = r4.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["userassignedidentity", "userassignedidentity_foo"]
    assert fields["userassignedidentity_foo"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity_foo"].properties == {"name": "foo", "tags": {"test": "value"}}
    # assert fields['userassignedidentity_foo'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity_foo"].extensions == {}
    assert fields["userassignedidentity_foo"].existing == False
    assert fields["userassignedidentity_foo"].version
    assert fields["userassignedidentity_foo"].symbol == symbols[0]
    assert fields["userassignedidentity_foo"].resource_group == None
    assert fields["userassignedidentity_foo"].name == "foo"
    assert fields["userassignedidentity_foo"].defaults

    param1 = Parameter("testA")
    param2 = Parameter("testB")
    r5 = UserAssignedIdentity(name=param1, tags={"foo": param2})
    assert r5.properties == {"name": param1, "tags": {"foo": param2}}
    params = dict(GLOBAL_PARAMS)
    fields = {}
    symbols = r5.__bicep__(fields, parameters=params)
    assert list(fields.keys()) == ["userassignedidentity_testa"]
    assert fields["userassignedidentity_testa"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity_testa"].properties == {"name": param1, "tags": {"foo": param2}}
    # assert fields['userassignedidentity_testa'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity_testa"].extensions == {}
    assert fields["userassignedidentity_testa"].existing == False
    assert fields["userassignedidentity_testa"].version
    assert fields["userassignedidentity_testa"].symbol == symbols[0]
    assert fields["userassignedidentity_testa"].resource_group == None
    assert fields["userassignedidentity_testa"].name == param1
    assert fields["userassignedidentity_testa"].defaults

    assert params.get("testA") == param1
    assert params.get("testB") == param2


def test_identity_reference():
    r = UserAssignedIdentity.reference(name="foo")
    assert r.properties == {"name": "foo"}
    assert r._existing == True
    assert not r.parent
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
    assert list(fields.keys()) == ["userassignedidentity_foo"]
    assert fields["userassignedidentity_foo"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity_foo"].properties == {"name": "foo"}
    # assert fields['userassignedidentity_foo'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity_foo"].extensions == {}
    assert fields["userassignedidentity_foo"].existing == True
    assert fields["userassignedidentity_foo"].version
    assert fields["userassignedidentity_foo"].symbol == symbols[0]
    assert fields["userassignedidentity_foo"].resource_group == None
    assert fields["userassignedidentity_foo"].name == "foo"
    assert not fields["userassignedidentity_foo"].defaults

    r = UserAssignedIdentity.reference(name="bar", resource_group="rgtest")
    assert r.properties == {"name": "bar", "resource_group": ResourceGroup(name="rgtest")}
    assert r._settings["resource_group"]() == "rgtest"
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_rgtest", "userassignedidentity_bar"]
    assert fields["userassignedidentity_bar"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity_bar"].properties == {
        "name": "bar",
        "scope": ResourceSymbol("resourcegroup_rgtest"),
    }
    # assert fields['userassignedidentity_bar'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity_bar"].extensions == {}
    assert fields["userassignedidentity_bar"].existing == True
    assert fields["userassignedidentity_bar"].version
    assert fields["userassignedidentity_bar"].symbol == symbols[0]
    assert fields["userassignedidentity_bar"].resource_group == ResourceSymbol("resourcegroup_rgtest")
    assert fields["userassignedidentity_bar"].name == "bar"
    assert not fields["userassignedidentity_bar"].defaults

    r = UserAssignedIdentity.reference(
        name="bar", resource_group=ResourceGroup.reference(name="rgtest", subscription=TEST_SUB)
    )
    assert r.properties == {"name": "bar", "resource_group": ResourceGroup(name="rgtest")}
    assert r._settings["resource_group"]() == "rgtest"
    assert r._settings["subscription"]() == TEST_SUB
    assert (
        r._settings["resource_id"]()
        == f"/subscriptions/{TEST_SUB}/resourceGroups/rgtest/providers/Microsoft.ManagedIdentity/userAssignedIdentities/bar"
    )
    fields = {}
    symbols = r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    assert list(fields.keys()) == ["resourcegroup_rgtest", "userassignedidentity_bar"]
    assert fields["userassignedidentity_bar"].resource == "Microsoft.ManagedIdentity/userAssignedIdentities"
    assert fields["userassignedidentity_bar"].properties == {
        "name": "bar",
        "scope": ResourceSymbol("resourcegroup_rgtest"),
    }
    # assert fields['userassignedidentity_bar'].outputs == {'client_id': Output('AZURE_CLIENT_ID', "properties.clientId", symbols[0])}
    assert fields["userassignedidentity_bar"].extensions == {}
    assert fields["userassignedidentity_bar"].existing == True
    assert fields["userassignedidentity_bar"].version
    assert fields["userassignedidentity_bar"].symbol == symbols[0]
    assert fields["userassignedidentity_bar"].resource_group == ResourceSymbol("resourcegroup_rgtest")
    assert fields["userassignedidentity_bar"].name == "bar"
    assert not fields["userassignedidentity_bar"].defaults


def test_identity_defaults():
    ua_name = Parameter("uaName")
    r = UserAssignedIdentity(name=ua_name)
    fields = {}
    r.__bicep__(fields, parameters=dict(GLOBAL_PARAMS))
    add_defaults(fields, parameters=dict(GLOBAL_PARAMS))
    field: FieldType = fields.popitem()[1]
    assert field.properties == {
        "name": ua_name,
        "location": GLOBAL_PARAMS["location"],
        "tags": GLOBAL_PARAMS["azdTags"],
    }


def test_identity_export(export_dir):
    class test(AzureInfrastructure):
        r: UserAssignedIdentity = UserAssignedIdentity()

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_identity_export_with_properties(export_dir):
    class test(AzureInfrastructure):
        identity: UserAssignedIdentity = field(
            default=UserAssignedIdentity(name="foo", location="westus", tags={"key": "value"})
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_identity_export_with_parameter(export_dir):
    param = Parameter("testLocation")

    class test(AzureInfrastructure):
        identity: UserAssignedIdentity = field(default=UserAssignedIdentity(location=param))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2], parameters={"testLocation": "eastus"})


def test_identity_export_existing(export_dir):
    class test(AzureInfrastructure):
        identity: UserAssignedIdentity = field(default=UserAssignedIdentity.reference(name="exists"))

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_identity_export_existing_with_resourcegroup(export_dir):
    class test(AzureInfrastructure):
        r: UserAssignedIdentity = field(
            default=UserAssignedIdentity.reference(name="exists", resource_group="rgexists")
        )

    export(test(), output_dir=export_dir[0], infra_dir=export_dir[2])


def test_identity_export_existing_with_resourcegroup_and_subscription(export_dir):
    class test(AzureInfrastructure):
        identity: UserAssignedIdentity = field(default=UserAssignedIdentity.reference(name="exists"))

    export(
        test(resource_group=ResourceGroup.reference(name="rgexists", subscription=TEST_SUB)),
        output_dir=export_dir[0],
        infra_dir=export_dir[2],
    )


def test_identity_infra():
    class TestInfra(AzureInfrastructure):
        identity: UserAssignedIdentity = field()

    with pytest.raises(AttributeError):
        TestInfra.identity
    with pytest.raises(TypeError):
        infra = TestInfra()
    infra = TestInfra(identity=UserAssignedIdentity())
    assert isinstance(infra.identity, UserAssignedIdentity)
    assert infra.identity.properties == {}

    infra = TestInfra(identity=UserAssignedIdentity(name="foo"))
    assert infra.identity._settings["name"]() == "foo"
