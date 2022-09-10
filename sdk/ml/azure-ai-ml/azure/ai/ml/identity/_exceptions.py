# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.core.exceptions import ClientAuthenticationError


class CredentialUnavailableError(ClientAuthenticationError):
    """The credential did not attempt to authenticate because required data or state is unavailable."""
