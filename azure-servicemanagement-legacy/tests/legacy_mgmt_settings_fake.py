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
CONN_TYPE_REQUESTS_STRING_CERT = 'requests_with_string_cert'

SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
STORAGE_ACCOUNT_NAME = "storagename"
STORAGE_ACCOUNT_KEY = "NzhL3hKZbJBuJ2484dPTR+xF30kYaWSSCbs2BzLgVVI1woqeST/1IgqaLm6QAOTxtGvxctSNbIR/1hW8yH+bJg=="
SERVICEBUS_NAME = "fakesbnamespace"
CONNECTION_TYPE = CONN_TYPE_REQUESTS_CERT
PFX_LOCATION = "CURRENT_USER\\my\\<certificate name here>"
PEM_PATH = "<path to .pem file>"
PEM_STRING_VALID = """-----BEGIN CERTIFICATE-----
MIICsDCCAhmgAwIBAgIJAON7Ez7ITeWwMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIEwpTb21lLVN0YXRlMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTcwODI3MDI1MjQyWhcNMTgwODI3MDI1MjQyWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECBMKU29tZS1TdGF0ZTEhMB8GA1UEChMYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKB
gQDQQXraVeUfY8Rnl5/3syg2p37vKwJS2QRQMa6J/rPhwbbeq01R/BP6+2pdM1xT
8ZuLYf3dM6nEOLjD3tgPJSgya+ajBLYiZJqcjXbZQNScdPMEdm4puhhVd+eVxx+s
Zrn6w+ppUOm5vrUYJ49ubvwRSzBVOMLVdr1uikKYhDdxHQIDAQABo4GnMIGkMB0G
A1UdDgQWBBRDJ1lNDadV7Td+LoCrE7LE3zy0vzB1BgNVHSMEbjBsgBRDJ1lNDadV
7Td+LoCrE7LE3zy0v6FJpEcwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgTClNvbWUt
U3RhdGUxITAfBgNVBAoTGEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZIIJAON7Ez7I
TeWwMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEASajELNwq1VjymiyA
b5B+iNYs8Ddt05b3bWPNnZFF5nP/EBtQcoPXpfG2sfq/+ElY9638+/RR7iJBdUyL
K7K/PU9TR3z+VqxLAv9PBRUPXvIMIN7E9lkTsK6dz9//yXaYSip8vHsJ+P7VB9A3
4urC+mM1UgBcfVCzRnBWEB+vl7A=
-----END CERTIFICATE-----
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDQQXraVeUfY8Rnl5/3syg2p37vKwJS2QRQMa6J/rPhwbbeq01R
/BP6+2pdM1xT8ZuLYf3dM6nEOLjD3tgPJSgya+ajBLYiZJqcjXbZQNScdPMEdm4p
uhhVd+eVxx+sZrn6w+ppUOm5vrUYJ49ubvwRSzBVOMLVdr1uikKYhDdxHQIDAQAB
AoGAHzVA0MlAbaTIwPFi4n6xjwcoqXSbg4jL8ayQSFOn5zPdUJ8BFkEdSWY1uUPC
GT5Cne+QWH6ueR466fdSD2r1C9vLQWRnhn9A3yIJrfHeD9l3zF6wwW+na7hdKE9e
89Dw4a/jlH3CTBr+juJymaZ4bTQqkPZmF6BAoF+FEtfjWi0CQQD9C+n7wyna5A2O
KRu8Eg+oDsq9X5yURIfUbR6yKhfZBBzHcVzoz3ORbbkoD1Bb6A/YOSUFQSqwCKsG
OjecLFvrAkEA0q+77+1lKcdIg/zN0nAv2/DslD9e68fhjx+hr93AI8HyFuxoxx7x
jp7GiM5/Rma5M/6j1WDtQ1mXsannW+DNFwJANqh4JhWF2O4hr29Zukn8b8SiLj2U
yMH0xQG8+6bz98BXpwzpkLAeum8E645DQVbi9UWCpZvp6JQ2vOWeVXGPeQJAOIJe
HCpGWgBTmOMzqV/h1lI2gkTFBuSjwSmwymTl5jFc530dVVsdWy2G/qa0SIPA5QtF
kjPfL5NWNpblsSUInQJBAJhCXRq6+o6dqwxuR7O8bQoSSYwYHdBGEGHKz4E+3djf
gWEhMJ02GnZ2+vQPRM45gRzW6HmLjrQwIVuXA+2NQ1I=
-----END RSA PRIVATE KEY-----"""
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

