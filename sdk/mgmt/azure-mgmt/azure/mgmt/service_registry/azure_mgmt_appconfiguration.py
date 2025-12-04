from typing import TYPE_CHECKING, Any

from azure.core.rest import HttpResponse
from .service_factory import ServiceProviderFactory

if TYPE_CHECKING:
    from .._client import ManagementClient

class AppConfigurationFactory(ServiceProviderFactory):
    """Factory for Microsoft.AppConfiguration service provider."""

    def __init__(self, client: "ManagementClient", subscription_id: str = None):
        super().__init__(client, "Microsoft.AppConfiguration", subscription_id)

    def virtual_networks(self, resource_group: str, vnet_name: str = None, **kwargs: Any) -> HttpResponse:
        """Manage virtual networks."""
        return self.get_resource("virtualNetworks", vnet_name, resource_group, **kwargs)
    
    def create_virtual_network(self, resource_group: str, vnet_name: str, vnet_config: Any, **kwargs: Any) -> HttpResponse:
        """Create a virtual network."""
        return self.create_resource("virtualNetworks", vnet_name, vnet_config, resource_group, **kwargs)
    
    def public_ip_addresses(self, resource_group: str, ip_name: str = None, **kwargs: Any) -> HttpResponse:
        """Manage public IP addresses."""
        return self.get_resource("publicIPAddresses", ip_name, resource_group, **kwargs)
    
    def create_public_ip(self, resource_group: str, ip_name: str, ip_config: Any, **kwargs: Any) -> HttpResponse:
        """Create a public IP address."""
        return self.create_resource("publicIPAddresses", ip_name, ip_config, resource_group, **kwargs)
    
    def network_security_groups(self, resource_group: str, nsg_name: str = None, **kwargs: Any) -> HttpResponse:
        """Manage network security groups."""
        return self.get_resource("networkSecurityGroups", nsg_name, resource_group, **kwargs)
    
    def create_network_security_group(self, resource_group: str, nsg_name: str, nsg_config: Any, **kwargs: Any) -> HttpResponse:
        """Create a network security group."""
        return self.create_resource("networkSecurityGroups", nsg_name, nsg_config, resource_group, **kwargs)
