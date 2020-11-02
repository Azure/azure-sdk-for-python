# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 354
# Methods Covered : 353
# Examples Total  : 425
# Examples Tested : 425
# Coverage %      : 100
# ----------------------

# Current Operation Coverage:
#   RecoverableDatabases: 2/2
#   RestorableDroppedDatabases: 2/2
#   ServerConnectionPolicies: 2/2
#   DatabaseThreatDetectionPolicies: 2/2
#   DataMaskingPolicies: 2/2
#   DataMaskingRules: 2/2
#   FirewallRules: 4/4
#   GeoBackupPolicies: 3/3
#   Databases: 16/16
#   ElasticPools: 8/8
#   RecommendedElasticPools: 3/3
#   ReplicationLinks: 6/6
#   ServerCommunicationLinks: 4/4
#   ServiceObjectives: 2/2
#   ElasticPoolActivities: 1/1
#   ElasticPoolDatabaseActivities: 1/1
#   ServiceTierAdvisors: 2/2
#   TransparentDataEncryptions: 2/2
#   TransparentDataEncryptionActivities: 1/1
#   ServerUsages: 1/1
#   DatabaseUsages: 1/1
#   DatabaseAutomaticTuning: 2/2
#   EncryptionProtectors: 4/4
#   FailoverGroups: 7/7
#   Operations: 0/1
#   ServerKeys: 4/4
#   SyncAgents: 6/6
#   SubscriptionUsages: 2/2
#   VirtualClusters: 5/5
#   VirtualNetworkRules: 4/4
#   ExtendedDatabaseBlobAuditingPolicies: 3/3
#   ExtendedServerBlobAuditingPolicies: 3/3
#   ServerBlobAuditingPolicies: 3/3
#   DatabaseBlobAuditingPolicies: 3/3
#   DatabaseVulnerabilityAssessmentRuleBaselines: 3/3
#   DatabaseVulnerabilityAssessments: 4/4
#   JobAgents: 5/5
#   JobCredentials: 4/4
#   JobExecutions: 6/6
#   Jobs: 4/4
#   JobStepExecutions: 2/2
#   JobSteps: 6/6
#   JobTargetExecutions: 3/3
#   JobTargetGroups: 4/4
#   JobVersions: 2/2
#   LongTermRetentionBackups: 10/10
#   BackupLongTermRetentionPolicies: 3/3
#   ManagedBackupShortTermRetentionPolicies: 4/4
#   ManagedRestorableDroppedDatabaseBackupShortTermRetentionPolicies: 4/4
#   ServerAutomaticTuning: 2/2
#   ServerDnsAliases: 5/5
#   ServerSecurityAlertPolicies: 3/3
#   RestorableDroppedManagedDatabases: 2/2
#   RestorePoints: 4/4
#   ManagedDatabaseSecurityAlertPolicies: 3/3
#   ManagedServerSecurityAlertPolicies: 3/3
#   SensitivityLabels: 7/7
#   ManagedInstanceAdministrators: 4/4
#   DatabaseOperations: 2/2
#   ElasticPoolOperations: 2/2
#   DatabaseVulnerabilityAssessmentScans: 4/4
#   ManagedDatabaseVulnerabilityAssessmentRuleBaselines: 3/3
#   ManagedDatabaseVulnerabilityAssessmentScans: 4/4
#   ManagedDatabaseVulnerabilityAssessments: 4/4
#   InstanceFailoverGroups: 6/6
#   TdeCertificates: 1/1
#   ManagedInstanceTdeCertificates: 1/1
#   ManagedInstanceKeys: 4/4
#   ManagedInstanceEncryptionProtectors: 4/4
#   RecoverableManagedDatabases: 2/2
#   ManagedInstanceVulnerabilityAssessments: 4/4
#   ServerVulnerabilityAssessments: 4/4
#   ManagedDatabaseSensitivityLabels: 7/7
#   InstancePools: 6/6
#   Usages: 1/1
#   PrivateEndpointConnections: 4/4
#   PrivateLinkResources: 2/2
#   Servers: 7/7
#   Capabilities: 1/1
#   LongTermRetentionManagedInstanceBackups: 10/10
#   ManagedInstanceLongTermRetentionPolicies: 3/3
#   WorkloadGroups: 4/4
#   WorkloadClassifiers: 4/4
#   ManagedInstanceOperations: 3/3
#   ServerAzureADAdministrators: 4/4
#   SyncGroups: 11/11
#   SyncMembers: 7/7
#   ManagedInstances: 8/8
#   BackupShortTermRetentionPolicies: 4/4
#   ManagedDatabaseRestoreDetails: 1/1
#   ManagedDatabases: 7/7
#   ServerAzureADOnlyAuthentications: 4/4

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
            from azure.mgmt.network import NetworkManagementClient
            self.network_client = self.create_mgmt_client(
                NetworkManagementClient
            )

    def create_virtual_network(self, group_name, location, network_name, subnet_name):

        azure_operation_poller = self.network_client.virtual_networks.create_or_update(
            group_name,
            network_name,
            {
                'location': location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/16']
                }
            },
        )
        result_create = azure_operation_poller.result()

        async_subnet_creation = self.network_client.subnets.create_or_update(
            group_name,
            network_name,
            subnet_name,
            {'address_prefix': '10.0.0.0/24'}
        )
        subnet_info = async_subnet_creation.result()

        return subnet_info

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_sql(self, resource_group):

        UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myServer" + UNIQUE
        DATABASE_NAME = "myDatabase"
        RESTORABLE_DROPPEDED_DATABASE_ID = "myRestorableDroppededDatabaseId"
        CONNECTION_POLICY_NAME = "myConnectionPolicy"
        SECURITY_ALERT_POLICY_NAME = "mySecurityAlertPolicy"
        DATA_MASKING_POLICY_NAME = "myDataMaskingPolicy"
        DATA_MASKING_RULE_NAME = "myDataMaskingRule"
        FIREWALL_RULE_NAME = "myFirewallRule"
        GEO_BACKUP_POLICY_NAME = "myGeoBackupPolicy"
        EXTENSION_NAME = "myExtension"
        RESTORABLE_DROPPED_DATABASE_NAME = "myRestorableDroppedDatabase"
        ELASTIC_POOL_NAME = "myElasticPool"
        RECOMMENDED_ELASTIC_POOL_NAME = "myRecommendedElasticPool"
        LINK_ID = "myLinkId"
        COMMUNICATION_LINK_NAME = "myCommunicationLink"
        SERVICE_OBJECTIVE_NAME = "myServiceObjective"
        SERVICE_TIER_ADVISOR_NAME = "myServiceTierAdvisor"
        TRANSPARENT_DATA_ENCRYPTION_NAME = "myTransparentDataEncryption"
        AUTOMATIC_TUNING_NAME = "myAutomaticTuning"
        ENCRYPTION_PROTECTOR_NAME = "myEncryptionProtector"
        FAILOVER_GROUP_NAME = "myFailoverGroup"
        KEY_NAME = "myKey"
        SYNC_AGENT_NAME = "mySyncAgent"
        LOCATION_NAME = "myLocation"
        USAGE_NAME = "myUsage"
        VIRTUAL_CLUSTER_NAME = "myVirtualCluster"
        VIRTUAL_NETWORK_RULE_NAME = "myVirtualNetworkRule"
        VIRTUAL_NETWORK_NAME = "myVirtualNetwork"
        SUBNET_NAME = "mySubnet"
        BLOB_AUDITING_POLICY_NAME = "myBlobAuditingPolicy"
        VULNERABILITY_ASSESSMENT_NAME = "myVulnerabilityAssessment"
        RULE_ID = "myRuleId"
        BASELINE_NAME = "myBaseline"
        JOB_AGENT_NAME = "myJobAgent"
        CREDENTIAL_NAME = "myCredential"
        JOB_NAME = "myJob"
        JOB_EXECUTION_ID = "myJobExecutionId"
        STEP_NAME = "myStep"
        JOB_VERSION = "myJobVersion"
        TARGET_GROUP_NAME = "myTargetGroup"
        TARGET_ID = "myTargetId"
        LONG_TERM_RETENTION_SERVER_NAME = "myLongTermRetentionServer"
        LONG_TERM_RETENTION_DATABASE_NAME = "myLongTermRetentionDatabase"
        BACKUP_NAME = "myBackup"
        POLICY_NAME = "myPolicy"
        MANAGED_INSTANCE_NAME = "myManagedInstance"
        RESTORABLE_DROPPED_DATABASE_ID = "myRestorableDroppedDatabaseId"
        DNS_ALIAS_NAME = "myDnsAlias"
        RESTORE_POINT_NAME = "myRestorePoint"
        SCHEMA_NAME = "mySchema"
        TABLE_NAME = "myTable"
        COLUMN_NAME = "myColumn"
        SENSITIVITY_LABEL_SOURCE = "mySensitivityLabelSource"
        ADMINISTRATOR_NAME = "myAdministrator"
        OPERATION_ID = "myOperationId"
        SCAN_ID = "myScanId"
        RECOVERABLE_DATABASE_NAME = "myRecoverableDatabase"
        INSTANCE_POOL_NAME = "myInstancePool"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        GROUP_NAME = "myGroup"
        WORKLOAD_GROUP_NAME = "myWorkloadGroup"
        WORKLOAD_CLASSIFIER_NAME = "myWorkloadClassifier"
        SYNC_GROUP_NAME = "mySyncGroup"
        SYNC_MEMBER_NAME = "mySyncMember"
        PUBLIC_MAINTENANCE_CONFIGURATION_NAME = "myPublicMaintenanceConfiguration"
        RESTORE_DETAILS_NAME = "myRestoreDetails"
        AUTHENTICATION_NAME = "myAuthentication"

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
        # /InstancePools/put/Create an instance pool with min properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "GP_Gen5",
            "tier": "GeneralPurpose",
            "family": "Gen5"
          },
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetwork/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "v_cores": "8",
          "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client.instance_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstancePools/put/Create an instance pool with all properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "GP_Gen5",
            "tier": "GeneralPurpose",
            "family": "Gen5"
          },
          "tags": {
            "a": "b"
          },
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetwork/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "v_cores": "8",
          "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client.instance_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/put/Create managed instance with all properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          },
          "location": AZURE_LOCATION,
          "sku": {
            "name": "GP_Gen5",
            "tier": "GeneralPurpose"
          },
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "v_cores": "8",
          "storage_size_in_gb": "1024",
          "license_type": "LicenseIncluded",
          "collation": "SQL_Latin1_General_CP1_CI_AS",
          "dns_zone_partner": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/managedInstances/" + MANAGED_INSTANCE_NAME,
          "public_data_endpoint_enabled": False,
          "proxy_override": "Redirect",
          "timezone_id": "UTC",
          "instance_pool_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/instancePools/" + INSTANCE_POOL_NAME,
          "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/" + PUBLIC_MAINTENANCE_CONFIGURATION_NAME,
          "storage_account_type": "GRS"
        }
        result = self.mgmt_client.managed_instances.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/put/Create managed instance with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "GP_Gen4",
            "tier": "GeneralPurpose"
          },
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME,
          "v_cores": "8",
          "storage_size_in_gb": "1024",
          "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client.managed_instances.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerKeys/put/Creates or updates a server key[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "uri": "https://someVault.vault.azure.net/keys/someKey/01234567890123456789012345678901"
        }
        result = self.mgmt_client.server_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a VCore database by specifying sku name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "BC_Gen4_2"
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a Hyperscale database and specifies the number of readonly replicas.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "HS_Gen4",
            "tier": "Hyperscale",
            "capacity": "1"
          },
          "read_replica_count": "3"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database from recoverableDatabaseId.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Restore",
          "restorable_dropped_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/restorableDroppedDatabases/" + RESTORABLE_DROPPED_DATABASE_NAME
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database from restore with restorableDroppedDatabaseId.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Copy",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database from restore with database deletion time.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Restore",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME,
          "source_database_deletion_date": "2017-07-14T06:41:06.613Z"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database from PointInTimeRestore.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "PointInTimeRestore",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME,
          "restore_point_in_time": "2017-07-14T05:35:31.503Z"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database as an on-line secondary.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Secondary",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database as a copy.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Copy",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database with default mode.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "S0",
            "tier": "Standard"
          },
          "create_mode": "Default",
          "collation": "SQL_Latin1_General_CP1_CI_AS",
          "max_size_bytes": "1073741824"
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database with minimum number of parameters.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a data warehouse by specifying service objective name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "DW1000c"
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a VCore database by specifying sku name and capacity.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "BC_Gen4",
            "capacity": "2"
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a VCore database by specifying service objective name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "BC",
            "family": "Gen4",
            "capacity": "2"
          }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/put/Create or update a job agent with all properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "Agent",
            "capacity": "100"
          },
          "tags": {
            "octopus": "agent"
          },
          "database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.job_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/put/Create or update a job agent with minimum properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.job_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/put/Create server DNS alias[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.server_dns_aliases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/put/Create a new sync agent[put]
