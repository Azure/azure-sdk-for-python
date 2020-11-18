import datetime as dt

import azure.mgmt.rdbms.mysql_flexibleservers
from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
    AzureMgmtPreparer, FakeResource
  )
from azure_devtools.scenario_tests.utilities import create_random_name
from .flexible_server_test_common import (
  flexible_server_database_mgmt_test,
  flexible_server_firewall_rule_mgmt_test,
  flexible_server_configuration_mgmt_test
  # flexible_server_key_mgmt_test
)

AZURE_LOCATION = 'westus2'
ZERO = dt.timedelta(0)

class UTC(dt.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class MySqlFlexibleServerPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='pythonsdk-mysql-server'):
        super(MySqlFlexibleServerPreparer, self).__init__(name_prefix, 30)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            async_server_create = self.test_class_instance.mgmt_client.servers.create(
                kwargs['resource_group'].name,
                'mysql-testserver2134',
                {
                  'location': AZURE_LOCATION,
                  "sku": {
                    "name": "Standard_B1ms",
                    "tier": "Burstable"
                    }, 
                  "properties": {
                    "administratorLogin": 'testuser',
                    "administratorLoginPassword": 'testuser123!@#',
                    "version": "5.7",
                    "storageProfile": {
                      "backupRetentionDays": 7, 
                      "storageMB": 102400
                      }, 
                    "createMode": "Default"
                    }
                }
            )
            server = async_server_create.result()
        else:
            server = FakeResource(name='mysql-testserver2134', id='')

        return {
            'server': server
        }

class MgmtMySqlFlexibleServerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMySqlFlexibleServerTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.rdbms.mysql_flexibleservers.MySQLManagementClient
        )
        self.keyvault_mgmt_client = self.create_mgmt_client(
          azure.mgmt.keyvault.KeyVaultManagementClient
        )
        self.location = AZURE_LOCATION
    
    @ResourceGroupPreparer(location=AZURE_LOCATION, name_prefix='pythonsdk-mysql-rg')
    def test_mysql_flexible_server_mgmt(self, resource_group):
      server_name = 'mysql-testserver2134'
      subscription_id = self.settings.SUBSCRIPTION_ID
      resource_group_name = resource_group.name
      username = "testuser"
      password = "test123!@#"
      server_restore_name = server_name + "-restore2134"
      server_replica_name = server_name + "-replica2134"
      sku_name = "Standard_B1ms"
      tier = "Burstable"

      # Create a new server[put]
      parameters = {
        "location": self.location, 
        "sku": {
          "name": "Standard_B1ms",
          "tier": "Burstable"
          }, 
        "properties": {
          "administratorLogin": username,
          "administratorLoginPassword": password,
          "version": "5.7",
          "storageProfile": {
            "backupRetentionDays": 7, 
            "storageMB": 102400
            }, 
          "createMode": "Default"
          }
      }

      result = self.mgmt_client.servers.create(resource_group_name, server_name, parameters)
      result = result.result()
      
      result = self.mgmt_client.servers.get(resource_group_name, server_name)

      parameters = {
        "properties": {
          "storageProfile": {
            "backupRetentionDays": 10,
            "storageMB": 1024*256,
          },
          "administrator_login_password": "newpa$$w0rd",
          "ssl_enforcement": "Enabled"
        }
      }

      result = self.mgmt_client.servers.update(resource_group_name, server_name, parameters)
      result = result.result()

      result = self.mgmt_client.servers.restart(resource_group_name, server_name)
      result = result.result()

      result = self.mgmt_client.servers.stop(resource_group_name, server_name)
      result = result.result()

      result = self.mgmt_client.servers.start(resource_group_name, server_name)
      result = result.result()

      result = self.mgmt_client.servers.list_by_resource_group(resource_group_name)
      self.assertEqual(len(list(result)), 1)

      result = self.mgmt_client.servers.list()

      result = self.mgmt_client.location_based_capabilities.list(self.location)

      result = self.mgmt_client.operations.list()

      result = self.mgmt_client.check_name_availability.execute(create_random_name(prefix="servernamethatdoesnotexist", length=40), type="Microsoft.DBforMySQL/flexibleServers")
      self.assertEqual(result.name_available, True)

      result = self.mgmt_client.check_name_availability.execute(server_name, type="Microsoft.DBforMySQL/flexibleServers")
      self.assertEqual(result.name_available, False)

      parameters = azure.mgmt.rdbms.mysql_flexibleservers.models.Server(
        sku=azure.mgmt.rdbms.mysql_flexibleservers.models.Sku(name=sku_name, tier=tier),
        source_server_id="/subscriptions/" + subscription_id + "/resourceGroups/" + resource_group_name + "/providers/Microsoft.DBforMySQL/flexibleServers/" + server_name + "",
        location=self.location,
        create_mode="Replica")
      result = self.mgmt_client.servers.create(resource_group_name, server_replica_name, parameters)
      result = result.result()

      point_in_time = (dt.datetime.now(tz=UTC()) - dt.timedelta(minutes=5)).isoformat()
      parameters = azure.mgmt.rdbms.mysql_flexibleservers.models.Server(
        source_server_id="/subscriptions/" + subscription_id + "/resourceGroups/" + resource_group_name + "/providers/Microsoft.DBforMySQL/flexibleServers/" + server_name + "",
        restore_point_in_time=point_in_time,
        location=self.location,
        create_mode="PointInTimeRestore"
      )
      result = self.mgmt_client.servers.create(resource_group_name, server_restore_name, parameters)
      result = result.result()

      result = self.mgmt_client.servers.delete(resource_group_name, server_name)
      result = result.result()


    @ResourceGroupPreparer(location=AZURE_LOCATION, name_prefix='pythonsdk-mysql-rg')
    @MySqlFlexibleServerPreparer()
    def test_mysql_flexible_server_proxy_resource_mgmt(self, resource_group, server):
      server_name = server.name
      resource_group_name = resource_group.name

      flexible_server_database_mgmt_test(self, resource_group_name, server_name)
      flexible_server_firewall_rule_mgmt_test(self, resource_group_name, server_name)
      flexible_server_configuration_mgmt_test(self, resource_group_name, server_name, "wait_timeout", 28800, 30000)


#------------------------------------------------------------------------------
if __name__ == '__main__':
  unittest.main()
