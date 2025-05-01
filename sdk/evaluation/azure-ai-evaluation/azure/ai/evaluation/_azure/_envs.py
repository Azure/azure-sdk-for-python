# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# NOTE:
# This is a simplified version of the original code from azure-ai-ml:
# sdk\ml\azure-ai-ml\azure\ai\ml\_azure_environments.py

import asyncio
import os

from typing import Any, Dict, Final, Mapping, Optional, Sequence, TypedDict

from azure.core import AsyncPipelineClient
from azure.core.configuration import Configuration
from azure.core.rest import HttpRequest
from azure.core.pipeline.policies import ProxyPolicy, AsyncRetryPolicy


class AzureEnvironmentMetadata(TypedDict):
    """Configuration for various Azure environments. All endpoints include a trailing slash."""
    portal_endpoint: str
    """The management portal for the Azure environment (e.g. https://portal.azure.com/)"""
    resource_manager_endpoint: str
    """The API endpoint for Azure control plan (e.g. https://management.azure.com/)"""
    active_directory_endpoint: str
    """The active directory endpoint used for authentication (e.g. https://login.microsoftonline.com/)"""
    aml_resource_endpoint: str
    """The endpoint for Azure Machine Learning resources (e.g. https://ml.azure.com/)"""
    storage_suffix: str
    """The suffix to use for storage endpoint URLs (e.g. core.windows.net)"""
    registry_discovery_endpoint: str


_ENV_ARM_CLOUD_METADATA_URL: Final[str] = "ARM_CLOUD_METADATA_URL"
_ENV_DEFAULT_CLOUD_NAME: Final[str] = "AZUREML_CURRENT_CLOUD"
_ENV_REGISTRY_DISCOVERY_URL: Final[str] = "REGISTRY_DISCOVERY_ENDPOINT_URL"
_ENV_REGISTRY_DISCOVERY_REGION: Final[str] = "REGISTRY_DISCOVERY_ENDPOINT_REGION"
_DEFAULT_REGISTRY_DISCOVERY_REGION: Final[str] = "west"
_DEFAULT_AZURE_ENV_NAME: Final[str] = "AzureCloud"


_ASYNC_LOCK = asyncio.Lock()
_KNOWN_AZURE_ENVIRONMENTS: Dict[str, AzureEnvironmentMetadata] = {
    _DEFAULT_AZURE_ENV_NAME: {
        "portal_endpoint": "https://portal.azure.com/",
        "resource_manager_endpoint": "https://management.azure.com/",
        "active_directory_endpoint": "https://login.microsoftonline.com/",
        "aml_resource_endpoint": "https://ml.azure.com/",
        "storage_suffix": "core.windows.net",
        "registry_discovery_endpoint": "https://eastus.api.azureml.ms/",
    },
    "AzureChinaCloud": {
        "portal_endpoint": "https://portal.azure.cn/",
        "resource_manager_endpoint": "https://management.chinacloudapi.cn/",
        "active_directory_endpoint": "https://login.chinacloudapi.cn/",
        "aml_resource_endpoint": "https://ml.azure.cn/",
        "storage_suffix": "core.chinacloudapi.cn",
        "registry_discovery_endpoint": "https://chinaeast2.api.ml.azure.cn/",
    },
    "AzureUSGovernment": {
        "portal_endpoint": "https://portal.azure.us/",
        "resource_manager_endpoint": "https://management.usgovcloudapi.net/",
        "active_directory_endpoint": "https://login.microsoftonline.us/",
        "aml_resource_endpoint": "https://ml.azure.us/",
        "storage_suffix": "core.usgovcloudapi.net",
        "registry_discovery_endpoint": "https://usgovarizona.api.ml.azure.us/",
    },
}


