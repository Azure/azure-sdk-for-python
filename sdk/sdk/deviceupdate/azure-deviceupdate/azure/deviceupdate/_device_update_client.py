# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
# --------------------------------------------------------------------------

from msrest.service_client import SDKClient
from msrest import Serializer, Deserializer

from ._configuration import DeviceUpdateClientConfiguration
from msrest.exceptions import HttpOperationError
from .operations import UpdatesOperations
from .operations import DevicesOperations
from .operations import DeploymentsOperations
from . import models


class DeviceUpdateClient(SDKClient):
    """Device Update for IoT Hub is an Azure service that enables customers to publish update for their IoT devices to the cloud, and then deploy that update to their devices (approve updates to groups of devices managed and provisioned in IoT Hub). It leverages the proven security and reliability of the Windows Update platform, optimized for IoT devices. It works globally and knows when and how to update devices, enabling customers to focus on their business goals and let Device Update for IoT Hub handle the updates.

    :ivar config: Configuration for client.
    :vartype config: DeviceUpdateClientConfiguration

    :ivar updates: Updates operations
    :vartype updates: azure.deviceupdate.operations.UpdatesOperations
    :ivar devices: Devices operations
    :vartype devices: azure.deviceupdate.operations.DevicesOperations
    :ivar deployments: Deployments operations
    :vartype deployments: azure.deviceupdate.operations.DeploymentsOperations

    :param account_endpoint: Account endpoint.
    :type account_endpoint: str
    :param instance_id: Account instance identifier.
    :type instance_id: str
    :param credentials: Subscription credentials which uniquely identify
     client subscription.
    :type credentials: None
    """

    def __init__(
            self, account_endpoint, instance_id, credentials):

        self.config = DeviceUpdateClientConfiguration(account_endpoint, instance_id, credentials)
        super(DeviceUpdateClient, self).__init__(self.config.credentials, self.config)

        client_models = {k: v for k, v in models.__dict__.items() if isinstance(v, type)}
        self.api_version = '2020-09-01'
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)

        self.updates = UpdatesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.devices = DevicesOperations(
            self._client, self.config, self._serialize, self._deserialize)
        self.deployments = DeploymentsOperations(
            self._client, self.config, self._serialize, self._deserialize)
