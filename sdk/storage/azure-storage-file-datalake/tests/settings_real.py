# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# NOTE: these keys are fake, but valid base-64 data, they were generated using:
# base64.b64encode(os.urandom(64))
STORAGE_ACCOUNT_NAME = "emilystageaccount"
STORAGE_ACCOUNT_KEY = "itrQjOZ72UwPJgMBebaxQb18AT19r1i+FRipReO5htNuarcw5A1htWTiWEHWooCsaUZDYM0smd3Zqom5spP/PA=="
STORAGE_DATA_LAKE_ACCOUNT_NAME = 'xiafuhns'
STORAGE_DATA_LAKE_ACCOUNT_KEY = "aR4FWKsZ0SDojBn6Yj2sOitrVPvRoE8HdaPAyoTD3VXS7/9+zArc8Rst1Kj5y1WkaXUz6o5NXnOzoLVw5eTbCQ=="

# STORAGE_ACCOUNT_NAME = "emilydevtest"
# STORAGE_ACCOUNT_KEY = "ERK9NVzqkrkUCwXyAGpIp7LKr6Jc3eZVFp+ygPIAOB7CMBTQ3rlgGImBJp8eyBV3JL0wnpas7UBFs0xlxHJSWA=="
BLOB_STORAGE_ACCOUNT_NAME = "blobstoragename"
BLOB_STORAGE_ACCOUNT_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="
REMOTE_STORAGE_ACCOUNT_NAME = "emilystageaccount"
REMOTE_STORAGE_ACCOUNT_KEY = "MBU1D9S8fPyc88L8LO45i+TpUCyAgKBhhu+zUQkEishdPZaVzkHWl5yeeCJmt3mZ+4r4dMjtMZ4KtbG3TP3vfA=="
PREMIUM_STORAGE_ACCOUNT_NAME = "premiumstoragename"
PREMIUM_STORAGE_ACCOUNT_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="
# OAUTH_STORAGE_ACCOUNT_NAME = "zestageoauth"
# OAUTH_STORAGE_ACCOUNT_KEY = "XBB/q/JtBoMBlekznQwAzDJHvZO1gJmCh8CUT12Gv5aCkWaDeGA=="
OAUTH_STORAGE_ACCOUNT_NAME = "emilydevtest"
OAUTH_STORAGE_ACCOUNT_KEY = "ERK9NVzqkrkUCwXyAGpIp7LKr6Jc3eZVFp+ygPIAOB7CMBTQ3rlgGImBJp8eyBV3JL0wnpas7UBFs0xlxHJSWA=="

# Configurations related to Active Directory, which is used to obtain a token credential
ACTIVE_DIRECTORY_APPLICATION_ID = "68390a19-a643-458b-b726-408abf67b4fc"
ACTIVE_DIRECTORY_APPLICATION_SECRET = "3Usxz7pzkOeE7flc6Z187ubs5/cJnszGPjAiXmcwhaY="
ACTIVE_DIRECTORY_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
ACTIVE_DIRECTORY_AUTH_ENDPOINT = "https://login.microsoftonline.com"

# Use instead of STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY if custom settings are needed
CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=emilydevtest;AccountKey=ERK9NVzqkrkUCwXyAGpIp7LKr6Jc3eZVFp+ygPIAOB7CMBTQ3rlgGImBJp8eyBV3JL0wnpas7UBFs0xlxHJSWA==;EndpointSuffix=core.windows.net"
BLOB_CONNECTION_STRING = ""
PREMIUM_CONNECTION_STRING = ""
# Use 'https' or 'http' protocol for sending requests, 'https' highly recommended
PROTOCOL = "http"

# Set to true if server side file encryption is enabled
IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED = True

# Decide which test mode to run against. Possible options:
#   - Playback: run against stored recordings
#   - Record: run tests against live storage and update recordings
#   - RunLiveNoRecord: run tests against live storage without altering recordings
TEST_MODE = 'RunLiveNoRecord'

# Set to true to enable logging for the tests
# logging is not enabled by default because it pollutes the CI logs
ENABLE_LOGGING = True

# Set up proxy support
USE_PROXY = False
PROXY_HOST = "192.168.15.116"
PROXY_PORT = "8118"
PROXY_USER = ""
PROXY_PASSWORD = ""