#--------------------------------------------------------------------------
        BODY = {
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/put/Update a sync agent[put]
#--------------------------------------------------------------------------
        BODY = {
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/put/Create or update elastic pool with all parameter[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "GP_Gen4_2",
            "tier": "GeneralPurpose",
            "capacity": "2"
          },
          "per_database_settings": {
            "min_capacity": "0.25",
            "max_capacity": "2"
          }
        }
        result = self.mgmt_client.elastic_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/put/Create or update elastic pool with minimum parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.elastic_pools.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/put/Creates or updates a managed instance key[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "uri": "https://someVault.vault.azure.net/keys/someKey/01234567890123456789012345678901"
        }
        result = self.mgmt_client.managed_instance_keys.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FirewallRules/put/Update a firewall rule max/min[put]
#--------------------------------------------------------------------------
        BODY = {
          "start_ip_address": "0.0.0.1",
          "end_ip_address": "0.0.0.1"
        }
        result = self.mgmt_client.firewall_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /FirewallRules/put/Create a firewall rule max/min[put]
#--------------------------------------------------------------------------
        BODY = {
          "start_ip_address": "0.0.0.3",
          "end_ip_address": "0.0.0.3"
        }
        result = self.mgmt_client.firewall_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/put/Creates or updates an existing Azure Active Directory administrator.[put]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_type": "ActiveDirectory",
          "login": "bob@contoso.com",
          "sid": "c6b82b90-a647-49cb-8a62-0d2d3cb7ac7c",
          "tenant_id": TENANT_ID
        }
        result = self.mgmt_client.server_azure_adadministrators.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/put/Create failover group[put]
#--------------------------------------------------------------------------
        BODY = {
          "read_write_endpoint": {
            "failover_policy": "Automatic",
            "failover_with_data_loss_grace_period_minutes": "480"
          },
          "read_only_endpoint": {
            "failover_policy": "Disabled"
          },
          "partner_servers": [
            {
              "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME
            }
          ],
          "databases": [
            "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/Default/providers/Microsoft.Sql/servers/failover-group-primary-server/databases/testdb-1",
            "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/Default/providers/Microsoft.Sql/servers/failover-group-primary-server/databases/testdb-2"
          ]
        }
        result = self.mgmt_client.failover_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerConnectionPolicies/put/Create or update a server's secure connection policy[put]
#--------------------------------------------------------------------------
        BODY = {
          "connection_type": "Proxy"
        }
        result = self.mgmt_client.server_connection_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, connection_policy_name=CONNECTION_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database from restoring a long term retention backup[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "create_mode": "RestoreExternalBackup",
          "storage_container_uri": "https://myaccountname.blob.core.windows.net/backups",
          "storage_container_sas_token": "sv=2015-12-11&sr=c&sp=rl&sig=1234",
          "collation": "SQL_Latin1_General_CP1_CI_AS"
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database from restoring a geo-replicated backup[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "create_mode": "Recovery",
          "recoverable_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/managedInstances/" + MANAGED_INSTANCE_NAME + "/recoverableDatabases/" + RECOVERABLE_DATABASE_NAME
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database by restoring from an external backup[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "create_mode": "RestoreExternalBackup",
          "storage_container_uri": "https://myaccountname.blob.core.windows.net/backups",
          "storage_container_sas_token": "sv=2015-12-11&sr=c&sp=rl&sig=1234",
          "collation": "SQL_Latin1_General_CP1_CI_AS",
          "auto_complete_restore": True,
          "last_backup_name": "last_backup_name"
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database using point in time restore[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "create_mode": "PointInTimeRestore",
          "source_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/managedInstances/" + MANAGED_INSTANCE_NAME + "/databases/" + DATABASE_NAME,
          "restore_point_in_time": "2017-07-14T05:35:31.503Z"
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with maximal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          },
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabases/put/Creates a new managed database with minimal properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.managed_databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/put/Update a server's blob auditing policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net",
          "retention_days": "6",
          "storage_account_subscription_id": "00000000-1234-0000-5678-000000000000",
          "is_storage_secondary_key_in_use": False,
          "queue_delay_ms": "4000",
          "audit_actions_and_groups": [
            "SUCCESSFUL_DATABASE_AUTHENTICATION_GROUP",
            "FAILED_DATABASE_AUTHENTICATION_GROUP",
            "BATCH_COMPLETED_GROUP"
          ],
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/put/Update a server's blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/put/Create a server communication link[put]
#--------------------------------------------------------------------------
        BODY = {
          "partner_server": "sqldcrudtest-test"
        }
        result = self.mgmt_client.server_communication_links.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Jobs/put/Create a job with all properties specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "description": "my favourite job",
          "schedule": {
            "start_time": "2015-09-24T18:30:01Z",
            "end_time": "2015-09-24T23:59:59Z",
            "type": "Recurring",
            "interval": "PT5M",
            "enabled": True
          }
        }
        result = self.mgmt_client.jobs.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Jobs/put/Create a job with default properties[put]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.jobs.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/put/Create or update a virtual network rule[put]
#--------------------------------------------------------------------------
        BODY = {
          "ignore_missing_vnet_service_endpoint": False,
          "virtual_network_subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME
        }
        result = self.mgmt_client.virtual_network_rules.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /EncryptionProtectors/put/Update the encryption protector to service managed[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "ServiceManaged",
          "server_key_name": "ServiceManaged"
        }
        result = self.mgmt_client.encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /EncryptionProtectors/put/Update the encryption protector to key vault[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "server_key_name": "someVault_someKey_01234567890123456789012345678901"
        }
        result = self.mgmt_client.encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/put/Creates or updates Azure Active Directory only authentication object.[put]
#--------------------------------------------------------------------------
        BODY = {
          "azure_adonly_authentication": False
        }
        result = self.mgmt_client.server_azure_adonly_authentications.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/put/Create failover group[put]
#--------------------------------------------------------------------------
        BODY = {
          "read_write_endpoint": {
            "failover_policy": "Automatic",
            "failover_with_data_loss_grace_period_minutes": "480"
          },
          "read_only_endpoint": {
            "failover_policy": "Disabled"
          },
          "partner_regions": [
            {
              "location": AZURE_LOCATION
            }
          ],
          "managed_instance_pairs": [
            {
              "primary_managed_instance_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/managedInstances/" + MANAGED_INSTANCE_NAME,
              "partner_managed_instance_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/managedInstances/" + MANAGED_INSTANCE_NAME
            }
          ]
        }
        result = self.mgmt_client.instance_failover_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, failover_group_name=FAILOVER_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/put/Update a server's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Disabled",
          "email_account_admins": True,
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/put/Update a server's threat detection policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "email_account_admins": True,
          "email_addresses": [
            "testSecurityAlert@microsoft.com"
          ],
          "disabled_alerts": [
            "Access_Anomaly",
            "Usage_Anomaly"
          ],
          "retention_days": "5",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/put/Update a server's extended blob auditing policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net",
          "retention_days": "6",
          "storage_account_subscription_id": "00000000-1234-0000-5678-000000000000",
          "is_storage_secondary_key_in_use": False,
          "audit_actions_and_groups": [
            "SUCCESSFUL_DATABASE_AUTHENTICATION_GROUP",
            "FAILED_DATABASE_AUTHENTICATION_GROUP",
            "BATCH_COMPLETED_GROUP"
          ],
          "predicate_expression": "object_name = 'SensitiveData'",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.extended_server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/put/Update a server's extended blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.extended_server_blob_auditing_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceAdministrators/put/Update administrator of managed instance[put]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_type": "ActiveDirectory",
          "login": "bob@contoso.com",
          "sid": "44444444-3333-2222-1111-000000000000",
          "tenant_id": TENANT_ID
        }
        result = self.mgmt_client.managed_instance_administrators.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, administrator_name=ADMINISTRATOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceAdministrators/put/Create administrator of managed instance[put]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_type": "ActiveDirectory",
          "login": "bob@contoso.com",
          "sid": "44444444-3333-2222-1111-000000000000",
          "tenant_id": TENANT_ID
        }
        result = self.mgmt_client.managed_instance_administrators.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, administrator_name=ADMINISTRATOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/put/Create a server's vulnerability assessment with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "recurring_scans": {
            "is_enabled": True,
            "email_subscription_admins": True,
            "emails": [
              "email1@mail.com",
              "email2@mail.com"
            ]
          }
        }
        result = self.mgmt_client.server_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/put/Create a server's vulnerability assessment with minimal parameters, when storageAccountAccessKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.server_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/put/Create a server's vulnerability assessment with minimal parameters, when storageContainerSasKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.server_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

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
        result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_create_import_operation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, extension_name=EXTENSION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/put/Update a sync group[put]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/put/Create a sync group[put]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobCredentials/put/Create or update a credential[put]
