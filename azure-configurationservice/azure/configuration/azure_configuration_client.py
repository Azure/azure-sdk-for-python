from . import _generated
from .azure_configuration_requests import AzConfigRequestsCredentialsPolicy


from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest, RequestsTransport
from azure.core.pipeline.policies import UserAgentPolicy, NetworkTraceLoggingPolicy
from azure.core.configuration import Configuration


class AzureConfigurationClient(object):
    """Represents an azconfig client

    :ivar config: Configuration for client.
    :vartype config: AzureConfigurationClientConfiguration

    :param connection_string: Credentials needed for the client to connect to Azure.
    :type connection_string: str
    """

    def __init__(
            self, connection_string):

        self._client = _generated.AzureConfigurationClientImp(None, connection_string)
        self._client._client.config.pipeline = self._create_azconfig_pipeline()
    
    def _create_azconfig_pipeline(self):
        policies = [
            UserAgentPolicy("azconfig"),  # UserAgent policy
            AzConfigRequestsCredentialsPolicy(self._client.config)
        ]

        config = Configuration()
        config.connection.timeout = self._client.config.connection.timeout
        config.connection.cert = self._client.config.connection.cert
        config.connection.verify = self._client.config.connection.verify


        return Pipeline(
            RequestsTransport(config.connection),  # Send HTTP request using requests
            policies
        )

    def list_key_values(
            self, label=None, key=None, accept_date_time=None, fields=None, custom_headers=None):
        """List key values.

        List the key values in the configuration store, optionally filtered by
        label.

        :param label: Filter returned values based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type label: list[str]
        :param key: Filter returned values based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type key: list[str]
        :param accept_date_time: Obtain representation of the result related
         to past time.
        :type accept_date_time: datetime
        :param fields: Specify which fields to return
        :type fields: list[str]
        :param dict custom_headers: headers that will be added to the request
        :return: An iterator like instance of KeyValue
        :rtype:
         ~azure.configurationservice.models.KeyValuePaged[~azure.configurationservice.models.KeyValue]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_key_values(label, key, accept_date_time, fields, custom_headers)
    
    def get_key_value(
            self, key, label="%00", accept_date_time=None, custom_headers=None):
        
        """Get a KeyValue.

        Get the KeyValue for the given key and label.

        :param key: string
        :type key: str
        :param label: Label of key to retreive
        :type label: str
        :param accept_date_time: Obtain representation of the result related
         to past time.
        :type accept_date_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.get_key_value(key, label, accept_date_time, custom_headers)

    def create_key_value(
            self, key_value, key, label="%00", custom_headers=None):
        """Create a KeyValue.

        Create a KeyValue.

        :param key_value:
        :type key_value: ~azure.configurationservice.models.KeyValue
        :param key: string
        :type key: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        if_none_match = {'If-None-Match':'*'}
        if custom_headers is None:
            custom_headers = if_none_match
        elif custom_headers.get('If-None-Match', '*') == '*':
            custom_headers.update(if_none_match)
        return self._client.create_or_update_key_value(key_value, key, label, custom_headers)
    
    def update_key_value(
            self, key, value=None, content_type=None, tags=None, etag=None, label="%00", custom_headers=None):
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
        :param etag:
        :type etag: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        current_key_value = self._client.get_key_value(key, label)
        if etag is not None:
            if_match = {'If-Match': etag}
        else:
            if_match = {'If-Match': '*'}
        if custom_headers is None:
            custom_headers = if_match
        elif custom_headers.get('If-Match', '*') == '*':
            custom_headers.update(if_match)
        if value is not None:
            current_key_value.value = value
        if content_type is not None:
            current_key_value.content_type = content_type
        if tags is not None:
            current_key_value.tags = tags
        return self._client.create_or_update_key_value(current_key_value, key, label, custom_headers)
    
    def set_key_value(
            self, key_value, key, label="%00", custom_headers=None):
        """Set a KeyValue.

        Create or update a KeyValue.

        :param key_value:
        :type key_value: ~azure.configurationservice.models.KeyValue
        :param key: string
        :type key: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.create_or_update_key_value(key_value, key, label, custom_headers)
    
    def delete_key_value(
            self, key, label=None, custom_headers=None):
        """Delete a KeyValue.

        :param key: string
        :type key: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.delete_key_value(key, label, custom_headers)

    def list_keys(
            self, name=None, accept_date_time=None, custom_headers=None):
        """

        :param name:
        :type name: str
        :param accept_date_time: Obtain representation of the result related
         to past time.
        :type accept_date_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :return: An iterator like instance of Key
        :rtype:
         ~azure.configurationservice.models.KeyPaged[~azure.configurationservice.models.Key]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_keys(name, accept_date_time, custom_headers)
    
    def list_labels(
            self, accept_date_time=None, fields=None, name=None, custom_headers=None):
        """List labels.

        :param accept_date_time: Obtain representation of the result related
         to past time.
        :type accept_date_time: datetime
        :param fields: Specify which fields to return
        :type fields: list[str]
        :param name:
        :type name: str
        :param dict custom_headers: headers that will be added to the request
        :return: An iterator like instance of Label
        :rtype:
         ~azure.configurationservice.models.LabelPaged[~azure.configurationservice.models.Label]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_labels(accept_date_time, fields, name, custom_headers)

    def lock_key_value(
            self, key, label=None, custom_headers=None):
        """

        :param key:
        :type key: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.lock_key_value(key, label, custom_headers)
    
    def unlock_key_value(
            self, key, label=None, custom_headers=None):
        """

        :param key:
        :type key: str
        :param label:
        :type label: str
        :param dict custom_headers: headers that will be added to the request
        :return: KeyValue
        :rtype: ~azure.configurationservice.models.KeyValue
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.unlock_key_value(key, label, custom_headers)
    
    def list_revisions(
            self, label=None, key=None, fields=None, accept_date_time=None, custom_headers=None):
        """

        :param label: Filter returned values based on their label. '*' can be
         used as wildcard in the beginning or end of the filter
        :type label: list[str]
        :param key: Filter returned values based on their keys. '*' can be
         used as wildcard in the beginning or end of the filter
        :type key: list[str]
        :param fields: Specify which fields to return
        :type fields: list[str]
        :param accept_date_time: Obtain representation of the result related
         to past time.
        :type accept_date_time: datetime
        :param dict custom_headers: headers that will be added to the request
        :return: An iterator like instance of KeyValue
        :rtype:
         ~azure.configurationservice.models.KeyValuePaged[~azure.configurationservice.models.KeyValue]
        :raises: :class:`CloudError<msrestazure.azure_exceptions.CloudError>`
        """
        return self._client.list_revisions(label, key, fields, accept_date_time, custom_headers)