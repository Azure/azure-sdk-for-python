# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class EnvironmentVariables:
    # TODO: align cross-language
    AZURE_CLIENT_ID = "AZURE_CLIENT_ID"
    AZURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
    AZURE_TENANT_ID = "AZURE_TENANT_ID"
    CLIENT_SECRET_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

    AZURE_PRIVATE_KEY_FILE = "AZURE_PRIVATE_KEY_FILE"
    AZURE_THUMBPRINT = "AZURE_THUMBPRINT"
    CERT_VARS = (AZURE_CLIENT_ID, AZURE_PRIVATE_KEY_FILE, AZURE_TENANT_ID, AZURE_THUMBPRINT)


# https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http
IMDS_ENDPOINT = "http://169.254.169.254/metadata/identity/oauth2/token"

OAUTH_ENDPOINT = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"
