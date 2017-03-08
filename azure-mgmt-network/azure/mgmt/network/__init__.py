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
    elif api_version == '2016-09-01':
        from .v2016_09_01 import models
        return models
    raise NotImplementedError("APIVersion {} is not available".format(api_version))

class ClientConfiguration(AzureConfiguration):
    """Configuration for NetworkManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id=None, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(ClientConfiguration, self).__init__(base_url)

        self.add_user_agent('networkmanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id


class Client(object):
    """The Network Management Client.

    :ivar config: Configuration for client.
    :vartype config: ClientConfiguration

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
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")

        self.credentials = credentials
        self.subscription_id = subscription_id
        self.base_url = base_url

        self.config = ClientConfiguration(self.credentials, self.subscription_id, self.base_url)
        self.client = ServiceClient(self.credentials, self.config)

    def _instantiate_operation_class(self, local_models, operation_class):
        client_models = {k: v for k, v in local_models.__dict__.items() if isinstance(v, type)}
        serialize = Serializer(client_models)
        deserialize = Deserializer(client_models)
        return operation_class(self.client, self.config, serialize, deserialize)

    def virtual_network_gateways(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import VirtualNetworkGatewaysOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import VirtualNetworkGatewaysOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def express_route_circuit_authorizations(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import ExpressRouteCircuitAuthorizationsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import ExpressRouteCircuitAuthorizationsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def application_gateways(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import ApplicationGatewaysOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import ApplicationGatewaysOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def virtual_networks(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import VirtualNetworksOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import VirtualNetworksOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def network_security_groups(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import NetworkSecurityGroupsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import NetworkSecurityGroupsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def subnets(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import SubnetsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import SubnetsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def local_network_gateways(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import LocalNetworkGatewaysOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import LocalNetworkGatewaysOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def express_route_service_providers(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import ExpressRouteServiceProvidersOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import ExpressRouteServiceProvidersOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def routes(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import RoutesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import RoutesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def load_balancers(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import LoadBalancersOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import LoadBalancersOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def virtual_network_peerings(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import VirtualNetworkPeeringsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import VirtualNetworkPeeringsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def usages(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import UsagesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import UsagesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def route_tables(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import RouteTablesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import RouteTablesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def express_route_circuits(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import ExpressRouteCircuitsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import ExpressRouteCircuitsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def virtual_network_gateway_connections(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import VirtualNetworkGatewayConnectionsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import VirtualNetworkGatewayConnectionsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def security_rules(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import SecurityRulesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import SecurityRulesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def express_route_circuit_peerings(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import ExpressRouteCircuitPeeringsOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import ExpressRouteCircuitPeeringsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def public_ip_addresses(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import PublicIPAddressesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import PublicIPAddressesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)

    def network_interfaces(self, api_version='2016-09-01'):
        if api_version =='2015-06-15':
            from .v2015_06_15.operations import NetworkInterfacesOperations as OperationClass
        elif api_version =='2016-09-01':
            from .v2016_09_01.operations import NetworkInterfacesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {{}} is not available".format(api_version))
        return self._instantiate_operation_class(models(api_version), OperationClass)