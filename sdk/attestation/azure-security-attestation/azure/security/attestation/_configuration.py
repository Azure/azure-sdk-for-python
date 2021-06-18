# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import NoReturn, TYPE_CHECKING

from azure.core.configuration import Configuration
from azure.core.pipeline import policies

from ._version import VERSION
from ._models import TokenValidationOptions

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import TokenCredential


class AttestationClientConfiguration(Configuration):
    """Configuration for AttestationClient.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    :param instance_url: The attestation instance base URI, for example https://mytenant.attest.azure.net.
    :type instance_url: str
    :keyword validation_options: Optional token validation options.
    :type validation_options: TokenValidationOptions
    """

    def __init__(
        self,
        credential,  # type: "TokenCredential"
        instance_url,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
#        if credential is None:
#            raise ValueError("Parameter 'credential' must not be None.")
#        if instance_url is None:
#            raise ValueError("Parameter 'instance_url' must not be None.")
        super(AttestationClientConfiguration, self).__init__(**kwargs)

        self.token_validation_options = kwargs.pop('token_validation_options',
            TokenValidationOptions(validate_token=True)) # type: TokenValidationOptions
#        self.credential = credential
#        self.instance_url = instance_url
