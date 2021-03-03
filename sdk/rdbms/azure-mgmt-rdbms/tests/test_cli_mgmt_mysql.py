# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 29
# Methods Covered : 29
# Examples Total  : 33
# Examples Tested : 33
# Coverage %      : 100
# ----------------------

import datetime as dt
import unittest

import azure.mgmt.rdbms.mysql
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'
ZERO = dt.timedelta(0)


class UTC(dt.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


class MgmtMySQLTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMySQLTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.rdbms.mysql.MySQLManagementClient
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_mysql(self, resource_group):
        SERVER_NAME = "testserver21341"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_GEO_NAME = "servergeo21341"
        SERVER_REPLICA_NAME = "serverreplica21341"
        SERVER_POINT_NAME = "serverpoint21341"
        DATABASE_NAME = "testdatabase21341"
        FIREWALL_RULE_NAME = "firewallrule"
        CONFIGURATION_NAME = "configuration"
        VIRTUAL_NETWORK_RULE_NAME = "virutal_networkrule"
        SECURITY_ALERT_POLICY_NAME = "securityalertpolicy"
        LOCATION_NAME = "eastus"

        # Create a new server[put]
        BODY = {
            "location": "eastus",
            "properties": {
                "administrator_login": "cloudsa",
                "administrator_login_password": "pass$w0rd",
                "ssl_enforcement": "Enabled",
                "storage_profile": {
                    "storage_mb": "128000",
                    "backup_retention_days": "7",
                    "geo_redundant_backup": "Enabled"
                },
                "create_mode": "Default"
            },
            "sku": {
                "name": "GP_Gen5_2",
                "tier": "GeneralPurpose",
                "capacity": "2",
                "family": "Gen5"
            },
            "tags": {
                "elastic_server": "1"
            }
        }
        result = self.mgmt_client.servers.begin_create(resource_group.name, SERVER_NAME, BODY)
        result = result.result()

        # Create a server as a geo restore [put]
        # BODY = {
        #   "location": "eastus",
        #   "properties":{
        #     "create_mode": "GeoRestore",
        #     "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMySQL/servers/" + SERVER_NAME + ""
        #   },
        #   "sku": {
        #     "name": "GP_Gen5_2",
        #     "tier": "GeneralPurpose",
        #     "family": "Gen5",
        #     "capacity": "2"
        #   },
        #   "tags": {
        #     "elastic_server": "1"
        #   }
        # }
        # result = self.mgmt_client.servers.create(resource_group.name, SERVER_GEO_NAME, BODY)
        # result = result.result()

        # Create a replica server[put]
        BODY = {
            "location": "eastus",
            "properties": {
                "create_mode": "Replica",
                "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMySQL/servers/" + SERVER_NAME + ""
            }
        }
        result = self.mgmt_client.servers.begin_create(resource_group.name, SERVER_REPLICA_NAME, BODY)
        result = result.result()

        # Create a database as a point in time restore[put]
        # point_in_time = (dt.datetime.now(tz=UTC()) - dt.timedelta(minutes=1)).isoformat()
        # BODY = {
        #  "location": "eastus",
        #  "properties":{
        #    "restore_point_in_time": point_in_time,
        #    "create_mode": "PointInTimeRestore",
        #    "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMySQL/servers/" + SERVER_NAME + ""
        #  },
        #  "sku": {
        #    "name": "GP_Gen5_2",
        #    "tier": "GeneralPurpose",
        #    "family": "Gen5",
        #    "capacity": "2"
        #  },
        #  "tags": {
        #    "elastic_server": "1"
        #  }
        # }
        # result = self.mgmt_client.servers.create(resource_group.name, SERVER_POINT_NAME, BODY)
        # result = result.result()

        # DatabaseCreate[put]
        BODY = {
            "properties": {
                "charset": "utf8",
                "collation": "utf8_general_ci"
            }
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group.name, SERVER_NAME, DATABASE_NAME, BODY)
        result = result.result()

        # FirewallRuleCreate[put]
        # BODY = {
        #   "properties": {
        #     "start_ip_address": "0.0.0.0",
        #     "end_ip_address": "255.255.255.255"
        #   }
        # }
        from azure.mgmt.rdbms.mysql.models import FirewallRule
        firewall_rule = FirewallRule(start_ip_address='0.0.0.0', end_ip_address='255.255.255.255')
        result = self.mgmt_client.firewall_rules.begin_create_or_update(resource_group.name, SERVER_NAME, FIREWALL_RULE_NAME, firewall_rule)
        result = result.result()

        # ConfigurationCreateOrUpdate[put]
        # TODO: ERROR:{"name":"d97e92a0-5750-4c59-86f5-e5667b8ff035","status":"Failed","startTime":"2020-02-19T17:53:07.27Z","error":{"code":"ConfigurationNotExists","message":"The
        # configuration ''configuration'' does not exist for MySQL server version 5.7."}}
        # BODY = {
        #   "properties": {
        #     "value": "off",
        #     "source": "user-override"
        #   }
        # }
        # VALUE = "off"
        # SOURCE = "user-override"
        # result = self.mgmt_client.configurations.create_or_update(resource_group.name, SERVER_NAME, CONFIGURATION_NAME, VALUE, SOURCE)
        # result = result.result()

        # Create or update a virtual network rule[put]
        # TODO: need subnet
        # BODY = {
        #   "ignore_missing_vnet_service_endpoint": False,
        #   "virtual_network_subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        # }
        # result = self.mgmt_client.virtual_network_rules.create_or_update(resource_group.name, SERVER_NAME, VIRTUAL_NETWORK_RULE_NAME, BODY)
        # result = result.result()

        # Update a server's threat detection policy with all parameters[put]
        BODY = {
            "properties": {
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
        }
        result = self.mgmt_client.server_security_alert_policies.begin_create_or_update(resource_group.name,
                                                                                        SERVER_NAME,
                                                                                        SECURITY_ALERT_POLICY_NAME,
                                                                                        BODY)
        result = result.result()

        # Update a server's threat detection policy with minimal parameters[put]
        BODY = {
            "properties": {
                "state": "Disabled",
                "email_account_admins": True
            }
        }
        result = self.mgmt_client.server_security_alert_policies.begin_create_or_update(resource_group.name,
                                                                                        SERVER_NAME,
                                                                                        SECURITY_ALERT_POLICY_NAME,
                                                                                        BODY)
        result = result.result()

        # Get a server's threat detection policy[get]
        result = self.mgmt_client.server_security_alert_policies.get(resource_group.name, SERVER_NAME,
                                                                     SECURITY_ALERT_POLICY_NAME)

        # # Gets a virtual network rule[get]
        # result = self.mgmt_client.virtual_network_rules.get(resource_group.name, SERVER_NAME, VIRTUAL_NETWORK_RULE_NAME)

        # # ConfigurationGet[get]
        # result = self.mgmt_client.configurations.get(resource_group.name, SERVER_NAME, CONFIGURATION_NAME)

        # FirewallRuleGet[get]
        result = self.mgmt_client.firewall_rules.get(resource_group.name, SERVER_NAME, FIREWALL_RULE_NAME)

        # DatabaseGet[get]
        result = self.mgmt_client.databases.get(resource_group.name, SERVER_NAME, DATABASE_NAME)

        # # List virtual network rules[get]
        # result = self.mgmt_client.virtual_network_rules.list_by_server(resource_group.name, SERVER_NAME)

        # ConfigurationList[get]
        result = self.mgmt_client.configurations.list_by_server(resource_group.name, SERVER_NAME)

        # FirewallRuleList[get]
        result = self.mgmt_client.firewall_rules.list_by_server(resource_group.name, SERVER_NAME)

        # DatabaseList[get]
        result = self.mgmt_client.databases.list_by_server(resource_group.name, SERVER_NAME)

        # LogFileList[get]
        result = self.mgmt_client.log_files.list_by_server(resource_group.name, SERVER_NAME)

        # ReplicasListByServer[get]
        result = self.mgmt_client.replicas.list_by_server(resource_group.name, SERVER_NAME)

        # ServerGet[get]
        result = self.mgmt_client.servers.get(resource_group.name, SERVER_NAME)

        # PerformanceTiersList[get]
        result = self.mgmt_client.location_based_performance_tier.list(LOCATION_NAME)

        # ServerListByResourceGroup[get]
        result = self.mgmt_client.servers.list_by_resource_group(resource_group.name)

        # ServerList[get]
        result = self.mgmt_client.servers.list()

        # OperationList[get]
        result = self.mgmt_client.operations.list()

        # ServerRestart[post]
        result = self.mgmt_client.servers.begin_restart(resource_group.name, SERVER_NAME)
        result = result.result()

        # ServerUpdate[patch]
        BODY = {
            "properties": {
                "administrator_login_password": "newpa$$w0rd",
                "ssl_enforcement": "Disabled"
            }
        }
        result = self.mgmt_client.servers.begin_update(resource_group.name, SERVER_NAME, BODY)
        result = result.result()

        # NameAvailability[post]
        # BODY = {
        #   "name": "name1",
        #   "type": "Microsoft.DBforMySQL"
        # }
        NAME = self.create_random_name("name1")
        from azure.mgmt.rdbms.mysql.models import NameAvailabilityRequest
        nameAvailabilityRequest = NameAvailabilityRequest(name=NAME, type="Microsoft.DBforMySQL")
        result = self.mgmt_client.check_name_availability.execute(nameAvailabilityRequest)

        # # Delete a virtual network rule[delete]
        # result = self.mgmt_client.virtual_network_rules.delete(resource_group.name, SERVER_NAME, VIRTUAL_NETWORK_RULE_NAME)
        # result = result.result()

        # FirewallRuleDelete[delete]
        result = self.mgmt_client.firewall_rules.begin_delete(resource_group.name, SERVER_NAME, FIREWALL_RULE_NAME)
        result = result.result()

        # DatabaseDelete[delete]
        result = self.mgmt_client.databases.begin_delete(resource_group.name, SERVER_NAME, DATABASE_NAME)
        result = result.result()

        # ServerDelete[delete]
        result = self.mgmt_client.servers.begin_delete(resource_group.name, SERVER_NAME)
        result = result.result()


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()