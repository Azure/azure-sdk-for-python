# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from typing import Any, TYPE_CHECKING
import six

from azure.core.pipeline.policies import SansIOHTTPPolicy

if TYPE_CHECKING:
    from azure.core.credentials import AzureSasCredential


class EventGridSasCredentialPolicy(SansIOHTTPPolicy):
    """Adds a token header for the provided credential.
    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.core.credentials.AzureSasCredential
    :param str name: The name of the token header used for the credential.
    :raises: ValueError or TypeError
    """

    def __init__(self, credential, name, **kwargs):  # pylint: disable=unused-argument
        # type: (AzureSasCredential, str, Any) -> None
        super(EventGridSasCredentialPolicy, self).__init__()
        self._credential = credential
        if not name:
            raise ValueError("name can not be None or empty")
        if not isinstance(name, six.string_types):
            raise TypeError("name must be a string.")
        self._name = name

    def on_request(self, request):
        # Request must contain one of the following authorization signature: aeg-sas-token, aeg-sas-key
        request.http_request.headers[self._name] = self._credential.signature
