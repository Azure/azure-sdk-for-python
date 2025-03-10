# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from azure.core.configuration import Configuration
from azure.core.pipeline.policies import RedirectPolicy, ProxyPolicy

# This code violates config-missing-kwargs-in-policy

class TestFindsConfigPoliciesWithoutKwargs():
    def create_configuration(self, **kwargs):
        config = Configuration(**kwargs)
        config.headers_policy = kwargs.get('headers_policy')
        config.user_agent_policy = kwargs.get('user_agent_policy')
        config.retry_policy = kwargs.get('retry_policy')
        config.redirect_policy = RedirectPolicy(**kwargs)
        config.logging_policy = kwargs.get('logging_policy')
        config.proxy_policy = ProxyPolicy()
        return config

    @staticmethod
    def create_config(credential, api_version="08", **kwargs):
        config = Configuration(**kwargs)
        config.credential = credential
        config.api_version = api_version
        return config
