# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    keyvault_secret_url="https://Sanitized.vault.azure.net/secrets/fake-secret/",
    appconfiguration_keyvault_secret_url="https://Sanitized.vault.azure.net/secrets/fake-secret/",
    keyvault_secret_url2="https://Sanitized.vault.azure.net/secrets/fake-secret2/",
    appconfiguration_keyvault_secret_url2="https://Sanitized.vault.azure.net/secrets/fake-secret2/",
    appconfiguration_connection_string="Endpoint=https://Sanitized.azconfig.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=lamefakesecretlamefakesecretlamefakesecrett=",
    appconfiguration_endpoint_string="https://Sanitized.azconfig.io",
)
