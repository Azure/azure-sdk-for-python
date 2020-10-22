from datetime import datetime, timedelta, tzinfo
import time
from dateutil.tz import tzutc

import azure.mgmt.rdbms.postgresql_flexibleservers
from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
    AzureMgmtPreparer, FakeResource
  )
from azure_devtools.scenario_tests.utilities import create_random_name
from .flexible_server_test_common import (
  flexible_server_firewall_rule_mgmt_test,
  flexible_server_configuration_mgmt_test,
)


AZURE_LOCATION = 'eastus'
ZERO = timedelta(0)

class PostgresFlexibleServerPreparer(AzureMgmtPreparer):
    def __init__(self, name_prefix='pythonsdk-postgres-server'):
        super(PostgresFlexibleServerPreparer, self).__init__(name_prefix, 30)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            async_server_create = self.test_class_instance.mgmt_client.servers.create(
                kwargs['resource_group'].name,
                'pg-testserver2134',
                {
                  'location': AZURE_LOCATION,
                  "sku": {
                    "name": "Standard_D2s_v3",
                    "tier": "GeneralPurpose"
                    }, 
                  "properties": {
                    "administratorLogin": "testuser",
                    "administratorLoginPassword": "testpassword123!@#",
                    "version": "12",
                    "storageProfile": {
                      "backupRetentionDays": 7, 
                      "storageMB": 1024*128
                      }, 
                    "createMode": "Default"
                    }
                }
            )
            server = async_server_create.result()
        else:
            server = FakeResource(name='pg-testserver2134', id='')

        return {
            'server': server
        }

class MgmtPostgresFlexibleServerTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtPostgresFlexibleServerTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.rdbms.postgresql_flexibleservers.PostgreSQLManagementClient
        )
        self.location = AZURE_LOCATION
    
    @ResourceGroupPreparer(location=AZURE_LOCATION, name_prefix='postgres-rg')
    def test_postgres_flexible_server_mgmt(self, resource_group):

      server_name = 'pg-testserver2134'
      subscription_id = self.settings.SUBSCRIPTION_ID
      resource_group_name = resource_group.name
      username = "testuser"
      password = "test123!@#"
      server_restore_name = server_name + "restore2134"

      # Create a new server[put]
      parameters = {
        "location": self.location, 
        "sku": {
          "name": "Standard_D2s_v3",
          "tier": "GeneralPurpose"
          }, 
        "properties": {
          "administratorLogin": username,
          "administratorLoginPassword": password,
          "version": "12",
          "storageProfile": {
            "backupRetentionDays": 7, 
            "storageMB": 65536
            }, 
          "createMode": "Default"
          }
      }

      result = self.mgmt_client.servers.create(resource_group_name, server_name, parameters)
      result = result.result()
      current_time = datetime.utcnow()
      
      result = self.mgmt_client.servers.get(resource_group_name, server_name)

      parameters = {
        "properties": {
          "storageProfile": {
            "backupRetentionDays": 10,
            "storageMB": 1024*256
          },
          "administrator_login_password": "newpa$$w0rd",
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

      result = self.mgmt_client.servers.list()

      result = self.mgmt_client.operations.list()

      result = self.mgmt_client.location_based_capabilities.execute(self.location)

      result = self.mgmt_client.check_name_availability.execute(create_random_name(prefix="servernamethatdoesnotexist", length=40), type="Microsoft.DBforPostgreSQL/flexibleServers")
      self.assertEqual(result.name_available, True)

      result = self.mgmt_client.check_name_availability.execute(server_name, type="Microsoft.DBforPostgreSQL/flexibleServers")
      self.assertEqual(result.name_available, False)

      # result = self.mgmt_client.virtual_network_subnet_usage.execute(self.location)

      time.sleep(600)
      point_in_time = (current_time + timedelta(minutes=10)).replace(tzinfo=tzutc()).isoformat()
      parameters = azure.mgmt.rdbms.postgresql_flexibleservers.models.Server(
        point_in_time_utc=point_in_time,
        source_server_name=server_name,  # this should be the source server name, not id
        create_mode="PointInTimeRestore",
        location=self.location)
      result = self.mgmt_client.servers.create(resource_group_name, server_restore_name, parameters)
      result = result.result()

      result = self.mgmt_client.servers.delete(resource_group_name, server_name)
      result = result.result()

      result = self.mgmt_client.servers.delete(resource_group_name, server_restore_name)
      result = result.result()


    @ResourceGroupPreparer(location=AZURE_LOCATION, name_prefix='postgres-rg')
    @PostgresFlexibleServerPreparer()
    def test_postgres_flexible_server_proxy_resource_mgmt(self, resource_group, server):
      server_name = server.name
      resource_group_name = resource_group.name

      flexible_server_firewall_rule_mgmt_test(self, resource_group_name, server_name)
      flexible_server_configuration_mgmt_test(self, resource_group_name, server_name, "lock_timeout", 0, 2000)

#------------------------------------------------------------------------------
if __name__ == '__main__':
  unittest.main()
