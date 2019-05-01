# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from abc import abstractmethod
import re
from datetime import datetime
from requests.structures import CaseInsensitiveDict
from msrest.paging import Paged
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
)
from ._generated.models import ConfigurationSetting


class AzureConfigurationClientAbstract(object):
    """Represents an client that calls restful API of Azure App Configuration service.

    :param connection_string: Connection String (one of the access keys of the Azure App Configuration resource)
        used to access the Azure App Configuration.
    :type connection_string: str

    """

    def __init__(self):
        self._impl = None  # to be set by subclass
        self._config = None

    @abstractmethod
    def list_configuration_settings(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        # type: (list, list, datetime, list, dict) -> Paged

        """List the configuration settings stored in the configuration service, optionally filtered by
        label and accept_date_time

        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param accept_date_time: filter out ConfigurationSetting created after this datetime
        :type accept_date_time: datetime
        :param fields: specify which fields to include in the results. Leave None to include all fields
        :type fields: list[str]
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`Paged`
        :raises: :class:`HttpRequestError`

        """
        labels = AzureConfigurationClientAbstract.escape_and_tolist(labels)
        keys = AzureConfigurationClientAbstract.escape_and_tolist(keys)
        return self._impl.list_configuration_settings(
            label=labels,
            key=keys,
            fields=fields,
            accept_date_time=accept_date_time,
            headers=kwargs.get("headers"),
        )

    @abstractmethod
    def get_configuration_setting(
        self, key, label=None, accept_date_time=None, **kwargs
    ):
        # type: (str, str, datetime, dict) -> ConfigurationSetting

        """Get the matched ConfigurationSetting from Azure App Configuration service

        :param key: key of the ConfigurationSetting
        :type key: str
        :param label: label of the ConfigurationSetting
        :type label: str
        :param accept_date_time: The retrieved ConfigurationSetting must be created no later than this datetime
        :type accept_date_time: datetime
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The matched ConfigurationSetting object
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceNotFoundError`, :class:`HttpRequestError`

        """
        error_map = {404: ResourceNotFoundError, 412: ResourceNotFoundError}
        return self._impl.get_configuration_setting(
            key=key,
            label=label,
            accept_date_time=accept_date_time,
            headers=kwargs.get("headers"),
            error_map=error_map,
        )

    @abstractmethod
    def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add a ConfigurationSetting into the Azure App Configuration service.

        :param configuration_setting: the ConfigurationSetting object to be added
        :type configuration_setting: :class:`ConfigurationSetting<azure.configuration.ConfigurationSetting>`
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting object returned from the App Configuration service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceExistsError`, :class:`HttpRequestError`

        """

        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        custom_headers["if-none-match"] = "*"
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            headers=custom_headers,
            error_map={412: ResourceExistsError},
        )

    @abstractmethod
    def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):
        # type: (str, str, str, dict, str, str, dict) -> ConfigurationSetting
        """Update specified attributes of the ConfigurationSetting

        :param key: key used to identify the ConfigurationSetting
        :param value: the value to be updated to the ConfigurationSetting. None means unchanged.
        :param content_type: the content type to be updated to the ConfigurationSetting. None means unchanged.
        :param tags: tags to be updated to the ConfigurationSetting. None means unchanged.
        :param label: lable used together with key to identify the ConfigurationSetting.
        :param etag: the ETag (http entity tag) of the ConfigurationSetting.
            Used to check if the configuration setting has changed. Leave None to skip the check.
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceNotFoundError`, :class:`ResourceModifiedError`, :class:`HttpRequestError`

        """
        pass

    @abstractmethod
    def set_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add or update a ConfigurationSetting.
        If the configuration setting identified by key and label does not exist, this is a create.
        Otherwise this is an update.

        :param configuration_setting: the ConfigurationSetting to be added (if not exists) or updated (if exists) to the service
        :type configuration_setting: :class:`ConfigurationSetting`
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :type kwargs: dict
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceModifiedError`, :class:`HttpRequestError`

        """
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        etag = configuration_setting.etag
        if etag:
            custom_headers["if-match"] = AzureConfigurationClientAbstract.quote_etag(
                etag
            )
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            headers=custom_headers,
            error_map={412: ResourceModifiedError},
        )

    @abstractmethod
    def delete_configuration_setting(self, key, label=None, etag=None, **kwargs):
        # type: (str, str, str, dict) -> ConfigurationSetting

        """Delete a ConfigurationSetting if it exists

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param label: label used to identify the ConfigurationSetting
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request
        :type kwargs: dict
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`ResourceNotFoundError`, :class:`ResourceModifiedError`, :class:`HttpRequestError`

        """
        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        if etag:
            custom_headers["if-match"] = AzureConfigurationClientAbstract.quote_etag(
                etag
            )
        return self._impl.delete_configuration_setting(
            key=key,
            label=label,
            headers=custom_headers,
            error_map={
                404: ResourceNotFoundError,  # 404 doesn't happen actually. return None if no match
                412: ResourceModifiedError,
            },
        )

    @abstractmethod
    def list_revisions(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        # type: (list, list, datetime, list, dict) -> Paged

        """
        Find the ConfigurationSetting revision history.

        :param labels: filter results based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: filter results based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param accept_date_time: filter out ConfigurationSetting created after this datetime
        :type accept_date_time: datetime
        :param fields: specify which fields to include in the results. Leave None to include all fields
        :type fields: list[str]
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: An iterator of :class:`ConfigurationSetting`
        :rtype: :class:`Paged`
        :raises: :class:`HttpRequestError`

        """

        labels = AzureConfigurationClientAbstract.escape_and_tolist(labels)
        keys = AzureConfigurationClientAbstract.escape_and_tolist(keys)
        return self._impl.list_revisions(
            label=labels,
            key=keys,
            fields=fields,
            accept_date_time=accept_date_time,
            headers=kwargs.get("headers"),
        )

    @staticmethod
    def prep_update_configuration_setting(key, etag=None, **kwargs):
        # type: (str, str, dict) -> CaseInsensitiveDict
        if not key:
            raise ValueError("key is mandatory to update a ConfigurationSetting")

        custom_headers = CaseInsensitiveDict(kwargs.get("headers"))
        if etag:
            custom_headers["if-match"] = AzureConfigurationClientAbstract.quote_etag(
                etag
            )
        elif "if-match" not in custom_headers:
            custom_headers["if-match"] = "*"

        return custom_headers

    @staticmethod
    def quote_etag(etag):
        if etag != "*" and etag is not None:
            return '"' + etag + '"'
        else:
            return etag

    @staticmethod
    def escape_reserved(value):
        """
        Reserved characters are star(*), comma(,) and backslash(\\)
        If a reserved character is part of the value, then it must be escaped using \\{Reserved Character}.
        Non-reserved characters can also be escaped.

        """
        if value is None:
            return None
        elif value == "":
            return "\0"  # '\0' will be encoded to %00 in the url.
        else:
            if isinstance(value, list):
                return [
                    AzureConfigurationClientAbstract.escape_reserved(s) for s in value
                ]
            else:
                value = str(value)  # value is unicode for Python 2.7
                # precede all reserved characters with a backslash.
                # But if a * is at the beginning or the end, don't add the backslash
                return re.sub(r"((?!^)\*(?!$)|\\|,)", r"\\\1", value)

    @staticmethod
    def escape_and_tolist(value):
        if value is not None:
            if isinstance(value, str):
                value = [value]
            value = AzureConfigurationClientAbstract.escape_reserved(value)
        return value
