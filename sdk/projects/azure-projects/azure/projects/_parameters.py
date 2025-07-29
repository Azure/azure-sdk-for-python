# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing_extensions import TypedDict

from ._bicep.expressions import Parameter, UniqueString, Subscription, Variable, PlaceholderParameter


LOCATION = Parameter(
    "location", description="Primary location for all resources", min_length=1, env_var="AZURE_LOCATION", type="string"
)
ENV_NAME = Parameter(
    "environmentName",
    description="AZD environment name",
    min_length=1,
    max_length=64,
    env_var="AZURE_ENV_NAME",
    type="string",
)
NAME_PREFIX = Parameter("defaultNamePrefix", default="azproj", type="string")
DEFAULT_NAME = Parameter(
    "defaultName",
    default=NAME_PREFIX.format() + UniqueString(Subscription().subscription_id, ENV_NAME, LOCATION).format(),
    type="string",
)
# TODO: Rename to something like "UserPrincipal"?
LOCAL_PRINCIPAL = Parameter(
    "principalId",
    description="ID of the user or app to assign application roles",
    env_var="AZURE_PRINCIPAL_ID",
    type="string",
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
    type="string",
)
_MANAGED_IDENTITY_ID = PlaceholderParameter(
    "managedIdentityId",
    description="ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_ID",
    default="",
    type="string",
)
# TODO: The ManagedIdentity parameters are a bit wonky. Need to test more thoroughly.
_MANAGED_IDENTITY_PRINCIPAL_ID = PlaceholderParameter(
    "managedIdentityPrincipalId",
    description="Principal ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_PRINCIPAL_ID",
    secure=True,
    default="",
    type="string",
)
_MANAGED_IDENTITY_CLIENT_ID = PlaceholderParameter(
    "managedIdentityClientId",
    description="Client ID of the managed identity to assign application roles",
    env_var="AZURE_MANAGED_IDENTITY_CLIENT_ID",
    secure=True,
    default="",
    type="string",
)


class GlobalParamsType(TypedDict):
    location: Parameter
    environmentName: Parameter
    defaultNamePrefix: Parameter
    defaultName: Parameter
    principalId: Parameter
    tenantId: Parameter
    azdTags: Parameter
    managedIdentityId: Parameter
    managedIdentityPrincipalId: Parameter
    managedIdentityClientId: Parameter


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
