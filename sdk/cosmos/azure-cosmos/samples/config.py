# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

settings = {
    'host': os.environ.get('ACCOUNT_HOST', '[YOUR ENDPOINT]'),
    'master_key': os.environ.get('ACCOUNT_KEY', '[YOUR KEY]'),
    'database_id': os.environ.get('COSMOS_DATABASE', '[YOUR DATABASE]'),
    'container_id': os.environ.get('COSMOS_CONTAINER', '[YOUR CONTAINER]'),
    'tenant_id': os.environ.get('TENANT_ID', '[YOUR TENANT ID]'),
    'client_id': os.environ.get('CLIENT_ID', '[YOUR CLIENT ID]'),
    'client_secret': os.environ.get('CLIENT_SECRET', '[YOUR CLIENT SECRET]'),
}