class AzureEnvironmentClient:
    DEFAULT_API_VERSION: Final[str] = "2019-05-01"
    DEFAULT_AZURE_CLOUD_NAME: Final[str] = _DEFAULT_AZURE_ENV_NAME

    def __init__(self, *, base_url: Optional[str] = None, **kwargs: Any) -> None:
        base_url = base_url if base_url is not None else AzureEnvironmentClient.get_default_metadata_url()

        config: Configuration = kwargs.pop("config", Configuration(**kwargs))
        if config.retry_policy is None:
            config.retry_policy = AsyncRetryPolicy(**kwargs)
        if config.proxy_policy is None and "proxy" in kwargs:
            config.proxy_policy = ProxyPolicy(proxies={"http": kwargs["proxy"], "https": kwargs["proxy"]})

        self._async_client = AsyncPipelineClient(base_url, config=config, **kwargs)

    async def get_default_cloud_name_async(self, *, update_cached: bool = True) -> str:
        current_cloud_env = os.getenv(_ENV_DEFAULT_CLOUD_NAME)
        if current_cloud_env is not None:
            return current_cloud_env

        arm_metadata_url = os.getenv(_ENV_ARM_CLOUD_METADATA_URL)
        if arm_metadata_url is None:
            return _DEFAULT_AZURE_ENV_NAME

        # load clouds from metadata url
        clouds = await self.get_clouds_async(metadata_url=arm_metadata_url, update_cached=update_cached)
        matched = next(filter(lambda t: t[1]["resource_manager_endpoint"] in arm_metadata_url, clouds.items()), None)
        if matched is None:
            return _DEFAULT_AZURE_ENV_NAME

        os.environ[_ENV_DEFAULT_CLOUD_NAME] = matched[0]
        return matched[0]

    async def get_cloud_async(self, name: str, *, update_cached: bool = True) -> Optional[AzureEnvironmentMetadata]:
        default_endpoint: Optional[str]

        def case_insensitive_match(d: Mapping[str, Any], key: str) -> Optional[Any]:
            key = key.strip().lower()
            return next((v for k,v in d.items() if k.strip().lower() == key), None)

        async with _ASYNC_LOCK:
            cloud = _KNOWN_AZURE_ENVIRONMENTS.get(name) or case_insensitive_match(_KNOWN_AZURE_ENVIRONMENTS, name)
            if cloud:
                return cloud
            default_endpoint = (_KNOWN_AZURE_ENVIRONMENTS
                .get(_DEFAULT_AZURE_ENV_NAME, {})
                .get("resource_manager_endpoint"))

        metadata_url = self.get_default_metadata_url(default_endpoint)
        clouds = await self.get_clouds_async(metadata_url=metadata_url, update_cached=update_cached)
        cloud_metadata = clouds.get(name) or case_insensitive_match(clouds, name)

        return cloud_metadata

    async def get_clouds_async(
        self,
        *,
        metadata_url: Optional[str] = None,
        update_cached: bool = True
    ) -> Mapping[str, AzureEnvironmentMetadata]:
        metadata_url = metadata_url or self.get_default_metadata_url()

        clouds: Mapping[str, AzureEnvironmentMetadata]
        async with self._async_client.send_request(HttpRequest("GET", metadata_url)) as response:  # type: ignore
            response.raise_for_status()
            clouds = await self._parse_cloud_endpoints_async(response.json())

        if update_cached:
            async with _ASYNC_LOCK:
                recursive_update(_KNOWN_AZURE_ENVIRONMENTS, clouds)
        return clouds

    async def close(self) -> None:
        await self._async_client.close()

    @staticmethod
    def get_default_metadata_url(default_endpoint: Optional[str] = None) -> str:
        default_endpoint = default_endpoint or "https://management.azure.com/"
        metadata_url = os.getenv(
            _ENV_ARM_CLOUD_METADATA_URL,
            f"{default_endpoint}metadata/endpoints?api-version={AzureEnvironmentClient.DEFAULT_API_VERSION}")
        return metadata_url

    @staticmethod
    async def _get_registry_discovery_url_async(cloud_name: str, cloud_suffix: str) -> str:
        async with _ASYNC_LOCK:
            discovery_url = _KNOWN_AZURE_ENVIRONMENTS.get(cloud_name, {}).get("registry_discovery_endpoint")
            if discovery_url:
                return discovery_url

        discovery_url = os.getenv(_ENV_REGISTRY_DISCOVERY_URL)
        if discovery_url is not None:
            return discovery_url

        region = os.getenv(_ENV_REGISTRY_DISCOVERY_REGION, _DEFAULT_REGISTRY_DISCOVERY_REGION)
        return f"https://{cloud_name.lower()}{region}.api.ml.azure.{cloud_suffix}/"

    @staticmethod
    async def _parse_cloud_endpoints_async(data: Any) -> Mapping[str, AzureEnvironmentMetadata]:
        # If there is only one cloud, you will get a dict, otherwise a list of dicts
        cloud_data: Sequence[Mapping[str, Any]] = data if not isinstance(data, dict) else [data]
        clouds: Dict[str, AzureEnvironmentMetadata] = {}

        def append_trailing_slash(url: str) -> str:
            return url if url.endswith("/") else f"{url}/"

        for cloud in cloud_data:
            try:
                name: str = cloud["name"]
                portal_endpoint: str = cloud["portal"]
                cloud_suffix = ".".join(portal_endpoint.split(".")[2:]).replace("/", "")
                discovery_url = await AzureEnvironmentClient._get_registry_discovery_url_async(name, cloud_suffix)
                clouds[name] = {
                    "portal_endpoint": append_trailing_slash(portal_endpoint),
                    "resource_manager_endpoint": append_trailing_slash(cloud["resourceManager"]),
                    "active_directory_endpoint": append_trailing_slash(cloud["authentication"]["loginEndpoint"]),
                    "aml_resource_endpoint": append_trailing_slash(f"https://ml.azure.{cloud_suffix}/"),
                    "storage_suffix": cloud["suffixes"]["storage"],
                    "registry_discovery_endpoint": append_trailing_slash(discovery_url),
                }
            except KeyError:
                continue

        return clouds


def recursive_update(d: Dict, u: Mapping) -> None:
    """Recursively update a dictionary.
    
    :param Dict d: The dictionary to update.
    :param Mapping u: The mapping to update from.
    """
    for k, v in u.items():
        if isinstance(v, Dict) and k in d:
            recursive_update(d[k], v)
        else:
            d[k] = v
