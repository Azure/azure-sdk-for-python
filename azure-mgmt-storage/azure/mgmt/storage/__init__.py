# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.service_client import ServiceClient
from msrest import Serializer, Deserializer
from msrestazure import AzureConfiguration
from .version import VERSION


def models(api_version=None):
    if api_version == '2015-06-15':
        from .v2015_06_15 import models
        return models
    elif api_version == '2016-01-01':
        from .v2016_01_01 import models
        return models
    elif api_version == '2016-12-01':
        from .v2016_12_01 import models
        return models
    raise NotImplementedError("APIVersion {} is not available".format(api_version))

class ClientConfiguration(AzureConfiguration):
    """Configuration for StorageManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param api_version: Client Api Version.
    :type api_version: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id, api_version='2015-06-15', base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")
        if api_version is not None and not isinstance(api_version, str):
            raise TypeError("Optional parameter 'api_version' must be str.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(ClientConfiguration, self).__init__(base_url)

        self.add_user_agent('storagemanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id
        self.api_version = api_version


class Client(object):
    """The Storage Management Client.

    :ivar config: Configuration for client.
    :vartype config: StorageManagementClientConfiguration

    :ivar storage_accounts: StorageAccounts operations
    :vartype storage_accounts: .operations.StorageAccountsOperations
    :ivar usage: Usage operations
    :vartype usage: .operations.UsageOperations

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(self, credentials, subscription_id, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")

        self.credentials = credentials
        self.subscription_id = subscription_id
        self.base_url = base_url

        self.config = ClientConfiguration(self.credentials, self.subscription_id, "FakeValue", self.base_url)
        self.client = ServiceClient(self.credentials, self.config)

    def _instantiate_operation_class(self, api_version, local_models, operation_class):
        config = ClientConfiguration(self.credentials, self.subscription_id, api_version, self.base_url)
        client_models = {k: v for k, v in local_models.__dict__.items() if isinstance(v, type)}
        serialize = Serializer(client_models)
        deserialize = Deserializer(client_models)
        return operation_class(self.client, config, serialize, deserialize)

    def storage_accounts(self, api_version='2016-12-01'):
        if api_version == '2015-06-15':
            from .v2015_06_15.operations.storage_accounts_operations import StorageAccountsOperations as OperationClass
        elif api_version == '2016-01-01':
            from .v2016_01_01.operations.storage_accounts_operations import StorageAccountsOperations as OperationClass
        elif api_version == '2016-12-01':
            from .v2016_12_01.operations.storage_accounts_operations import StorageAccountsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def usage(self, api_version='2016-12-01'):
        if api_version == '2015-06-15':
            from .v2015_06_15.operations.usage_operations import UsageOperations as OperationClass
        elif api_version == '2016-01-01':
            from .v2016_01_01.operations.usage_operations import UsageOperations as OperationClass
        elif api_version == '2016-12-01':
            from .v2016_12_01.operations.usage_operations import UsageOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))

        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)
