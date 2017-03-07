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
    if api_version == '2015-12-01':
        from .v2015_12_01 import models
        return models
    elif api_version == '2016-06-01':
        from .v2016_06_01 import models
        return models
    elif api_version == '2016-09-01':
        from .v2016_09_01 import models
        return models
    elif api_version == '2016-12-01':
        from .v2016_12_01 import models
        return models
    raise NotImplementedError("APIVersion {} is not available".format(api_version))

class ClientConfiguration(AzureConfiguration):
    """Configuration for ResourceManagementClient
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
            self, credentials, subscription_id=None, api_version='2015-06-15', base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        # In Resource client, subscription_id can be None because subscription sub-client does not need it
        #if subscription_id is None:
        #    raise ValueError("Parameter 'subscription_id' must not be None.")
        #if not isinstance(subscription_id, str):
        #    raise TypeError("Parameter 'subscription_id' must be str.")
        if api_version is not None and not isinstance(api_version, str):
            raise TypeError("Optional parameter 'api_version' must be str.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(ClientConfiguration, self).__init__(base_url)

        self.add_user_agent('resourcemanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id
        self.api_version = api_version


class Client(object):
    """The Resource Management Client.

    :ivar config: Configuration for client.
    :vartype config: ResourceManagementClientConfiguration

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(self, credentials, subscription_id=None, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        # In Resource client, subscription_id can be None because subscription sub-client does not need it
        #if subscription_id is None:
        #    raise ValueError("Parameter 'subscription_id' must not be None.")
        #if not isinstance(subscription_id, str):
        #    raise TypeError("Parameter 'subscription_id' must be str.")

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

    def features(self, api_version='2015-12-01'):
        if api_version =='2015-12-01':
            from .v2015_12_01.operations.features_operations import FeaturesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def subscriptions(self, api_version='2016-06-01'):
        if api_version =='2016-06-01':
            from .v2016_06_01.operations.subscriptions_operations import SubscriptionsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def tenants(self, api_version='2016-06-01'):
        if api_version =='2016-06-01':
            from .v2016_06_01.operations.tenants_operations import TenantsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def deployments(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.deployments_operations import DeploymentsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def providers(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.providers_operations import ProvidersOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def resource_groups(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.resource_groups_operations import ResourceGroupsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def resources(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.resources_operations import ResourcesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def tags(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.tags_operations import TagsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def deployment_operations(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.deployment_operations import DeploymentOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def resource_links(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.resource_links_operations import ResourceLinksOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def management_locks(self, api_version='2016-09-01'):
        if api_version =='2016-09-01':
            from .v2016_09_01.operations.management_locks_operations import ManagementLocksOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def policy_assignments(self, api_version='2016-12-01'):
        if api_version =='2016-12-01':
            from .v2016_12_01.operations.policy_assignments_operations import PolicyAssignmentsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)
    
    def policy_definitions(self, api_version='2016-12-01'):
        if api_version =='2016-12-01':
            from .v2016_12_01.operations.policy_definitions_operations import PolicyDefinitionsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)
