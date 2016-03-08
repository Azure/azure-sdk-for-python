# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------

try:
    from msrest.exceptions import (
        ClientException,
        SerializationError,
        DeserializationError,
        TokenExpiredError,
        ClientRequestError,
        AuthenticationError,
        HttpOperationError,
    )
except ImportError:
    raise ImportError("You need to install 'msrest' to use this feature")

try:
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    raise ImportError("You need to install 'msrestazure' to use this feature")
