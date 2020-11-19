# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 49
# Methods Covered : 49
# Examples Total  : 53
# Examples Tested : 53
# Coverage %      : 100
# ----------------------

import datetime as dt
import unittest

import azure.mgmt.rdbms.mariadb
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


class MgmtMariaDBTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMariaDBTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.rdbms.mariadb.MariaDBManagementClient
        )

    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_mariadb(self, resource_group):
        SERVER_NAME = "testserver21827"
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_GEO_NAME = "servergeo21827"
        SERVER_REPLICA_NAME = "serverreplica21827"
        SERVER_POINT_NAME = "serverpoint21827"
        DATABASE_NAME = "testdatabase21827"
        FIREWALL_RULE_NAME = "firewallrule"
        CONFIGURATION_NAME = "configuration"
        VIRTUAL_NETWORK_RULE_NAME = "virutal_networkrule"
        SECURITY_ALERT_POLICY_NAME = "securityalertpolicy"
        LOCATION_NAME = "eastus"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "privateendpoint"

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

        # Create a replica server[put]
        BODY = {
            "location": "eastus",
            "properties": {
                "create_mode": "Replica",
                "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMariaDB/servers/" + SERVER_NAME + ""
            }
        }
        result = self.mgmt_client.servers.begin_create(resource_group.name, SERVER_REPLICA_NAME, BODY)
        result = result.result()

        # Create a database as a point in time restore[put]
        # point_in_time = dt.datetime.now(tz=UTC()).isoformat()
        # BODY = {
        #  "location": "eastus",
        #  "properties": {
        #    "restore_point_in_time": point_in_time,
        #    "create_mode": "PointInTimeRestore",
        #    "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMariaDB/servers/" + SERVER_NAME + ""
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

        # # Create a server as a geo restore [put]
        # BODY = {
        #   "location": "eastus",
        #   "properties": {
        #     "create_mode": "GeoRestore",
        #     "source_server_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.DBforMariaDB/servers/" + SERVER_NAME + ""
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
        from azure.mgmt.rdbms.mariadb.models import FirewallRule
        firewall_rule = FirewallRule(start_ip_address='0.0.0.0', end_ip_address='255.255.255.255')
        result = self.mgmt_client.firewall_rules.begin_create_or_update(resource_group.name, SERVER_NAME, FIREWALL_RULE_NAME, firewall_rule)
        result = result.result()

        # ConfigurationCreateOrUpdate[put]
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

        # # Create or update a virtual network rule[put]
        # BODY = {
        #   "properties": {
        #     "ignore_missing_vnet_service_endpoint": False,
        #     "virtual_network_subnet_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Network/virtualNetworks/" + VIRTUAL_NETWORK_NAME + "/subnets/" + SUBNET_NAME + ""
        #   }
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

        # # Approve or reject a private endpoint connection with a given name.[put]
        # TODO: private_endpoint_connections not exist
        # BODY = {
        #   "properties": {
        #     "private_link_service_connection_state": {
        #       "status": "Approved",
        #       "description": "Approved by johndoe@contoso.com"
        #     }
        #   }
        # }
        # result = self.mgmt_client.private_endpoint_connections.create_or_update(resource_group.name, SERVER_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)
        # result = result.result()

        # # RecommendedActionsGet[get]
        # TODO: recommended_actions not exist.
        # result = self.mgmt_client.recommended_actions.get(resource_group.name, SERVER_NAME, ADVISOR_NAME, RECOMMENDED_ACTION_NAME)

        # # RecommendedActionSessionOperationStatus[get]
        # result = self.mgmt_client.location_based_recommended_action_sessions_operation_status.get(LOCATION_NAME, RECOMMENDED_ACTION_SESSIONS_AZURE_ASYNC_OPERATION_NAME)

        # # Gets private endpoint connection.[get]
        # TODO: private_endpoint_connections not exist
        # result = self.mgmt_client.private_endpoint_connections.get(resource_group.name, SERVER_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)

        # # RecommendedActionSessionResult[get]
        # result = self.mgmt_client.location_based_recommended_action_sessions_result.list(LOCATION_NAME, RECOMMENDED_ACTION_SESSIONS_OPERATION_RESULT_NAME)

        # Get a server's threat detection policy[get]
        result = self.mgmt_client.server_security_alert_policies.get(resource_group.name, SERVER_NAME, SECURITY_ALERT_POLICY_NAME)

        # # Gets a private link resource for MariaDB.[get]
        # TODO: private_link_resources is not exist.
        # result = self.mgmt_client.private_link_resources.get(resource_group.name, SERVER_NAME, PRIVATE_LINK_RESOURCE_NAME)

        # # Gets a virtual network rule[get]
        # result = self.mgmt_client.virtual_network_rules.get(resource_group.name, SERVER_NAME, VIRTUAL_NETWORK_RULE_NAME)

        # # TopQueryStatisticsGet[get]
        # TODO: top_query_statistics is not exist.
        # result = self.mgmt_client.top_query_statistics.get(resource_group.name, SERVER_NAME, TOP_QUERY_STATISTIC_NAME)

        # # RecommendedActionsListByServer[get]
        # TODO: recommended_actions is not exist.
        # result = self.mgmt_client.recommended_actions.list_by_server(resource_group.name, SERVER_NAME, ADVISOR_NAME)

        # # WaitStatisticsGet[get]
        # TODO: wait_statistics is not exist.
        # result = self.mgmt_client.wait_statistics.get(resource_group.name, SERVER_NAME, WAIT_STATISTIC_NAME)

        # # ConfigurationGet[get]
        # result = self.mgmt_client.configurations.get(resource_group.name, SERVER_NAME, CONFIGURATION_NAME)

        # FirewallRuleGet[get]
        result = self.mgmt_client.firewall_rules.get(resource_group.name, SERVER_NAME, FIREWALL_RULE_NAME)

        # # QueryTextsGet[get]
        # TODO: query_texts is not exist.
        # result = self.mgmt_client.query_texts.get(resource_group.name, SERVER_NAME, QUERY_TEXT_NAME)

        # DatabaseGet[get]
        result = self.mgmt_client.databases.get(resource_group.name, SERVER_NAME, DATABASE_NAME)

        # # AdvisorsGet[get]
        # TODO: advisors is not exist.
        # result = self.mgmt_client.advisors.get(resource_group.name, SERVER_NAME, ADVISOR_NAME)

        # # Gets list of private endpoint connections on a server.[get]
        # TODO: private_endpoint_connections is not exist.
        # result = self.mgmt_client.private_endpoint_connections.list_by_server(resource_group.name, SERVER_NAME)

        # # Gets private link resources for MariaDB.[get]
        # TODO: private_link_resources is not exist.
        # result = self.mgmt_client.private_link_resources.list_by_server(resource_group.name, SERVER_NAME)

        # List virtual network rules[get]
        result = self.mgmt_client.virtual_network_rules.list_by_server(resource_group.name, SERVER_NAME)

        # # TopQueryStatisticsListByServer[get]
        # TODO: top_query_statistics is not exist.
        # result = self.mgmt_client.top_query_statistics.list_by_server(resource_group.name, SERVER_NAME)

        # # WaitStatisticsListByServer[get]
        # TODO: wait_statistics is not exist.
        # result = self.mgmt_client.wait_statistics.list_by_server(resource_group.name, SERVER_NAME)

        # ConfigurationList[get]
        result = self.mgmt_client.configurations.list_by_server(resource_group.name, SERVER_NAME)

        # FirewallRuleList[get]
        result = self.mgmt_client.firewall_rules.list_by_server(resource_group.name, SERVER_NAME)

        # # QueryTextsListByServer[get]
        # TODO: query_texts is not exist.
        # result = self.mgmt_client.query_texts.list_by_server(resource_group.name, SERVER_NAME)

        # DatabaseList[get]
        result = self.mgmt_client.databases.list_by_server(resource_group.name, SERVER_NAME)

        # LogFileList[get]
        result = self.mgmt_client.log_files.list_by_server(resource_group.name, SERVER_NAME)

        # # AdvisorsListByServer[get]
        # TODO: advisors is not exist.
        # result = self.mgmt_client.advisors.list_by_server(resource_group.name, SERVER_NAME)

        # # ReplicasListByServer[get]
        # TODO: replicas is not exist.
        # result = self.mgmt_client.replicas.list_by_server(resource_group.name, SERVER_NAME)

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

        # # Update private endpoint connection Tags[patch]
        # TODO: private_endpoint_connections is not exist.
        # BODY = {
        #   "tags": {
        #     "key1": "val1",
        #     "key2": "val2"
        #   }
        # }
        # result = self.mgmt_client.private_endpoint_connections.update_tags(resource_group.name, SERVER_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME, BODY)
        # result = result.result()

        # # RecommendedActionSessionCreate[post]
        # TODO: recommended action is not exist.
        # result = self.mgmt_client..create_recommended_action_session(resource_group.name, SERVER_NAME, ADVISOR_NAME)
        # result = result.result()

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
        #   "type": "Microsoft.DBforMariaDB"
        # }
        NAME = self.create_random_name("name1")
        from azure.mgmt.rdbms.mariadb.models import NameAvailabilityRequest
        nameAvailabilityRequest = NameAvailabilityRequest(name=NAME, type="Microsoft.DBforMariaDB")
        result = self.mgmt_client.check_name_availability.execute(nameAvailabilityRequest)

        # # Deletes a private endpoint connection with a given name.[delete]
        # TODO: private_endpoint_connections is not exist.
        # result = self.mgmt_client.private_endpoint_connections.delete(resource_group.name, SERVER_NAME, PRIVATE_ENDPOINT_CONNECTION_NAME)
        # result = result.result()

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