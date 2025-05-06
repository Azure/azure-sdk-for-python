from uuid import uuid4

import pytest
from unittest.mock import ANY

from azure.projects.resources._extension import add_roles
from azure.projects.resources._extension.roles import BUILT_IN_ROLES, RoleAssignment
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._resource import FieldType
from azure.projects._bicep.expressions import ResourceSymbol, Output, Guid, Variable, RoleDefinition
from azure.projects import Parameter, export, AzureInfrastructure

TEST_SUB = str(uuid4())
RG = ResourceSymbol("resourcegroup")
IDENTITY = Output(None, "properties.principalId", ResourceSymbol("userassignedidentity"))
CONTRIB_GUID = Guid(
    "MicrosoftStoragestorageAccounts",
    GLOBAL_PARAMS["environmentName"],
    "foo",
    "ServicePrincipal",
    "Storage Blob Data Contributor",
)
OWNER_GUID = Guid(
    "MicrosoftStoragestorageAccounts",
    GLOBAL_PARAMS["environmentName"],
    "foo",
    "ServicePrincipal",
    "Storage Blob Data Owner",
)


def test_roles_properties():
    r = StorageAccount(
        name="foo", roles=["Storage Blob Data Contributor"], user_roles=["Storage Blob Data Contributor"]
    )
    assert r.properties == {"name": "foo", "properties": {}, "tags": {'azd-env-name': None}, "identity": {}}
    assert r.extensions == {
        "managed_identity_roles": ["Storage Blob Data Contributor"],
        "user_roles": ["Storage Blob Data Contributor"],
    }
    fields = {}
    parameters = dict(GLOBAL_PARAMS)
    # TODO: Test with and without managed identity
    UserAssignedIdentity().__bicep__(fields, parameters=parameters)
    symbols = r.__bicep__(fields, parameters=parameters)

    r = StorageAccount(name="foo", roles=["Storage Blob Data Owner"], user_roles=["Owner"])
    assert r.properties == {"name": "foo", "properties": {}, "tags": {'azd-env-name': None}, "identity": {}}
    assert r.extensions == {"managed_identity_roles": ["Storage Blob Data Owner"], "user_roles": ["Owner"]}
    with pytest.raises(ValueError):
        symbols = r.__bicep__(fields, parameters=parameters)
    add_roles(fields, parameters)

    user_role_field = fields.popitem()[1]
    ma_role_field = fields.popitem()[1]
    assert ma_role_field.resource == "Microsoft.Authorization/roleAssignments"
    assert ma_role_field.properties == {
        "name": CONTRIB_GUID,
        "scope": symbols[0],
        "properties": {
            "principalId": IDENTITY,
            "principalType": "ServicePrincipal",
            "roleDefinitionId": RoleDefinition("ba92f5b4-2d11-453d-a403-e96b0029c9fe"),
        },
    }
    assert ma_role_field.resource_group == None


def test_roles_defaults():
    base = RoleAssignment({})
    r = StorageAccount(
        name="foo", roles=["Storage Blob Data Contributor"], user_roles=["Storage Blob Data Contributor"]
    )
    assert r.properties == {"name": "foo", "properties": {}, "tags": {'azd-env-name': None}, "identity": {}}
    assert r.extensions == {
        "managed_identity_roles": ["Storage Blob Data Contributor"],
        "user_roles": ["Storage Blob Data Contributor"],
    }
    fields = {}
    parameters = dict(GLOBAL_PARAMS)
    UserAssignedIdentity().__bicep__(fields, parameters=parameters)
    symbols = r.__bicep__(fields, parameters=parameters)
    add_roles(fields, parameters)
    user_role_field = fields.popitem()[1]
    ma_role_field = fields.popitem()[1]
    assert ma_role_field.properties == {
        "name": CONTRIB_GUID,
        "scope": symbols[0],
        "properties": {
            "principalId": IDENTITY,
            "principalType": "ServicePrincipal",
            "roleDefinitionId": BUILT_IN_ROLES["Storage Blob Data Contributor"],
        },
    }


def test_roles_export_with_parameters(export_dir):
    user_role = Parameter("userRole", default="Storage Blob Data Contributor")
    roles = Parameter("allRoles", default=["Owner"])

    class test(AzureInfrastructure):
        storage: StorageAccount

    r = test(storage=StorageAccount(name="foo", roles=roles, user_roles=[user_role]))
    assert r.storage.properties == {"name": "foo", "properties": {}, "tags": {'azd-env-name': None}, "identity": {}}
    assert r.storage.extensions == {"managed_identity_roles": roles, "user_roles": [user_role]}
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2])
