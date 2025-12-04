from typing import Any, Optional, TYPE_CHECKING, Union, Dict

from azure.core.rest import HttpRequest, HttpResponse

if TYPE_CHECKING:
    from .._client import ManagementClient
class ServiceProviderFactory:
    """Base factory class for service providers with HTTP operations."""
    
    def __init__(self, client: "ManagementClient", service_provider: str, subscription_id: Optional[str] = None):
        self.client = client
        self.service_provider = service_provider
        # Use provided subscription_id or fall back to client's default
        self.subscription_id = subscription_id or client._config.subscription_id
        self.base_url = f"/subscriptions/{self.subscription_id}/providers/{service_provider}"
    
    def get(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a GET request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("GET", full_url)
        return self.client._send_request(request, **kwargs)

    def post(self, url: str, *, model: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> HttpResponse:
        """Send a POST request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword model: Model data to send in the request body (takes precedence over json/data).
        :type model: Optional[Dict[str, Any]]
        :keyword json: JSON data to send in the request body.
        :keyword data: Data to send in the request body.
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("POST", full_url)
        if model is not None:
            request.set_json_body(model)
        elif json is not None:
            request.set_json_body(json)
        elif data is not None:
            request.set_bytes_body(data)
        return self.client._send_request(request, **kwargs)

    def put(self, url: str, *, model: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> HttpResponse:
        """Send a PUT request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword model: Model data to send in the request body (takes precedence over json/data).
        :type model: Optional[Dict[str, Any]]
        :keyword json: JSON data to send in the request body.
        :keyword data: Data to send in the request body.
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("PUT", full_url)
        if model is not None:
            request.set_json_body(model)
        elif json is not None:
            request.set_json_body(json)
        elif data is not None:
            request.set_bytes_body(data)
        return self.client._send_request(request, **kwargs)

    def patch(self, url: str, *, model: Optional[Dict[str, Any]] = None, json: Any = None, data: Any = None, **kwargs: Any) -> HttpResponse:
        """Send a PATCH request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword model: Model data to send in the request body (takes precedence over json/data).
        :type model: Optional[Dict[str, Any]]
        :keyword json: JSON data to send in the request body.
        :keyword data: Data to send in the request body.
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("PATCH", full_url)
        if model is not None:
            request.set_json_body(model)
        elif json is not None:
            request.set_json_body(json)
        elif data is not None:
            request.set_bytes_body(data)
        return self.client._send_request(request, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a DELETE request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("DELETE", full_url)
        return self.client._send_request(request, **kwargs)

    def head(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send a HEAD request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("HEAD", full_url)
        return self.client._send_request(request, **kwargs)

    def options(self, url: str, **kwargs: Any) -> HttpResponse:
        """Send an OPTIONS request.
        
        :param url: The relative URL to send the request to. Can be absolute or relative to provider.
        :type url: str
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call.
        :rtype: ~azure.core.rest.HttpResponse
        """
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("OPTIONS", full_url)
        return self.client._send_request(request, **kwargs)
    
    # Higher-level resource management methods
    def get_resource(self, resource_type: str, resource_name: Optional[str] = None, resource_group: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """Get a resource or list resources of a specific type.
        
        :param resource_type: The type of resource (e.g., 'virtualMachines')
        :type resource_type: str
        :param resource_name: Optional name of specific resource
        :type resource_name: str
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        """
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}"
        else:
            url = f"{self.base_url}/{resource_type}"
        
        if resource_name:
            url += f"/{resource_name}"
        return self.get(url, **kwargs)
    
    def create_resource(self, resource_type: str, resource_name: str, resource_data: Dict[str, Any], resource_group: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """Create a new resource.
        
        :param resource_type: The type of resource (e.g., 'virtualMachines')
        :type resource_type: str
        :param resource_name: Name of the resource to create
        :type resource_name: str
        :param resource_data: Resource configuration data
        :type resource_data: Dict[str, Any]
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        """
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        return self.put(url, model=resource_data, **kwargs)
    
    def update_resource(self, resource_type: str, resource_name: str, resource_data: Dict[str, Any], resource_group: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """Update an existing resource.
        
        :param resource_type: The type of resource (e.g., 'virtualMachines')
        :type resource_type: str
        :param resource_name: Name of the resource to update
        :type resource_name: str
        :param resource_data: Resource configuration data
        :type resource_data: Dict[str, Any]
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        """
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        return self.patch(url, model=resource_data, **kwargs)
    
    def delete_resource(self, resource_type: str, resource_name: str, resource_group: Optional[str] = None, **kwargs: Any) -> HttpResponse:
        """Delete a resource.
        
        :param resource_type: The type of resource (e.g., 'virtualMachines')
        :type resource_type: str
        :param resource_name: Name of the resource to delete
        :type resource_name: str
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        """
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        return self.delete(url, **kwargs)
