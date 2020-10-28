# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   ManagedDatabases: 6/7
#   ManagedDatabaseSecurityAlertPolicies: 3/3
#   ManagedServerSecurityAlertPolicies: 3/3
#   ManagedBackupShortTermRetentionPolicies: 4/4
#   ManagedInstanceLongTermRetentionPolicies: 0/3
#   LongTermRetentionManagedInstanceBackups: 0/10

import unittest

import azure.mgmt.sql
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

        if self.is_live:
            from azure.mgmt.storage import StorageManagementClient
            self.storage_client = self.create_mgmt_client(
                StorageManagementClient
            )

    def create_blob_container(self, location, group_name, account_name, container_name):

        # StorageAccountCreate[put]
        BODY = {
          "sku": {
            "name": "Standard_GRS"
          },
          "kind": "StorageV2",
          "location": location,
          "encryption": {
            "services": {
              "file": {
                "key_type": "Account",
                "enabled": True
              },
              "blob": {
                "key_type": "Account",
                "enabled": True
              }
            },
            "key_source": "Microsoft.Storage"
          },
          "tags": {
            "key1": "value1",
            "key2": "value2"
          }
        }
        result = self.storage_client.storage_accounts.begin_create(group_name, account_name, BODY)
        storageaccount = result.result()

        # PutContainers[put]
        result = self.storage_client.blob_containers.create(group_name, account_name, container_name, {})

        # StorageAccountRegenerateKey[post]
        BODY = {
          "key_name": "key2"
        }
        key = self.storage_client.storage_accounts.regenerate_key(group_name, account_name, BODY)
        return key.keys[0].value

    @unittest.skip("(None) Archived backup is not supported")
    def test_managed_instance_long_term_retention_policy(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        DATABASE_NAME = "mydatabase"
        POLICY_NAME = "default"

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceLongTermRetentionPolicies/put/Create or update the LTR policy for the managed database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "weekly_retention": "P1M",
          "monthly_retention": "P1Y",
          "yearly_retention": "P5Y",
          "week_of_year": "5"
        }
        result = self.mgmt_client.managed_instance_long_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceLongTermRetentionPolicies/get/Get the long term retention policy for the managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_long_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceLongTermRetentionPolicies/get/Get the long term retention policies for the managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_long_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/delete/Delete managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)
        result = result.result()


    def test_managed_backup_short_term_policy(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        DATABASE_NAME = "mydatabase"
        POLICY_NAME = "default"

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/put/Update the short term retention policy for the database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_backup_short_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/get/Get the short term retention policy list for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_backup_short_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/patch/Update the short term retention policy for the database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_backup_short_term_retention_policies.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/delete/Delete managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)
        result = result.result()

    def test_managed_security_alert_policy(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        DATABASE_NAME = "mydatabase"
        SECURITY_ALERT_POLICY_NAME = "default"
        STORAGE_ACCOUNT_NAME = "mystorageaccountxydb"
        BLOB_CONTAINER_NAME = "myblobcontainer"

        if self.is_live:
            ACCESS_KEY = self.create_blob_container(AZURE_LOCATION, RESOURCE_GROUP, STORAGE_ACCOUNT_NAME, BLOB_CONTAINER_NAME)
        else:
            ACCESS_KEY = "accesskey"

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/put/Update a server's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": ACCESS_KEY,
          "storage_endpoint": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net"
        }
        result = self.mgmt_client.managed_server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/put/Update a database's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled"
        }
        result = self.mgmt_client.managed_database_security_alert_policies.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/get/Get a managed server's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_server_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/get/Get a database's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/get/Get the managed server's threat detection policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_server_security_alert_policies.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/get/Get a list of the database's threat detection policies.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_security_alert_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/delete/Delete managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)
        result = result.result()

    # @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_managed_db(self):

        RESOURCE_GROUP = "testManagedInstance"
        MANAGED_INSTANCE_NAME = "testinstancexxy"
        DATABASE_NAME = "mydatabase"

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/Gets a managed database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/List inaccessible managed databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.list_inaccessible_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/List databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/post/Completes a managed database external backup restore.[post]
#--------------------------------------------------------------------------
        BODY = {
          "last_backup_name": "testdb1_log4"
        }
        # result = self.mgmt_client.managed_databases.begin_complete_restore(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/patch/Updates a managed database with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          }
        }
        result = self.mgmt_client.managed_databases.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/delete/Delete managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)
        result = result.result()

