# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Databases: 8/16
#   DatabaseUsages: 1/1
#   ServerConnectionPolicies: 2/2
#   RecoverableDatabases: 1/2
#   DataMaskingPolicies: 2/2
#   DataMaskingRules: 1/2
#   GeoBackupPolicies: 3/3
#   TransparentDataEncryptions: 2/2
#   TransparentDataEncryptionActivities: 1/1
#   DatabaseBlobAuditingPolicies: 3/3
#   ExtendedDatabaseBlobAuditingPolicies: 3/3
#   BackupLongTermRetentionPolicies: 3/3
#   DatabaseOperations: 0/2
#   WorkloadGroups: 0/4
#   WorkloadClassifiers: 0/4
#   DatabaseThreatDetectionPolicies: 2/2
#   ServiceTierAdvisors: 2/2
#   DatabaseAutomaticTuning: 2/2
#   RestorePoints: 4/4
#   BackupShortTermRetentionPolicies: 4/4
#   LongTermRetentionBackups: 6/10

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

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_backup_short_term_retention_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        DATABASE_NAME = "mydatabase"
        SERVER_NAME = "myserverxpxy"
        POLICY_NAME = "default"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "BC_Gen5",
            "capacity": 2
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/put/Update the short term retention policy for the database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.backup_short_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_short_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/patch/Update the short term retention policy for the database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.backup_short_term_retention_policies.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_restore_points(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        DATABASE_NAME = "mydatabase"
        SERVER_NAME = "myserverxpxy"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "DataWarehouse",
            "tier": "DataWarehouse"
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /RestorePoints/post/Creates datawarehouse database restore point.[post]
#--------------------------------------------------------------------------
        BODY = {
          "restore_point_label": "mylabel"
        }
        result = self.mgmt_client.restore_points.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /RestorePoints/get/List datawarehouse database restore points.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        RESTORE_POINT_NAME = result.next().name

#--------------------------------------------------------------------------
        # /RestorePoints/get/Gets a database restore point.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, restore_point_name=RESTORE_POINT_NAME)

#--------------------------------------------------------------------------
        # /RestorePoints/delete/Deletes a restore point.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, restore_point_name=RESTORE_POINT_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_database_automatic_tuning(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        DATABASE_NAME = "mydatabase"
        SERVER_NAME = "myserverxpxy"
        AUTOMATIC_TUNING_NAME = "current"
        
#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/get/Get a database's automatic tuning settings[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_automatic_tuning.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/patch/Updates database automatic tuning settings with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto"
        }
        result = self.mgmt_client.database_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_service_tier_advisor(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        DATABASE_NAME = "mydatabase"
        SERVER_NAME = "myserverxpxy"
        
#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServiceTierAdvisors/get/Get a list of a service tier advisors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_tier_advisors.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        SERVICE_TIER_ADVISOR_NAME = result.next().name
    
#--------------------------------------------------------------------------
        # /ServiceTierAdvisors/get/Get a service tier advisor[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_tier_advisors.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, service_tier_advisor_name=SERVICE_TIER_ADVISOR_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_database_threat_detection_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        STORAGE_ACCOUNT_NAME = "mystorageaccountxyc"
        BLOB_CONTAINER_NAME = "myblobcontainer"
        SECURITY_ALERT_POLICY_NAME = "default"

        if self.is_live:
            ACCESS_KEY = self.create_blob_container(AZURE_LOCATION, RESOURCE_GROUP, STORAGE_ACCOUNT_NAME, BLOB_CONTAINER_NAME)
        else:
            ACCESS_KEY = "accesskey"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseThreatDetectionPolicies/put/Create database security alert policy min[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": ACCESS_KEY,
          "storage_endpoint": "https://" + STORAGE_ACCOUNT_NAME + ".blob.core.windows.net"
        }
        result = self.mgmt_client.database_threat_detection_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseThreatDetectionPolicies/get/Get database security alert policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_threat_detection_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_workload_group(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        WORKLOAD_GROUP_NAME = "myworkloadgroup"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WorkloadGroups/put/Create a workload group with all properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "min_resource_percent": "0",
          "max_resource_percent": "100",
          "min_resource_percent_per_request": "3"
        }
        result = self.mgmt_client.workload_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WorkloadGroups/get/Gets a workload group for a data warehouse[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME)

#--------------------------------------------------------------------------
        # /WorkloadGroups/get/Get the list of workload groups for a data warehouse[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /WorkloadGroups/delete/Delete a workload group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_long_term_retention_backup(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        LONG_TERM_RETENTION_SERVER_NAME = "myserverxpxyz"
        LONG_TERM_RETENTION_DATABASE_NAME = "mydatabase"
        LOCATION_NAME = AZURE_LOCATION
        BACKUP_NAME = "t"
        POLICY_NAME = "Default"

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get the long term retention backup.[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.long_term_retention_backups.get_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_database(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get the long term retention backup.[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.long_term_retention_backups.get_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_database(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the server.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_server(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the server.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_server(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_location(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_location(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.long_term_retention_backups.begin_delete_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.long_term_retention_backups.begin_delete_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)
        # result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_backup_long_term_retention_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        POLICY_NAME = "Default"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /BackupLongTermRetentionPolicies/put/Create or update the long term retention policy for the database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "weekly_retention": "P1M",
          "monthly_retention": "P1Y",
          "yearly_retention": "P5Y",
          "week_of_year": "5"
        }
        result = self.mgmt_client.backup_long_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /BackupLongTermRetentionPolicies/get/Get the long term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_long_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /BackupLongTermRetentionPolicies/get/Get the long term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_long_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_database_blob_auditing_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        BLOB_AUDITING_POLICY_NAME = "blobauditingpolicy"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/put/Create or update a database's azure monitor auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/put/Create or update an extended database's azure monitor auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.extended_database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/get/Get an extended database's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_database_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/get/Get a database's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/get/List extended auditing settings of a database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_database_blob_auditing_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/get/List audit settings of a database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_blob_auditing_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()


    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_transparent_data_encryption(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        TRANSPARENT_DATA_ENCRYPTION_NAME = "current"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TransparentDataEncryptions/put/Create or update a database's transparent data encryption configuration[put]
#--------------------------------------------------------------------------
        BODY = {
          "status": "Enabled"
        }
        result = self.mgmt_client.transparent_data_encryptions.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /TransparentDataEncryptions/get/Get a database's transparent data encryption configuration[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.transparent_data_encryptions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME)

#--------------------------------------------------------------------------
        # /TransparentDataEncryptionActivities/get/List a database's transparent data encryption activities[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.transparent_data_encryption_activities.list_by_configuration(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_geo_backup_policy(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        GEO_BACKUP_POLICY_NAME = "Default"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/put/Update geo backup policy[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled"
        }
        result = self.mgmt_client.geo_backup_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, geo_backup_policy_name=GEO_BACKUP_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/get/Get geo backup policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.geo_backup_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, geo_backup_policy_name=GEO_BACKUP_POLICY_NAME)

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/get/List geo backup policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.geo_backup_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_data_masking(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        DATA_MASKING_POLICY_NAME = "mydatamaskingpolicy"
        DATA_MASKING_RULE_NAME = "name"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "version": "12.0"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DataMaskingRules/put/Create/Update data masking rule for default min[put]
#--------------------------------------------------------------------------
        BODY = {
          "schema_name": "dbo",
          "table_name": "table1",
          "column_name": "column1",
          "masking_function": "Number",
          "number_from": "0",
          "number_to": "10"
        }
        # result = self.mgmt_client.data_masking_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_rule_name=DATA_MASKING_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingPolicies/put/Create or update data masking policy min[put]
#--------------------------------------------------------------------------
        BODY = {
          "data_masking_state": "Disabled"
        }
        result = self.mgmt_client.data_masking_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingRules/get/List data masking rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.data_masking_rules.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DataMaskingPolicies/get/Get data masking policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.data_masking_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip("unavailable")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_database_operation(self, resource_group):

        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "read_scale": "Disabled"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseOperations/get/List the database management operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_operations.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        OPERATION_ID = result.next().value[0].name

#--------------------------------------------------------------------------
        # /DatabaseOperations/post/Cancel the database management operation[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_operations.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_database(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        CONNECTION_POLICY_NAME = "myconnectionpolicy"

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "read_scale": "Disabled"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerConnectionPolicies/put/Create or update a server's secure connection policy[put]
#--------------------------------------------------------------------------
        BODY = {
          "connection_type": "Proxy"
        }
        result = self.mgmt_client.server_connection_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, connection_policy_name=CONNECTION_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Databases/put/Import bacpac into an existing database Min with SAS key[put]
#--------------------------------------------------------------------------
        BODY = {
          "operation_mode": "Import",
          "storage_key_type": "SharedAccessKey",
          "storage_key": "?sr=b&sp=rw&se=2018-01-01T00%3A00%3A00Z&sig=sdfsdfklsdjflSLIFJLSIEJFLKSDJFDd/%2wdfskdjf3%3D&sv=2015-07-08",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!"
        }
        # result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Import bacpac into an existing database Max with SAS key[put]
#--------------------------------------------------------------------------
        BODY = {
          "name": "Import",
          "type": "Microsoft.Sql/servers/databases/extensions",
          "operation_mode": "Import",
          "storage_key_type": "SharedAccessKey",
          "storage_key": "?sr=b&sp=rw&se=2018-01-01T00%3A00%3A00Z&sig=sdfsdfklsdjflSLIFJLSIEJFLKSDJFDd/%2wdfskdjf3%3D&sv=2015-07-08",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Import bacpac into an existing database Min with storage key[put]
#--------------------------------------------------------------------------
        BODY = {
          "operation_mode": "Import",
          "storage_key_type": "StorageAccessKey",
          "storage_key": "sdlfkjdsf+sdlfkjsdlkfsjdfLDKFJSDLKFDFKLjsdfksjdflsdkfD2342309432849328479324/3RSD==",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!"
        }
        # result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Import bacpac into an existing database Max with storage key[put]
#--------------------------------------------------------------------------
        BODY = {
          "name": "Import",
          "type": "Microsoft.Sql/servers/databases/extensions",
          "operation_mode": "Import",
          "storage_key_type": "StorageAccessKey",
          "storage_key": "sdlfkjdsf+sdlfkjsdlkfsjdfLDKFJSDLKFDFKLjsdfksjdflsdkfD2342309432849328479324/3RSD==",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /RecoverableDatabases/get/Get a recoverable database[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.recoverable_databases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ServerConnectionPolicies/get/Get a server's secure connection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_connection_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, connection_policy_name=CONNECTION_POLICY_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/Gets a list of databases in an elastic pool.[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.databases.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /Databases/get/Gets a database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/Gets a list of databases.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /RecoverableDatabases/get/Get list of restorable dropped databases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recoverable_databases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /DatabaseUsages/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_usages.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/post/Upgrades a data warehouse.[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.databases.begin_upgrade_data_warehouse(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Export a database into a new bacpac file with storage key[post]
#--------------------------------------------------------------------------
        BODY = {
          "storage_key_type": "StorageAccessKey",
          "storage_key": "sdlfkjdsf+sdlfkjsdlkfsjdfLDKFJSDLKFDFKLjsdfksjdflsdkfD2342309432849328479324/3RSD==",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_export(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Export a database into a new bacpac file with SAS key[post]
#--------------------------------------------------------------------------
        BODY = {
          "storage_key_type": "SharedAccessKey",
          "storage_key": "?sr=b&sp=rw&se=2018-01-01T00%3A00%3A00Z&sig=sdfsdfklsdjflSLIFJLSIEJFLKSDJFDd/%2wdfskdjf3%3D&sv=2015-07-08",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_export(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Resumes a database.[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.databases.begin_resume(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        # result = result.result()


#--------------------------------------------------------------------------
        # /ElasticPools/patch/Update an elastic pool with minimum parameters[patch]
#--------------------------------------------------------------------------
        BODY = {}
        # result = self.mgmt_client.elastic_pools.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Pauses a database.[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.databases.begin_pause(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Renames a database.[post]
#--------------------------------------------------------------------------
        DATABASE_NAME_2 = DATABASE_NAME + "2"
        BODY = {
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME_2
        }
        result = self.mgmt_client.databases.rename(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

        DATABASE_NAME = DATABASE_NAME_2

#--------------------------------------------------------------------------
        # /Databases/patch/Updates a database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "S1",
            "tier": "Standard"
          },
          "collation": "SQL_Latin1_General_CP1_CI_AS",
          "max_size_bytes": "1073741824"
        }
        result = self.mgmt_client.databases.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Import bacpac into new database Max with storage key[post]
#--------------------------------------------------------------------------
        BODY = {
          "database_name": "TestDbImport",
          "edition": "Basic",
          "service_objective_name": "Basic",
          "max_size_bytes": "2147483648",
          "storage_key_type": "StorageAccessKey",
          "storage_key": "sdlfkjdsf+sdlfkjsdlkfsjdfLDKFJSDLKFDFKLjsdfksjdflsdkfD2342309432849328479324/3RSD==",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Import bacpac into new database Min with storage key[post]
#--------------------------------------------------------------------------
        BODY = {
          "database_name": "TestDbImport",
          "edition": "Basic",
          "service_objective_name": "Basic",
          "max_size_bytes": "2147483648",
          "storage_key_type": "StorageAccessKey",
          "storage_key": "sdlfkjdsf+sdlfkjsdlkfsjdfLDKFJSDLKFDFKLjsdfksjdflsdkfD2342309432849328479324/3RSD==",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!"
        }
        # result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Import bacpac into new database Max with SAS key[post]
#--------------------------------------------------------------------------
        BODY = {
          "database_name": "TestDbImport",
          "edition": "Basic",
          "service_objective_name": "Basic",
          "max_size_bytes": "2147483648",
          "storage_key_type": "SharedAccessKey",
          "storage_key": "?sr=b&sp=rw&se=2018-01-01T00%3A00%3A00Z&sig=sdfsdfklsdjflSLIFJLSIEJFLKSDJFDd/%2wdfskdjf3%3D&sv=2015-07-08",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!",
          "authentication_type": "SQL"
        }
        # result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Import bacpac into new database Min with SAS key[post]
#--------------------------------------------------------------------------
        BODY = {
          "database_name": "TestDbImport",
          "edition": "Basic",
          "service_objective_name": "Basic",
          "max_size_bytes": "2147483648",
          "storage_key_type": "SharedAccessKey",
          "storage_key": "?sr=b&sp=rw&se=2018-01-01T00%3A00%3A00Z&sig=sdfsdfklsdjflSLIFJLSIEJFLKSDJFDd/%2wdfskdjf3%3D&sv=2015-07-08",
          "storage_uri": "https://test.blob.core.windows.net/bacpacs/testbacpac.bacpac",
          "administrator_login": "dummyLogin",
          "administrator_login_password": "Un53cuRE!"
        }
        # result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Failover an database[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, replica_type="Primary")
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
