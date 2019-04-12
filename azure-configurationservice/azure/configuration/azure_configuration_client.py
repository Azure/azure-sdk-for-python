# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from datetime import datetime

from msrest.pipeline.requests import PipelineRequestsHTTPSender, RequestsPatchSession
from msrest.pipeline import Request, Pipeline
from msrest.universal_http.requests import RequestsHTTPSender

from . import _generated
from ._generated.models import ConfigurationSetting

from .azure_configuration_requests import AzConfigRequestsCredentialsPolicy
from .azure_configuration_client_abstract import AzureConfigurationClientAbstract
from .utils import get_endpoint_from_connection_string


class AzureConfigurationClient(AzureConfigurationClientAbstract):
    __doc__ = AzureConfigurationClientAbstract.__doc__

    def __init__(self, connection_string):

        base_url = "https://" + get_endpoint_from_connection_string(connection_string)
        self._impl = _generated.AzureConfigurationClientImp(
            connection_string, base_url
        )
        self._impl._client.config.pipeline = self._create_azconfig_pipeline()

    def _create_azconfig_pipeline(self):
        policies = [
            self._impl.config.user_agent_policy,  # UserAgent policy
            RequestsPatchSession(),  # Support deprecated operation config at the session level
            self._impl.config.http_logger_policy,  # HTTP request/response log
            AzConfigRequestsCredentialsPolicy(self._impl.config),
        ]

        return Pipeline(
            policies,
            PipelineRequestsHTTPSender(
                RequestsHTTPSender(self._impl.config)
            ),  # Send HTTP request using requests
        )

    def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):
        # type: (str, str, str, dict, str, str, dict) -> ConfigurationSetting

        __doc__ = super().__class__.__doc__

        custom_headers = AzureConfigurationClientAbstract.prep_update_configuration_setting(key, etag, **kwargs)

        current_configuration_setting = self._impl.get_configuration_setting(
            key, label
        )
        if value is not None:
            current_configuration_setting.value = value
        if content_type is not None:
            current_configuration_setting.content_type = content_type
        if tags is not None:
            current_configuration_setting.tags = tags
        return self._impl.create_or_update_configuration_setting(
            configuration_setting=current_configuration_setting,
            key=key,
            label=label,
            custom_headers=custom_headers,
        )