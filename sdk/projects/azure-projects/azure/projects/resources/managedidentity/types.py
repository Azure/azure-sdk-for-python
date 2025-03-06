from typing import TypedDict, Dict, Union


from ..._bicep.expressions import Parameter

RESOURCE = "Microsoft.ManagedIdentity/userAssignedIdentities"
VERSION = "2023-07-31-preview"


class UserAssignedIdentityResource(TypedDict, total=False):
    name: Union[str, Parameter[str]]
    """The name of the User Assigned Identity."""
    location: Union[str, Parameter[str]]
    """Location of the identity. It uses the deployment's location when not provided."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Tags of the resource."""
