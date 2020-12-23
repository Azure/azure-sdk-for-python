# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.datamigration
import azure.mgmt.network.models

from azure.mgmt.datamigration.models import (DataMigrationService,
                                             ServiceSku,
                                             Project,
                                             SqlConnectionInfo,
                                             MigrateSqlServerSqlDbTaskProperties,
                                             MigrateSqlServerSqlDbTaskInput,
                                             MigrateSqlServerSqlDbDatabaseInput,
                                             MigrationValidationOptions)
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

@unittest.skip("skip test")
class MgmtDataMigrationTest(AzureMgmtTestCase):
    location_name = 'centralus'

    def setUp(self):
        super(MgmtDataMigrationTest, self).setUp()
        self.dms_sdk_client = self.create_mgmt_client(azure.mgmt.datamigration.DataMigrationManagementClient)
        self.network_sdk_client = self.create_mgmt_client(azure.mgmt.network.NetworkManagementClient)

    @ResourceGroupPreparer(name_prefix='dms_sdk_test', location=location_name)
    def test_datamigration(self, resource_group):
        vnet_name = self.get_resource_name('pysdkdmstestvnet')
        vsubnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/subnet1'
        service_name = self.get_resource_name('pysdkdmstestservice')
        sku_name = 'GeneralPurpose_2vCores'
        project_name = self.get_resource_name('pysdkdmstestproject')
        task_name = self.get_resource_name('pysdkdmstesttask')

        # ensure the service name is available
        name_availability = self.dms_sdk_client.services.check_name_availability(
            location = self.location_name,
            name = service_name,
            type = 'services')
        self.assertTrue(name_availability.name_available)

        # DMS requires a real vnet plus subnet
        if self.is_live:
            vnet_creation_async = self.network_sdk_client.virtual_networks.create_or_update(
                resource_group.name,
                vnet_name,
                {
                    'location': self.location_name,
                    'address_space': {
                        'address_prefixes': ['10.0.0.0/16']
                    }
                }
            )
            vnet_creation_async.wait()
            self.network_sdk_client.subnets.create_or_update(
                resource_group.name,
                vnet_name,
                'subnet1',
                {'address_prefix': '10.0.0.0/24'}
            ).wait()

        # create the service
        params_create_service = DataMigrationService(
            location = self.location_name,
            virtual_subnet_id = vsubnet_id.format(self.settings.SUBSCRIPTION_ID, resource_group.name, vnet_name),
            sku=ServiceSku(name=sku_name))
        service_creation_async = self.dms_sdk_client.services.create_or_update(
            parameters = params_create_service,
            group_name = resource_group.name,
            service_name = service_name)
        service_creation_async.wait()

        # check the service
        dms_service = self.dms_sdk_client.services.get(group_name = resource_group.name, service_name = service_name)
        self.assertEqual(dms_service.provisioning_state, 'Succeeded')
        self.assertEqual(dms_service.name, service_name)
        self.assertEqual(dms_service.location, self.location_name)
        self.assertEqual(dms_service.sku.name, sku_name)

        # the service name should not be available
        name_availability = self.dms_sdk_client.services.check_name_availability(
            location = self.location_name,
            name = service_name,
            type = 'services')
        self.assertFalse(name_availability.name_available)

        # create a project
        params_create_project = Project(
            location = self.location_name,
            source_platform = 'SQL',
            target_platform = 'SQLDB')
        project_creation = self.dms_sdk_client.projects.create_or_update(
            parameters = params_create_project,
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name)

        # check the project
        dms_project = self.dms_sdk_client.projects.get(
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name)
        self.assertEqual(dms_project.provisioning_state, 'Succeeded')
        self.assertEqual(dms_project.name, project_name)
        self.assertEqual(dms_project.source_platform, 'SQL')
        self.assertEqual(dms_project.target_platform, 'SQLDB')

        # create a task
        database_options = []
        database_options.append(
            MigrateSqlServerSqlDbDatabaseInput(
                name = 'Test_Source',
                target_database_name = 'Test_Target',
                make_source_db_read_only = False,
                table_map = { "dbo.TestTableForeign": "dbo.TestTableForeign", "dbo.TestTablePrimary": "dbo.TestTablePrimary" }))

        validation_options = MigrationValidationOptions(
            enable_schema_validation = False,
            enable_data_integrity_validation = False,
            enable_query_analysis_validation = False)

        task_input = MigrateSqlServerSqlDbTaskInput(
            source_connection_info = {
                'userName': 'testuser',
                'password': 'password',
                'dataSource': 'testsource.microsoft.com',
                'authentication': 'SqlAuthentication',
                'encryptConnection': True,
                'trustServerCertificate': True
                },
            target_connection_info = {
                'userName': 'testuser',
                'password': 'password',
                'dataSource': 'testtarget.microsoft.com',
                'authentication': 'SqlAuthentication',
                'encryptConnection': True,
                'trustServerCertificate': True
                },
            selected_databases = database_options,
            validation_options = validation_options)

        migration_properties = MigrateSqlServerSqlDbTaskProperties(input = task_input)

        task_creation = self.dms_sdk_client.tasks.create_or_update(
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name,
            task_name = task_name,
            properties = migration_properties)

        # check the task
        dms_task = self.dms_sdk_client.tasks.get(
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name,
            task_name = task_name)
        self.assertEqual(dms_task.name, task_name)
        self.assertEqual(dms_task.properties.input.selected_databases[0].name, 'Test_Source')
        self.assertEqual(dms_task.properties.input.source_connection_info.data_source, 'testsource.microsoft.com')
        self.assertEqual(dms_task.properties.input.target_connection_info.data_source, 'testtarget.microsoft.com')
        self.assertFalse(dms_task.properties.input.validation_options.enable_schema_validation)
        self.assertEqual(dms_task.properties.task_type, 'Migrate.SqlServer.SqlDb')

        # delete the task
        self.dms_sdk_client.tasks.delete(
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name,
            task_name = task_name,
            delete_running_tasks = True)

        # delete the project
        self.dms_sdk_client.projects.delete(
            group_name = resource_group.name,
            service_name = service_name,
            project_name = project_name)

        # delete the service
        service_deletion_async = self.dms_sdk_client.services.delete(
            group_name = resource_group.name,
            service_name = service_name)
        service_deletion_async.wait()

        # ensure the service name is available again
        name_availability = self.dms_sdk_client.services.check_name_availability(
            location = self.location_name,
            name = service_name,
            type = 'services')
        self.assertTrue(name_availability.name_available)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
