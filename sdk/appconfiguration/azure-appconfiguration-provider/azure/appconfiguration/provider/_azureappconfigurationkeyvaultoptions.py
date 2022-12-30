# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


class AzureAppConfigurationKeyVaultOptions:
    """
    Options for connecting to Key Vault.

    :param credential: A credential for authenticating with the key vault. This is optional if secret_clients is
     provided.
    :type credential: ~azure.core.credentials.TokenCredential
    :param secret_clients: A list of SecretClient from azure-keyvault-secrets. This is optional if credential is
     provided.
    :type secret_clients: list[~azure.keyvault.secrets.SecretClient]
    :param secret_resolver: A function that takes a URI and returns a value.
    :type secret_resolver: callable
    """

    def __init__(self, credential=None, secret_clients=None, secret_resolver=None):
        # type: (TokenCredential, List[SecretClient], Callable) -> None
        self.credential = credential
        self.secret_clients = secret_clients
        self.secret_resolver = secret_resolver

        if self.secret_clients is None:
            self.secret_clients = {}
