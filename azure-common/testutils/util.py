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
import json
import os
import os.path
from requests import Session


def get_test_file_path(relative_path):
    base_path = os.path.dirname(__file__)
    absolute_path = os.path.join(base_path, relative_path)
    return absolute_path


def create_storage_service(service_class, settings, account_name=None, account_key=None):
    account_name = account_name or settings.STORAGE_ACCOUNT_NAME
    account_key = account_key or settings.STORAGE_ACCOUNT_KEY
    session = Session()
    service = service_class(
        account_name,
        account_key,
        request_session=session,
    )
    set_service_options(service, settings)
    return service


def set_service_options(service, settings):
    if settings.USE_PROXY:
        service.set_proxy(
            settings.PROXY_HOST,
            settings.PROXY_PORT,
            settings.PROXY_USER,
            settings.PROXY_PASSWORD,
        )
