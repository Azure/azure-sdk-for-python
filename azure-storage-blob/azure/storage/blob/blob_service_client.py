# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, Iterable, Dict, List,
    TYPE_CHECKING
)

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport
from azure.core.pipeline.policies import (
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
    NetworkTraceLoggingPolicy,
    ProxyPolicy
)

from ._generated import AzureBlobStorage
from .container_client import ContainerClient

if TYPE_CHECKING:
    from datetime import datetime
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.pipeline.policies import HTTPPolicy
    from .models import (
        AccountPermissions,
        ResourceTypes,
        ContainerProperties
    )


class BlobServiceClient(object):

    def __init__(
            self, url,  # type: str
            credentials=None,  # type: Optional[HTTPPolicy]
            configuration=None, # type: Optional[Configuration]
            **kwargs  # type: Any
        ):
        # type: (...) -> None
        config = configuration or BlobServiceClient.create_configuration(**kwargs)
        transport = kwargs.get('transport')
        if not transport:
            transport = RequestsTransport(config)
        pipeline = self._create_pipeline(config, transport, credentials)
        self._client = AzureBlobStorage(url, pipeline=pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        # type: (**Any) -> Configuration
        config = Configuration(**kwargs)
        config.headers_policy = HeadersPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.redirect_policy = RedirectPolicy(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config

    def _create_pipeline(self, config, transport, credentials):  # pylint: disable=no-self-use
        # type: (Configuration, HttpTransport, Optional[HTTPPolicy]) -> Pipeline
        policies = [
            config.user_agent_policy,
            config.headers_policy,
            credentials,
            ContentDecodePolicy(),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        return Pipeline(transport, policies=policies)

    def make_url(self, protocol=None, sas_token=None):
        # type: (Optional[str], Optional[str]) -> str
        pass

    def generate_shared_access_signature(
            self, resource_types,  # type: Union[ResourceTypes, str]
            permission,  # type: Union[AccountPermissions, str]
            expiry,  # type: Optional[Union[datetime, str]]
            start=None,  # type: Optional[Union[datetime, str]]
            ip=None,  # type: Optional[str]
            protocol=None  # type: Optional[str]
        ):
        pass

    def get_account_information(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, str]
        """
        :returns: A dict of account information (SKU and account type).
        """

    def get_service_stats(self, timeout=None):
        # type: (Optional[int]) -> Dict[str, Any]
        """
        :returns ServiceStats.
        """
        response = self._client.service.get_statistics(timeout=timeout)  # type: Dict[str, Any]
        return response.__dict__

    def get_service_properties(self, timeout=None):
        # type(Optional[int]) -> Dict[str, Any]
        """
        :returns: A dict of service properties.
        """

    def set_service_properties(
            self, logging=None,  # type: Any
            hour_metrics=None,  # type: Any
            minute_metrics=None,  # type: Any
            cors=None,  # type: List[Any]
            target_version=None,  # type: Optional[str]
            timeout=None,  # type: Optional[int]
            delete_retention_policy=None,  # type: Any
            static_website=None  # type: Any
        ):
        # type: (...) -> None
        """
        TODO: Fix type hints
        :returns: None
        """

    def list_container_properties(
            self, prefix=None,  # type: Optional[str]
            include_metadata=False,  # type: Optional[bool]
            timeout=None  # type: Optional[int]
        ):
        # type: (...) -> Iterable[ContainerProperties]
        """
        :returns: An iterable (auto-paging) of ContainerProperties.
        """

    def get_container_client(self, container):
        # type: (Union[ContainerProperties, str]) -> ContainerClient
        """
        :returns: A ContainerClient.
        """
