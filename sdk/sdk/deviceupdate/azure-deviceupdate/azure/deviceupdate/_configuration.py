# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#
# --------------------------------------------------------------------------

from msrest import Configuration

from .version import VERSION


class DeviceUpdateClientConfiguration(Configuration):
    """Configuration for DeviceUpdateClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

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

        if account_endpoint is None:
            raise ValueError("Parameter 'account_endpoint' must not be None.")
        if instance_id is None:
            raise ValueError("Parameter 'instance_id' must not be None.")
        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        base_url = 'https://{accountEndpoint}'

        super(DeviceUpdateClientConfiguration, self).__init__(base_url)

        # Starting Autorest.Python 4.0.64, make connection pool activated by default
        self.keep_alive = True

        self.add_user_agent('azure-deviceupdate/{}'.format(VERSION))

        self.account_endpoint = account_endpoint
        self.instance_id = instance_id
        self.credentials = credentials
