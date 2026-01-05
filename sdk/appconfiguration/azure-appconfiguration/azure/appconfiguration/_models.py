# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import collections
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast, Callable, TypeVar, Iterator, AsyncIterator

from azure.core import MatchConditions
from azure.core.exceptions import AzureError
from azure.core.rest import HttpResponse
from azure.core.paging import PageIterator, ItemPaged
from azure.core.async_paging import AsyncPageIterator, AsyncItemPaged, AsyncList
from ._generated._serialization import Model
from ._generated.models import (
    KeyValue,
    KeyValueFilter,
    Snapshot as GeneratedConfigurationSnapshot,
    SnapshotStatus,
    SnapshotComposition,
)
from ._generated._model_base import _deserialize

ReturnType = TypeVar("ReturnType")


class ConfigurationSetting(Model):
    """A setting, defined by a unique combination of a key and label."""

    value: str
    """The value of the configuration setting."""
    etag: str
    """A value representing the current state of the resource."""
    key: str
    """The key of the configuration setting."""
    label: str
    """The label of the configuration setting."""
    content_type: Optional[str]
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }

    kind = "Generic"
    content_type = None

    def __init__(self, **kwargs: Any) -> None:
        super(ConfigurationSetting, self).__init__(**kwargs)
        self.key = kwargs.get("key", None)
        self.label = kwargs.get("label", None)
        self.value = kwargs.get("value", None)
        self.etag = kwargs.get("etag", None)
        self.content_type = kwargs.get("content_type", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "ConfigurationSetting":
        # pylint:disable=protected-access
        if key_value.content_type is not None:
            try:
                if key_value.content_type.startswith(
                    FeatureFlagConfigurationSetting._feature_flag_content_type
                ) and key_value.key.startswith(  # type: ignore
                    FeatureFlagConfigurationSetting._key_prefix
                ):
                    config_setting = FeatureFlagConfigurationSetting._from_generated(key_value)
                    if key_value.value:
                        config_setting.value = key_value.value
                    return config_setting
                if key_value.content_type.startswith(
                    SecretReferenceConfigurationSetting._secret_reference_content_type
                ):
                    return SecretReferenceConfigurationSetting._from_generated(key_value)
            except (KeyError, AttributeError):
                pass

        return cls(
            key=key_value.key,
            label=key_value.label,
            value=key_value.value,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )


class FeatureFlagConfigurationSetting(ConfigurationSetting):  # pylint: disable=too-many-instance-attributes
    """A configuration setting that stores a feature flag value."""

    etag: str
    """A value representing the current state of the resource."""
    feature_id: str
    """The identity of the configuration setting."""
    key: str
    """The key of the configuration setting."""
    enabled: bool
    """The value indicating whether the feature flag is enabled. A feature is OFF if enabled is false.
        If enabled is true, then the feature is ON if there are no conditions or if all conditions are satisfied."""
    filters: Optional[List[Dict[str, Any]]]
    """Filters that must run on the client and be evaluated as true for the feature
        to be considered enabled."""
    label: str
    """The label used to group this configuration setting with others."""
    display_name: str
    """The name for the feature to use for display rather than the ID."""
    description: str
    """The description of the feature."""
    content_type: str
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "feature_id": {"key": "feature_id", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "_feature_flag_content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }
    _key_prefix = ".appconfig.featureflag/"
    _feature_flag_content_type = "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"
    kind = "FeatureFlag"

    def __init__(  # pylint: disable=super-init-not-called
        self,
        feature_id: str,
        *,
        enabled: bool = False,
        filters: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        """
        :param feature_id: The identity of the configuration setting.
        :type feature_id: str
        :keyword enabled: The value indicating whether the feature flag is enabled.
            A feature is OFF if enabled is false. If enabled is true, then the feature is ON
            if there are no conditions or if all conditions are satisfied. Default value of this property is False.
        :paramtype enabled: bool
        :keyword filters: Filters that must run on the client and be evaluated as true for the feature
            to be considered enabled.
        :paramtype filters: list[dict[str, Any]] or None
        """
        if "value" in kwargs:
            raise TypeError("Unexpected keyword argument, do not provide 'value' as a keyword-arg")
        self.feature_id = feature_id
        self.key = kwargs.get("key", None) or (self._key_prefix + self.feature_id)
        self.label = kwargs.get("label", None)
        self.content_type = kwargs.get("content_type", self._feature_flag_content_type)
        self.last_modified = kwargs.get("last_modified", None)
        self.tags = kwargs.get("tags", {})
        self.read_only = kwargs.get("read_only", None)
        self.etag = kwargs.get("etag", None)
        self.description = kwargs.get("description", None)
        self.display_name = kwargs.get("display_name", None)
        self.filters = [] if filters is None else filters
        self.enabled = enabled
        self._value = json.dumps(
            {"id": self.feature_id, "enabled": self.enabled, "conditions": {"client_filters": self.filters}}
        )

    @property
    def value(self) -> str:
        """The value of the configuration setting.

        :rtype: str
        """
        try:
            temp = json.loads(self._value)
            temp["id"] = self.feature_id
            temp["enabled"] = self.enabled
            temp["display_name"] = self.display_name
            temp["description"] = self.description
            if "conditions" not in temp.keys():
                temp["conditions"] = {}
            temp["conditions"]["client_filters"] = self.filters
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        try:
            temp = json.loads(new_value)
            temp["id"] = self.feature_id
            self._value = json.dumps(temp)
            self.enabled = temp.get("enabled", False)
            self.display_name = temp.get("display_name", None)
            self.description = temp.get("description", None)
            self.filters = None
            conditions = temp.get("conditions", None)
            if conditions:
                self.filters = conditions.get("client_filters", None)
        except (json.JSONDecodeError, ValueError):
            self._value = new_value
            self.enabled = False
            self.filters = None

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "FeatureFlagConfigurationSetting":
        enabled = False
        filters = None
        display_name = None
        description = None
        feature_id = None
        try:
            temp = json.loads(key_value.value)  # type: ignore
            if isinstance(temp, dict):
                enabled = temp.get("enabled", False)
                display_name = temp.get("display_name")
                description = temp.get("description")
                feature_id = temp.get("id")

                if "conditions" in temp.keys():
                    filters = temp["conditions"].get("client_filters")
        except (ValueError, json.JSONDecodeError):
            pass

        return cls(
            feature_id=feature_id,  # type: ignore
            key=key_value.key,
            label=key_value.label,
            content_type=key_value.content_type,
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
            enabled=enabled,
            filters=filters,
            display_name=display_name,
            description=description,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )


class SecretReferenceConfigurationSetting(ConfigurationSetting):
    """A configuration value that references a configuration setting secret."""

    etag: str
    """A value representing the current state of the resource."""
    key: str
    """The key of the configuration setting."""
    secret_id: Optional[str]
    """The identity of the configuration setting."""
    label: str
    """The label used to group this configuration setting with others."""
    content_type: str
    """The content_type of the configuration setting."""
    last_modified: datetime
    """A date representing the last time the key-value was modified."""
    read_only: bool
    """Indicates whether the key-value is locked."""
    tags: Dict[str, str]
    """The tags assigned to the configuration setting."""

    _attribute_map = {
        "etag": {"key": "etag", "type": "str"},
        "key": {"key": "key", "type": "str"},
        "label": {"key": "label", "type": "str"},
        "content_type": {"key": "content_type", "type": "str"},
        "value": {"key": "value", "type": "str"},
        "last_modified": {"key": "last_modified", "type": "iso-8601"},
        "read_only": {"key": "read_only", "type": "bool"},
        "tags": {"key": "tags", "type": "{str}"},
    }
    _secret_reference_content_type = "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8"
    kind = "SecretReference"

    def __init__(self, key: str, secret_id: str, **kwargs: Any) -> None:  # pylint: disable=super-init-not-called
        """
        :param key: The key of the configuration setting.
        :type key: str
        :param secret_id: The identity of the configuration setting.
        :type secret_id: str
        """
        if "value" in kwargs:
            raise TypeError("Unexpected keyword argument, do not provide 'value' as a keyword-arg")
        self.key = key
        self.label = kwargs.pop("label", None)
        self.content_type = kwargs.get("content_type", self._secret_reference_content_type)
        self.etag = kwargs.get("etag", None)
        self.last_modified = kwargs.get("last_modified", None)
        self.read_only = kwargs.get("read_only", None)
        self.tags = kwargs.get("tags", {})
        self.secret_id = secret_id
        self._value = json.dumps({"uri": secret_id})

    @property
    def value(self) -> str:
        """The value of the configuration setting.

        :rtype: str
        """
        try:
            temp = json.loads(self._value)
            temp["uri"] = self.secret_id
            self._value = json.dumps(temp)
            return self._value
        except (json.JSONDecodeError, ValueError):
            return self._value

    @value.setter
    def value(self, new_value: str) -> None:
        try:
            temp = json.loads(new_value)
            self._value = new_value
            self.secret_id = temp.get("uri")
        except (json.JSONDecodeError, ValueError):
            self._value = new_value
            self.secret_id = None

    @classmethod
    def _from_generated(cls, key_value: KeyValue) -> "SecretReferenceConfigurationSetting":
        secret_uri = None
        try:
            temp = json.loads(key_value.value)  # type: ignore
            secret_uri = temp.get("uri")
            if not secret_uri:
                secret_uri = temp.get("secret_uri")
        except (ValueError, json.JSONDecodeError):
            pass

        return cls(
            key=key_value.key,  # type: ignore
            label=key_value.label,
            secret_id=secret_uri,  # type: ignore
            last_modified=key_value.last_modified,
            tags=key_value.tags,
            read_only=key_value.locked,
            etag=key_value.etag,
        )

    def _to_generated(self) -> KeyValue:
        return KeyValue(
            key=self.key,
            label=self.label,
            value=self.value,
            content_type=self.content_type,
            last_modified=self.last_modified,
            tags=self.tags,
            locked=self.read_only,
            etag=self.etag,
        )


class ConfigurationSettingsFilter:
    """Enables filtering of configuration settings."""

    key: str
    """Filters configuration settings by their key field. Required."""
    label: Optional[str]
    """Filters configuration settings by their label field."""
    tags: Optional[List[str]]
    """Filters key-values by their tags field."""

    def __init__(self, *, key: str, label: Optional[str] = None, tags: Optional[List[str]] = None) -> None:
        """
        :keyword key: Filters configuration settings by their key field. Required.
        :paramtype key: str
        :keyword label: Filters configuration settings by their label field.
        :paramtype label: str or None
        :keyword tags: Filters key-values by their tags field.
        :paramtype tags: list[str] or None
        """
        self.key = key
        self.label = label
        self.tags = tags


class ConfigurationSnapshot:  # pylint: disable=too-many-instance-attributes
    """A point-in-time snapshot of configuration settings."""

    name: Optional[str]
    """The name of the configuration snapshot."""
    status: Optional[Union[str, SnapshotStatus]]
    """The current status of the snapshot. Known values are: "provisioning", "ready",
        "archived", and "failed"."""
    filters: List[ConfigurationSettingsFilter]
    """A list of filters used to filter the key-values included in the configuration snapshot. Required."""
    composition_type: Optional[Union[str, SnapshotComposition]]
    """The composition type describes how the key-values within the configuration snapshot
        are composed. The 'key' composition type ensures there are no two key-values containing the
        same key. The 'key_label' composition type ensures there are no two key-values containing the
        same key and label. Known values are: "key" and "key_label"."""
    created: Optional[datetime]
    """The time that the configuration snapshot was created."""
    expires: Optional[datetime]
    """The time that the configuration snapshot will expire."""
    retention_period: Optional[int]
    """The amount of time, in seconds, that a configuration snapshot will remain in the
        archived state before expiring. This property is only writable during the creation of a configuration
        snapshot. If not specified, the default lifetime of key-value revisions will be used."""
    size: Optional[int]
    """The size in bytes of the configuration snapshot."""
    items_count: Optional[int]
    """The amount of key-values in the configuration snapshot."""
    tags: Optional[Dict[str, str]]
    """The tags of the configuration snapshot."""
    etag: Optional[str]
    """A value representing the current state of the configuration snapshot."""

    def __init__(
        self,
        filters: List[ConfigurationSettingsFilter],
        *,
        composition_type: Optional[Union[str, SnapshotComposition]] = None,
        retention_period: Optional[int] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        :param filters: A list of filters used to filter the key-values included in the configuration snapshot.
            Required.
        :type filters: list[~azure.appconfiguration.ConfigurationSettingsFilter]
        :keyword composition_type: The composition type describes how the key-values within the configuration
            snapshot are composed. The 'key' composition type ensures there are no two key-values
            containing the same key. The 'key_label' composition type ensures there are no two key-values
            containing the same key and label. Known values are: "key" and "key_label".
        :paramtype composition_type: str or None
        :keyword retention_period: The amount of time, in seconds, that a configuration snapshot will remain in the
            archived state before expiring. This property is only writable during the creation of a configuration
            snapshot. If not specified, the default lifetime of key-value revisions will be used.
        :paramtype retention_period: int or None
        :keyword tags: The tags of the configuration snapshot.
        :paramtype tags: dict[str, str] or None
        """
        self.name = None
        self.status = None
        self.filters = filters
        self.composition_type = composition_type
        self.created = None
        self.expires = None
        self.retention_period = retention_period
        self.size = None
        self.items_count = None
        self.tags = tags
        self.etag = None

    @classmethod
    def _from_generated(cls, generated: GeneratedConfigurationSnapshot) -> "ConfigurationSnapshot":
        if generated is None:
            return generated

        filters = []
        if generated.filters:
            for config_setting_filter in generated.filters:
                filters.append(
                    ConfigurationSettingsFilter(
                        key=config_setting_filter.key,
                        label=config_setting_filter.label,
                        tags=config_setting_filter.tags,
                    )
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(SnapshotComposition, generated.composition_type),
            retention_period=generated.retention_period,
            tags=generated.tags,
        )
        snapshot.name = generated.name
        snapshot.status = generated.status
        snapshot.created = generated.created
        snapshot.expires = generated.expires
        snapshot.size = generated.size
        snapshot.items_count = generated.items_count
        snapshot.etag = generated.etag

        return snapshot

    @classmethod
    def _from_deserialized(
        cls,
        response: HttpResponse,  # pylint:disable=unused-argument
        deserialized: GeneratedConfigurationSnapshot,
        response_headers: Dict,  # pylint:disable=unused-argument
    ) -> "ConfigurationSnapshot":
        if deserialized is None:
            return deserialized
        filters = []
        if deserialized.filters:
            for config_setting_filter in deserialized.filters:
                filters.append(
                    ConfigurationSettingsFilter(
                        key=config_setting_filter.key,
                        label=config_setting_filter.label,
                        tags=config_setting_filter.tags,
                    )
                )
        snapshot = cls(
            filters=filters,
            composition_type=cast(SnapshotComposition, deserialized.composition_type),
            retention_period=deserialized.retention_period,
            tags=deserialized.tags,
        )
        snapshot.name = deserialized.name
        snapshot.status = deserialized.status
        snapshot.created = deserialized.created
        snapshot.expires = deserialized.expires
        snapshot.size = deserialized.size
        snapshot.items_count = deserialized.items_count
        snapshot.etag = deserialized.etag

        return snapshot

    def _to_generated(self) -> GeneratedConfigurationSnapshot:
        config_setting_filters = []
        for kv_filter in self.filters:
            config_setting_filters.append(KeyValueFilter(key=kv_filter.key, label=kv_filter.label, tags=kv_filter.tags))
        return GeneratedConfigurationSnapshot(
            filters=config_setting_filters,
            composition_type=self.composition_type,
            retention_period=self.retention_period,
            tags=self.tags,
        )


class ConfigurationSettingLabel:
    """The label info of a configuration setting."""

    name: Optional[str]
    """The name of the ConfigurationSetting label."""

    def __init__(self, *, name: Optional[str] = None) -> None:
        """
        :keyword name: The configuration setting label name.
        :paramtype composition_type: str or None
        """
        self.name = name


def _return_deserialized_and_headers(_, deserialized, response_headers):
    return deserialized, response_headers


class ConfigurationSettingPropertiesPagedBase:  # pylint:disable=too-many-instance-attributes
    """Base class for iterable of ConfigurationSetting properties."""

    etag: str
    """The current etag"""
    _etags: List[str]
    """The etag expected for the pages."""
    _current_etag: int = 0
    """Current index in the etags list."""

    def __init__(self, command: Callable, **kwargs: Any):
        """Initialize common attributes for paged configuration settings.

        :param command: The command to execute for pagination.
        :type command: Callable
        """
        self._command = command
        self._key = kwargs.get("key")
        self._label = kwargs.get("label")
        self._accept_datetime = kwargs.get("accept_datetime")
        self._select = kwargs.get("select")
        self._tags = kwargs.get("tags")
        self._etags: List[str] = kwargs.get("etags", [])
        self._current_etag = 0
        self._match_condition = kwargs.get("match_condition")
        self._deserializer = lambda objs: [
            ConfigurationSetting._from_generated(x) for x in objs  # pylint:disable=protected-access
        ]

    def _next_etag(self):
        etag = None
        if self._etags and len(self._etags) > self._current_etag:
            etag = self._etags[self._current_etag]
            self._current_etag += 1
        return etag

    def _extract_data_cb_base(self, get_next_return):
        deserialized, response_headers = get_next_return
        self.etag = response_headers.get("ETag", self._etags[self._current_etag - 1] if self._etags else None)
        next_link = deserialized.get("@nextLink") or None
        page = None
        if "items" in deserialized:
            list_of_elem = _deserialize(List[KeyValue], deserialized["items"])
            page = iter(self._deserializer(list_of_elem))
        return next_link, page


class ConfigurationSettingPropertiesPaged(
    ConfigurationSettingPropertiesPagedBase, PageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of ConfigurationSetting properties."""

    def __init__(self, command: Callable, **kwargs: Any):
        super().__init__(command, **kwargs)
        PageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return self._command(
            key=self._key,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    def __next__(self) -> Iterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        if self.continuation_token is None and self._did_a_call_already:
            raise StopIteration("End of paging")
        try:
            self._response = self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = self._extract_data(self._response)
        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return self.__next__()
        return iter(self._current_page)


class ConfigurationSettingPropertiesPagedAsync(
    ConfigurationSettingPropertiesPagedBase, AsyncPageIterator
):  # pylint:disable=too-many-instance-attributes
    """An iterable of ConfigurationSetting properties."""

    def __init__(self, command: Callable, **kwargs: Any):
        ConfigurationSettingPropertiesPagedBase.__init__(self, command, **kwargs)
        AsyncPageIterator.__init__(
            self,
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=kwargs.get("continuation_token"),
        )

    async def _get_next_cb(self, continuation_token, **kwargs):
        etag = self._next_etag()
        return await self._command(
            key=self._key,
            label=self._label,
            accept_datetime=self._accept_datetime,
            select=self._select,
            tags=self._tags,
            etag=etag,
            match_condition=self._match_condition,
            continuation_token=continuation_token,
            cls=kwargs.pop("cls", None) or _return_deserialized_and_headers,
        )

    async def _extract_data_cb(self, get_next_return):
        return self._extract_data_cb_base(get_next_return)

    async def __anext__(self) -> AsyncIterator[ReturnType]:
        """Get the next page in the iterator.

        :returns: An iterator of objects in the next page.
        :rtype: iterator[ReturnType]
        :raises StopIteration: If there are no more pages to return.
        :raises AzureError: If the request fails.
        """
        if self.continuation_token is None and self._did_a_call_already:
            raise StopAsyncIteration("End of paging")
        try:
            self._response = await self._get_next(self.continuation_token)
        except AzureError as error:
            if not error.continuation_token:
                error.continuation_token = self.continuation_token
            raise

        self._did_a_call_already = True

        self.continuation_token, self._current_page = await self._extract_data(self._response)

        if self._current_page is None:
            # We skip over pages that are empty, change from mach conditions
            return await self.__anext__()

        # If current_page was a sync list, wrap it async-like
        if isinstance(self._current_page, collections.abc.Iterable):
            self._current_page = AsyncList(self._current_page)

        return self._current_page


class ConfigurationSettingPaged(ItemPaged):
    """
    An iterable of ConfigurationSettings that supports etag-based change detection.

    This class extends ItemPaged to provide efficient monitoring of configuration changes
    by using ETags. When used with the `match_conditions` parameter in `by_page()`,
    it only returns pages that have changed since the provided ETags were collected.

    Example:
        # Get initial page ETags
        items = client.list_configuration_settings(key_filter="sample_*")
        match_conditions = [page.etag for page in items.by_page()]

        # Later, check for changes - only changed pages are returned
        items = client.list_configuration_settings(key_filter="sample_*")
        for page in items.by_page(match_conditions=match_conditions):
             # Process only changed pages
             pass
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An iterator of pages (themselves iterator of objects)
        :rtype: iterator[iterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)


class ConfigurationSettingPagedAsync(AsyncItemPaged):
    """
    An async iterable of ConfigurationSettings that supports etag-based change detection.

    This class provides asynchronous iteration over configuration settings, with optional support for
    etag-based change detection. By supplying a list of etags via the `match_conditions` parameter to
    the `by_page` method, you can efficiently detect and retrieve only those pages that have changed
    since your last retrieval.

    Example usage:

        async for setting in ConfigurationSettingPagedAsync(...):
            # Process each setting asynchronously
            print(setting)

        # To iterate by page and use etag-based change detection:
        etags = ["etag1", "etag2", "etag3"]
        async for page in paged.by_page(match_conditions=etags):
            async for setting in page:
                print(setting)

    When `match_conditions` is provided, each page is checked against the corresponding etag.
    If the page has not changed (HTTP 304), it is skipped. If the page has changed (HTTP 200),
    the new page is returned. This allows efficient polling for changes without retrieving
    unchanged data.
    """

    def by_page(self, continuation_token: Optional[str] = None, *, match_conditions: Optional[List[str]] = None) -> Any:
        """Get an async iterator of pages of objects, instead of an iterator of objects.

        :param str continuation_token:
            An opaque continuation token. This value can be retrieved from the
            continuation_token field of a previous generator object. If specified,
            this generator will begin returning results from this point.
        :keyword match_conditions: A list of etags to check for changes. If provided, the iterator will
            check each page against the corresponding etag and only return pages that have changed.
        :paramtype match_conditions: list[str] or None
        :returns: An async iterator of pages (themselves iterator of objects)
        :rtype: AsyncIterator[AsyncIterator[ReturnType]]
        """
        if "match_conditions" not in self._kwargs and match_conditions:
            self._kwargs["etags"] = match_conditions
            self._kwargs["match_condition"] = MatchConditions.IfModified
        return self._page_iterator_class(continuation_token=continuation_token, *self._args, **self._kwargs)
