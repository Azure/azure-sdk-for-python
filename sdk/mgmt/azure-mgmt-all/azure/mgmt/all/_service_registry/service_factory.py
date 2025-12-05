from typing import Any, Optional, TYPE_CHECKING, Union, Dict, Callable, cast

from azure.core.polling import LROPoller, PollingMethod, NoPolling
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.pipeline import PipelineResponse, PipelineContext
from azure.mgmt.core.polling.arm_polling import ARMPolling


if TYPE_CHECKING:
    from .._client import ManagementClient
class ServiceProviderFactory:
    """Base factory class for service providers with HTTP operations."""
    
    def __init__(self, client: "ManagementClient", service_provider: str, subscription_id: Optional[str] = None, api_version: Optional[str] = None):
        self.client = client
        self.service_provider = service_provider
        # Use provided subscription_id or fall back to client's default
        self.subscription_id = subscription_id or client._config.subscription_id
        # Store API version for use in requests - use provided version, class default, or global default
        self.api_version = api_version
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
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        separator = "&" if "?" in full_url else "?"
        full_url += f"{separator}api-version={api_version}"
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
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        separator = "&" if "?" in full_url else "?"
        full_url += f"{separator}api-version={api_version}"
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
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        separator = "&" if "?" in full_url else "?"
        full_url += f"{separator}api-version={api_version}"
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
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        separator = "&" if "?" in full_url else "?"
        full_url += f"{separator}api-version={api_version}"
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
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        separator = "&" if "?" in full_url else "?"
        full_url += f"{separator}api-version={api_version}"
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
        print(f"Creating resource at URL: {url}")
        return self.put(url, model=resource_data, **kwargs)
    
    def begin_create_resource(self, resource_type: str, resource_name: str, resource_data: Dict[str, Any], 
                            resource_group: Optional[str] = None, output_type: Optional[str] = None, **kwargs: Any) -> LROPoller[Any]:
        """Begin creating a new resource with long-running operation support.
        
        :param resource_type: The type of resource (e.g., 'configurationStores')
        :type resource_type: str
        :param resource_name: Name of the resource to create
        :type resource_name: str
        :param resource_data: Resource configuration data
        :type resource_data: Dict[str, Any]
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        :param output_type: Optional type name for deserialization
        :type output_type: str
        :return: An LROPoller for the long-running operation
        :rtype: LROPoller[Any]
        """
        # Set up polling configuration
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", 30)  # Default to 30 seconds
        
        # Create the initial request
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("PUT", full_url)
        request.set_json_body(resource_data)
        
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        request.url += f"?api-version={api_version}" if "?" not in request.url else f"&api-version={api_version}"
        
        # Execute the initial request
        raw_result = self.client._send_request(request, **kwargs)
        
        def get_long_running_output(pipeline_response):
            # Extract the result from the pipeline response
            response_json = pipeline_response.http_response.json() if hasattr(pipeline_response.http_response, 'json') else {}
            return response_json
        
        if polling is True:
            polling_method: PollingMethod = cast(PollingMethod, ARMPolling(lro_delay, **kwargs))
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        
        # Create a proper pipeline response
        pipeline_response = PipelineResponse(request, raw_result, PipelineContext(None))
        
        return LROPoller[Any](
            client=self.client._client,
            initial_response=pipeline_response,
            deserialization_callback=get_long_running_output,
            polling_method=polling_method
        )
    
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
    
    def begin_update_resource(self, resource_type: str, resource_name: str, resource_data: Dict[str, Any], 
                            resource_group: Optional[str] = None, output_type: Optional[str] = None, **kwargs: Any) -> LROPoller[Any]:
        """Begin updating a resource with long-running operation support.
        
        :param resource_type: The type of resource (e.g., 'configurationStores')
        :type resource_type: str
        :param resource_name: Name of the resource to update
        :type resource_name: str
        :param resource_data: Resource configuration data
        :type resource_data: Dict[str, Any]
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        :param output_type: Optional type name for deserialization
        :type output_type: str
        :return: An LROPoller for the long-running operation
        :rtype: LROPoller[Any]
        """
        # Set up polling configuration
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", 30)  # Default to 30 seconds
        
        # Create the initial request
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("PATCH", full_url)
        request.set_json_body(resource_data)
        
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        request.url += f"?api-version={api_version}" if "?" not in request.url else f"&api-version={api_version}"
        
        # Execute the initial request
        raw_result = self.client._send_request(request, **kwargs)
        
        def get_long_running_output(pipeline_response):
            # Extract the result from the pipeline response
            response_json = pipeline_response.http_response.json() if hasattr(pipeline_response.http_response, 'json') else {}
            return response_json
        
        if polling is True:
            polling_method: PollingMethod = cast(PollingMethod, ARMPolling(lro_delay, **kwargs))
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        
        # Create a proper pipeline response
        pipeline_response = PipelineResponse(request, raw_result, PipelineContext(None))
        
        return LROPoller[Any](
            client=self.client._client,
            initial_response=pipeline_response,
            deserialization_callback=get_long_running_output,
            polling_method=polling_method
        )
    
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
    
    def begin_delete_resource(self, resource_type: str, resource_name: str, 
                            resource_group: Optional[str] = None, **kwargs: Any) -> LROPoller[None]:
        """Begin deleting a resource with long-running operation support.
        
        :param resource_type: The type of resource (e.g., 'configurationStores')
        :type resource_type: str
        :param resource_name: Name of the resource to delete
        :type resource_name: str
        :param resource_group: Optional resource group name for scoped resources
        :type resource_group: str
        :return: An LROPoller for the long-running operation
        :rtype: LROPoller[None]
        """
        # Set up polling configuration
        polling: Union[bool, PollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", 30)  # Default to 30 seconds
        
        # Create the initial request
        if resource_group:
            url = f"/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/{self.service_provider}/{resource_type}/{resource_name}"
        else:
            url = f"{self.base_url}/{resource_type}/{resource_name}"
        
        full_url = url if url.startswith('/') else f"{self.base_url}/{url}"
        request = HttpRequest("DELETE", full_url)
        
        # Add required api-version parameter
        api_version = kwargs.pop("api_version", self.api_version)
        request.url += f"?api-version={api_version}" if "?" not in request.url else f"&api-version={api_version}"
        
        # Execute the initial request
        raw_result = self.client._send_request(request, **kwargs)
        
        def get_long_running_output(pipeline_response):
            # Delete operations return None
            return None
        
        if polling is True:
            polling_method: PollingMethod = cast(PollingMethod, ARMPolling(lro_delay, **kwargs))
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        
        # Create a proper pipeline response
        pipeline_response = PipelineResponse(request, raw_result, PipelineContext(None))
        
        return LROPoller[None](
            client=self.client._client,
            initial_response=pipeline_response,
            deserialization_callback=get_long_running_output,
            polling_method=polling_method
        )