#--------------------------------------------------------------------------
        BODY = {
          "username": "myuser",
          "password": "<password>"
        }
        result = self.mgmt_client.job_credentials.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/put/Approve or reject a private endpoint connection with a given name.[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Approved by johndoe@contoso.com"
          }
        }
        result = self.mgmt_client.private_endpoint_connections.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobTargetGroups/put/Create or update a target group with minimal properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "members": []
        }
        result = self.mgmt_client.job_target_groups.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobTargetGroups/put/Create or update a target group with all properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "members": [
            {
              "membership_type": "Exclude",
              "type": "SqlDatabase",
              "server_name": "server1",
              "database_name": "database1"
            },
            {
              "membership_type": "Include",
              "type": "SqlServer",
              "server_name": "server1",
              "refresh_credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME
            },
            {
              "membership_type": "Include",
              "type": "SqlElasticPool",
              "server_name": "server2",
              "elastic_pool_name": "pool1",
              "refresh_credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME
            },
            {
              "membership_type": "Include",
              "type": "SqlShardMap",
              "server_name": "server3",
              "shard_map_name": "shardMap1",
              "database_name": "database1",
              "refresh_credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME
            }
          ]
        }
        result = self.mgmt_client.job_target_groups.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /WorkloadGroups/put/Create a workload group with all properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "min_resource_percent": "0",
          "max_resource_percent": "100",
          "min_resource_percent_per_request": "3",
          "max_resource_percent_per_request": "3",
          "importance": "normal",
          "query_execution_timeout": "0"
        }
        result = self.mgmt_client.workload_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WorkloadGroups/put/Create a workload group with the required properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "min_resource_percent": "0",
          "max_resource_percent": "100",
          "min_resource_percent_per_request": "3"
        }
        result = self.mgmt_client.workload_groups.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/put/Update the encryption protector to service managed[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "ServiceManaged",
          "server_key_name": "ServiceManaged"
        }
        result = self.mgmt_client.managed_instance_encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/put/Update the encryption protector to key vault[put]
#--------------------------------------------------------------------------
        BODY = {
          "server_key_type": "AzureKeyVault",
          "server_key_name": "someVault_someKey_01234567890123456789012345678901"
        }
        result = self.mgmt_client.managed_instance_encryption_protectors.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobSteps/put/Create or update a job step with all properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "step_id": "1",
          "target_group": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/targetGroups/" + TARGET_GROUP_NAME,
          "credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME,
          "action": {
            "type": "TSql",
            "source": "Inline",
            "value": "select 2"
          },
          "output": {
            "type": "SqlDatabase",
            "subscription_id": "3501b905-a848-4b5d-96e8-b253f62d735a",
            "resource_group_name": "group3",
            "server_name": "server3",
            "database_name": "database3",
            "schema_name": "myschema1234",
            "table_name": "mytable5678",
            "credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME
          },
          "execution_options": {
            "timeout_seconds": "1234",
            "retry_attempts": "42",
            "initial_retry_interval_seconds": "11",
            "maximum_retry_interval_seconds": "222",
            "retry_interval_backoff_multiplier": "3"
          }
        }
        result = self.mgmt_client.job_steps.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobSteps/put/Create or update a job step with minimal properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "target_group": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/targetGroups/" + TARGET_GROUP_NAME,
          "credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME,
          "action": {
            "value": "select 1"
          }
        }
        result = self.mgmt_client.job_steps.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/put/Update a server's threat detection policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "email_account_admins": True,
          "email_addresses": [
            "testSecurityAlert@microsoft.com"
          ],
          "disabled_alerts": [
            "Access_Anomaly",
            "Usage_Anomaly"
          ],
          "retention_days": "5",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.managed_server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/put/Update a server's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.managed_server_security_alert_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/put/Update geo backup policy[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled"
        }
        result = self.mgmt_client.geo_backup_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, geo_backup_policy_name=GEO_BACKUP_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/put/Create or update a database's azure monitor auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/put/Create or update a database's blob auditing policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net",
          "retention_days": "6",
          "storage_account_subscription_id": "00000000-1234-0000-5678-000000000000",
          "is_storage_secondary_key_in_use": False,
          "queue_delay_ms": "4000",
          "audit_actions_and_groups": [
            "DATABASE_LOGOUT_GROUP",
            "DATABASE_ROLE_MEMBER_CHANGE_GROUP",
            "UPDATE on database::TestDatabaseName by public"
          ],
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/put/Create or update a database's blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/put/Create a managed instance's vulnerability assessment with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "recurring_scans": {
            "is_enabled": True,
            "email_subscription_admins": True,
            "emails": [
              "email1@mail.com",
              "email2@mail.com"
            ]
          }
        }
        result = self.mgmt_client.managed_instance_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/put/Create a managed instance's vulnerability assessment with minimal parameters, when storageContainerSasKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.managed_instance_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/put/Create a managed instance's vulnerability assessment with minimal parameters, when storageAccountAccessKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.managed_instance_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

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
        # /BackupShortTermRetentionPolicies/put/Update the short term retention policy for the database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14",
          "diff_backup_interval_in_hours": "24"
        }
        result = self.mgmt_client.backup_short_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DataMaskingPolicies/put/Create or update data masking policy min[put]
#--------------------------------------------------------------------------
        BODY = {
          "data_masking_state": "Enabled"
        }
        result = self.mgmt_client.data_masking_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingPolicies/put/Create or update data masking policy max[put]
#--------------------------------------------------------------------------
        BODY = {
          "data_masking_state": "Enabled",
          "exempt_principals": "testuser;"
        }
        result = self.mgmt_client.data_masking_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobExecutions/put/Create job execution.[put]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseThreatDetectionPolicies/put/Create database security alert policy max[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "email_account_admins": "Enabled",
          "email_addresses": "test@microsoft.com;user@microsoft.com",
          "disabled_alerts": "Sql_Injection;Usage_Anomaly;",
          "retention_days": "6",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net",
          "use_server_default": "Enabled"
        }
        result = self.mgmt_client.database_threat_detection_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseThreatDetectionPolicies/put/Create database security alert policy min[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.database_threat_detection_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/put/Create or update an extended database's azure monitor auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.extended_database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/put/Create or update an extended database's blob auditing policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net",
          "retention_days": "6",
          "storage_account_subscription_id": "00000000-1234-0000-5678-000000000000",
          "is_storage_secondary_key_in_use": False,
          "audit_actions_and_groups": [
            "DATABASE_LOGOUT_GROUP",
            "DATABASE_ROLE_MEMBER_CHANGE_GROUP",
            "UPDATE on database::TestDatabaseName by public"
          ],
          "predicate_expression": "statement = 'select 1'",
          "is_azure_monitor_target_enabled": True
        }
        result = self.mgmt_client.extended_database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/put/Create or update an extended database's blob auditing policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.extended_database_blob_auditing_policies.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/put/Create a database's vulnerability assessment with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "recurring_scans": {
            "is_enabled": True,
            "email_subscription_admins": True,
            "emails": [
              "email1@mail.com",
              "email2@mail.com"
            ]
          }
        }
        result = self.mgmt_client.database_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/put/Create a database's vulnerability assessment with minimal parameters, when storageAccountAccessKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_account_access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.database_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/put/Create a database's vulnerability assessment with minimal parameters, when storageContainerSasKey is specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.database_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /TransparentDataEncryptions/put/Create or update a database's transparent data encryption configuration[put]
#--------------------------------------------------------------------------
        BODY = {
          "status": "Enabled"
        }
        result = self.mgmt_client.transparent_data_encryptions.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /SyncMembers/put/Update a sync member[put]
#--------------------------------------------------------------------------
        BODY = {
          "database_type": "AzureSqlDatabase",
          "server_name": "syncgroupcrud-3379.database.windows.net",
          "database_name": "syncgroupcrud-7421",
          "user_name": "myUser",
          "sync_direction": "Bidirectional",
          "use_private_link_connection": True,
          "sync_member_azure_database_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_members.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/put/Create a new sync member[put]
#--------------------------------------------------------------------------
        BODY = {
          "database_type": "AzureSqlDatabase",
          "server_name": "syncgroupcrud-3379.database.windows.net",
          "database_name": "syncgroupcrud-7421",
          "user_name": "myUser",
          "sync_direction": "Bidirectional",
          "use_private_link_connection": True,
          "sync_member_azure_database_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_members.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME, parameters=BODY)
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
        # /ManagedBackupShortTermRetentionPolicies/put/Update the short term retention policy for the database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_backup_short_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/put/Update a database's threat detection policy with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled",
          "email_account_admins": True,
          "email_addresses": [
            "test@microsoft.com",
            "user@microsoft.com"
          ],
          "disabled_alerts": [
            "Sql_Injection",
            "Usage_Anomaly"
          ],
          "retention_days": "6",
          "storage_account_access_key": "sdlfkjabc+sdlfkjsdlkfsjdfLDKFTERLKFDFKLjsdfksjdflsdkfD2342309432849328476458/3RSD==",
          "storage_endpoint": "https://mystorage.blob.core.windows.net"
        }
        result = self.mgmt_client.managed_database_security_alert_policies.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, database_security_alert_policy_resource=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/put/Update a database's threat detection policy with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "state": "Enabled"
        }
        result = self.mgmt_client.managed_database_security_alert_policies.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME, database_security_alert_policy_resource=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessments/put/Create a database's vulnerability assessment with minimal parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        }
        result = self.mgmt_client.managed_database_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessments/put/Create a database's vulnerability assessment with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "storage_container_path": "https://myStorage.blob.core.windows.net/vulnerability-assessment/",
          "storage_container_sas_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
          "recurring_scans": {
            "is_enabled": True,
            "email_subscription_admins": True,
            "emails": [
              "email1@mail.com",
              "email2@mail.com"
            ]
          }
        }
        result = self.mgmt_client.managed_database_vulnerability_assessments.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingRules/put/Create/Update data masking rule for default max[put]
