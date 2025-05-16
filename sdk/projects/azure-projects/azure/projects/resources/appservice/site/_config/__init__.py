# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Union,
    Optional,
)
from typing_extensions import TypeVar

from ...._identifiers import ResourceIdentifiers
from ....._bicep.utils import generate_name
from ....._bicep.expressions import Output, Parameter, Expression, ResourceSymbol
from ....._resource import Resource

if TYPE_CHECKING:
    from .. import AppSite
    from .types import SiteConfigResource


SiteConfigResourceType = TypeVar("SiteConfigResourceType", bound=Mapping[str, Any], default="SiteConfigResource")


class SiteConfig(Resource, Generic[SiteConfigResourceType]):
    properties: SiteConfigResourceType
    parent: "AppSite"  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["SiteConfigResource"] = None,
        *,
        name: Optional[Union[str, Expression]],
        parent: "AppSite[Any]",
        settings: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        properties = properties or {}
        if "properties" not in properties:
            if settings:
                properties["properties"] = settings
            else:
                properties["properties"] = {}
        if name:
            properties["name"] = name
        super().__init__(
            properties,
            parent=parent,
            subresource="config",
            service_prefix=["site_config"],
            identifier=ResourceIdentifiers.app_service_site_config,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.Web/sites/config"]:
        return "Microsoft.Web/sites/config"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        if suffix:
            resource_ref = f"siteconfig_{generate_name(suffix)}"
        else:
            resource_ref = "siteconfig"
        return ResourceSymbol(resource_ref)

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}
