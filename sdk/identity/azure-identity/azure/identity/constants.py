# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class EnvironmentVariables:
    AZURE_CLIENT_ID = "AZURE_CLIENT_ID"
    AZURE_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
    AZURE_TENANT_ID = "AZURE_TENANT_ID"
    CLIENT_SECRET_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)

    AZURE_CLIENT_CERTIFICATE_PATH = "AZURE_CLIENT_CERTIFICATE_PATH"
    CERT_VARS = (AZURE_CLIENT_ID, AZURE_CLIENT_CERTIFICATE_PATH, AZURE_TENANT_ID)


class Endpoints:
    # https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/how-to-use-vm-token#get-a-token-using-http
    IMDS = "http://169.254.169.254/metadata/identity/oauth2/token"

    # TODO: other clouds have other endpoints
    AAD_OAUTH2_V2_FORMAT = "https://login.microsoftonline.com/{}/oauth2/v2.0/token"

    # https://docs.microsoft.com/en-us/azure/app-service/overview-managed-identity#obtaining-tokens-for-azure-resources

MSI_ENDPOINT = "MSI_ENDPOINT"
MSI_SECRET = "MSI_SECRET"
