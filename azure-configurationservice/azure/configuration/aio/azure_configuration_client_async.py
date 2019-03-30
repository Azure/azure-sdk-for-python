from .._generated.aio import AzureConfigurationClientImp
from ..azure_configuration_requests import AzConfigRequestsCredentialsPolicy


from ..azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from msrest.pipeline.requests import RequestsPatchSession

from msrest.pipeline import Request, Pipeline

from msrest.universal_http.async_requests import AsyncRequestsHTTPSender
from msrest.pipeline.async_requests import (
    AsyncPipelineRequestsHTTPSender
)

from ..utils import get_endpoint_from_connection_string


class AzureConfigurationClientAsync(object):
    """Represents an azconfig client

    :ivar config: Configuration for client.
    :vartype config: AzureConfigurationClientConfiguration

    :param connection_string: Credentials needed for the client to connect to Azure.
    :type connection_string: str
    """

    def __init__(
            self, connection_string):

        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        self._client = AzureConfigurationClientImp(connection_string, base_url)
        self._client._client.config.pipeline = self._create_azconfig_pipeline()
    
    def _create_azconfig_pipeline(self):
        policies = [
            self._client.config.user_agent_policy,  # UserAgent policy
            RequestsPatchSession(),         # Support deprecated operation config at the session level
            self._client.config.http_logger_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self._client.config)
        ]

        return Pipeline(
            policies,
            AsyncPipelineRequestsHTTPSender(
                AsyncRequestsHTTPSender(self._client.config)  # Send HTTP request using requests
            )
        )

    def list_configuration_settings(
            self, labels=None, keys=None, fields=None, **kwargs):
        """List key values.

        List the key values in the configuration store, optionally filtered by
        label.

        :param labels: Filter returned values based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: Filter returned values based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param fields: Specify which fields to return
        :type fields: list[str]
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: An iterator like instance of KeyValue
        :rtype:
         ~azure.configurationservice.models.KeyValuePaged[~azure.configurationservice.models.KeyValue]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_configuration_settings(label=labels, key=keys, fields=fields, custom_headers=kwargs.get("headers"))
    
    async def get_configuration_setting(
            self, key, label=None, **kwargs):
        """Get a KeyValue.

        Get the KeyValue for the given key and label.

        :param key: string
        :type key: str
        :param label: Label of key to retreive
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return await self._client.get_configuration_setting(key=key, label=label, custom_headers=kwargs.get("headers"))

    async def add_configuration_setting(
            self, configuration_setting, **kwargs):
        """Create a KeyValue.

        Create a KeyValue.

        :param configuration_setting:
        :type configuration_setting: ~azure.configurationservice.models.KeyValue
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if configuration_setting is None:
            #throw?
            return None
        key = configuration_setting.key
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        if_none_match = {'If-None-Match':'"*"'}
        if custom_headers is None:
            custom_headers = if_none_match
        elif custom_headers.get('If-None-Match', '"*"') == '"*"':
            custom_headers.update(if_none_match)
        return await self._client.create_or_update_configuration_setting(configuration_setting=configuration_setting, key=key, label=configuration_setting.label, custom_headers=custom_headers)
    
    async def update_configuration_setting(
            self, key, value=None, content_type=None, tags=None, label=None, etag=None, **kwargs):
        """Update a KeyValue.

        Update a KeyValue.

        :param key: string
        :type key: str
        :param value:
        :type value: str
        :param content_type:
        :type content_type: str
        :param tags:
        :type tags: dict
        :param label:
        :type label: str
        :param etag:
        :type etag: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        current_configuration_setting = await self._client.get_configuration_setting(key, label)
        if etag is not None:
            if_match = {'If-Match': '"' + etag + '"'}
        else:
            if_match = {'If-Match': '"*"'}
        if custom_headers is None:
            custom_headers = if_match
        elif custom_headers.get('If-Match', '"*"') == '"*"':
            custom_headers.update(if_match)
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return await self._client.create_or_update_configuration_setting(configuration_setting=current_configuration_setting, key=key, label=label, custom_headers=custom_headers)
    
    async def set_configuration_setting(
            self, configuration_setting, **kwargs):
        """Set a KeyValue.

        Create or update a KeyValue.

        :param configuration_setting:
        :type configuration_setting: ~azure.configurationservice.models.KeyValue
        :param key: string
        :type key: str
        :param label:
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if configuration_setting is None:
            #throw?
            return None
        key = configuration_setting.key
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        etag = configuration_setting.etag
        if etag is not None:
            if_match = {'If-Match': '"' + etag + '"'}
            if custom_headers is None:
                custom_headers = if_match
            else:
                custom_headers.update(if_match)
        return await self._client.create_or_update_configuration_setting(configuration_setting=configuration_setting, key=key, label=configuration_setting.label, custom_headers=custom_headers)
    
    async def delete_configuration_setting(
            self, key, label=None, etag=None, **kwargs):
        """Delete a KeyValue.

        :param key: string
        :type key: str
        :param label:
        :type label: str
        :param etag:
        :type etag: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        if etag is not None:
            if_match = {'If-Match': '"' + etag + '"'}
            if custom_headers is None:
                custom_headers = if_match
            else:
                custom_headers.update(if_match)
        return await self._client.delete_configuration_setting(key=key, label=label, custom_headers=custom_headers)

    async def lock_configuration_setting(
            self, key, label=None, **kwargs):
        """

        :param key:
        :type key: str
        :param label:
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        return await self._client.lock_configuration_setting(key=key, label=label, custom_headers=custom_headers)
    
    async def unlock_configuration_setting(
            self, key, label=None, **kwargs):
        """

        :param key:
        :type key: str
        :param label:
        :type label: str
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if key is None:
            #throw?
            return None
        custom_headers = kwargs.get("headers")
        return await self._client.unlock_configuration_setting(key=key, label=label, custom_headers=custom_headers)
    
    def list_revisions(
            self, labels=None, keys=None, fields=None, **kwargs):
        """

        :param labels: Filter returned values based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type labels: list[str]
        :param keys: Filter returned values based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type keys: list[str]
        :param fields: Specify which fields to return
        :type fields: list[str]
        :param dict kwargs: if headers key exists, it will be added to the request
        :return: An iterator like instance of KeyValue
        :rtype:
         ~azure.configurationservice.models.KeyValuePaged[~azure.configurationservice.models.KeyValue]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_revisions(label=labels, key=keys, fields=fields, custom_headers=kwargs.get("headers"))