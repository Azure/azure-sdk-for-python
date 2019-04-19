# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import sys
import platform
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AsyncioRequestsTransport

from .._generated.aio import AzureConfigurationClientImp
from .._generated.aio import AzureConfigurationClientImpConfiguration

from ..azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from ..azure_configuration_client_abstract import AzureConfigurationClientAbstract
from azure.core import ResourceModifiedError, ResourceNotFoundError


from ..utils import get_endpoint_from_connection_string


class AzureConfigurationClient(AzureConfigurationClientAbstract):
    __doc__ = AzureConfigurationClientAbstract.__doc__

    def __init__(self, connection_string):

        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        program_name = os.path.basename(sys.argv[0]) or "noprogram"
        self.config = AzureConfigurationClientImpConfiguration(
            connection_string,
            base_user_agent=program_name,
            logging_enable=True,
        )
        self.config.user_agent_policy.add_user_agent("{}{}".format(platform.python_implementation(), platform.python_version()))
        self.config.user_agent_policy.add_user_agent(platform.platform())
        self._impl = AzureConfigurationClientImp(connection_string, base_url, config=self.config)
        self._impl.pipeline = self._create_azconfig_pipeline()

    def _create_azconfig_pipeline(self):
        policies = [
            self.config.user_agent_policy,  # UserAgent policy
            self.config.logging_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self.config.credentials)
        ]

        return AsyncPipeline(
            AsyncioRequestsTransport(self.config),  # Send HTTP request using requests
            policies
        )

    async def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):
        __doc__ = super().__doc__

        custom_headers = AzureConfigurationClientAbstract.prep_update_configuration_setting(key, etag, **kwargs)
        current_configuration_setting = await self.get_configuration_setting(
            key, label
        )
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return await self._impl.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            custom_headers=custom_headers,
            error_map={
                404: ResourceNotFoundError,
                412: ResourceModifiedError,
            },
        )

