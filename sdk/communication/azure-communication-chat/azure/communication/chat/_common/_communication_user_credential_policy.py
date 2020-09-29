# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.core.pipeline.policies import SansIOHTTPPolicy

HEADER_NAME = "Authorization"


class CommunicationUserCredentialPolicy(SansIOHTTPPolicy):
    """Adds a key header for the provided credential.

    :param credential: The credential used to authenticate requests.
    :type credential: ~azure.communication.chat.common.CommunicationUserCredential
    """
    def __init__(self, credential, **kwargs):  # pylint: disable=unused-argument
        # type: (CommunicationUserCredential, str, Any) -> None
        super(CommunicationUserCredentialPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request):
        request.http_request.headers[HEADER_NAME] = "Bearer " + self._credential.get_token().token
