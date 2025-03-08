# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    Union,
    Optional,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..._identifiers import ResourceIdentifiers
from ...._bicep.utils import generate_name
from ...._bicep.expressions import Output, Parameter
from ...._resource import ExtensionResources, Resource

if TYPE_CHECKING:
    from .. import AIHub, AIProject
    from .types import ConnectionResource


class ConnectionKwargs(TypedDict, total=False):
    category: Union[str, Parameter]
    """Category of the connection."""
    connection_properties: Dict[str, object]
    """The properties of the connection, specific to the auth type."""
    target: str
    """The target of the connection."""
    expiry_time: str
    """The expiry time of the connection."""
    is_shared_to_all: bool
    """Indicates whether the connection is shared to all users in the workspace."""
    metadata: Dict[str, object]
    """User metadata for the connection."""
    shared_user_list: List[object]
    """The shared user list of the connection."""


_DEFAULT_CONNECTION: "ConnectionResource" = {
    "properties": {"authType": "AAD", "isSharedToAll": True, "sharedUserList": []}
}
ConnectionResourceType = TypeVar("ConnectionResourceType", default="ConnectionResource")


class AIConnection(Resource[ConnectionResourceType]):
    DEFAULTS: "ConnectionResource" = _DEFAULT_CONNECTION
    properties: ConnectionResourceType
    parent: Union["AIHub", "AIProject"]

    def __init__(
        self,
        properties: Optional["ConnectionResource"] = None,
        /,
        name: Optional[str] = None,
        *,
        parent: Union["AIProject", "AIHub"],
        **kwargs: Unpack[ConnectionKwargs],
    ) -> None:
        from .. import AIHub

        existing = kwargs.pop("existing", False)
        extensions: ExtensionResources = defaultdict(list)
        properties = properties or {}
        if "properties" not in properties:
            properties["properties"] = {}
        if name:
            properties["name"] = name
        if "category" in kwargs:
            properties["properties"]["category"] = kwargs.pop("category")
        if "target" in kwargs:
            properties["properties"]["target"] = kwargs.pop("target")
        if "metadata" in kwargs:
            properties["properties"]["metadata"] = kwargs.pop("metadata")
        super().__init__(
            properties,
            extensions=extensions,
            existing=existing,
            parent=parent,
            subresource="connections",
            service_prefix=["ai_connection"],
            identifier=ResourceIdentifiers.ai_connection,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.MachineLearningServices/workspaces/connections"]:
        return "Microsoft.MachineLearningServices/workspaces/connections"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _build_suffix(self, value: Optional[Union[str, Parameter]]) -> str:
        try:
            return "_" + generate_name(value.value)
        except AttributeError:
            return "_" + generate_name(value)

    def _outputs(self, **kwargs) -> Dict[str, Output]:
        return {}
