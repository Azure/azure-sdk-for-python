#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# NOTE: these keys are fake, but valid base-64 data, they were generated using:
# base64.b64encode(os.urandom(32))

SERVICEBUS_NAME = "fakesbnamespace"
SERVICEBUS_SAS_KEY_NAME = "RootManageSharedAccessKey"
SERVICEBUS_SAS_KEY_VALUE = "WnFy94qL+8MHkWyb2vxnIIh3SomfV97F+u7sl2ULW7Q="

EVENTHUB_NAME = "fakehubnamespace"
EVENTHUB_SAS_KEY_NAME = "RootManageSharedAccessKey"
EVENTHUB_SAS_KEY_VALUE = "ELT4OCAZT5jgnsKts1vvHZXSevv5uXf8yACEiqEhFH4="

USE_PROXY = False
PROXY_HOST = "192.168.15.116"
PROXY_PORT = "8118"
PROXY_USER = ""
PROXY_PASSWORD = ""
