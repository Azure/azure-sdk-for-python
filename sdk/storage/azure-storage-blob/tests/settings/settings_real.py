# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

STORAGE_ACCOUNT_NAME = "tamerdevtest"
STORAGE_ACCOUNT_KEY = "hY4It1A68difJ/MSh35DCAPEIXB3i+pUq1b4d69vG8JZfUcaAV9I89T7SyAQly6zt1QiNyaeTT2+7AoBMSDMow=="

SECONDARY_STORAGE_ACCOUNT_NAME = "fakename"
SECONDARY_STORAGE_ACCOUNT_KEY = "fakekey"
BLOB_STORAGE_ACCOUNT_NAME = "fakename"
BLOB_STORAGE_ACCOUNT_KEY = "fakekey"
VERSIONED_STORAGE_ACCOUNT_NAME = "fakename"
VERSIONED_STORAGE_ACCOUNT_KEY = "fakekey"
PREMIUM_STORAGE_ACCOUNT_NAME = "fakename"
PREMIUM_STORAGE_ACCOUNT_KEY = "fakekey"
STORAGE_RESOURCE_GROUP_NAME = "fakename"

TENANT_ID = "00000000-0000-0000-0000-000000000000"
CLIENT_ID = "00000000-0000-0000-0000-000000000000"
CLIENT_SECRET = "00000000-0000-0000-0000-000000000000"

ACCOUNT_URL_SUFFIX = 'core.windows.net'
RUN_IN_LIVE = "True"
SKIP_LIVE_RECORDING = "True"

PROTOCOL = "https"



#-----------------------------------------------------------------------------------------------------------------------
# # -------------------------------------------------------------------------
# # Copyright (c) Microsoft Corporation. All rights reserved.
# # Licensed under the MIT License. See License.txt in the project root for
# # license information.
# # --------------------------------------------------------------------------
#
# # NOTE: these keys are fake, but valid base-64 data, they were generated using:
# # base64.b64encode(os.urandom(64))
#
# import os
#
# STORAGE_DATA_LAKE_ACCOUNT_NAME = "seannsecanary"
# STORAGE_DATA_LAKE_ACCOUNT_KEY = "jQSiRFbxmqawspccEYDwStgh/uZY68gpSx4qDsgJTYGNjI0GhX/HmEz2i1zReWtmzE1tyruYRzbjxJp6jIIhYw=="
#
# # Configurations related to Active Directory, which is used to obtain a token credential
# ACTIVE_DIRECTORY_TENANT_ID = os.getenv('ACTIVE_DIRECTORY_TENANT_ID', "72f988bf-86f1-41af-91ab-2d7cd011db47")
# ACTIVE_DIRECTORY_APPLICATION_ID = os.getenv('ACTIVE_DIRECTORY_APPLICATION_ID', "68390a19-a643-458b-b726-408abf67b4fc")
# ACTIVE_DIRECTORY_APPLICATION_SECRET = os.getenv('ACTIVE_DIRECTORY_APPLICATION_SECRET', "nc~7Kk3fEyo_4oVE7ziNWs1~g2l7CFO_AN")
#
# # Use instead of STORAGE_ACCOUNT_NAME and STORAGE_ACCOUNT_KEY if custom settings are needed
# CONNECTION_STRING = os.getenv('CONNECTION_STRING', "DefaultEndpointsProtocol=https;AccountName=emilydevtest;AccountKey=RprwXjTuqZirPsnX980WinVcRQaP382OhXSFI4gJWSX6pJsK4dqBaStS78/2uScIFIqXgVMHhnmCdMLH5kbFaQ==;EndpointSuffix=core.windows.net==;EndpointSuffix=core.windows.net")
#
# # Use 'https' or 'http' protocol for sending requests, 'https' highly recommended
# PROTOCOL = "https"
#
# # Set to true if server side file encryption is enabled
# IS_SERVER_SIDE_FILE_ENCRYPTION_ENABLED = True
#
# # Decide which test mode to run against. Possible options:
# #   - Playback: run against stored recordings
# #   - Record: run tests against live storage and update recordings
# #   - RunLiveNoRecord: run tests against live storage without altering recordings
# TEST_MODE = "Record"
#
# # Set to true to enable logging for the tests
# # logging is not enabled by default because it pollutes the CI logs
# ENABLE_LOGGING = False
#
# # Set up proxy support
# USE_PROXY = False
# PROXY_HOST = "192.168.15.116"
# PROXY_PORT = "8118"
# PROXY_USER = ""
# PROXY_PASSWORD = ""
#
# STORAGE_ACCOUNT_KEY = "ZZzqTjkCd0t+eu2YDRcKW/dr7B1ASmLbMQlnE8EwZu7/zpi5nY7b4ACIcJtXXFsJ0J5HJInIyBA7OR4SKnkRLg=="
# STORAGE_ACCOUNT_NAME = "seanstageoauth"
# AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=seanstageoauth;AccountKey=ZZzqTjkCd0t+eu2YDRcKW/dr7B1ASmLbMQlnE8EwZu7/zpi5nY7b4ACIcJtXXFsJ0J5HJInIyBA7OR4SKnkRLg==;EndpointSuffix=core.windows.net"
# RUN_IN_LIVE = "True"
# SKIP_LIVE_RECORDING = "False"
# ACCOUNT_URL_SUFFIX = 'core.windows.net'
#
