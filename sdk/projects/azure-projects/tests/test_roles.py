from uuid import uuid4

import pytest
from unittest.mock import ANY

from azure.projects.resources._extension import add_extensions
from azure.projects.resources._extension.roles import BUILT_IN_ROLES, RoleAssignment
from azure.projects.resources.storage import StorageAccount
from azure.projects.resources.resourcegroup import ResourceGroup
from azure.projects.resources.managedidentity import UserAssignedIdentity
from azure.projects._parameters import GLOBAL_PARAMS
from azure.projects._resource import FieldType
from azure.projects._bicep.expressions import ResourceSymbol, Output, Guid, Variable, RoleDefinition
from azure.projects import Parameter, export

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
    assert r.properties == {"name": "foo", "properties": {}}
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
    assert r.properties == {"name": "foo", "properties": {}}
    assert r.extensions == {"managed_identity_roles": ["Storage Blob Data Owner"], "user_roles": ["Owner"]}
    symbols = r.__bicep__(fields, parameters=parameters)
    add_extensions(fields, parameters)
    assert len(fields[f"storageaccount_foo"].extensions["managed_identity_roles"]) == 2
    assert len(fields[f"storageaccount_foo"].extensions["user_roles"]) == 2
    role_symbol = fields[f"storageaccount_foo"].extensions["managed_identity_roles"][0]
    assert fields[f"{role_symbol.value}"].resource == "Microsoft.Authorization/roleAssignments"
    assert fields[f"{role_symbol.value}"].properties == {
        "name": CONTRIB_GUID,
        "scope": symbols[0],
        "properties": {
            "principalId": IDENTITY,
            "principalType": "ServicePrincipal",
            "roleDefinitionId": RoleDefinition("ba92f5b4-2d11-453d-a403-e96b0029c9fe"),
        },
    }
    assert fields[f"{role_symbol.value}"].symbol == role_symbol
    assert fields[f"{role_symbol.value}"].resource_group == None


def test_roles_defaults():
    base = RoleAssignment({})
    r = StorageAccount(
        name="foo", roles=["Storage Blob Data Contributor"], user_roles=["Storage Blob Data Contributor"]
    )
    assert r.properties == {"name": "foo", "properties": {}}
    assert r.extensions == {
        "managed_identity_roles": ["Storage Blob Data Contributor"],
        "user_roles": ["Storage Blob Data Contributor"],
    }
    fields = {}
    parameters = dict(GLOBAL_PARAMS)
    UserAssignedIdentity().__bicep__(fields, parameters=parameters)
    symbols = r.__bicep__(fields, parameters=parameters)
    add_extensions(fields, parameters)
    role_symbol = fields[f"storageaccount_foo"].extensions["managed_identity_roles"][0]
    assert fields[f"{role_symbol.value}"].properties == {
        "name": CONTRIB_GUID,
        "scope": symbols[0],
        "properties": {
            "principalId": IDENTITY,
            "principalType": "ServicePrincipal",
            "roleDefinitionId": BUILT_IN_ROLES["Storage Blob Data Contributor"],
        },
    }


@pytest.mark.skip("TODO: Parameterization of roles doesn't work yet")
def test_roles_export_with_parameters(export_dir):
    user_role = Parameter("userRole", default={})
    roles = Parameter("allRoles", default=[])
    r = StorageAccount(name="foo", roles=roles, user_roles=[user_role])
    assert r.properties == {"name": "foo", "properties": {}}
    assert r.extensions == {"managed_identity_roles": roles, "user_roles": [user_role]}
    export(r, output_dir=export_dir[0], infra_dir=export_dir[2])
