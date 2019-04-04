# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime

from msrest.pipeline.requests import PipelineRequestsHTTPSender, RequestsPatchSession
from msrest.pipeline import Request, Pipeline
from msrest.universal_http.requests import RequestsHTTPSender

from . import _generated
from ._generated.models import ConfigurationSettingPaged, ConfigurationSetting

from .azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from .azure_configuration_client_prep import *
from .utils import get_endpoint_from_connection_string


class AzureConfigurationClient(object):
    """
    Represents an client that calls restful API of Azure App Configuration service

    :param connection_string: Connection String used to access the Azure App Configuration. Looks like "Endpoint= \
     https://appconfigname.azconfig.io;Id=1-l1-s0:gLY4fS/9qc8tXKudKsH6;Secret=c333C5sWw5B7PIDQeE8vd6k38SQFxiRbsTN0VmbjxfQ="
    :type connection_string: str

    Example

    .. literalinclude:: ../examples/test_example_configurationservice.py
        :start-after: [START create_app_configuration_client]
        :end-before: [END create_app_configuration_client]
        :language: python
        :dedent: 4
        :caption: Create an Azure configuration client
    """

    def __init__(self, connection_string):

        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        self._client = _generated.AzureConfigurationClientImp(
            connection_string, base_url
        )
        self._client._client.config.pipeline = self._create_azconfig_pipeline()

    def _create_azconfig_pipeline(self):
        policies = [
            self._client.config.user_agent_policy,  # UserAgent policy
            RequestsPatchSession(),  # Support deprecated operation config at the session level
            self._client.config.http_logger_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self._client.config),
        ]

        return Pipeline(
            policies,
            PipelineRequestsHTTPSender(
                RequestsHTTPSender(self._client.config)
            ),  # Send HTTP request using requests
        )

    def list_configuration_settings(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        # type: (list, list, datetime, list, dict) -> ConfigurationSettingPaged

        """
        List the configuration settings stored in the configuration service, optionally filtered by
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
        :rtype: :class:`ConfigurationSettingPaged`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START list_configuration_setting]
            :end-before: [END list_configuration_setting]
            :language: python
            :dedent: 4
            :caption: List ConfigurationService
        """
        return self._client.list_configuration_settings(
            label=labels,
            key=keys,
            fields=fields,
            accept_date_time=accept_date_time,
            custom_headers=kwargs.get("headers"),
        )

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
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`


        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START get_configuration_setting]
            :end-before: [END get_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Get a ConfigurationSetting
        """

        custom_headers = prep_get_configuration_setting(key, **kwargs)

        return self._client.get_configuration_setting(
            key=key,
            label=label,
            accept_date_time=accept_date_time,
            custom_headers=custom_headers,
        )

    def add_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """Add a ConfigurationSetting into the Azure App Configuration service.
        Exception is raised if it already exists.

        .. seealso::
            :meth:`set_configuration_setting`

        :param configuration_setting:
        :type configuration_setting: :class:`ConfigurationSetting<azure.configuration.ConfigurationSetting>`
        :param dict kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :return: The ConfigurationSetting object returned from the App Configuration service.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example:

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START add_configuration_setting]
            :end-before: [END add_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Add a new ConfigurationService
        """


        custom_headers = prep_add_configuration_setting(configuration_setting, **kwargs)
        return self._client.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            custom_headers=custom_headers,
        )

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

        """
        Partially update a ConfigurationSetting.
        Exception is raised if it doesn't exist.

        .. seealso::
            :meth:`set_configuration_setting`

        :param key: key used to identify the ConfigurationSetting
        :type key: str
        :param value: value to be set to the ConfigurationSetting
        :type value: str
        :param content_type: content_type to be set to the ConfigurationSetting
        :type content_type: str
        :param tags: tags to be set to the ConfigurationSetting
        :type tags: dict
        :param label: label used to identify the ConfigurationSetting
        :type label: str
        :param etag: etag used to check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str
        :param dict kwargs: if “headers” exists, its value (a dict) will be added to the http request 
        :return: The updated ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START update_configuration_setting]
            :end-before: [END update_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Update some attributes of ConfigurationService
        """

        custom_headers = prep_update_configuration_setting(key, etag, **kwargs)

        current_configuration_setting = self._client.get_configuration_setting(
            key, label
        )
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return self._client.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            custom_headers=custom_headers,
        )

    def set_configuration_setting(self, configuration_setting, **kwargs):
        # type: (ConfigurationSetting, dict) -> ConfigurationSetting

        """
        Set a ConfigurationSetting. If the ConfigurationSetting already exists, it gets updated. Otherwise a new one is added.

        .. seealso::
            :meth:`update_configuration_setting`
            :meth:`add_configuration_setting`

        :param configuration_setting: the ConfigurationSetting to be added (if not exists) or updated (if exists) to the service
        :type configuration_setting: :class:`ConfigurationSetting`
        :param kwargs: if "headers" exists, its value (a dict) will be added to the http request header
        :type kwargs: dict
        :return: The ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START set_configuration_setting]
            :end-before: [END set_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Set a ConfigurationSetting
        """
        custom_headers = prep_set_configuration_setting(configuration_setting, **kwargs)
        return self._client.create_or_update_configuration_setting(
            configuration_setting=configuration_setting,
            key=configuration_setting.key,
            label=configuration_setting.label,
            custom_headers=custom_headers,
        )

    def delete_configuration_setting(self, key, label=None, etag=None, **kwargs):
        # type: (str, str, str, dict) -> ConfigurationSetting

        """
        Delete a ConfigurationSetting if it exists. Otherwise raise an exception.

        :param key: identify the ConfigurationSetting
        :type key: str
        :param label: identify the ConfigurationSetting
        :type label: str
        :param etag: check if the ConfigurationSetting is changed. Set None to skip checking etag
        :type etag: str
        :param kwargs: if “headers” exists, its value (a dict) will be added to the http request 
        :type kwargs: dict
        :return: The deleted ConfigurationSetting returned from the service, or None if it doesn't exist.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START delete_configuration_setting]
            :end-before: [END delete_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Delete a ConfigurationSetting
        """
        custom_headers = prep_delete_configuration_setting(key, etag, **kwargs)
        return self._client.delete_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    def lock_configuration_setting(self, key, label=None, **kwargs):
        # type: (str, str, dict) -> ConfigurationSetting

        """
        Lock a ConfigurationSetting

        :param key: identify the ConfigurationSetting
        :type key: str
        :param label: identify the ConfigurationSetting
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the http request header
        :return: The locked ConfigurationSetting returned from the service
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START lock_configuration_setting]
            :end-before: [END lock_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Lock a ConfigurationSetting
        """
        custom_headers = prep_lock_configuration_setting(key, **kwargs)
        return self._client.lock_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    def unlock_configuration_setting(self, key, label=None, **kwargs):
        # type: (str, str, dict) -> ConfigurationSetting

        """ Unlock a ConfigurationSetting

        :param key: identify the ConfigurationSetting
        :type key: str
        :param label: identify the ConfigurationSetting
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the http request header
        :return: The locked ConfigurationSetting returned from the service.
        :rtype: :class:`ConfigurationSetting`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START unlock_configuration_setting]
            :end-before: [END unlock_configuration_setting]
            :language: python
            :dedent: 4
            :caption: Unlock a ConfigurationSetting
        """
        custom_headers = prep_unlock_configuration_setting(key, **kwargs)
        return self._client.unlock_configuration_setting(
            key=key, label=label, custom_headers=custom_headers
        )

    def list_revisions(
        self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        # type: (list, list, datetime, list, dict) -> ConfigurationSettingPaged

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
        :rtype: :class:`ConfigurationSettingPaged`
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`

        Example

        .. literalinclude:: ../examples/test_example_configurationservice.py
            :start-after: [START list_revisions]
            :end-before: [END list_revisions]
            :language: python
            :dedent: 4
            :caption: List ConfigurationSetting revisions
        """
        return self._client.list_revisions(
            label=labels,
            key=keys,
            fields=fields,
            accept_date_time=accept_date_time,
            custom_headers=kwargs.get("headers"),
        )
