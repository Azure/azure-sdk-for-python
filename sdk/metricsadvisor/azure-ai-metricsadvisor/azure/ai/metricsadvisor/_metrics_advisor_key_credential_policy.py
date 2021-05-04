# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any
from azure.core.pipeline.policies import SansIOHTTPPolicy
from ._metrics_advisor_key_credential import MetricsAdvisorKeyCredential

_API_KEY_HEADER_NAME = "Ocp-Apim-Subscription-Key"
_X_API_KEY_HEADER_NAME = "x-api-key"


class MetricsAdvisorKeyCredentialPolicy(SansIOHTTPPolicy):
    """Adds a key header for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :param str name: The name of the key header used for the credential.
    :raises: ValueError or TypeError
    """
    def __init__(self, credential, **kwargs):  # pylint: disable=unused-argument
        # type: (MetricsAdvisorKeyCredential, Any) -> None
        super(MetricsAdvisorKeyCredentialPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request):
        request.http_request.headers[_API_KEY_HEADER_NAME] = self._credential.subscription_key
        request.http_request.headers[_X_API_KEY_HEADER_NAME] = self._credential.api_key
