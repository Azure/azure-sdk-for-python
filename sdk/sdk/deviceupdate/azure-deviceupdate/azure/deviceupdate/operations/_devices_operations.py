# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
# --------------------------------------------------------------------------

from msrest.pipeline import ClientRawResponse
from msrest.exceptions import HttpOperationError

from .. import models


class DevicesOperations(object):
    """DevicesOperations operations.

    You should not instantiate directly this class, but create a Client instance that will create it for you and attach it as attribute.

    :param client: Client for service requests.
    :param config: Configuration of service client.
    :param serializer: An object model serializer.
    :param deserializer: An object model deserializer.
    """

    models = models

    def __init__(self, client, config, serializer, deserializer):

        self._client = client
        self._serialize = serializer
        self._deserialize = deserializer

        self.config = config

    def get_all_device_classes(
            self, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a list of all device classes (unique combinations of device
        manufacturer and model) for all devices connected to Device Update for
        IoT Hub.

        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfDeviceClasses or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfDeviceClasses or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_all_device_classes.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfDeviceClasses', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_all_device_classes.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/deviceclasses'}

    def get_device_class(
            self, device_class_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets the properties of a device class.

        :param device_class_id: Device class identifier.
        :type device_class_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeviceClass or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.DeviceClass or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_device_class.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'deviceClassId': self._serialize.url("device_class_id", device_class_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('DeviceClass', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_device_class.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/deviceclasses/{deviceClassId}'}

    def get_device_class_device_ids(
            self, device_class_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a list of device identifiers in a device class.

        :param device_class_id: Device class identifier.
        :type device_class_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfStrings or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfStrings or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_device_class_device_ids.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'deviceClassId': self._serialize.url("device_class_id", device_class_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfStrings', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_device_class_device_ids.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/deviceclasses/{deviceClassId}/deviceids'}

    def get_device_class_installable_updates(
            self, device_class_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a list of installable updates for a device class.

        :param device_class_id: Device class identifier.
        :type device_class_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfUpdateIds or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfUpdateIds or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_device_class_installable_updates.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'deviceClassId': self._serialize.url("device_class_id", device_class_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfUpdateIds', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_device_class_installable_updates.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/deviceclasses/{deviceClassId}/installableupdates'}

    def get_all_devices(
            self, account_options, filter=None, custom_headers=None, raw=False, **operation_config):
        """Gets a list of devices connected to Device Update for IoT Hub.

        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param filter: Restricts the set of devices returned. You can only
         filter on device GroupId.
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfDevices or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfDevices or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_all_devices.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if filter is not None:
            query_parameters['$filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfDevices', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_all_devices.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/devices'}

    def get_device(
            self, device_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets the device properties and latest deployment status for a device
        connected to Device Update for IoT Hub.

        :param device_id: Device identifier in Azure IOT Hub.
        :type device_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Device or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.Device or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_device.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'deviceId': self._serialize.url("device_id", device_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('Device', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_device.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/devices/{deviceId}'}

    def get_update_compliance(
            self, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets the breakdown of how many devices are on their latest update, have
        new updates available, or are in progress receiving new updates.

        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpdateCompliance or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.UpdateCompliance or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_update_compliance.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('UpdateCompliance', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_update_compliance.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/updatecompliance'}

    def get_all_device_tags(
            self, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a list of available group device tags for all devices connected to
        Device Update for IoT Hub.

        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfDeviceTags or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfDeviceTags or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_all_device_tags.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfDeviceTags', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_all_device_tags.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/devicetags'}

    def get_device_tag(
            self, tag_name, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a count of how many devices have a device tag.

        :param tag_name: Tag name.
        :type tag_name: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: DeviceTag or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.DeviceTag or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_device_tag.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'tagName': self._serialize.url("tag_name", tag_name, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('DeviceTag', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_device_tag.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/devicetags/{tagName}'}

    def get_all_groups(
            self, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets a list of all device groups.

        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfGroups or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfGroups or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_all_groups.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfGroups', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_all_groups.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups'}

    def get_group(
            self, group_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Gets the properties of a group.

        :param group_id: Group identifier.
        :type group_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Group or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.Group or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_group.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'groupId': self._serialize.url("group_id", group_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('Group', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_group.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups/{groupId}'}

    def create_or_update_group(
            self, group_id, group, account_options, custom_headers=None, raw=False, **operation_config):
        """Create or update a device group.

        :param group_id: Group identifier.
        :type group_id: str
        :param group: The group properties.
        :type group: ~azure.deviceupdate.models.Group
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: Group or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.Group or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.create_or_update_group.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'groupId': self._serialize.url("group_id", group_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        header_parameters['Content-Type'] = 'application/json; charset=utf-8'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct body
        body_content = self._serialize.body(group, 'Group')

        # Construct and send request
        request = self._client.put(url, query_parameters, header_parameters, body_content)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 400, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('Group', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    create_or_update_group.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups/{groupId}'}

    def delete_group(
            self, group_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Deletes a device group.

        :param group_id: Group identifier.
        :type group_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: None or ClientRawResponse if raw=true
        :rtype: None or ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.delete_group.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'groupId': self._serialize.url("group_id", group_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.delete(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 204]:
            raise HttpOperationError(self._deserialize, response)

        if raw:
            client_raw_response = ClientRawResponse(None, response)
            return client_raw_response
    delete_group.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups/{groupId}'}

    def get_group_update_compliance(
            self, group_id, account_options, custom_headers=None, raw=False, **operation_config):
        """Get group update compliance information such as how many devices are on
        their latest update, how many need new updates, and how many are in
        progress on receiving a new update.

        :param group_id: Group identifier.
        :type group_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: UpdateCompliance or ClientRawResponse if raw=true
        :rtype: ~azure.deviceupdate.models.UpdateCompliance or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_group_update_compliance.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'groupId': self._serialize.url("group_id", group_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('UpdateCompliance', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_group_update_compliance.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups/{groupId}/updateCompliance'}

    def get_group_best_updates(
            self, group_id, account_options, filter=None, custom_headers=None, raw=False, **operation_config):
        """Get the best available updates for a group and a count of how many
        devices need each update.

        :param group_id: Group identifier.
        :type group_id: str
        :param account_options: Additional parameters for the operation
        :type account_options: ~azure.deviceupdate.models.AccountOptions
        :param filter: Restricts the set of bestUpdates returned. You can
         filter on update Provider, Name and Version property.
        :type filter: str
        :param dict custom_headers: headers that will be added to the request
        :param bool raw: returns the direct response alongside the
         deserialized response
        :param operation_config: :ref:`Operation configuration
         overrides<msrest:optionsforoperations>`.
        :return: PageableListOfUpdatableDevices or ClientRawResponse if
         raw=true
        :rtype: ~azure.deviceupdate.models.PageableListOfUpdatableDevices or
         ~msrest.pipeline.ClientRawResponse
        :raises:
         :class:`HttpOperationError<msrest.exceptions.HttpOperationError>`
        """
        self.config.selfconfiginstance_id = None
        if account_options is not None:
            self.config.selfconfiginstance_id = account_options.instance_id

        # Construct URL
        url = self.get_group_best_updates.metadata['url']
        path_format_arguments = {
            'accountEndpoint': self._serialize.url("self.config.account_endpoint", self.config.account_endpoint, 'str', skip_quote=True),
            'groupId': self._serialize.url("group_id", group_id, 'str'),
            'instanceId': self._serialize.url("self.config.selfconfiginstance_id", self.config.selfconfiginstance_id, 'str', skip_quote=True)
        }
        url = self._client.format_url(url, **path_format_arguments)

        # Construct parameters
        query_parameters = {}
        if filter is not None:
            query_parameters['$filter'] = self._serialize.query("filter", filter, 'str')

        # Construct headers
        header_parameters = {}
        header_parameters['Accept'] = 'application/json'
        if custom_headers:
            header_parameters.update(custom_headers)

        # Construct and send request
        request = self._client.get(url, query_parameters, header_parameters)
        response = self._client.send(request, stream=False, **operation_config)

        if response.status_code not in [200, 404]:
            raise HttpOperationError(self._deserialize, response)

        deserialized = None
        if response.status_code == 200:
            deserialized = self._deserialize('PageableListOfUpdatableDevices', response)

        if raw:
            client_raw_response = ClientRawResponse(deserialized, response)
            return client_raw_response

        return deserialized
    get_group_best_updates.metadata = {'url': '/deviceupdate/{instanceId}/v2/management/groups/{groupId}/bestUpdates'}
