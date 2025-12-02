# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys
from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy

NO_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. No authentication token audience was provided. "
    "Please set the audience via credential_scopes when constructing AzureAppConfigurationClient for the target cloud. "
    "For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
INCORRECT_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. An incorrect token audience was provided. "
    "Please set the audience via credential_scopes when constructing AzureAppConfigurationClient to the appropriate audience for this cloud. "
    "For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
AAD_AUDIENCE_ERROR_CODE = "AADSTS500011"


class AudiencePolicy(SansIOHTTPPolicy):
    def __init__(self, audience=None):
        self.audience = audience

    def on_exception(self, request: PipelineRequest):
        ex_type, ex_value, _ = sys.exc_info()
        if ex_type is None:
            return None
        if ex_type is ClientAuthenticationError:
            self._handle_audience_exception(ex_value)
        return ex_value

    def _handle_audience_exception(self, ex):
        if ex.message and AAD_AUDIENCE_ERROR_CODE in ex.message:
            message = NO_AUDIENCE_ERROR_MESSAGE if self.audience is None else INCORRECT_AUDIENCE_ERROR_MESSAGE
            err = ClientAuthenticationError(message, ex.response)
            err.message = message
            raise err