#--------------------------------------------------------------------------
        BODY = {
          "alias_name": "nickname",
          "schema_name": "dbo",
          "table_name": "Table_1",
          "column_name": "test1",
          "masking_function": "Default",
          "rule_state": "Enabled"
        }
        result = self.mgmt_client.data_masking_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, data_masking_rule_name=DATA_MASKING_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingRules/put/Create/Update data masking rule for default min[put]
#--------------------------------------------------------------------------
        BODY = {
          "schema_name": "dbo",
          "table_name": "Table_1",
          "column_name": "test1",
          "masking_function": "Default"
        }
        result = self.mgmt_client.data_masking_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, data_masking_rule_name=DATA_MASKING_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingRules/put/Create/Update data masking rule for numbers[put]
#--------------------------------------------------------------------------
        BODY = {
          "schema_name": "dbo",
          "table_name": "Table_1",
          "column_name": "test1",
          "masking_function": "Number",
          "number_from": "0",
          "number_to": "2"
        }
        result = self.mgmt_client.data_masking_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, data_masking_rule_name=DATA_MASKING_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DataMaskingRules/put/Create/Update data masking rule for text[put]
#--------------------------------------------------------------------------
        BODY = {
          "schema_name": "dbo",
          "table_name": "Table_1",
          "column_name": "test1",
          "masking_function": "Text",
          "prefix_size": "1",
          "suffix_size": "0",
          "replacement_string": "asdf"
        }
        result = self.mgmt_client.data_masking_rules.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME, data_masking_rule_name=DATA_MASKING_RULE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /WorkloadClassifiers/put/Create a workload group with all properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "member_name": "dbo",
          "label": "test_label",
          "context": "test_context",
          "start_time": "12:00",
          "end_time": "14:00",
          "importance": "high"
        }
        result = self.mgmt_client.workload_classifiers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, workload_classifier_name=WORKLOAD_CLASSIFIER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WorkloadClassifiers/put/Create a workload group with the required properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "member_name": "dbo"
        }
        result = self.mgmt_client.workload_classifiers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, workload_classifier_name=WORKLOAD_CLASSIFIER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedRestorableDroppedDatabaseBackupShortTermRetentionPolicies/put/Update the short term retention policy for the restorable dropped database.[put]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_restorable_dropped_database_backup_short_term_retention_policies.begin_create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, restorable_dropped_database_id=RESTORABLE_DROPPED_DATABASE_ID, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentRuleBaselines/put/Creates or updates a database's vulnerability assessment rule baseline.[put]
#--------------------------------------------------------------------------
        BODY = {
          "baseline_results": [
            {
              "result": [
                "userA",
                "SELECT"
              ]
            },
            {
              "result": [
                "userB",
                "SELECT"
              ]
            },
            {
              "result": [
                "userC",
                "SELECT",
                "tableId_4"
              ]
            }
          ]
        }
        result = self.mgmt_client.database_vulnerability_assessment_rule_baselines.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /SensitivityLabels/put/Updates the sensitivity label of a given column with all parameters[put]
#--------------------------------------------------------------------------
        BODY = {
          "information_type": "PhoneNumber",
          "information_type_id": "d22fa6e9-5ee4-3bde-4c2b-a409604c4646",
          "label_id": "bf91e08c-f4f0-478a-b016-25164b2a65ff",
          "label_name": "PII"
        }
        result = self.mgmt_client.sensitivity_labels.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentRuleBaselines/put/Creates or updates a database's vulnerability assessment rule baseline.[put]
#--------------------------------------------------------------------------
        BODY = {
          "baseline_results": [
            {
              "result": [
                "userA",
                "SELECT"
              ]
            },
            {
              "result": [
                "userB",
                "SELECT"
              ]
            },
            {
              "result": [
                "userC",
                "SELECT",
                "tableId_4"
              ]
            }
          ]
        }
        result = self.mgmt_client.managed_database_vulnerability_assessment_rule_baselines.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/put/Updates or creates a sensitivity label of a given column with all parameters in a managed database[put]
#--------------------------------------------------------------------------
        BODY = {
          "information_type": "PhoneNumber",
          "information_type_id": "d22fa6e9-5ee4-3bde-4c2b-a409604c4646",
          "label_id": "bf91e08c-f4f0-478a-b016-25164b2a65ff",
          "label_name": "PII"
        }
        result = self.mgmt_client.managed_database_sensitivity_labels.create_or_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE, parameters=BODY)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get the long term retention backup.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.get_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/get/Gets the sensitivity label of a given column in a managed database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get the long term retention backup.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.get_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentRuleBaselines/get/Gets a database's vulnerability assessment rule baseline.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessment_rule_baselines.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_database(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SensitivityLabels/get/Gets the sensitivity label of a given column[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_database(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentRuleBaselines/get/Gets a database's vulnerability assessment rule baseline.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessment_rule_baselines.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get the long term retention backup.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.get_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get the long term retention backup of a managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.get(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, backup_name=BACKUP_NAME)

#--------------------------------------------------------------------------
        # /ManagedRestorableDroppedDatabaseBackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_restorable_dropped_database_backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, restorable_dropped_database_id=RESTORABLE_DROPPED_DATABASE_ID, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/Get a job step target execution[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID, step_name=STEP_NAME, target_id=TARGET_ID)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentScans/get/Gets a database vulnerability assessment scan record by scan ID[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessment_scans.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_database(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME)

