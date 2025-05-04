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
    TypedDict,
    Generic,
    Literal,
    Mapping,
    Union,
    Optional,
    cast,
)
from typing_extensions import TypeVar, Unpack

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
    from ._types import AppServicePlanResource


class AppServicePlanKwargs(TypedDict, total=False):
    reserved: bool
    """Defaults to false when creating Windows/app App Service Plan. Required if creating a Linux App Service Plan
    and must be set to true.
    """
    # diagnosticSettings: List['DiagnosticSetting']
    # """The diagnostic settings of the service."""
    elastic_scale_enabled: Union[bool, Parameter]
    """Enable/Disable ElasticScaleEnabled App Service Plan."""
    kind: Union[Literal["App", "Elastic", "FunctionApp", "Linux", "Windows"], Parameter]
    """Kind of server OS."""
    location: Union[str, Parameter]
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
        list[
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
        list[
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
    capacity: Union[int, Parameter]
    """Number of workers associated with the App Service Plan. This defaults to 3, to leverage availability zones."""
    sku: Union[str, Parameter]
    """The name of the SKU will Determine the tier, size, family of the App Service Plan. This defaults to P1v3 to
    leverage availability zones.
    """
    tags: Union[dict[str, Union[str, Parameter]], Parameter]
    """Tags of the resource."""
    target_worker_count: Union[int, Parameter]
    """Scaling worker count."""
    target_worker_size: Union[Literal[0, 1, 2], Parameter]
    """The instance size of the hosting plan (small, medium, or large)."""
    worker_tier_name: Union[str, Parameter]
    """Target worker tier assigned to the App Service plan."""
    zone_redundant: Union[bool, Parameter]
    """Zone Redundant server farms can only be used on Premium or ElasticPremium SKU tiers within ZRS Supported
    regions (https://learn.microsoft.com/azure/storage/common/redundancy-regions-zrs).
    """


AppServicePlanResourceType = TypeVar(
    "AppServicePlanResourceType", bound=Mapping[str, Any], default="AppServicePlanResource"
)
_DEFAULT_APP_SERVICE_PLAN: "AppServicePlanResource" = {
    "name": GLOBAL_PARAMS["defaultName"],
    "location": GLOBAL_PARAMS["location"],
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
    """Azure App Service Plan resource.

    :param properties: The properties of the App Service Plan resource
    :type properties: Optional[AppServicePlanResource]
    :param name: The name of the App Service Plan
    :type name: Optional[Union[str, Parameter]]

    :keyword reserved: Defaults to false for Windows App Service Plan. Must be true for Linux App Service Plan
    :paramtype reserved: bool
    :keyword elastic_scale_enabled: Enable/Disable ElasticScaleEnabled App Service Plan
    :paramtype elastic_scale_enabled: Union[bool, Parameter]
    :keyword kind: Kind of server OS
    :paramtype kind: Union[Literal["App", "Elastic", "FunctionApp", "Linux", "Windows"], Parameter]
    :keyword location: Location for all resources
    :paramtype location: Union[str, Parameter]
    :keyword maximum_elastic_worker_count: Maximum number of total workers allowed for ElasticScaleEnabled plan
    :paramtype maximum_elastic_worker_count: int
    :keyword per_site_scaling: If true, apps can be scaled independently
    :paramtype per_site_scaling: bool
    :keyword roles: Array of role assignments to create
    :paramtype roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword user_roles: Array of Role assignments to create for user principal ID
    :paramtype user_roles: Union[Parameter, list[Union[Parameter, RoleAssignment, str]]]
    :keyword capacity: Number of workers associated with the App Service Plan (defaults to 3)
    :paramtype capacity: Union[int, Parameter]
    :keyword sku: Name of the SKU determining tier, size, family of App Service Plan (defaults to P1v3)
    :paramtype sku: Union[str, Parameter]
    :keyword tags: Tags of the resource
    :paramtype tags: Union[dict[str, Union[str, Parameter]], Parameter]
    :keyword target_worker_count: Scaling worker count
    :paramtype target_worker_count: Union[int, Parameter]
    :keyword target_worker_size: Instance size of hosting plan (0=small, 1=medium, 2=large)
    :paramtype target_worker_size: Union[Literal[0, 1, 2], Parameter]
    :keyword worker_tier_name: Target worker tier assigned to the App Service plan
    :paramtype worker_tier_name: Union[str, Parameter]
    :keyword zone_redundant: Enable zone redundancy (Premium/ElasticPremium SKU only, ZRS supported regions)
    :paramtype zone_redundant: Union[bool, Parameter]

    :ivar DEFAULTS: Default configuration for App Service Plan
    :vartype DEFAULTS: AppServicePlanResource
    :ivar DEFAULT_EXTENSIONS: Default extensions configuration
    :vartype DEFAULT_EXTENSIONS: ExtensionResources
    :ivar properties: The properties of the App Service Plan
    :vartype properties: AppServicePlanResourceType
    :ivar parent: Parent resource (None for App Service Plan)
    :vartype parent: None
    """

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
        if not existing:
            properties = properties or {}
            if "properties" not in properties:
                properties["properties"] = {}
            if name:
                properties["name"] = name
            if "location" in kwargs:
                properties["location"] = kwargs.pop("location")
            if "reserved" in kwargs:
                properties["properties"]["reserved"] = kwargs.pop("reserved")
            if "elastic_scale_enabled" in kwargs:
                properties["properties"]["elasticScaleEnabled"] = kwargs.pop("elastic_scale_enabled")
            if "maximum_elastic_worker_count" in kwargs:
                properties["properties"]["maximumElasticWorkerCount"] = kwargs.pop("maximum_elastic_worker_count")
            if "per_site_scaling" in kwargs:
                properties["properties"]["perSiteScaling"] = kwargs.pop("per_site_scaling")
            if "target_worker_count" in kwargs:
                properties["properties"]["targetWorkerCount"] = kwargs.pop("target_worker_count")
            if "target_worker_size" in kwargs:
                properties["properties"]["targetWorkerSizeId"] = kwargs.pop("target_worker_size")
            if "worker_tier_name" in kwargs:
                properties["properties"]["workerTierName"] = kwargs.pop("worker_tier_name")
            if "zone_redundant" in kwargs:
                properties["properties"]["zoneRedundant"] = kwargs.pop("zone_redundant")
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
            elif "tags" not in properties:
                properties["tags"] = {}
            if "azd-env-name" not in properties["tags"]:
                properties["tags"]["azd-env-name"] = None
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
        from ._types import VERSION

        return VERSION

    def _outputs(self, **kwargs) -> dict[str, list[Output]]:
        return {}
