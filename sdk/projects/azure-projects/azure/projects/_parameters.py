# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import TypedDict
from typing_extensions import NotRequired

from ._bicep.expressions import Parameter, UniqueString, Subscription, Variable


LOCATION = Parameter(
    "location", description="Primary location for all resources", min_length=1, env_var="AZURE_LOCATION"
)
ENV_NAME = Parameter(
    "environmentName",
    description="AZD environment name",
    min_length=1,
    max_length=64,
    env_var="AZURE_ENV_NAME",
)
NAME_PREFIX = Parameter("defaultNamePrefix", default="azproj")
DEFAULT_NAME = Parameter(
    "defaultName",
    default=NAME_PREFIX.format() + UniqueString(Subscription().subscription_id, ENV_NAME, LOCATION).format(),
)
# TODO: Rename to something like "UserPrincipal"?
LOCAL_PRINCIPAL = Parameter(
    "principalId",
    description="ID of the user or app to assign application roles",
    env_var="AZURE_PRINCIPAL_ID",
)
AZD_TAGS = Variable(
    "azdTags", value={"azd-env-name": ENV_NAME}, description="Tags to apply to all resources in AZD environment."
)
TENANT_ID = Parameter(
    "tenantId",
    description="The Azure Active Directory tenant ID.",
    default=Subscription().tenant_id,
    secure=True,
    env_var="AZURE_TENANT_ID",
)
_MANAGED_IDENTITY_ID: Parameter = Parameter(
    "managedIdentityId",
    description="ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_ID",
    default="",
)
_MANAGED_IDENTITY_PRINCIPAL_ID = Parameter(
    "managedIdentityPrincipalId",
    description="Principal ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_PRINCIPAL_ID",
    secure=True,
    default="",
)
_MANAGED_IDENTITY_CLIENT_ID = Parameter(
    "managedIdentityClientId",
    description="Client ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_CLIENT_ID",
    secure=True,
    default="",
)


class GlobalParamsType(TypedDict):
    location: Parameter
    environmentName: Parameter
    defaultNamePrefix: Parameter
    defaultName: Parameter
    principalId: Parameter
    tenantId: Parameter
    azdTags: Parameter
    managedIdentityId: NotRequired[Parameter]
    managedIdentityPrincipalId: NotRequired[Parameter]
    managedIdentityClientId: NotRequired[Parameter]


GLOBAL_PARAMS: GlobalParamsType = {
    "location": LOCATION,
    "environmentName": ENV_NAME,
    "defaultNamePrefix": NAME_PREFIX,
    "defaultName": DEFAULT_NAME,
    "principalId": LOCAL_PRINCIPAL,
    "tenantId": TENANT_ID,
    "azdTags": AZD_TAGS,
    "managedIdentityId": _MANAGED_IDENTITY_ID,
    "managedIdentityPrincipalId": _MANAGED_IDENTITY_PRINCIPAL_ID,
    "managedIdentityClientId": _MANAGED_IDENTITY_CLIENT_ID,
}
