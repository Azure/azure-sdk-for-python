# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import binascii
import hashlib
import io
import json
import logging
import time
import unittest

import pytest
import requests
import six
import os

import azure.mgmt.batch
from azure.mgmt.batch import models
import azure.mgmt.network.models
from mgmt_batch_preparers import KeyVaultPreparer, SimpleBatchPreparer

from azure_devtools.scenario_tests.recording_processors import GeneralNameReplacer, RecordingProcessor
from devtools_testutils import (
    AzureMgmtRecordedTestCase, recorded_by_proxy,
    ResourceGroupPreparer,
    StorageAccountPreparer
)

# When running live, these variables may need to be updated depending on the
# test environment
AZURE_ARM_ENDPOINT = "https://centraluseuap.management.azure.com"
AZURE_LOCATION = 'eastus'
EXISTING_BATCH_ACCOUNT = {'name': 'dawatroupp2acct', 'location': 'eastus'}
EXPECTED_ACCOUNT_QUOTA = 3
EXPECTED_DEDICATED_CORE_QUOTA = 500
EXPECTED_LOW_PRIO_CORE_QUOTA = 500
EXPECTED_POOL_QUOTA = 100
SECRET_FIELDS = ["primary", "secondary"]


def get_redacted_key(key):
    redacted_value = "redacted"
    digest = hashlib.sha256(six.ensure_binary(key)).digest()
    redacted_value += six.ensure_str(binascii.hexlify(digest))[:6]
    return redacted_value


class RecordingRedactor(RecordingProcessor):
    """Removes keys from test recordings"""

    def process_response(self, response):
        try:
            body = json.loads(response["body"]["string"])
        except (KeyError, ValueError):
            return response

        for field in body:
            if field in SECRET_FIELDS:
                body[field] = get_redacted_key(body[field])

        response["body"]["string"] = json.dumps(body)
        return response