#--------------------------------------------------------------------------
        # /WorkloadClassifiers/get/Gets a workload classifier for a data warehouse[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_classifiers.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, workload_classifier_name=WORKLOAD_CLASSIFIER_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_database(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedRestorableDroppedDatabaseBackupShortTermRetentionPolicies/get/Get the short term retention policy list for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_restorable_dropped_database_backup_short_term_retention_policies.list_by_restorable_dropped_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, restorable_dropped_database_id=RESTORABLE_DROPPED_DATABASE_ID)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentScans/get/Gets the list of a database vulnerability assessment scan records[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessment_scans.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/List job step target executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_executions.list_by_job_execution(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /TransparentDataEncryptionActivities/get/List a database's transparent data encryption activities[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.transparent_data_encryption_activities.list_by_configuration(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentScans/get/Gets a database vulnerability assessment scan record by scan ID[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessment_scans.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessments/get/Get a database's vulnerability assessment[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessments.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /JobStepExecutions/get/Get a job step execution[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_step_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the managed instance.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_instance(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/get/Get a sync member schema[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.list_member_schemas(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/get/Get a database's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/Get the specified version of a job step.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.get_by_version(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceLongTermRetentionPolicies/get/Get the long term retention policy for the managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_long_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/get/Get a sync member[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentScans/get/Gets the list of a database vulnerability assessment scan records[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessment_scans.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /TransparentDataEncryptions/get/Get a database's transparent data encryption configuration[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.transparent_data_encryptions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, transparent_data_encryption_name=TRANSPARENT_DATA_ENCRYPTION_NAME)

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/List job step target executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_executions.list_by_job_execution(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the server.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_server(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/get/Get a database's vulnerability assessment[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessments.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /JobStepExecutions/get/List job step executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_step_executions.list_by_job_execution(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /WorkloadClassifiers/get/Get the list of workload classifiers for a workload group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_classifiers.list_by_workload_group(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseRestoreDetails/get/Managed database restore details.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_restore_details.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, restore_details_name=RESTORE_DETAILS_NAME)

#--------------------------------------------------------------------------
        # /DataMaskingRules/get/List data masking rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.data_masking_rules.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/get/Get an extended database's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_database_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /DatabaseThreatDetectionPolicies/get/Get database security alert policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_threat_detection_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/Get a job execution.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /JobSteps/get/List job steps for the specified version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.list_by_version(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION)

#--------------------------------------------------------------------------
        # /RestorableDroppedManagedDatabases/get/Gets a restorable dropped managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restorable_dropped_managed_databases.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, restorable_dropped_database_id=RESTORABLE_DROPPED_DATABASE_ID)

#--------------------------------------------------------------------------
        # /ServiceTierAdvisors/get/Get a service tier advisor[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_tier_advisors.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, service_tier_advisor_name=SERVICE_TIER_ADVISOR_NAME)

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/get/Get the short term retention policy list for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_backup_short_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DataMaskingPolicies/get/Get data masking policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.data_masking_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, data_masking_policy_name=DATA_MASKING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceLongTermRetentionPolicies/get/Get the long term retention policies for the managed database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_long_term_retention_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /BackupLongTermRetentionPolicies/get/Get the long term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_long_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/get/Get a managed instance's vulnerability assessment[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_vulnerability_assessments.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/get/Get a database's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobVersions/get/Get a version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_versions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/get/Gets the recommended sensitivity labels of a given database in a managed database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.list_recommended_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/get/Get geo backup policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.geo_backup_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, geo_backup_policy_name=GEO_BACKUP_POLICY_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/get/List sync members under a sync group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.list_by_sync_group(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/get/Get a database's automatic tuning settings[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_automatic_tuning.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME)

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/get/Get a managed server's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_server_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessments/get/Get a database's vulnerability assessments list[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessments.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/get/Gets the current sensitivity labels of a given database in a managed database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.list_current_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a hub database schema.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_hub_schemas(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/Get the latest version of a job step.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /RecoverableManagedDatabases/get/Gets a recoverable databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recoverable_managed_databases.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, recoverable_database_name=RECOVERABLE_DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSecurityAlertPolicies/get/Get a list of the database's threat detection policies.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_security_alert_policies.list_by_database(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/get/Get the encryption protector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_encryption_protectors.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)

#--------------------------------------------------------------------------
        # /WorkloadGroups/get/Gets a workload group for a data warehouse[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the managed instance.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_instance(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /RestorePoints/get/Gets a datawarehouse database restore point.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, restore_point_name=RESTORE_POINT_NAME)

#--------------------------------------------------------------------------
        # /RestorePoints/get/Gets a database restore point.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, restore_point_name=RESTORE_POINT_NAME)

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/Get recommended elastic pool metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, recommended_elastic_pool_name=RECOMMENDED_ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /JobTargetGroups/get/Get a target group.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get sync group logs[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_logs(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, start_time="2017-01-01T00:00:00", end_time="2017-12-31T00:00:00", type="All")

#--------------------------------------------------------------------------
        # /RestorableDroppedDatabases/get/Get a restorable dropped database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restorable_dropped_databases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, restorable_droppeded_database_id=RESTORABLE_DROPPEDED_DATABASE_ID)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets private endpoint connection.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

#--------------------------------------------------------------------------
        # /ElasticPoolDatabaseActivities/get/List elastic pool database activity[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_database_activities.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /JobCredentials/get/Get a credential[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a sync group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/get/Get the short term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_short_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/List a job's executions.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /BackupLongTermRetentionPolicies/get/Get the long term retention policy for the database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.backup_long_term_retention_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME)

#--------------------------------------------------------------------------
        # /ReplicationLinks/get/Get a replication link[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replication_links.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, link_id=LINK_ID)

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/get/Get a server's vulnerability assessment[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_vulnerability_assessments.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/Get a recommended elastic pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, recommended_elastic_pool_name=RECOMMENDED_ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /JobVersions/get/Get all versions of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_versions.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /SensitivityLabels/get/Gets the recommended sensitivity labels of a given database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.list_recommended_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceAdministrators/get/Get administrator of managed instance[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_administrators.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, administrator_name=ADMINISTRATOR_NAME)

#--------------------------------------------------------------------------
        # /ElasticPoolActivities/get/List Elastic pool activity[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_activities.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/get/Get a server's blob extended auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_server_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/List job steps for the latest version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the server.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_server(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /ExtendedDatabaseBlobAuditingPolicies/get/List extended auditing settings of a database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_database_blob_auditing_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/get/Get the database's vulnerability assessment policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessments.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/get/Get a server's threat detection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_security_alert_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, security_alert_policy_name=SECURITY_ALERT_POLICY_NAME)

#--------------------------------------------------------------------------
        # /SensitivityLabels/get/Gets the current sensitivity labels of a given database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.list_current_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/get/Get failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_failover_groups.get(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, failover_group_name=FAILOVER_GROUP_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/get/Gets a Azure Active Directory only authentication property.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adonly_authentications.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME)

#--------------------------------------------------------------------------
        # /EncryptionProtectors/get/Get the encryption protector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/get/Gets a virtual network rule[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME)

#--------------------------------------------------------------------------
        # /Jobs/get/Get a job[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /ServiceTierAdvisors/get/Get a list of a service tier advisors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_tier_advisors.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/get/Get a server communication link[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get sync agent linked databases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.list_linked_databases(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/get/Get a server's blob auditing policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_blob_auditing_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, blob_auditing_policy_name=BLOB_AUDITING_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/get/Gets the managed instance management operation[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_operations.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/Gets a managed database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ServerConnectionPolicies/get/Get a server's secure connection policy[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_connection_policies.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, connection_policy_name=CONNECTION_POLICY_NAME)

#--------------------------------------------------------------------------
        # /GeoBackupPolicies/get/List geo backup policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.geo_backup_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /ElasticPoolOperations/get/List the elastic pool management operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_operations.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/List inaccessible managed databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.list_inaccessible_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/Gets a list of databases in an elastic pool.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_by_elastic_pool(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /ReplicationLinks/get/List Replication links[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replication_links.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ServiceObjectives/get/Get a service objective[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_objectives.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, service_objective_name=SERVICE_OBJECTIVE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseBlobAuditingPolicies/get/List audit settings of a database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_blob_auditing_policies.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /RestorableDroppedManagedDatabases/get/List restorable dropped databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restorable_dropped_managed_databases.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /WorkloadGroups/get/Get the list of workload groups for a data warehouse[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /JobTargetGroups/get/Get all target groups in an agent.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /ServerAutomaticTuning/get/Get a server's automatic tuning settings[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_automatic_tuning.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME)

#--------------------------------------------------------------------------
        # /RestorePoints/get/List datawarehouse database restore points.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /RestorePoints/get/List database restore points.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/get/Get a managed instance's vulnerability assessment policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_vulnerability_assessments.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_location(location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /JobCredentials/get/List credentials in a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/List all job executions in a job agent.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/List all job executions in a job agent with filtering.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, create_time_min="2017-03-21T19:00:00Z", create_time_max="2017-03-21T19:05:00Z", end_time_min="2017-03-21T19:20:00Z", end_time_max="2017-03-21T19:25:00Z")

#--------------------------------------------------------------------------
        # /RecoverableDatabases/get/Get a recoverable database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recoverable_databases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /FailoverGroups/get/Get failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)

#--------------------------------------------------------------------------
        # /ManagedServerSecurityAlertPolicies/get/Get the managed server's threat detection policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_server_security_alert_policies.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /DatabaseOperations/get/List the database management operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_operations.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/get/List sync groups under a given database[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /RecoverableManagedDatabases/get/List recoverable databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recoverable_managed_databases.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/get/Gets a Azure Active Directory administrator.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adadministrators.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/get/Get Firewall Rule[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/get/Get the managed instance key[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/get/List encryption protectors by managed instance[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_encryption_protectors.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_metrics(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, filter="name/value eq 'cpu_percent' and timeGrain eq '00:10:00' and startTime eq '2017-06-02T18:35:00Z' and endTime eq '2017-06-02T18:55:00Z'")

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets a private link resource for SQL.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, group_name=GROUP_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/get/Get an elastic pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)

#--------------------------------------------------------------------------
        # /DatabaseUsages/get/List database usage metrics[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_usages.list_by_database(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /Jobs/get/List jobs in a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceAdministrators/get/List administrators of managed instance[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_administrators.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get a sync agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /ServerDnsAliases/get/Get server DNS alias[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME)

#--------------------------------------------------------------------------
        # /JobAgents/get/Get a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/Gets a database.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/get/List the managed instance management operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_operations.list_by_managed_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances by instance pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list_by_instance_pool(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_location(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/get/List databases by managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /RestorableDroppedDatabases/get/Get list of restorable dropped databases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restorable_dropped_databases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/get/List failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_failover_groups.list_by_location(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/get/Gets list of private endpoint connections on a server.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/get/Gets a list of Azure Active Directory only authentication object.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adonly_authentications.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ExtendedServerBlobAuditingPolicies/get/List extended auditing settings of a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.extended_server_blob_auditing_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/get/Get a server's vulnerability assessment policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_vulnerability_assessments.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /RecommendedElasticPools/get/List recommended elastic pools[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recommended_elastic_pools.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/get/List the keys for a managed instance.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.list_by_instance(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ServerSecurityAlertPolicies/get/List the server's threat detection policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_security_alert_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /RecoverableDatabases/get/Get list of restorable dropped databases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.recoverable_databases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /PrivateLinkResources/get/Gets private link resources for SQL.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_link_resources.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /EncryptionProtectors/get/List encryption protectors by server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerKeys/get/Get the server key[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME)

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/get/List virtual network rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Usages/get/List instance pool usages.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.usages.list_by_instance_pool(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)

#--------------------------------------------------------------------------
        # /Usages/get/List instance pool usages expanded with children.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.usages.list_by_instance_pool(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, expand_children="true")

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/get/List server communication links[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/Get managed instance[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.get(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)

#--------------------------------------------------------------------------
        # /ServiceObjectives/get/List service objectives[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.service_objectives.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /VirtualClusters/get/Get virtual cluster[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_clusters.get(resource_group_name=RESOURCE_GROUP, virtual_cluster_name=VIRTUAL_CLUSTER_NAME)

#--------------------------------------------------------------------------
        # /ServerBlobAuditingPolicies/get/List auditing settings of a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_blob_auditing_policies.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /FailoverGroups/get/List failover group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/get/Gets a list of Azure Active Directory administrator.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adadministrators.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /FirewallRules/get/List Firewall Rules[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ElasticPools/get/Get all elastic pools in a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /InstancePools/get/Get an instance pool[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.get(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)

#--------------------------------------------------------------------------
        # /SyncAgents/get/Get sync agents under a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerDnsAliases/get/List server DNS aliases[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Databases/get/Gets a list of databases.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /JobAgents/get/List job agents in a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.list_by_location(location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /ServerUsages/get/List servers usages[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_usages.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /ServerKeys/get/List the server keys by server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /Servers/get/Get server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/get/Get all long term retention backups under the location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.list_by_resource_group_location(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /SubscriptionUsages/get/Get specific subscription usage in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscription_usages.get(location_name=LOCATION_NAME, usage_name=USAGE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /VirtualClusters/get/List virtual clusters by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_clusters.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /InstancePools/get/List instance pools by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /SyncGroups/get/Get a sync database ID[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.list_sync_database_ids(location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /Servers/get/List servers by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Capabilities/get/List subscription capabilities in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.capabilities.list_by_location(location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /SubscriptionUsages/get/List subscription usages in the given location.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.subscription_usages.list_by_location(location_name=LOCATION_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstances/get/List managed instances[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.list()

#--------------------------------------------------------------------------
        # /VirtualClusters/get/List virtualClusters[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_clusters.list()

#--------------------------------------------------------------------------
        # /InstancePools/get/List instance pools in the subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.list()

#--------------------------------------------------------------------------
        # /Servers/get/List servers[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.list()

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/post/Disables the sensitivity recommendations on a given column[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.disable_recommendation(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/post/Enables the sensitivity recommendations on a given column[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.enable_recommendation(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /SensitivityLabels/post/Disables sensitivity recommendations on a given column[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.disable_recommendation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /SensitivityLabels/post/Enables sensitivity recommendations on a given column[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.enable_recommendation(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentScans/post/Executes a database's vulnerability assessment scan.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessment_scans.begin_initiate_scan(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentScans/post/Export a database's vulnerability assessment scan results.[post]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.managed_database_vulnerability_assessment_scans.export(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedRestorableDroppedDatabaseBackupShortTermRetentionPolicies/patch/Update the short term retention policy for the restorable dropped database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_restorable_dropped_database_backup_short_term_retention_policies.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, restorable_dropped_database_id=RESTORABLE_DROPPED_DATABASE_ID, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentScans/post/Executes a database's vulnerability assessment scan.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessment_scans.begin_initiate_scan(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentScans/post/Export a database's vulnerability assessment scan results.[post]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.database_vulnerability_assessment_scans.export(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, scan_id=SCAN_ID, parameters=BODY)

#--------------------------------------------------------------------------
        # /SyncMembers/post/Refresh a sync member database schema[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.begin_refresh_member_schema(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedBackupShortTermRetentionPolicies/patch/Update the short term retention policy for the database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14"
        }
        result = self.mgmt_client.managed_backup_short_term_retention_policies.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncMembers/patch/Update an existing sync member[patch]
#--------------------------------------------------------------------------
        BODY = {
          "database_type": "AzureSqlDatabase",
          "server_name": "syncgroupcrud-3379.database.windows.net",
          "database_name": "syncgroupcrud-7421",
          "user_name": "myUser",
          "sync_direction": "Bidirectional",
          "use_private_link_connection": True,
          "sync_member_azure_database_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.sync_members.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobExecutions/post/Cancel a job execution.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /ReplicationLinks/post/Failover a replication link[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replication_links.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, link_id=LINK_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceEncryptionProtectors/post/Revalidates the encryption protector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_encryption_protectors.begin_revalidate(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /BackupShortTermRetentionPolicies/patch/Update the short term retention policy for the database.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "retention_days": "14",
          "diff_backup_interval_in_hours": "24"
        }
        result = self.mgmt_client.backup_short_term_retention_policies.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, policy_name=POLICY_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/post/Forced failover of a failover group allowing data loss[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_failover_groups.begin_force_failover_allow_data_loss(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/post/Refresh a hub database schema.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.begin_refresh_hub_schema(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/post/Trigger a sync group synchronization.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.trigger_sync(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/patch/Updates database automatic tuning settings with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto"
        }
        result = self.mgmt_client.database_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /DatabaseAutomaticTuning/patch/Updates database automatic tuning settings with all properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto",
          "options": {
            "create_index": {
              "desired_state": "Off"
            },
            "drop_index": {
              "desired_state": "On"
            },
            "force_last_good_plan": {
              "desired_state": "Default"
            }
          }
        }
        result = self.mgmt_client.database_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ElasticPoolOperations/post/Cancel the elastic pool management operation[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pool_operations.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /SyncGroups/post/Cancel a sync group synchronization[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.cancel_sync(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)

#--------------------------------------------------------------------------
        # /ReplicationLinks/post/Failover a replication link[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replication_links.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, link_id=LINK_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /ReplicationLinks/post/Delete replication link[post]
#--------------------------------------------------------------------------
        BODY = {
          "forced_termination": True
        }
        result = self.mgmt_client.replication_links.begin_unlink(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, link_id=LINK_ID, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/post/Forced failover of a failover group allowing data loss[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_force_failover_allow_data_loss(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseOperations/post/Cancel the database management operation[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_operations.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /ManagedDatabases/post/Completes a managed database external backup restore.[post]
#--------------------------------------------------------------------------
        BODY = {
          "last_backup_name": "testdb1_log4"
        }
        result = self.mgmt_client.managed_databases.begin_complete_restore(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /EncryptionProtectors/post/Revalidates the encryption protector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.encryption_protectors.begin_revalidate(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, encryption_protector_name=ENCRYPTION_PROTECTOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncGroups/patch/Update a sync group[patch]
#--------------------------------------------------------------------------
        BODY = {
          "interval": "-1",
          "conflict_resolution_policy": "HubWin",
          "sync_database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME,
          "hub_database_user_name": "hubUser",
          "hub_database_password": "hubPassword",
          "use_private_link_connection": False
        }
        result = self.mgmt_client.sync_groups.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/post/Planned failover of a failover group[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_failover_groups.begin_failover(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobExecutions/post/Start a job execution.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstanceOperations/post/Cancel the managed instance management operation[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_operations.cancel(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /Databases/post/Upgrades a data warehouse.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_upgrade_data_warehouse(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/post/Planned failover of a failover group[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

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
        # /ManagedDatabases/patch/Updates a managed database with maximal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          }
        }
        result = self.mgmt_client.managed_databases.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/post/Failover an elastic pool[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/post/Generate a sync agent key[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.generate_key(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)

#--------------------------------------------------------------------------
        # /ServerAutomaticTuning/patch/Updates server automatic tuning settings with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto"
        }
        result = self.mgmt_client.server_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ServerAutomaticTuning/patch/Updates server automatic tuning settings with all properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "desired_state": "Auto",
          "options": {
            "create_index": {
              "desired_state": "Off"
            },
            "drop_index": {
              "desired_state": "On"
            },
            "force_last_good_plan": {
              "desired_state": "Default"
            }
          }
        }
        result = self.mgmt_client.server_automatic_tuning.update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, automatic_tuning_name=AUTOMATIC_TUNING_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /RestorePoints/post/Creates datawarehouse database restore point.[post]
#--------------------------------------------------------------------------
        BODY = {
          "restore_point_label": "mylabel"
        }
        result = self.mgmt_client.restore_points.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/patch/Update failover group[patch]
#--------------------------------------------------------------------------
        BODY = {
          "read_write_endpoint": {
            "failover_policy": "Automatic",
            "failover_with_data_loss_grace_period_minutes": "120"
          },
          "databases": [
            "/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/Default/providers/Microsoft.Sql/servers/failover-group-primary-server/databases/testdb-1"
          ]
        }
        result = self.mgmt_client.failover_groups.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/post/Acquire server DNS alias[post]
#--------------------------------------------------------------------------
        BODY = {
          "old_server_dns_alias_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/dnsAliases/" + DNS_ALIASE_NAME
        }
        result = self.mgmt_client.server_dns_aliases.begin_acquire(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Failover an database[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_failover(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, replica_type="Primary")
        result = result.result()

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
        result = self.mgmt_client.databases.begin_export(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_export(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Resumes a database.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_resume(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/patch/Update an elastic pool with all parameter[patch]
#--------------------------------------------------------------------------
        BODY = {
          "sku": {
            "name": "BC_Gen4_2",
            "tier": "BusinessCritical",
            "capacity": "2"
          },
          "per_database_settings": {
            "min_capacity": "0.25",
            "max_capacity": "1"
          },
          "zone_redundant": True,
          "license_type": "LicenseIncluded"
        }
        result = self.mgmt_client.elastic_pools.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/patch/Update an elastic pool with minimum parameters[patch]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.elastic_pools.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Pauses a database.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_pause(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/post/Renames a database.[post]
#--------------------------------------------------------------------------
        BODY = {
          "id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.databases.rename(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /ManagedInstanceTdeCertificates/post/Upload a TDE certificate[post]
#--------------------------------------------------------------------------
        BODY = {
          "private_blob": "MIIJ+QIBAzCCCbUGCSqGSIb3DQEHAaCCCaYEggmiMIIJnjCCBhcGCSqGSIb3DQEHAaCCBggEggYEMIIGADCCBfwGCyqGSIb3DQEMCgECoIIE/jCCBPowHAYKKoZIhvcNAQwBAzAOBAgUeBd7F2KZUwICB9AEggTYSRi88/Xf0EZ9smyYDCr+jHa7a/510s19/5wjqGbLTT/CYBu2qSOhj+g9sNvjj5oWAcluaZ4XCl/oJhXlB+9q9ZYSC6pPhma7/Il+/zlZm8ZUMfgnUefpKXGj+Ilydghya2DOA0PONDGbqIJGBYC0JgtiL7WcYyA+LEiO0vXc2fZ+ccjQsHM+ePFOm6rTJ1oqE3quRC5Ls2Bv22PCmF+GWkWxqH1L5x8wR2tYfecEsx4sKMj318novQqBlJckOUPDrTT2ic6izFnDWS+zbGezSCeRkt2vjCUVDg7Aqm2bkmLVn+arA3tDZ/DBxgTwwt8prpAznDYG07WRxXMUk8Uqzmcds85jSMLSBOoRaS7GwIPprx0QwyYXd8H/go2vafuGCydRk8mA0bGLXjYWuYHAtztlGrE71a7ILqHY4XankohSAY4YF9Fc1mJcdtsuICs5vNosw1lf0VK5BR4ONCkiGFdYEKUpaUrzKpQiw3zteBN8RQs/ADKGWzaWERrkptf0pLH3/QnZvu9xwwnNWneygByPy7OVYrvgjD27x7Y/C24GyQweh75OTQN3fAvUj7IqeTVyWZGZq32AY/uUXYwASBpLbNUtUBfJ7bgyvVSZlPvcFUwDHJC1P+fSP8Vfcc9W3ec9HqVheXio7gYBEg9hZrOZwiZorl8HZJsEj5NxGccBme6hEVQRZfar5kFDHor/zmKohEAJVw8lVLkgmEuz8aqQUDSWVAcLbkfqygK/NxsR2CaC6xWroagQSRwpF8YbvqYJtAQvdkUXY9Ll4LSRcxKrWMZHgI+1Z22pyNtpy/kXLADche5CF3AVbHtzNNgn9L4GVuCW1Lqufu3U2+DEG+u53u1vraf45RS1y0IyLjTGC+8j0OTxcgUU6FrGgFny0m676v8potPrfyHvuOO511aOTe8UPBfnYyx0XHJPn8RaYGq0vMOBpFyfJkXtAnbRMgXjxxiO91yXTI2hbdVlAmOER1u8QemtF5PoKwZzaAjGBC5S0ARNtxZcWInGciGgtWJVVcyU6nJv3pa2T8jNvtcp8X7j+Il6j6Sju02L/f+S9MvAoGfgG6C5cInNIBEt7+mpYYV/6Mi9Nnj+8/Cq3eAMdTTo7XIzbFpeInzpVN2lAxPockRoAVj+odYO3CIBnzJ7mcA7JqtNk76vaWKasocMk9YS0Z+43o/Z5pZPwXvUv++UUv5fGRcsnIHEeQc+XJlSqRVoaLDo3mNRV6jp5GzJW2BZx3KkuLbohcmfBdr6c8ehGvHXhPm4k2jq9UNYvG9Gy58+1GqdhIYWbRc0Haid8H7UvvdkjA+Yul2rLj4fSTJ6yJ4f6xFAsFY7wIJthpik+dQO9lqPglo9DY30gEOXs3miuJmdmFtBoYlzxti4JBGwxXPwP3rtu6rY1JEOFsh1WmSEGE6Df2l9wtUQ0WAAD6bWgCxMiiRRv7TegxSeMtGn5QKuPC5lFuvzZvtJy1rR8WQwT7lVdHz32xLP2Rs4dayQPh08x3GsuI54d2kti2rcaSltGLRAOuODWc8KjYsPS6Ku4aN2NoQB5H9TEbHy2fsUNpNPMbCY54lH5bkgJtO4WmulnAHEApZG07u8G+Kk3a15npXemWgUW3N9gGtJ2XmieendXqS3RK1ZUYDsnAWW2jCZkjGB6jANBgkrBgEEAYI3EQIxADATBgkqhkiG9w0BCRUxBgQEAQAAADBXBgkqhkiG9w0BCRQxSh5IAGEAYgBjAGYAOABhADUAOQAtAGYAZQAzADIALQA0AGIAZgA0AC0AYQBiAGMAZgAtADkAOAA3AGIANwBmADgANwAzADEANgBjMGsGCSsGAQQBgjcRATFeHlwATQBpAGMAcgBvAHMAbwBmAHQAIABFAG4AaABhAG4AYwBlAGQAIABDAHIAeQBwAHQAbwBnAHIAYQBwAGgAaQBjACAAUAByAG8AdgBpAGQAZQByACAAdgAxAC4AMDCCA38GCSqGSIb3DQEHBqCCA3AwggNsAgEAMIIDZQYJKoZIhvcNAQcBMBwGCiqGSIb3DQEMAQMwDgQIbQcNiyMGeL4CAgfQgIIDOPSSP6SqJGYsXCPWCMQU0TqdqT55fauuadduHaAlQpyN0MVYdu9QguLqMaJjxWa8Coy3K7LAOcqJ4S8FWV2SrpTuNHPv7vrtZfYhltGl+vW8rIrogeGTV4T/45oc5605HSiyItOWX8vHYKnAJkRMW4ICZXgY3dZVb+fr6yPIRFvMywqzwkViVOJIKjZN2lsAQ0xlLU0Fu/va9uxADwI2ZUKfo+6nX6bITkLvUSJoNCvZ5e7UITasxC4ZauHdMZch38N7BPH2usrAQfr3omYcScFzSeN2onhE1JBURCPDQa8+CGiWMm6mxboUOIcUGasaDqYQ8pSAgZZqQf8lU0uH4FP/z/5Dd7PniDHjvqlwYa+vB6flgtrwh6jYFeTKluhkucLrfzusFR52kHpg8K4GaUL8MhvlsNdd8iHSFjfyOdXRpY9re+B8X9Eorx0Z3xsSsVWaCwmI+Spq+BZ5CSXVm9Um6ogeM0et8JciZS2yFLIlbl2o4U1BWblskYfj/29jm4/2UKjKzORZnpjE0O+qP4hReSrx6os9dr8sNkq/7OafZock8zXjXaOpW6bqB1V5NWMPiWiPxPxfRi1F/MQp6CPY03H7MsDALEFcF7MmtY4YpN/+FFfrrOwS19Fg0OnQzNIgFpSRywX9dxyKICt/wbvhM+RLpUN50ZekFVska+C27hJRJEZ9rSdVhOVdL1UNknuwqF1cCQQriaNsnCbeVHN3/Wgsms9+Kt+glBNyZQlU8Fk+fafcQFI5MlxyMmARVwnC70F8AScnJPPFVZIdgIrvOXCDrEh8wFgkVM/MHkaTZUF51yy3pbIZaPmNd5dsUfEvMsW2IY6esnUUxPRQUUoi5Ib8EFHdiQJrYY3ELfZRXb2I1Xd0DVhlGzogn3CXZtXR2gSAakdB0qrLpXMSJNS65SS2tVTD7SI8OpUGNRjthQIAEEROPue10geFUwarWi/3jGMG529SzwDUJ4g0ix6VtcuLIDYFNdClDTyEyeV1f70NSG2QVXPIpeF7WQ8jWK7kenGaqqna4C4FYQpQk9vJP171nUXLR2mUR11bo1N4hcVhXnJls5yo9u14BB9CqVKXeDl7M5zwMDswHzAHBgUrDgMCGgQUT6Tjuka1G4O/ZCBxO7NBR34YUYQEFLaheEdRIIuxUd25/hl5vf2SFuZuAgIH0A==",
          "cert_password": "password"
        }
        result = self.mgmt_client.managed_instance_tde_certificates.begin_create(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/patch/Update a job agent's tags.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "mytag1": "myvalue1"
          }
        }
        result = self.mgmt_client.job_agents.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, parameters=BODY)
        result = result.result()

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
        # /ManagedInstances/post/Failover a managed instance.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.begin_failover(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, replica_type="Primary")
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/patch/Update managed instance with minimal properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          }
        }
        result = self.mgmt_client.managed_instances.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/patch/Update managed instance with all properties[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          },
          "sku": {
            "name": "GP_Gen4",
            "tier": "GeneralPurpose",
            "capacity": "8"
          },
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!",
          "proxy_override": "Redirect",
          "public_data_endpoint_enabled": False,
          "license_type": "BasePrice",
          "v_cores": "8",
          "storage_size_in_gb": "448",
          "collation": "SQL_Latin1_General_CP1_CI_AS",
          "maintenance_configuration_id": "/subscriptions/" + SUBSCRIPTION_ID + "/providers/Microsoft.Maintenance/publicMaintenanceConfigurations/" + PUBLIC_MAINTENANCE_CONFIGURATION_NAME
        }
        result = self.mgmt_client.managed_instances.begin_update(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /VirtualClusters/patch/Update virtual cluster with tags[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "tag_key1": "TagValue1"
          }
        }
        result = self.mgmt_client.virtual_clusters.begin_update(resource_group_name=RESOURCE_GROUP, virtual_cluster_name=VIRTUAL_CLUSTER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TdeCertificates/post/Upload a TDE certificate[post]
#--------------------------------------------------------------------------
        BODY = {
          "private_blob": "MIIJ+QIBAzCCCbUGCSqGSIb3DQEHAaCCCaYEggmiMIIJnjCCBhcGCSqGSIb3DQEHAaCCBggEggYEMIIGADCCBfwGCyqGSIb3DQEMCgECoIIE/jCCBPowHAYKKoZIhvcNAQwBAzAOBAgUeBd7F2KZUwICB9AEggTYSRi88/Xf0EZ9smyYDCr+jHa7a/510s19/5wjqGbLTT/CYBu2qSOhj+g9sNvjj5oWAcluaZ4XCl/oJhXlB+9q9ZYSC6pPhma7/Il+/zlZm8ZUMfgnUefpKXGj+Ilydghya2DOA0PONDGbqIJGBYC0JgtiL7WcYyA+LEiO0vXc2fZ+ccjQsHM+ePFOm6rTJ1oqE3quRC5Ls2Bv22PCmF+GWkWxqH1L5x8wR2tYfecEsx4sKMj318novQqBlJckOUPDrTT2ic6izFnDWS+zbGezSCeRkt2vjCUVDg7Aqm2bkmLVn+arA3tDZ/DBxgTwwt8prpAznDYG07WRxXMUk8Uqzmcds85jSMLSBOoRaS7GwIPprx0QwyYXd8H/go2vafuGCydRk8mA0bGLXjYWuYHAtztlGrE71a7ILqHY4XankohSAY4YF9Fc1mJcdtsuICs5vNosw1lf0VK5BR4ONCkiGFdYEKUpaUrzKpQiw3zteBN8RQs/ADKGWzaWERrkptf0pLH3/QnZvu9xwwnNWneygByPy7OVYrvgjD27x7Y/C24GyQweh75OTQN3fAvUj7IqeTVyWZGZq32AY/uUXYwASBpLbNUtUBfJ7bgyvVSZlPvcFUwDHJC1P+fSP8Vfcc9W3ec9HqVheXio7gYBEg9hZrOZwiZorl8HZJsEj5NxGccBme6hEVQRZfar5kFDHor/zmKohEAJVw8lVLkgmEuz8aqQUDSWVAcLbkfqygK/NxsR2CaC6xWroagQSRwpF8YbvqYJtAQvdkUXY9Ll4LSRcxKrWMZHgI+1Z22pyNtpy/kXLADche5CF3AVbHtzNNgn9L4GVuCW1Lqufu3U2+DEG+u53u1vraf45RS1y0IyLjTGC+8j0OTxcgUU6FrGgFny0m676v8potPrfyHvuOO511aOTe8UPBfnYyx0XHJPn8RaYGq0vMOBpFyfJkXtAnbRMgXjxxiO91yXTI2hbdVlAmOER1u8QemtF5PoKwZzaAjGBC5S0ARNtxZcWInGciGgtWJVVcyU6nJv3pa2T8jNvtcp8X7j+Il6j6Sju02L/f+S9MvAoGfgG6C5cInNIBEt7+mpYYV/6Mi9Nnj+8/Cq3eAMdTTo7XIzbFpeInzpVN2lAxPockRoAVj+odYO3CIBnzJ7mcA7JqtNk76vaWKasocMk9YS0Z+43o/Z5pZPwXvUv++UUv5fGRcsnIHEeQc+XJlSqRVoaLDo3mNRV6jp5GzJW2BZx3KkuLbohcmfBdr6c8ehGvHXhPm4k2jq9UNYvG9Gy58+1GqdhIYWbRc0Haid8H7UvvdkjA+Yul2rLj4fSTJ6yJ4f6xFAsFY7wIJthpik+dQO9lqPglo9DY30gEOXs3miuJmdmFtBoYlzxti4JBGwxXPwP3rtu6rY1JEOFsh1WmSEGE6Df2l9wtUQ0WAAD6bWgCxMiiRRv7TegxSeMtGn5QKuPC5lFuvzZvtJy1rR8WQwT7lVdHz32xLP2Rs4dayQPh08x3GsuI54d2kti2rcaSltGLRAOuODWc8KjYsPS6Ku4aN2NoQB5H9TEbHy2fsUNpNPMbCY54lH5bkgJtO4WmulnAHEApZG07u8G+Kk3a15npXemWgUW3N9gGtJ2XmieendXqS3RK1ZUYDsnAWW2jCZkjGB6jANBgkrBgEEAYI3EQIxADATBgkqhkiG9w0BCRUxBgQEAQAAADBXBgkqhkiG9w0BCRQxSh5IAGEAYgBjAGYAOABhADUAOQAtAGYAZQAzADIALQA0AGIAZgA0AC0AYQBiAGMAZgAtADkAOAA3AGIANwBmADgANwAzADEANgBjMGsGCSsGAQQBgjcRATFeHlwATQBpAGMAcgBvAHMAbwBmAHQAIABFAG4AaABhAG4AYwBlAGQAIABDAHIAeQBwAHQAbwBnAHIAYQBwAGgAaQBjACAAUAByAG8AdgBpAGQAZQByACAAdgAxAC4AMDCCA38GCSqGSIb3DQEHBqCCA3AwggNsAgEAMIIDZQYJKoZIhvcNAQcBMBwGCiqGSIb3DQEMAQMwDgQIbQcNiyMGeL4CAgfQgIIDOPSSP6SqJGYsXCPWCMQU0TqdqT55fauuadduHaAlQpyN0MVYdu9QguLqMaJjxWa8Coy3K7LAOcqJ4S8FWV2SrpTuNHPv7vrtZfYhltGl+vW8rIrogeGTV4T/45oc5605HSiyItOWX8vHYKnAJkRMW4ICZXgY3dZVb+fr6yPIRFvMywqzwkViVOJIKjZN2lsAQ0xlLU0Fu/va9uxADwI2ZUKfo+6nX6bITkLvUSJoNCvZ5e7UITasxC4ZauHdMZch38N7BPH2usrAQfr3omYcScFzSeN2onhE1JBURCPDQa8+CGiWMm6mxboUOIcUGasaDqYQ8pSAgZZqQf8lU0uH4FP/z/5Dd7PniDHjvqlwYa+vB6flgtrwh6jYFeTKluhkucLrfzusFR52kHpg8K4GaUL8MhvlsNdd8iHSFjfyOdXRpY9re+B8X9Eorx0Z3xsSsVWaCwmI+Spq+BZ5CSXVm9Um6ogeM0et8JciZS2yFLIlbl2o4U1BWblskYfj/29jm4/2UKjKzORZnpjE0O+qP4hReSrx6os9dr8sNkq/7OafZock8zXjXaOpW6bqB1V5NWMPiWiPxPxfRi1F/MQp6CPY03H7MsDALEFcF7MmtY4YpN/+FFfrrOwS19Fg0OnQzNIgFpSRywX9dxyKICt/wbvhM+RLpUN50ZekFVska+C27hJRJEZ9rSdVhOVdL1UNknuwqF1cCQQriaNsnCbeVHN3/Wgsms9+Kt+glBNyZQlU8Fk+fafcQFI5MlxyMmARVwnC70F8AScnJPPFVZIdgIrvOXCDrEh8wFgkVM/MHkaTZUF51yy3pbIZaPmNd5dsUfEvMsW2IY6esnUUxPRQUUoi5Ib8EFHdiQJrYY3ELfZRXb2I1Xd0DVhlGzogn3CXZtXR2gSAakdB0qrLpXMSJNS65SS2tVTD7SI8OpUGNRjthQIAEEROPue10geFUwarWi/3jGMG529SzwDUJ4g0ix6VtcuLIDYFNdClDTyEyeV1f70NSG2QVXPIpeF7WQ8jWK7kenGaqqna4C4FYQpQk9vJP171nUXLR2mUR11bo1N4hcVhXnJls5yo9u14BB9CqVKXeDl7M5zwMDswHzAHBgUrDgMCGgQUT6Tjuka1G4O/ZCBxO7NBR34YUYQEFLaheEdRIIuxUd25/hl5vf2SFuZuAgIH0A==",
          "cert_password": "password"
        }
        result = self.mgmt_client.tde_certificates.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstancePools/patch/Patch an instance pool[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "x": "y"
          }
        }
        result = self.mgmt_client.instance_pools.begin_update(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME, parameters=BODY)
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
        result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

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
        result = self.mgmt_client.databases.begin_import(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/patch/Update a server[patch]
#--------------------------------------------------------------------------
        BODY = {
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/post/Check for a server name that already exists[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "server1",
          "type": "Microsoft.Sql/servers"
        }
        result = self.mgmt_client.servers.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /Servers/post/Check for a server name that is available[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "server1",
          "type": "Microsoft.Sql/servers"
        }
        result = self.mgmt_client.servers.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /Servers/post/Check for a server name that is invalid[post]
#--------------------------------------------------------------------------
        BODY = {
          "name": "SERVER1",
          "type": "Microsoft.Sql/servers"
        }
        result = self.mgmt_client.servers.check_name_availability(parameters=BODY)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.begin_delete_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseSensitivityLabels/delete/Deletes the sensitivity label of a given column in a managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_sensitivity_labels.delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.begin_delete(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, backup_name=BACKUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessmentRuleBaselines/delete/Removes a database's vulnerability assessment rule baseline.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessment_rule_baselines.delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME)

#--------------------------------------------------------------------------
        # /SensitivityLabels/delete/Deletes the sensitivity label of a given column[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sensitivity_labels.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, schema_name=SCHEMA_NAME, table_name=TABLE_NAME, column_name=COLUMN_NAME, sensitivity_label_source=SENSITIVITY_LABEL_SOURCE)

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessmentRuleBaselines/delete/Removes a database's vulnerability assessment rule baseline.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessment_rule_baselines.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME, rule_id=RULE_ID, baseline_name=BASELINE_NAME)

#--------------------------------------------------------------------------
        # /LongTermRetentionBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_backups.begin_delete_by_resource_group(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, long_term_retention_server_name=LONG_TERM_RETENTION_SERVER_NAME, long_term_retention_database_name=LONG_TERM_RETENTION_DATABASE_NAME, backup_name=BACKUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /LongTermRetentionManagedInstanceBackups/delete/Delete the long term retention backup.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.long_term_retention_managed_instance_backups.begin_delete(location_name=LOCATION_NAME, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, backup_name=BACKUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /WorkloadClassifiers/delete/Delete a workload classifier[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_classifiers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME, workload_classifier_name=WORKLOAD_CLASSIFIER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedDatabaseVulnerabilityAssessments/delete/Remove a database's vulnerability assessment[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_database_vulnerability_assessments.delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /SyncMembers/delete/Delete a sync member[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_members.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME, sync_member_name=SYNC_MEMBER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /DatabaseVulnerabilityAssessments/delete/Remove a database's vulnerability assessment[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.database_vulnerability_assessments.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceVulnerabilityAssessments/delete/Remove a managed instance's vulnerability assessment[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_vulnerability_assessments.delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/delete/Delete a job step.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /WorkloadGroups/delete/Delete a workload group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.workload_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, workload_group_name=WORKLOAD_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /RestorePoints/delete/Deletes a restore point.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.restore_points.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, restore_point_name=RESTORE_POINT_NAME)

#--------------------------------------------------------------------------
        # /JobTargetGroups/delete/Delete a target group.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME)

#--------------------------------------------------------------------------
        # /PrivateEndpointConnections/delete/Deletes a private endpoint connection with a given name.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.private_endpoint_connections.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobCredentials/delete/Delete a credential[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME)

#--------------------------------------------------------------------------
        # /SyncGroups/delete/Delete a sync group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, sync_group_name=SYNC_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ReplicationLinks/delete/Delete a replication link[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.replication_links.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, link_id=LINK_ID)

#--------------------------------------------------------------------------
        # /ServerVulnerabilityAssessments/delete/Remove a server's vulnerability assessment[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_vulnerability_assessments.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, vulnerability_assessment_name=VULNERABILITY_ASSESSMENT_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceAdministrators/delete/Delete administrator of managed instance[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_administrators.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, administrator_name=ADMINISTRATOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstanceFailoverGroups/delete/Delete failover group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_failover_groups.begin_delete(resource_group_name=RESOURCE_GROUP, location_name=LOCATION_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADOnlyAuthentications/delete/Deletes Azure Active Directory only authentication object.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adonly_authentications.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, authentication_name=AUTHENTICATION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /VirtualNetworkRules/delete/Delete a virtual network rule[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_network_rules.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, virtual_network_rule_name=VIRTUAL_NETWORK_RULE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Jobs/delete/Delete a job[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /ServerCommunicationLinks/delete/Delete a server communication link[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_communication_links.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, communication_link_name=COMMUNICATION_LINK_NAME)

#--------------------------------------------------------------------------
        # /ManagedDatabases/delete/Delete managed database[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_databases.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /FailoverGroups/delete/Delete failover group[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.failover_groups.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, failover_group_name=FAILOVER_GROUP_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerAzureADAdministrators/delete/Delete Azure Active Directory administrator.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_azure_adadministrators.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, administrator_name=ADMINISTRATOR_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /FirewallRules/delete/Delete a firewall rule[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.firewall_rules.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, firewall_rule_name=FIREWALL_RULE_NAME)

#--------------------------------------------------------------------------
        # /ManagedInstanceKeys/delete/Delete the managed instance key[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instance_keys.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME, key_name=KEY_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ElasticPools/delete/Delete an elastic pool[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.elastic_pools.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, elastic_pool_name=ELASTIC_POOL_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /SyncAgents/delete/Delete a sync agent[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.sync_agents.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, sync_agent_name=SYNC_AGENT_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerDnsAliases/delete/Delete server DNS alias[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_dns_aliases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, dns_alias_name=DNS_ALIAS_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/delete/Delete a job agent[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ServerKeys/delete/Delete the server key[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.server_keys.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, key_name=KEY_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ManagedInstances/delete/Delete managed instance[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.managed_instances.begin_delete(resource_group_name=RESOURCE_GROUP, managed_instance_name=MANAGED_INSTANCE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /VirtualClusters/delete/Delete virtual cluster[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.virtual_clusters.begin_delete(resource_group_name=RESOURCE_GROUP, virtual_cluster_name=VIRTUAL_CLUSTER_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /InstancePools/delete/Delete an instance pool[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.instance_pools.begin_delete(resource_group_name=RESOURCE_GROUP, instance_pool_name=INSTANCE_POOL_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
