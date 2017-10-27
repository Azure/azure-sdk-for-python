# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
import random
import base64
from datetime import datetime, timedelta

try:
    from urllib.parse import urlparse
except ImportError:
    # Python 2 compatibility
    from urlparse import urlparse

from azure.mgmt.recoveryservices.models import (Vault, Sku, SkuName, VaultProperties,
                                                VaultExtendedInfoResource,
                                                )


class MgmtRecoveryServicesTestDefinition(object):
    def __init__(self, subscription_id, vault_name, vault_rg_name, location):
        self.subscription_id = subscription_id
        self.vault_rg_name = vault_rg_name
        self.resource_name = vault_name
        self.location = location

    @property
    def get_vault_name(self):
        return self.resource_name


class MgmtRecoveryServicesTestHelper(object):

    def __init__(self, test_context):
        self.context = test_context
        self.client = self.context.client
        self.test_definition = self.context.test_definition
        self.resource_group = self.test_definition.vault_rg_name
        self.location = "westus"

    def create_vault(self, vault_name):
        params_sku = Sku(
            name= SkuName.standard,
        )
        params_create = Vault(
            location=self.location,
            sku=params_sku,
            properties= VaultProperties()
        )
        self.client.vaults.create_or_update(self.resource_group, vault_name, params_create)

    def list_vaults(self):
        return list(self.client.vaults.list_by_resource_group(self.resource_group))

    def delete_vaults(self, vault_name):
        return self.client.vaults.delete(self.resource_group, vault_name)

    def get_vault(self, vault_name):
        return self.client.vaults.get(self.resource_group, vault_name)

    def create_or_update_vault_extended_info(self, vault):
        params_ext_info = VaultExtendedInfoResource(
            algorithm= "None",
            integrity_key= self.generate_random_key()
        )
        return self.client.vault_extended_info.create_or_update(self.resource_group, vault.name, params_ext_info)

    def get_vault_extended_info(self, vault):
        return self.client.vault_extended_info.get(self.resource_group, vault.name)

    def list_vault_usages(self, vault_name):
        return list(self.client.usages.list_by_vaults(self.resource_group, vault_name))

    def list_replication_usages(self, vault_name):
        return list(self.client.replication_usages.list(self.resource_group, vault_name))

    def get_vault_config(self, vault_name):
        return self.client.backup_vault_configs.get(self.resource_group, vault_name)

    def update_vault_config(self, vault_name, backup_vault_config):
        return self.client.backup_vault_configs.update(vault_name, backup_vault_config)

    def get_storage_config(self, vault_name):
        return self.client.backup_storage_configs.get(self.resource_group, vault_name)

    def update_storage_config(self, vault_name, backup_storage_config):
        return self.client.backup_storage_configs.update(vault_name, backup_storage_config)

    def generate_random_key(self):
        return base64.b64encode(bytearray(random.getrandbits(8) for i in range(16)))

