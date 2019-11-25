# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# NOTE: these keys are fake, but valid base-64 data, they were generated using:
# base64.b64encode(os.urandom(64))

import os

STORAGE_ACCOUNT_NAME = os.getenv('STORAGE_ACCOUNT_NAME', "storagename")
STORAGE_ACCOUNT_KEY = os.getenv('STORAGE_ACCOUNT_KEY', "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==")
BLOB_STORAGE_ACCOUNT_NAME = os.getenv('BLOB_STORAGE_ACCOUNT_NAME', "blobstoragename")
BLOB_STORAGE_ACCOUNT_KEY = os.getenv('BLOB_STORAGE_ACCOUNT_KEY', "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==")
REMOTE_STORAGE_ACCOUNT_NAME = os.getenv('REMOTE_STORAGE_ACCOUNT_NAME', "storagename")
REMOTE_STORAGE_ACCOUNT_KEY = os.getenv('REMOTE_STORAGE_ACCOUNT_KEY', "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==")
PREMIUM_STORAGE_ACCOUNT_NAME = os.getenv('PREMIUM_STORAGE_ACCOUNT_NAME', "premiumstoragename")
PREMIUM_STORAGE_ACCOUNT_KEY = os.getenv('PREMIUM_STORAGE_ACCOUNT_KEY', "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==")
OAUTH_STORAGE_ACCOUNT_NAME = os.getenv('OAUTH_STORAGE_ACCOUNT_NAME', "oauthstoragename")
OAUTH_STORAGE_ACCOUNT_KEY = os.getenv('OAUTH_STORAGE_ACCOUNT_KEY', "XBB/YoZ41bDFBW1VcgCBNYmA1PDlc3NvQQaCk2rb/JtBoMBlekznQwAzDJHvZO1gJmCh8CUT12Gv3aCkWaDeGA==")

# Configurations related to Active Directory, which is used to obtain a token credential
ACTIVE_DIRECTORY_APPLICATION_ID = os.getenv('ACTIVE_DIRECTORY_APPLICATION_ID', "68390a19-a897-236b-b453-488abf67b4fc")
ACTIVE_DIRECTORY_APPLICATION_SECRET = os.getenv('ACTIVE_DIRECTORY_APPLICATION_SECRET', "3Ujhg7pzkOeE7flc6Z187ugf5/cJnszGPjAiXmcwhaY=")
ACTIVE_DIRECTORY_TENANT_ID = os.getenv('ACTIVE_DIRECTORY_TENANT_ID', "32f988bf-54f1-15af-36ab-2d7cd364db47")

# Use instead of STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY if custom settings are needed
CONNECTION_STRING = os.getenv('CONNECTION_STRING', "DefaultEndpointsProtocol=https;AccountName=storagename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net")
BLOB_CONNECTION_STRING = os.getenv('BLOB_CONNECTION_STRING', "DefaultEndpointsProtocol=https;AccountName=blobstoragename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net")
PREMIUM_CONNECTION_STRING = os.getenv('PREMIUM_CONNECTION_STRING', "DefaultEndpointsProtocol=https;AccountName=premiumstoragename;AccountKey=NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg==;EndpointSuffix=core.windows.net")
# Use 'https' or 'http' protocol for sending requests, 'https' highly recommended
PROTOCOL = os.getenv('PROTOCOL', "https")

# Set to true if server side file encryption is enabled
IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED = True

# Decide which test mode to run against. Possible options:
#   - Playback: run against stored recordings
#   - Record: run tests against live storage and update recordings
#   - RunLiveNoRecord: run tests against live storage without altering recordings
TEST_MODE = os.getenv('TEST_MODE', 'Playback')

# Set to true to enable logging for the tests
# logging is not enabled by default because it pollutes the CI logs
ENABLE_LOGGING = False

# Set up proxy support
USE_PROXY = False
PROXY_HOST = "192.168.15.116"
PROXY_PORT = "8118"
PROXY_USER = ""
PROXY_PASSWORD = ""
