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

# NOTE: these keys are fake, but valid base-64 data, they were generated using:
# base64.b64encode(os.urandom(32))

AUTH_TYPE_SAS = "sas"
AUTH_TYPE_ACS = "acs"

SERVICEBUS_AUTH_TYPE = AUTH_TYPE_SAS
SERVICEBUS_NAME = "fakesbnamespace"
SERVICEBUS_ACS_KEY = "u4T5Ue9OBB35KAlAkoVVc6Tcr/a+Ei4Vl9o7wcyQuPY="
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
