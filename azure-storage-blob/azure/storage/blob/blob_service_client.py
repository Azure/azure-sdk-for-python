# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import RequestsTransport, HttpRequest
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

class BlobServiceClient(object):

    def __init__(self, url, credentials=None, configuration=None, **kwargs):
        config = configuration or BlobServiceClient.create_configuration(**kwargs)
        transport = kwargs.get('transport')
        if not transport:
            transport = RequestsTransport(config)
        pipeline = self._create_pipeline(config, transport, credentials)
        self._client = AzureBlobStorage(url, pipeline=pipeline)

    @staticmethod
    def create_configuration(**kwargs):
        config = Configuration(**kwargs)
        config.headers_policy = HeadersPolicy(**kwargs)
        config.user_agent_policy = UserAgentPolicy(**kwargs)
        config.retry_policy = RetryPolicy(**kwargs)
        config.redirect_policy = RedirectPolicy(**kwargs)
        config.logging_policy = NetworkTraceLoggingPolicy(**kwargs)
        config.proxy_policy = ProxyPolicy(**kwargs)
        return config

    def _create_pipeline(self, config, transport, credentials):
        policies = [
            config.user_agent_policy,
            config.headers_policy,
            credentials,
            ContentDecodePolicy(),
            config.redirect_policy,
            config.retry_policy,
            config.logging_policy,
        ]
        self._pipeline = Pipeline(transport, policies=policies)

    def make_url(self, protocol=None, sas_token=None):
        pass

    def generate_shared_access_signature(self, resource_types, permission, expiry,
            start=None, ip=None, protocol=None):
        pass

    def get_account_information(self, timeout=None):
        """
        :returns: A dict of account information (SKU and account type).
        """
        pass

    def get_service_stats(self, timeout=None):
        """
        :returns ServiceStats.
        """
        return self._client.service.get_statistics(timeout=timeout)

    def get_service_properties(self, timeout=None):
        """
        :returns: A dict of service properties.
        """
        pass

    def set_service_properties(self, logging=None, hour_metrics=None, minute_metrics=None,
            cors=None, target_version=None, timeout=None, delete_retention_policy=None,
            static_website=None):
        """
        :returns: None
        """
        pass

    def list_container_properties(self, prefix=None, num_results=None, include_metadata=False,
            marker=None, timeout=None):
        """
        :returns: An iterable (auto-paging) of ContainerProperties.
        """
        pass

    def get_container_client(self, container):
        """
        :returns: A ContainerClient.
        """
        pass