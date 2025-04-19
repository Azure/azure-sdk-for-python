# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=arguments-differ

from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    Union,
    Optional,
    Any,
    cast,
)
from typing_extensions import TypeVar, Unpack, TypedDict

from ..._identifiers import ResourceIdentifiers
from ...._bicep.expressions import Output, Parameter, ResourceSymbol
from ...._bicep.utils import clean_name
from ...._resource import Resource, ExtensionResources, ResourceReference
from .. import ConfigStore


if TYPE_CHECKING:
    from ...resourcegroup import ResourceGroup
    from .types import ConfigSettingResource


class ConfigSettingKwargs(TypedDict, total=False):
    content_type: Union[str, Parameter]
    """The content type of the key-value's value. Providing a proper content-type can enable
    transformations of values when they are retrieved by applications.
    """
    tags: Union[Dict[str, Union[str, Parameter]], Parameter]
    """A dictionary of tags that can help identify what a key-value may be applicable for."""


_DEFAULT_CONFIG_SETTING: "ConfigSettingResource" = {}
_DEFAULT_CONFIG_SETTING_EXTENSIONS: ExtensionResources = {}
ConfigSettingResourceType = TypeVar(
    "ConfigSettingResourceType", bound=Mapping[str, Any], default="ConfigSettingResource"
)


class ConfigSetting(Resource, Generic[ConfigSettingResourceType]):
    DEFAULTS: "ConfigSettingResource" = _DEFAULT_CONFIG_SETTING  # type: ignore[assignment]
    DEFAULT_EXTENSIONS: ExtensionResources = _DEFAULT_CONFIG_SETTING_EXTENSIONS
    properties: ConfigSettingResourceType
    parent: ConfigStore  # type: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        properties: Optional["ConfigSettingResource"] = None,
        /,
        name: Optional[Union[str, Parameter]] = None,
        value: Optional[Union[str, Parameter]] = None,
        store: Optional[Union[str, Parameter, ConfigStore]] = None,
        **kwargs: Unpack["ConfigSettingKwargs"],
    ) -> None:
        # 'existing' is passed by the reference classmethod.
        existing = kwargs.pop("existing", False)  # type: ignore[typeddict-item]
        if isinstance(store, ConfigStore):
            parent = store
        else:
            # 'parent' is passed by the reference classmethod.
            parent = kwargs.pop("parent", ConfigStore(name=store))  # type: ignore[typeddict-item]
        properties = properties or {}
        if name:
            properties["name"] = name
        if not existing:
            if "properties" not in properties:
                properties["properties"] = {}
            if "name" not in properties:
                raise ValueError("Missing required property: 'name'.")
            if value:
                properties["properties"]["value"] = value
            elif "value" not in properties["properties"]:
                raise ValueError("Missing required property: 'value'.")
            if "tags" in kwargs:
                properties["properties"]["tags"] = kwargs.pop("tags")
            if "content_type" in kwargs:
                properties["properties"]["contentType"] = kwargs.pop("content_type")

        super().__init__(
            properties,
            existing=existing,
            parent=parent,
            subresource="keyValues",
            service_prefix=["appconfig_setting"],
            identifier=ResourceIdentifiers.config_setting,
            **kwargs,
        )

    @property
    def resource(self) -> Literal["Microsoft.AppConfiguration/configurationStores/keyValues"]:
        return "Microsoft.AppConfiguration/configurationStores/keyValues"

    @property
    def version(self) -> str:
        from .types import VERSION

        return VERSION

    @classmethod
    def reference(  # type: ignore[override]  # Parameter subset and renames
        cls,
        *,
        name: Union[str, Parameter],
        store: Optional[Union[str, Parameter, ConfigStore[ResourceReference]]] = None,
        resource_group: Optional[Union[str, Parameter, "ResourceGroup[ResourceReference]"]] = None,
    ) -> "ConfigSetting[ResourceReference]":
        parent: Optional[ConfigStore[ResourceReference]] = None
        if isinstance(store, (str, Parameter)):
            parent = ConfigStore.reference(
                name=store,
                resource_group=resource_group,
            )
        else:
            parent = store
        # Here the "value" param will be ignored because existing=True, so just set to empty str.
        existing = super().reference(name=name, parent=parent)
        return cast(ConfigSetting[ResourceReference], existing)

    def _build_symbol(self, suffix: Optional[Union[str, Parameter]]) -> ResourceSymbol:
        suffix_str = ""
        account_name = self.parent.properties.get("name")
        if account_name:
            suffix_str += f"_{clean_name(account_name).lower()}"
        if suffix:
            suffix_str += f"_{clean_name(suffix).lower()}"
        return ResourceSymbol(f"keyvalue{suffix_str}")

    def _outputs(self, **kwargs) -> Dict[str, List[Output]]:
        return {}
