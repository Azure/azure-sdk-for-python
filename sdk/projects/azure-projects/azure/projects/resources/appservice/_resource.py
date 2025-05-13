# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from collections import defaultdict
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
    cast,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..resourcegroup import ResourceGroup
from .._identifiers import ResourceIdentifiers
from .._extension import RoleAssignment
from ..._parameters import GLOBAL_PARAMS
from ..._bicep.expressions import Parameter, Output
from ..._resource import (
    Resource,
    ResourceReference,
    ExtensionResources,
)

if TYPE_CHECKING:
    from .types import AppServicePlanResource


class AppServicePlanKwargs(TypedDict, total=False):
    reserved: bool
    """Defaults to false when creating Windows/app App Service Plan. Required if creating a Linux App Service Plan
    and must be set to true.
    """
    app_service_environment: str
    """The Resource ID of the App Service Environment to use for the App Service Plan."""
    # diagnosticSettings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    elastic_scale_enabled: bool
    """Enable/Disable ElasticScaleEnabled App Service Plan."""
    kind: Literal["App", "Elastic", "FunctionApp", "Linux", "Windows"]
    """Kind of server OS."""
    location: str
    """Location for all resources."""
    # lock: 'Lock'
    # """The lock settings of the service."""
    maximum_elastic_worker_count: int
    """Maximum number of total workers allowed for this ElasticScaleEnabled App Service Plan."""
    per_site_scaling: bool
    """If true, apps assigned to this App Service plan can be scaled independently. If false, apps assigned to this App
    Service plan will scale to all instances of the plan.
    """
    roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Web Plan Contributor",
                    "Website Contributor",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of role assignments to create."""
    user_roles: Union[
        Parameter,
        List[
            Union[
                Parameter,
                "RoleAssignment",
                Literal[
                    "Web Plan Contributor",
                    "Website Contributor",
                    "Contributor",
                    "Owner",
                    "Reader",
                    "Role Based Access Control Administrator",
                    "User Access Administrator",
                ],
            ]
        ],
    ]
    """Array of Role assignments to create for user principal ID"""
    capacity: int
    """Number of workers associated with the App Service Plan. This defaults to 3, to leverage availability zones."""
    sku: str
    """The name of the SKU will Determine the tier, size, family of the App Service Plan. This defaults to P1v3 to
    leverage availability zones.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    target_worker_count: int
    """Scaling worker count."""
    target_worker_size: Literal[0, 1, 2]
    """The instance size of the hosting plan (small, medium, or large)."""
    worker_tier_name: str
    """Target worker tier assigned to the App Service plan."""
    zone_redundant: bool
    """Zone Redundant server farms can only be used on Premium or ElasticPremium SKU tiers within ZRS Supported
    regions (https://learn.microsoft.com/azure/storage/common/redundancy-regions-zrs).
    """


AppServicePlanResourceType = TypeVar(
    "AppServicePlanResourceType", bound=Mapping[str, Any], default="AppServicePlanResource"
)
_DEFAULT_APP_SERVICE_PLAN: "AppServicePlanResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
    "tags": GLOBAL_PARAMS["azdTags"],
    "kind": "linux",
    "properties": {
        "reserved": True,
    },
    "sku": {
        "name": "P1v3",
        "capacity": 3,
    },
}
_DEFAULT_APP_SERVICE_PLAN_EXTENSIONS: ExtensionResources = {"managed_identity_roles": [], "user_roles": []}


class AppServicePlan(Resource, Generic[AppServicePlanResourceType]):
    DEFAULTS: "AppServicePlanResource" = _DEFAULT_APP_SERVICE_PLAN  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_APP_SERVICE_PLAN_EXTENSIONS
    properties: AppServicePlanResourceType
    parent: None  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["AppServicePlanResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        **kwargs: Unpack[AppServicePlanKwargs],
    ) -> None:
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        extensions: ExtensionResources = defaultdict(list)  # type: ignore  # Doesn't like the default dict.
        if "roles" in kwargs:
            extensions["managed_identity_roles"] = kwargs.pop("roles")
        if "user_roles" in kwargs:
            extensions["user_roles"] = kwargs.pop("user_roles")
        # TODO: Finish populating kwarg properties
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "sku" in kwargs:
                sku = kwargs.pop("sku")
                properties["sku"] = {"name": sku}
            if "capacity" in kwargs:
                capacity = kwargs.pop("capacity")
                existing_sku = properties.pop("sku", {})
                try:
                    existing_sku["capacity"] = capacity  # type: ignore[index]
                    properties["sku"] = existing_sku
                except TypeError as e:
                    # This would mean that 'sku' is already using a parameter
                    raise ValueError(f"Cannot set property 'capacity' to {existing_sku}.") from e
            if "tags" in kwargs:
                properties["tags"] = kwargs.pop("tags")
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["app_service_plan"],
            existing=existing,
            identifier=ResourceIdentifiers.app_service_plan,
            **kwargs,
        )

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        resource_group: Optional[Union[str, Parameter, ResourceGroup[ResourceReference]]] = None,
    ) -> "AppServicePlan[ResourceReference]":
        existing = super().reference(
            name=name,
            resource_group=resource_group,
        )
        return cast(AppServicePlan[ResourceReference], existing)

    @property
    def resource(self) -> Literal["Microsoft.Web/serverfarms"]:
        return "Microsoft.Web/serverfarms"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}
