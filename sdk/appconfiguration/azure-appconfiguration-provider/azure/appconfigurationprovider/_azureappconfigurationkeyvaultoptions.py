# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class AzureAppConfigurationKeyVaultOptions:

    def __init__(self, credential=None, secret_clients=None, secret_resolver=None):
        """
        credential, secret_clients (clients for connecting to multiple key vaults with different credentials), secret_resolver
        """
        self.credential = credential
        self.secret_clients = secret_clients
        self.secret_resolver = secret_resolver
