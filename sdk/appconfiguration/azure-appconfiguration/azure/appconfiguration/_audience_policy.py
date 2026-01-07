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
    "Unable to authenticate to Azure App Configuration. No authentication token audience was provided. Please set the "
    "audience via credential_scopes when constructing AzureAppConfigurationClient for the target cloud. For details on "
    "how to configure the authentication token audience visit https://aka.ms/appconfig/client-token-audience."
)
INCORRECT_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. An incorrect token audience was provided. Please set the "
    "audience via credential_scopes when constructing AzureAppConfigurationClient to the appropriate audience for this "
    "cloud. For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
AAD_AUDIENCE_ERROR_CODE = "AADSTS500011"


class AudienceErrorHandlingPolicy(SansIOHTTPPolicy):
    """
    A policy to handle audience-related authentication errors for Azure App Configuration.
    Raises a ClientAuthenticationError with a helpful message if the audience is missing or incorrect.
    """

    def __init__(self, has_audience: bool = False):
        """
        Initialize the AudienceErrorHandlingPolicy.

        :param has_audience: Indicates if the expected audience is set for the authentication token.
        :type has_audience: bool
        """
        self.has_audience = has_audience

    def on_exception(self, request: PipelineRequest):
        """
        Handles exceptions raised during pipeline execution.
        If the exception is a ClientAuthenticationError related to audience, raises a more descriptive error.

        :param request: The pipeline request object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The exception if not handled, otherwise raises a new error.
        """
        ex_type, ex_value, _ = sys.exc_info()
        if ex_type is None:
            return None
        if ex_type is ClientAuthenticationError and isinstance(ex_value, ClientAuthenticationError):
            self._handle_audience_exception(ex_value)
        return ex_value

    def _handle_audience_exception(self, ex: ClientAuthenticationError):
        """
        Checks the exception message for audience errors and raises a descriptive ClientAuthenticationError.

        :param ex: The exception to check and potentially re-raise.
        :type ex: ClientAuthenticationError
        """
        if ex.message and AAD_AUDIENCE_ERROR_CODE in ex.message:
            message = INCORRECT_AUDIENCE_ERROR_MESSAGE if self.has_audience else NO_AUDIENCE_ERROR_MESSAGE
            err = ClientAuthenticationError(message, ex.response)
            err.message = message
            raise err