class TestMgmtBatch(AzureMgmtRecordedTestCase):
    scrubber = GeneralNameReplacer()
    redactor = RecordingRedactor()

    def setup_method(self, method):
        self.mgmt_batch_client = self.create_mgmt_client(
            azure.mgmt.batch.BatchManagementClient,
            base_url=AZURE_ARM_ENDPOINT)
        if self.is_live:
            self.mgmt_network = self.create_mgmt_client(
                azure.mgmt.network.NetworkManagementClient,
                base_url=AZURE_ARM_ENDPOINT)

    def _get_account_name(self):
        return self.get_resource_name('batch')[-24:]

    @recorded_by_proxy
    def test_mgmt_batch_list_operations(self):
        operations = self.mgmt_batch_client.operations.list()
        all_ops = list(operations)
        assert len(all_ops) == 54
        assert all_ops[0].name == 'Microsoft.Batch/batchAccounts/providers/Microsoft.Insights/diagnosticSettings/read'
        assert all_ops[0].origin == 'system'
        assert all_ops[0].display.provider == 'Microsoft Batch'
        assert all_ops[0].display.operation == 'Read diagnostic setting'

    @recorded_by_proxy
    def test_mgmt_batch_subscription_quota(self):
        quotas = self.mgmt_batch_client.location.get_quotas(AZURE_LOCATION)
        assert isinstance(quotas, models.BatchLocationQuota)
        assert quotas.account_quota == EXPECTED_ACCOUNT_QUOTA

    @recorded_by_proxy
    def test_mgmt_batch_account_name(self):
        # Test Invalid Account Name
        availability = self.mgmt_batch_client.location.check_name_availability(
            AZURE_LOCATION,
            {
                "name": "randombatchaccount@5^$g9873495873"
            }
        )
        assert isinstance(availability, models.CheckNameAvailabilityResult)
        assert availability.name_available == False
        assert availability.reason == models.NameAvailabilityReason.invalid

        # Test Unvailable Account Name
        availability = self.mgmt_batch_client.location.check_name_availability(
            EXISTING_BATCH_ACCOUNT['location'],
            {
                "name": EXISTING_BATCH_ACCOUNT['name']
            }
        )
        assert isinstance(availability, models.CheckNameAvailabilityResult)
        assert not availability.name_available
        assert availability.reason == models.NameAvailabilityReason.already_exists

        # Test Available Account Name
        availability = self.mgmt_batch_client.location.check_name_availability(
            AZURE_LOCATION,
            {
                "name": self._get_account_name()
            }
        )
        assert isinstance(availability, models.CheckNameAvailabilityResult)
        assert availability.name_available

    # @KeyVaultPreparer(location=AZURE_LOCATION)
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_byos_account(self, resource_group, location):
        # if self.is_live:
        #     keyvault = keyvault.result()
        batch_account = models.BatchAccountCreateParameters(
                location=location,
                pool_allocation_mode=models.PoolAllocationMode.user_subscription)
        with pytest.raises(Exception):  # TODO: What exception
            creating = self.mgmt_batch_client.batch_account.begin_create(
                resource_group.name,
                self._get_account_name(),
                batch_account)
            creating.result()

        # keyvault_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.KeyVault/vaults/{}".format(
        #     self.get_settings_value("SUBSCRIPTION_ID"), resource_group.name, keyvault.name)
        # keyvault_url = "https://{}.vault.azure.net/".format(keyvault.name)
        # batch_account = models.BatchAccountCreateParameters(
        #         location=location,
        #         pool_allocation_mode=models.PoolAllocationMode.user_subscription,
        #         key_vault_reference={'id': keyvault_id, 'url': keyvault_url})
        # creating = self.mgmt_batch_client.batch_account.begin_create(
        #         resource_group.name,
        #         self._get_account_name(),
        #         batch_account)
        # creating.result()

    @pytest.mark.skip('hard to test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_account(self, resource_group, location):
        batch_account = models.BatchAccountCreateParameters(
            location=location,
        )
        account_name = self._get_account_name()
        account_setup = self.mgmt_batch_client.batch_account.begin_create(
            resource_group.name,
            account_name,
            batch_account)
        account_setup.result()

        # Test Get Account
        account = self.mgmt_batch_client.batch_account.get(resource_group.name, account_name)
        assert account.dedicated_core_quota == EXPECTED_DEDICATED_CORE_QUOTA
        assert account.low_priority_core_quota == EXPECTED_LOW_PRIO_CORE_QUOTA
        assert account.pool_quota == EXPECTED_POOL_QUOTA
        assert account.pool_allocation_mode == 'BatchService'

        # Test List Accounts by Resource Group
        accounts = self.mgmt_batch_client.batch_account.list_by_resource_group(resource_group.name)
        assert len(list(accounts)) == 1

        # Test List Account Keys
        keys = self.mgmt_batch_client.batch_account.get_keys(resource_group.name, account_name)
        assert isinstance(keys, models.BatchAccountKeys)
        assert keys.account_name == account_name
        secondary = keys.secondary

        # Test Regenerate Account Key
        keys = self.mgmt_batch_client.batch_account.regenerate_key(
            resource_group.name,
            account_name,
            {
                "key_name": 'Secondary'
            }
        )
        assert isinstance(keys, models.BatchAccountKeys)
        assert not keys.secondary == secondary

        # Test Update Account
        update_tags = {'Name': 'tagName', 'Value': 'tagValue'}
        updated = self.mgmt_batch_client.batch_account.update(resource_group.name, account_name, models.BatchAccountUpdateParameters(tags=update_tags))
        assert isinstance(updated, models.BatchAccount)
        assert updated.tags['Name'] == 'tagName'
        assert updated.tags['Value'] == 'tagValue'

        # Test Delete Account
        response = self.mgmt_batch_client.batch_account.begin_delete(resource_group.name, account_name)
        assert response.result() is None

    @pytest.mark.skipif(os.getenv('AZURE_TEST_RUN_LIVE') not in ('yes', 'true'), reason='only run live test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @StorageAccountPreparer(name_prefix='batch', location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_applications(self, resource_group, location, storage_account, storage_account_key):
        # Test Create Account with Auto-Storage 
        storage_resource = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
            self.get_settings_value("SUBSCRIPTION_ID"),
            resource_group.name,
            storage_account.name
        )
        batch_account = models.BatchAccountCreateParameters(
            location=location,
            auto_storage=models.AutoStorageBaseProperties(storage_account_id=storage_resource)
        )
        # account_name = self._get_account_name()
        account_name = "batch11"
        account_setup = self.mgmt_batch_client.batch_account.begin_create(
            resource_group.name,
            account_name,
            batch_account)
        account_setup.result()

        # Test Sync AutoStorage Keys
        response = self.mgmt_batch_client.batch_account.synchronize_auto_storage_keys(
                                   resource_group.name, account_name)
        assert response is None

        # Test Add Application
        application_id = 'my_application_id'
        application_name = 'my_application_name'
        application_ver = 'v1.0'
        application_properties = models.Application(display_name=application_name, allow_updates=True)
        application = self.mgmt_batch_client.application.create(
            resource_group.name, account_name, application_id, parameters=application_properties)
        assert isinstance(application, models.Application)
        assert application_id in application.id
        assert application_name in application.display_name
        assert application.allow_updates

        # Test Mgmt Get Application
        application = self.mgmt_batch_client.application.get(resource_group.name, account_name, application_id)
        assert isinstance(application, models.Application)
        assert application_id in application.id
        assert application_name in application.display_name
        assert application.allow_updates

        # Test Mgmt List Applications
        applications = self.mgmt_batch_client.application.list(resource_group.name, account_name)
        assert len(list(applications)) > 0

        # Test Add Application Package
        package_ref = self.mgmt_batch_client.application_package.create(
            resource_group.name, account_name, application_id, application_ver)
        assert isinstance(package_ref, models.ApplicationPackage)
        with io.BytesIO(b'Hello World') as f:
            headers = {'x-ms-blob-type': 'BlockBlob'}
            upload = requests.put(package_ref.storage_url, headers=headers, data=f.read())
            if not upload:
                raise ValueError('Upload failed: {!r}'.format(upload))

        # Test Activate Application Package
        response = self.mgmt_batch_client.application_package.activate(
            resource_group.name,
            account_name,
            application_id,
            application_ver,
            {
                "format": 'zip'
            }
        )
        assert response.state == models.PackageState.active

        # Test Update Application
        params = models.Application(
            allow_updates=False,
            display_name='my_updated_name',
            default_version=application_ver
        )
        response = self.mgmt_batch_client.application.update(
            resource_group.name, account_name, application_id, params)
        assert application_ver in response.default_version
        assert 'my_updated_name' in response.display_name
        assert not response.allow_updates

        # Test Get Application Package
        package_ref = self.mgmt_batch_client.application_package.get(
            resource_group.name, account_name, application_id, application_ver)
        assert isinstance(package_ref, models.ApplicationPackage)
        assert application_id in package_ref.id
        assert package_ref.format == 'zip'
        assert package_ref.state == models.PackageState.active

        # Test Delete Application Package
        response = self.mgmt_batch_client.application_package.delete(
            resource_group.name, account_name, application_id, application_ver)
        assert response is None

        # Test Delete Application
        response = self.mgmt_batch_client.application.delete(
            resource_group.name, account_name, application_id)
        assert response is None

        # Test Delete Account
        response = self.mgmt_batch_client.batch_account.begin_delete(resource_group.name, account_name)
        assert response.result() is None

    @pytest.mark.skipif(os.getenv('AZURE_TEST_RUN_LIVE') not in ('yes', 'true'), reason='only run live test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @SimpleBatchPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_certificates(self, resource_group, location, batch_account):
        # Test Add Certificate
        parameters = models.CertificateCreateOrUpdateParameters(
            thumbprint='cff2ab63c8c955aaf71989efa641b906558d9fb7',
            thumbprint_algorithm='sha1',
            data='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',
            format=models.CertificateFormat.pfx,
            password='nodesdk')

        certificate = 'SHA1-cff2ab63c8c955aaf71989efa641b906558d9fb7'
        response = self.mgmt_batch_client.certificate.create(resource_group.name, batch_account.name, certificate, parameters)
        assert isinstance(response, models.Certificate)

        # Test List Certificates
        certs = self.mgmt_batch_client.certificate.list_by_batch_account(resource_group.name, batch_account.name)
        assert len(list(certs)) == 1

        # Test Get Certificate
        cert = self.mgmt_batch_client.certificate.get(resource_group.name, batch_account.name, certificate)
        assert isinstance(cert, models.Certificate)
        assert cert.thumbprint.lower() == 'cff2ab63c8c955aaf71989efa641b906558d9fb7'
        assert cert.thumbprint_algorithm == 'sha1'
        assert cert.delete_certificate_error is None

        # Test Update Certiciate
        parameters = models.CertificateCreateOrUpdateParameters(
            password='nodesdk',
            data='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',)
        response = self.mgmt_batch_client.certificate.update(resource_group.name, batch_account.name, certificate, parameters)
        assert isinstance(response, models.Certificate)

        # Test Cancel Certificate Delete
        #with pytest.raises(models.DeleteCertificateError):
        self.mgmt_batch_client.certificate.cancel_deletion(
            resource_group.name, batch_account.name, certificate)

        # Test Delete Certificate
        response = self.mgmt_batch_client.certificate.begin_delete(resource_group.name, batch_account.name, certificate)
        assert response.result() is None

    @pytest.mark.skipif(os.getenv('AZURE_TEST_RUN_LIVE') not in ('yes', 'true'), reason='only run live test')
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    @SimpleBatchPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_mgmt_batch_pools(self, resource_group, location, batch_account):
        # Test create PAAS pool
        paas_pool = "test_paas_pool"
        parameters = models.Pool(
            display_name="test_pool",
            vm_size='small',
            deployment_configuration=models.DeploymentConfiguration(
                cloud_service_configuration=models.CloudServiceConfiguration(os_family='5')
            ),
            start_task=models.StartTask(
                command_line="cmd.exe /c \"echo hello world\"",
                resource_files=[models.ResourceFile(http_url='https://blobsource.com', file_path='filename.txt')],
                environment_settings=[models.EnvironmentSetting(name='ENV_VAR', value='env_value')],
                user_identity=models.UserIdentity(
                    auto_user=models.AutoUserSpecification(
                        elevation_level=models.ElevationLevel.admin
                    )
                )
            ),
            user_accounts=[models.UserAccount(name='UserName', password='p@55wOrd')],
            scale_settings=models.ScaleSettings(
                fixed_scale=models.FixedScaleSettings(
                    target_dedicated_nodes=0,
                    target_low_priority_nodes=0
                )
            )
        )
        response = self.mgmt_batch_client.pool.create(
            resource_group.name, batch_account.name, paas_pool, parameters)
        assert isinstance(response, models.Pool)

        # Test create IAAS pool
        iaas_pool = "test_iaas_pool"
        parameters = models.Pool(
            display_name="test_pool",
            vm_size='Standard_A1',
            deployment_configuration=models.DeploymentConfiguration(
                virtual_machine_configuration=models.VirtualMachineConfiguration(
                    image_reference=models.ImageReference(
                        publisher='MicrosoftWindowsServer',
                        offer='WindowsServer',
                        sku='2016-Datacenter-smalldisk'
                    ),
                    node_agent_sku_id='batch.node.windows amd64',
                    windows_configuration=models.WindowsConfiguration(enable_automatic_updates=True)
                )
            ),
            scale_settings=models.ScaleSettings(
                fixed_scale=models.FixedScaleSettings(
                    target_dedicated_nodes=0,
                    target_low_priority_nodes=0
                )
            )
        )

        response = self.mgmt_batch_client.pool.create(
            resource_group.name, batch_account.name, iaas_pool, parameters)
        assert isinstance(response, models.Pool)

        # Test list pools
        pools = self.mgmt_batch_client.pool.list_by_batch_account(resource_group.name, batch_account.name)
        assert len(list(pools)) == 2

        # Test Update pool
        parameters = models.Pool(
            scale_settings=models.ScaleSettings(
                auto_scale=models.AutoScaleSettings(
                    # Change this to a value once accounts get default quotas
                    formula='$TargetDedicatedNodes=0'
                )
            )
        )
        if self.is_live:
            time.sleep(15)
        response = self.mgmt_batch_client.pool.update(
            resource_group.name, batch_account.name, iaas_pool, parameters)
        assert isinstance(response, models.Pool)

        # Test Get pool
        pool = self.mgmt_batch_client.pool.get(
            resource_group.name, batch_account.name, iaas_pool)
        assert isinstance(pool, models.Pool)
        assert pool.vm_size == 'STANDARD_A1'
        assert pool.display_name is not None
        # This assert should be reintroduced when targetDedidicated nodes can be 1+
        # assert pool.allocation_state == models.AllocationState.resizing
        assert pool.deployment_configuration.virtual_machine_configuration.node_agent_sku_id == 'batch.node.windows amd64'

        # Test stop resizing
        # with pytest.raises(CloudError):
        #     self.mgmt_batch_client.pool.stop_resize(resource_group.name, batch_account.name, iaas_pool)
        # if self.is_live:
        #     time.sleep(300)
        # # Test disable auto-scale
        # response = self.mgmt_batch_client.pool.disable_auto_scale(
        #     resource_group.name, batch_account.name, iaas_pool)
        # assert isinstance(response, models.Pool)

        # Test delete pool
        response = self.mgmt_batch_client.pool.begin_delete(
            resource_group.name, batch_account.name, iaas_pool)
        assert response.result() is None

    @pytest.mark.skipif(os.getenv('AZURE_TEST_RUN_LIVE') not in ('yes', 'true'), reason='only run live test')
    @ResourceGroupPreparer(location=AZURE_LOCATION, random_name_enabled=True)
    @recorded_by_proxy
    def test_mgmt_batch_account_advanced(self, resource_group, location):
        batch_account_name = self.get_resource_name('batchpendpoint')
        vnet_name = self.get_resource_name('vnet')
        subnet_name = self.get_resource_name('subnet')
        subnet_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}".format(
            self.get_settings_value("SUBSCRIPTION_ID"),
            resource_group.name,
            vnet_name,
            subnet_name)
        private_endpoint_name = self.get_resource_name('pe')
        private_connection_name = self.get_resource_name('pec')
        private_link_service_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Batch/batchAccounts/{}'.format(
            self.get_settings_value("SUBSCRIPTION_ID"),
            resource_group.name,
            batch_account_name)
        batch_account = models.BatchAccountCreateParameters(
            location=location,
            public_network_access='Disabled',
            identity=models.BatchAccountIdentity(
                type='SystemAssigned'
            ))
        self.mgmt_batch_client.batch_account.begin_create(
            resource_group_name=resource_group.name,
            account_name=batch_account_name,
            parameters=batch_account).result()
        if self.is_live:
            self.mgmt_network.virtual_networks.begin_create_or_update(
                resource_group_name=resource_group.name,
                virtual_network_name=vnet_name,
                parameters=self.mgmt_network.models().VirtualNetwork(
                    address_space=self.mgmt_network.models().AddressSpace(
                        address_prefixes=['10.0.0.0/16']),
                    location=location,
                    subnets=[
                        self.mgmt_network.models().Subnet(
                            address_prefix='10.0.0.0/24',
                            name=subnet_name,
                            private_endpoint_network_policies='Disabled')])
            ).result()
            self.mgmt_network.private_endpoints.begin_create_or_update(
                resource_group_name=resource_group.name,
                private_endpoint_name=private_endpoint_name,
                parameters=self.mgmt_network.models().PrivateEndpoint(
                    location=location,
                    subnet=self.mgmt_network.models().Subnet(
                        id=subnet_id
                    ),
                    manual_private_link_service_connections=[
                        self.mgmt_network.models().PrivateLinkServiceConnection(
                            private_link_service_id=private_link_service_id,
                            group_ids=['batchAccount'],
                            name=private_connection_name
                        )]
                )
            ).result()
        private_links = self.mgmt_batch_client.private_link_resource.list_by_batch_account(
            resource_group_name=resource_group.name,
            account_name=batch_account_name)
        private_link = private_links.__next__()
        self.mgmt_batch_client.private_link_resource.get(
            resource_group_name=resource_group.name,
            account_name=batch_account_name,
            private_link_resource_name=private_link.name)
        private_endpoints = self.mgmt_batch_client.private_endpoint_connection.list_by_batch_account(
            resource_group_name=resource_group.name,
            account_name=batch_account_name)

        private_endpoint = private_endpoints.__next__()
        self.mgmt_batch_client.private_endpoint_connection.get(
            resource_group_name=resource_group.name,
            account_name=batch_account_name,
            private_endpoint_connection_name=private_endpoint.name)
        self.mgmt_batch_client.private_endpoint_connection.begin_update(
            resource_group_name=resource_group.name,
            account_name=batch_account_name,
            private_endpoint_connection_name=private_endpoint.name,
            parameters={
                "private_link_service_connection_state": {
                    "status": "Approved",
                    "description": "Approved for test"
                }
            }
        ).result()
