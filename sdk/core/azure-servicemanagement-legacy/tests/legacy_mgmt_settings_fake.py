#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from azure.common.credentials import (
    BasicTokenAuthentication,
    UserPassCredentials
)

# NOTE: these keys are fake, but valid base-64 data, they were generated using:
# base64.b64encode(os.urandom(64))

CONN_TYPE_WINHTTP = 'winhttp'
CONN_TYPE_HTTPLIB = 'httplib'
CONN_TYPE_REQUESTS_TOKEN = 'requests_with_token'
CONN_TYPE_REQUESTS_CERT = 'requests_with_cert'

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
STORAGE_ACCOUNT_NAME = "storagename"
STORAGE_ACCOUNT_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="
SERVICEBUS_NAME = "fakesbnamespace"
CONNECTION_TYPE = CONN_TYPE_REQUESTS_TOKEN
PFX_LOCATION = "CURRENT_USER\\my\\<certificate name here>"
PEM_PATH = "<path to .pem file>"
LINUX_OS_VHD = "http://storagename.blob.core.windows.net/inputtestdatadonotdelete/ubuntu.vhd"
LINUX_VM_REMOTE_SOURCE_IMAGE_LINK = "https://portalvhds13tr49m9hm1m6.blob.core.windows.net/vhds/huvalotestub-image-os-2014-11-06.vhd"
LINUX_VM_IMAGE_NAME = "unittest-donotdelete-ubuntu1404"

USE_PROXY = False
PROXY_HOST = "192.168.15.116"
PROXY_PORT = "8118"
PROXY_USER = ""
PROXY_PASSWORD = ""

# Read for details of this file:
# https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests

def get_credentials():
    # Put your credentials here in the "real" file
    #return UserPassCredentials(
    #    'user@myaddomain.onmicrosoft.com',
    #    'Password'
    #)
    # Needed to play recorded tests
    return BasicTokenAuthentication(
        token = {
            'access_token':'faked_token'
        }
    )
# The easiest way to create a Linux OS vhd is to use the Azure management
# portal to create a Linux VM, and have it store the VHD in the
# storage account listed in the test settings file.  Then stop the VM,
# and use the following code to copy the VHD to another blob (if you
# try to use the VM's VHD directly without making a copy, you will get
# conflict errors).

# sourceblob = '/{0}/{1}/{2}'.format(STORAGE_ACCOUNT_NAME, 'vhdcontainername', 'vhdblobname')
# blob_service.copy_blob('vhdcontainername', 'targetvhdblobname', sourceblob)
#
# LINUX_OS_VHD = "http://storageservicesname.blob.core.windows.net/vhdcontainername/targetvhdblobname"

