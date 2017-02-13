# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def client(credentials, subscription_id, api_version=None, base_url=None):
    if api_version == '2015-06-15':
        from .v2015_06_15 import StorageManagementClient
        return StorageManagementClient(credentials, subscription_id, api_version, base_url)
    elif api_version == '2016-01-01':
        from .v2016_01_01 import StorageManagementClient
        return StorageManagementClient(credentials, subscription_id, api_version, base_url)
    elif api_version == '2016-12-01':
        from .v2016_12_01 import StorageManagementClient
        return StorageManagementClient(credentials, subscription_id, api_version, base_url)
    raise NotImplementedError("APIVersion {} is not available".format(api_version))

def models(api_version=None):
    if api_version == '2015-06-15':
        from .v2015_06_15 import models
        return models
    elif api_version == '2016-01-01':
        from .v2016_01_01 import models
        return models
    elif api_version == '2016-12-01':
        from .v2016_12_01 import models
        return models
    raise NotImplementedError("APIVersion {} is not available".format(api_version))
