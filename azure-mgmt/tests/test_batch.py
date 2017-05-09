# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import datetime
import io
import json
import logging
import os
import sys
import time
import unittest

import requests

from testutils.common_recordingtestcase import (
    RecordingTestCase,
    TestMode,
)
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase
import tests.mgmt_settings_fake as fake_settings
from testutils.common_recordingtestcase import record

import azure.mgmt.resource
import azure.mgmt.storage
import azure.mgmt.batch
import azure.mgmt.keyvault
import azure.batch as batch
from azure.batch.batch_auth import SharedKeyCredentials
from msrestazure.azure_active_directory import AADTokenCredentials
from azure.common.credentials import ServicePrincipalCredentials


AZURE_BATCH_ACCOUNT = 'pythonsdktest'
AZURE_RESOURCE_GROUP = 'python_batch_sdk_test'
AZURE_LOCATION = 'brazilsouth'
AZURE_STORAGE_ACCOUNT = 'batchpythonsdktest'
AZURE_KEY_VAULT = 'batchpythonsdktest'
AZURE_TENANT_ID = 'microsoft.onmicrosoft.com'
OUTPUT_CONTAINER = 'batch-sdk-test-outputs'
EXISTING_RESOURCES = False
CLEAN_UP = True

LOG = logging.getLogger('batch-python-tests')
LOG.level = logging.WARNING
LOG.addHandler(logging.StreamHandler())

def init_tst_mode(working_folder):
    try:
        path = os.path.join(working_folder, 'testsettings_local.json')
        with open(path) as testsettings_local_file:
            test_settings = json.load(testsettings_local_file)
        return test_settings['mode']
    except:
        return TestMode.playback


def validate_shared_key_auth(adapter, request, *args, **kwargs):
    assert(request.headers['Authorization'].startswith('SharedKey '))


def validate_token_auth(adapter, request, *args, **kwargs):
    assert(request.headers['Authorization'].startswith('Bearer '))


def create_mgmt_client(settings, client_class, **kwargs):
    client = client_class(
        credentials=settings.get_credentials(),
        subscription_id=settings.SUBSCRIPTION_ID,
        **kwargs
    )
    return client


def create_resource_group(client):
    group = {
        'name': AZURE_RESOURCE_GROUP,
        'location': AZURE_LOCATION
    }
    result_create = client.resource_groups.create_or_update(
        AZURE_RESOURCE_GROUP,
        group,
    )
    return result_create


def create_keyvault(client):
    result_create = client.vaults.create_or_update(
        AZURE_RESOURCE_GROUP,
        AZURE_KEY_VAULT,
        {
            'location': 'eastus2',
            'properties': {
                'sku': {'name': 'standard'},
                'tenant_id': "72f988bf-86f1-41af-91ab-2d7cd011db47",
                'enabled_for_deployment': True,
                'enabled_for_disk_encryption': True,
                'enabled_for_template_deployment': True,
                'access_policies': [ {
                    'tenant_id': "72f988bf-86f1-41af-91ab-2d7cd011db47",
                    'object_id': "f520d84c-3fd3-4cc8-88d4-2ed25b00d27a",
                    'permissions': {
                        'keys': ['all'],
                        'secrets': ['all']
                    }
                }]
            }
        })
    return result_create


def create_storage_account(client):
    params = {
        'sku': {'name': 'Standard_LRS'},
        'kind': 'Storage',
        'location': AZURE_LOCATION
    }
    result_create = client.storage_accounts.create(
        AZURE_RESOURCE_GROUP,
        AZURE_STORAGE_ACCOUNT,
        params,
    )
    result_create.result()


def create_storage_client(mgmt_client):
    import azure.storage.blob as storage
    keys = mgmt_client.storage_accounts.list_keys(
        AZURE_RESOURCE_GROUP,
        AZURE_STORAGE_ACCOUNT)
    account_key = keys.keys[0].value
    data_client = storage.BlockBlobService(AZURE_STORAGE_ACCOUNT, account_key)
    data_client.create_container(OUTPUT_CONTAINER, fail_on_exist=False)
    return data_client


def create_batch_account(client, settings, live):
    if live:
        if not EXISTING_RESOURCES:
            storage_resource = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
                settings.SUBSCRIPTION_ID,
                AZURE_RESOURCE_GROUP,
                AZURE_STORAGE_ACCOUNT
            )
            batch_account = azure.mgmt.batch.models.BatchAccountCreateParameters(
                location=AZURE_LOCATION,
                auto_storage=azure.mgmt.batch.models.AutoStorageBaseProperties(storage_resource)
            )
            account_setup = client.batch_account.create(AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, batch_account)
            new_account = account_setup.result()
        account_keys = client.batch_account.get_keys(AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
        shared_key_creds = SharedKeyCredentials(AZURE_BATCH_ACCOUNT, account_keys.primary)
        aad_creds = ServicePrincipalCredentials(settings.BATCH_CLIENT_ID, settings.BATCH_SECRET,
            tenant=AZURE_TENANT_ID,
            resource='https://batch.core.windows.net/')
    else:
        shared_key_creds = SharedKeyCredentials(AZURE_BATCH_ACCOUNT, 'ZmFrZV9hY29jdW50X2tleQ==')
        aad_creds = AADTokenCredentials(token={'access_token':'faked_token'})
    url = "https://{}.{}.batch.azure.com/".format(AZURE_BATCH_ACCOUNT, AZURE_LOCATION)
    sk_client = azure.batch.BatchServiceClient(shared_key_creds, base_url=url)
    sk_client._client._adapter.add_hook("request", validate_shared_key_auth)
    aad_client = azure.batch.BatchServiceClient(aad_creds, base_url=url)
    aad_client._client._adapter.add_hook("request", validate_token_auth)
    return (sk_client, aad_client)


class BatchMgmtTestCase(RecordingTestCase):

    @classmethod
    def setUpClass(cls):
        LOG.warning('Starting Batch tests')
        LOG.debug("Setting up Batch tests:")
        cls.working_folder = os.path.dirname(__file__)
        try:
            cls.test_mode = init_tst_mode(cls.working_folder)
            cls.fake_settings = fake_settings
            if TestMode.is_playback(cls.test_mode):
                LOG.debug("    running in playback mode")
                cls.live = False
                cls.settings = cls.fake_settings
            else:
                LOG.debug("    running in live mode")
                import tests.mgmt_settings_real as real_settings
                cls.settings = real_settings
                cls.live = True
            LOG.debug('    creating resource client')
            cls.resource_client = create_mgmt_client(cls.settings,
                azure.mgmt.resource.resources.ResourceManagementClient
            )
            LOG.debug('    creating keyvault client')
            cls.keyvault_client = create_mgmt_client(cls.settings,
                azure.mgmt.keyvault.KeyVaultManagementClient
            )
            LOG.debug('    creating storage client')
            cls.storage_client = create_mgmt_client(cls.settings,
                azure.mgmt.storage.StorageManagementClient
            )
            LOG.debug('    creating batch client')
            cls.batch_mgmt_client = create_mgmt_client(cls.settings,
                azure.mgmt.batch.BatchManagementClient
            )
            if cls.live:
                if not EXISTING_RESOURCES:
                    LOG.debug('    creating resource group')
                    create_resource_group(cls.resource_client)
                    LOG.debug('    creating storage')
                    create_storage_account(cls.storage_client)
                    LOG.debug('    creating keyvault')
                    create_keyvault(cls.keyvault_client)
                cls.storage_data_client = create_storage_client(cls.storage_client)
            else:
                cls.storage_data_client = None
            LOG.debug('    creating batch account')
            cls.batch_client_sk, cls.batch_client_aad = create_batch_account(cls.batch_mgmt_client, cls.settings, cls.live)
        except Exception as err:
            cls.tearDownClass()
            raise AssertionError("Failed to setup Batch Account: {}".format(err))
        LOG.debug("    finished setup")
        return super(BatchMgmtTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        LOG.debug("Tearing down Batch resources:")
        if cls.live and CLEAN_UP:
            try:
                LOG.debug("    deleting Batch account")
                deleting = cls.batch_mgmt_client.batch_account.delete(
                    AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
                deleting.wait()
            except: pass # This should get deleted with the resource group anyway
            try:
                LOG.debug("    deleting storage")
                cls.storage_client.storage_accounts.delete(
                    AZURE_RESOURCE_GROUP, AZURE_STORAGE_ACCOUNT)
            except: pass
            try:
                LOG.debug("    deleting resource group")
                deleting = cls.resource_client.resource_groups.delete(AZURE_RESOURCE_GROUP)
                deleting.wait()
            except: pass
        LOG.debug("    finished")
        LOG.warning("Batch tests complete")
        return super(BatchMgmtTestCase, cls).tearDownClass()

    def _scrub(self, val):
        if not hasattr(val, 'replace'):
            return val
        val = super(BatchMgmtTestCase, self)._scrub(val)
        real_to_fake_dict = {
            self.settings.SUBSCRIPTION_ID: self.fake_settings.SUBSCRIPTION_ID,
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val

    def _generate_container_sas_token(self):
        """Generate a container URL with SAS token."""
        if self.live:
            import azure.storage.blob as storage
            permission=storage.ContainerPermissions(True, True, True, True)
            sas_token = self.storage_data_client.generate_container_shared_access_signature(
                OUTPUT_CONTAINER,
                permission=permission,
                expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=2))
            url = '{}://{}/{}?{}'.format(
                self.storage_data_client.protocol,
                self.storage_data_client.primary_endpoint,
                OUTPUT_CONTAINER,
                sas_token)
        else:
            url = 'test_container_sas'
        return url

    def assertBatchError(self, error, message, code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            if message not in error:
                error[message] = "BatchErrorException expected but not raised"
        except batch.models.BatchErrorException as err:
            self.assertEqual(error, message, err.error.code, code)
        except Exception as err:
            if message not in error:
                error[message] = "Expected BatchErrorExcption, instead got: {!r}".format(err)

    def assertCloudError(self, error, message, code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            if message not in error:
                error[message] = "CloudError expected but not raised"
        except azure.common.exceptions.CloudError as err:
            self.assertTrue(error, message, code in str(err))
        except Exception as err:
            if message not in error:
                error[message] = "Expected CloudError, instead got: {!r}".format(err)

    def assertRuns(self, error, message, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            if message not in error:
                error[message] = str(err)

    def assertList(self, error, message, func, *args, **kwargs):
        response = self.assertRuns(error, message, func, *args, **kwargs)
        if response is None:
            if message not in error:
                error[message] = "Received uniterable response"
            return []
        try:
            return [r for r in response]
        except Exception as err:
            if message not in error:
                error[message] = str(err)
            return []

    def assertIsNone(self, error, message, obj):
        try:
            super(BatchMgmtTestCase, self).assertIsNone(obj)
        except AssertionError as err:
            if message not in error:
                error[message] = str(err)

    def assertEqual(self, error, message, first, second, msg = None):
        try:
            super(BatchMgmtTestCase, self).assertEqual(first, second)
        except AssertionError as err:
            if message not in error:
                error[message] = str(err)

    def assertTrue(self, error, message, expr, msg=None):
        try:
            super(BatchMgmtTestCase, self).assertTrue(expr, msg)
        except AssertionError as err:
            if message not in error:
                error[message] = str(err)

    def assertSuccess(self, errors):
        if errors:
            message = "The following errors occurred:\n"
            message += "\n".join(["{}: {!r}".format(k, v) for k, v in errors.items()])
            raise AssertionError(message)

    @record
    def test_batch_accounts(self):
        _e = {}

        _m = "Test List Batch Operations"
        LOG.debug(_m)
        operations = self.assertList(_e, _m, self.batch_mgmt_client.operations.list)
        self.assertEqual(_e, _m, len(operations), 19)
        self.assertEqual(_e, _m, operations[0].name, 'Microsoft.Batch/batchAccounts/providers/Microsoft.Insights/diagnosticSettings/read')
        self.assertEqual(_e, _m, operations[0].origin, 'system')
        self.assertEqual(_e, _m, operations[0].display.provider, 'Microsoft Batch')
        self.assertEqual(_e, _m, operations[0].display.operation, 'Read diagnostic setting')

        _m = "Test Get Subscription Quota"
        LOG.debug(_m)
        quotas = self.assertRuns(_e, _m, self.batch_mgmt_client.location.get_quotas,
                                 AZURE_LOCATION)
        self.assertTrue(_e, _m, isinstance(quotas, azure.mgmt.batch.models.BatchLocationQuota))
        if quotas:
            self.assertEqual(_e, _m, quotas.account_quota, 1)

        _m = "Test Create BYOS Account"
        LOG.debug(_m)
        batch_account = azure.mgmt.batch.models.BatchAccountCreateParameters(
                location='eastus2',
                pool_allocation_mode=azure.mgmt.batch.models.PoolAllocationMode.user_subscription)
        creating = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.create,
                                   AZURE_RESOURCE_GROUP,
                                   'batchpythonaccounttest',
                                    batch_account)
        try:
            creating.result()
            _e[_m] = "Expected CloudError to be raised."
        except Exception as error:
            # TODO: Figure out why this deserializes to HTTPError rather than CloudError
            if hasattr(error.inner_exception, 'error'):
                self.assertEqual(_e, _m, error.inner_exception.error, "InvalidRequestBody")

        _m = "Test Create Account with Key Vault Reference"
        keyvault_id = "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.KeyVault/vaults/{}".format(
            self.settings.SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, AZURE_KEY_VAULT)
        keyvault_url = "https://{}.vault.azure.net/".format(AZURE_KEY_VAULT)
        batch_account = azure.mgmt.batch.models.BatchAccountCreateParameters(
                location='eastus2',
                pool_allocation_mode=azure.mgmt.batch.models.PoolAllocationMode.user_subscription,
                key_vault_reference={'id': keyvault_id, 'url': keyvault_url})
        creating = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.create,
                                   AZURE_RESOURCE_GROUP,
                                   'batchpythonaccounttest',
                                    batch_account)
        self.assertRuns(_e, _m, creating.result)

        _m = "Test Get Account"
        LOG.debug(_m)
        account = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.get,
                                  AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
        self.assertTrue(_e, _m, isinstance(account, azure.mgmt.batch.models.BatchAccount))
        if account:
            self.assertEqual(_e, _m, account.dedicated_core_quota, 20)
            self.assertEqual(_e, _m, account.low_priority_core_quota, 50)
            self.assertEqual(_e, _m, account.pool_quota, 20)
            self.assertEqual(_e, _m, account.pool_allocation_mode.value, 'BatchService')

        _m = "Test List Accounts"  #TODO: Need to re-record
        LOG.debug('TODO: ' + _m)
        #accounts = self.assertList(_e, _m, self.batch_mgmt_client.batch_account.list)
        #self.assertTrue(_e, _m, len(accounts) > 0)

        _m = "Test List Accounts by Resource Group"
        LOG.debug(_m)
        accounts = self.assertList(_e, _m, self.batch_mgmt_client.batch_account.list_by_resource_group,
                                   AZURE_RESOURCE_GROUP)
        self.assertEqual(_e, _m, len(accounts), 2)

        _m = "Test List Account Keys"
        LOG.debug(_m)
        keys = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.get_keys,
                               AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
        self.assertTrue(_e, _m, isinstance(keys, azure.mgmt.batch.models.BatchAccountKeys))
        secondary = None
        if keys:
            self.assertEqual(_e, _m, keys.account_name, AZURE_BATCH_ACCOUNT)
            secondary = keys.secondary

        _m = "Test Regenerate Account Key"
        LOG.debug(_m)
        keys = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.regenerate_key,
                               AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'Secondary')
        self.assertTrue(_e, _m, isinstance(keys, azure.mgmt.batch.models.BatchAccountKeys))
        self.assertTrue(_e, _m, keys.secondary != secondary)
        
        _m = "Test Sync AutoStorage Keys"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.synchronize_auto_storage_keys,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
        self.assertIsNone(_e, _m, response)

        _m = "Test Update Account"
        LOG.debug(_m)
        update_tags = {'Name': 'tagName', 'Value': 'tagValue'}
        updated = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.update,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, update_tags)
        self.assertTrue(_e, _m, isinstance(updated, azure.mgmt.batch.models.BatchAccount))
        if updated:
            self.assertEqual(_e, _m, updated.tags['Name'], 'tagName')
            self.assertEqual(_e, _m, updated.tags['Value'], 'tagValue')

        _m = "Test Delete Account"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.batch_account.delete,
                                   AZURE_RESOURCE_GROUP, 'batchpythonaccounttest')
        self.assertIsNone(_e, _m, response.result())

        self.assertSuccess(_e)

    @record
    def test_batch_applications(self):
        _e = {}
        _m = "Test Add Application"
        LOG.debug(_m)
        application = self.assertRuns(_e, _m, self.batch_mgmt_client.application.create,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id',
                                   allow_updated=True, display_name='my_application_name')
        self.assertTrue(_e, _m, isinstance(application, azure.mgmt.batch.models.Application))
        if application:
            self.assertEqual(_e, _m, application.id, 'my_application_id')
            self.assertEqual(_e, _m, application.display_name, 'my_application_name')
            self.assertEqual(_e, _m, application.allow_updates, True)

        _m = "Test Mgmt Get Application"
        LOG.debug(_m)
        application = self.assertRuns(_e, _m, self.batch_mgmt_client.application.get,
                                      AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id')
        self.assertTrue(_e, _m, isinstance(application, azure.mgmt.batch.models.Application))
        if application:
            self.assertEqual(_e, _m, application.id, 'my_application_id')
            self.assertEqual(_e, _m, application.display_name, 'my_application_name')
            self.assertEqual(_e, _m, application.allow_updates, True)

        _m = "Test Mgmt List Applications"
        LOG.debug(_m)
        applications = self.assertList(_e, _m, self.batch_mgmt_client.application.list,
                                       AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT)
        self.assertTrue(_e, _m, len(applications) > 0)

        _m = "Test Add Application Package"
        LOG.debug(_m)
        package_ref = self.assertRuns(_e, _m, self.batch_mgmt_client.application_package.create,
                                      AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', 'v1.0')
        self.assertTrue(_e, _m, isinstance(package_ref, azure.mgmt.batch.models.ApplicationPackage))
        if package_ref:
            try:
                with io.BytesIO(b'Hello World') as f:
                    headers = {'x-ms-blob-type': 'BlockBlob'}
                    upload = requests.put(package_ref.storage_url, headers=headers, data=f.read())
                    if not upload:
                        raise ValueError('Upload failed: {!r}'.format(upload))
            except Exception as err:
                _e[_m] = 'Failed to upload test package: {}'.format(err)

        _m = "Test Activate Application Package"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.application_package.activate,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', 'v1.0', 'zip')
        self.assertIsNone(_e, _m, response)

        _m = "Test Update Application"
        LOG.debug(_m)
        params = azure.mgmt.batch.models.ApplicationUpdateParameters(
            allow_updates=False,
            display_name='my_updated_name',
            default_version='v1.0'
        )
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.application.update,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', params)
        self.assertIsNone(_e, _m, response)

        _m = "Test Get Application Package"
        LOG.debug(_m)
        package_ref = self.assertRuns(_e, _m, self.batch_mgmt_client.application_package.get,
                                      AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', 'v1.0')
        self.assertTrue(_e, _m, isinstance(package_ref, azure.mgmt.batch.models.ApplicationPackage))
        if package_ref:
            self.assertEqual(_e, _m, package_ref.id, 'my_application_id')
            self.assertEqual(_e, _m, package_ref.version, 'v1.0')
            self.assertEqual(_e, _m, package_ref.format, 'zip')
            self.assertEqual(_e, _m, package_ref.state, azure.mgmt.batch.models.PackageState.active)

        _m = "Test Service Get Application"
        LOG.debug(_m)
        application = self.assertRuns(_e, _m, self.batch_client_sk.application.get, 'my_application_id')
        self.assertTrue(_e, _m, isinstance(application, batch.models.ApplicationSummary))
        if application:
            self.assertEqual(_e, _m, application.id, 'my_application_id')
            self.assertEqual(_e, _m, application.display_name, 'my_updated_name')
            self.assertEqual(_e, _m, application.versions, ['v1.0'])

        _m = "Test Service List Applications"
        LOG.debug(_m)
        applications = self.assertList(_e, _m, self.batch_client_sk.application.list)
        self.assertTrue(_e, _m, len(applications) > 0)

        _m = "Test Delete Application Package"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.application_package.delete,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', 'v1.0')
        self.assertIsNone(_e, _m, response)

        _m = "Test Delete Application"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_mgmt_client.application.delete,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id')
        self.assertIsNone(_e, _m, response)
        self.assertSuccess(_e)

    @record
    def test_batch_certificates(self):
        _e = {}
        _m = "Test Add Certificate"
        LOG.debug(_m)
        certificate = batch.models.CertificateAddParameter(
            thumbprint='cff2ab63c8c955aaf71989efa641b906558d9fb7',
            thumbprint_algorithm='sha1',
            data='MIIGMQIBAzCCBe0GCSqGSIb3DQEHAaCCBd4EggXaMIIF1jCCA8AGCSqGSIb3DQEHAaCCA7EEggOtMIIDqTCCA6UGCyqGSIb3DQEMCgECoIICtjCCArIwHAYKKoZIhvcNAQwBAzAOBAhyd3xCtln3iQICB9AEggKQhe5P10V9iV1BsDlwWT561Yu2hVq3JT8ae/ebx1ZR/gMApVereDKkS9Zg4vFyssusHebbK5pDpU8vfAqle0TM4m7wGsRj453ZorSPUfMpHvQnAOn+2pEpWdMThU7xvZ6DVpwhDOQk9166z+KnKdHGuJKh4haMT7Rw/6xZ1rsBt2423cwTrQVMQyACrEkianpuujubKltN99qRoFAxhQcnYE2KlYKw7lRcExq6mDSYAyk5xJZ1ZFdLj6MAryZroQit/0g5eyhoNEKwWbi8px5j71pRTf7yjN+deMGQKwbGl+3OgaL1UZ5fCjypbVL60kpIBxLZwIJ7p3jJ+q9pbq9zSdzshPYor5lxyUfXqaso/0/91ayNoBzg4hQGh618PhFI6RMGjwkzhB9xk74iweJ9HQyIHf8yx2RCSI22JuCMitPMWSGvOszhbNx3AEDLuiiAOHg391mprEtKZguOIr9LrJwem/YmcHbwyz5YAbZmiseKPkllfC7dafFfCFEkj6R2oegIsZo0pEKYisAXBqT0g+6/jGwuhlZcBo0f7UIZm88iA3MrJCjlXEgV5OcQdoWj+hq0lKEdnhtCKr03AIfukN6+4vjjarZeW1bs0swq0l3XFf5RHa11otshMS4mpewshB9iO9MuKWpRxuxeng4PlKZ/zuBqmPeUrjJ9454oK35Pq+dghfemt7AUpBH/KycDNIZgfdEWUZrRKBGnc519C+RTqxyt5hWL18nJk4LvSd3QKlJ1iyJxClhhb/NWEzPqNdyA5cxen+2T9bd/EqJ2KzRv5/BPVwTQkHH9W/TZElFyvFfOFIW2+03RKbVGw72Mr/0xKZ+awAnEfoU+SL/2Gj2m6PHkqFX2sOCi/tN9EA4xgdswEwYJKoZIhvcNAQkVMQYEBAEAAAAwXQYJKwYBBAGCNxEBMVAeTgBNAGkAYwByAG8AcwBvAGYAdAAgAFMAdAByAG8AbgBnACAAQwByAHkAcAB0AG8AZwByAGEAcABoAGkAYwAgAFAAcgBvAHYAaQBkAGUAcjBlBgkqhkiG9w0BCRQxWB5WAFAAdgBrAFQAbQBwADoANABjAGUANgAwADQAZABhAC0AMAA2ADgAMQAtADQANAAxADUALQBhADIAYwBhAC0ANQA3ADcAMwAwADgAZQA2AGQAOQBhAGMwggIOBgkqhkiG9w0BBwGgggH/BIIB+zCCAfcwggHzBgsqhkiG9w0BDAoBA6CCAcswggHHBgoqhkiG9w0BCRYBoIIBtwSCAbMwggGvMIIBXaADAgECAhAdka3aTQsIsUphgIXGUmeRMAkGBSsOAwIdBQAwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3kwHhcNMTYwMTAxMDcwMDAwWhcNMTgwMTAxMDcwMDAwWjASMRAwDgYDVQQDEwdub2Rlc2RrMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC5fhcxbJHxxBEIDzVOMc56s04U6k4GPY7yMR1m+rBGVRiAyV4RjY6U936dqXHCVD36ps2Q0Z+OeEgyCInkIyVeB1EwXcToOcyeS2YcUb0vRWZDouC3tuFdHwiK1Ed5iW/LksmXDotyV7kpqzaPhOFiMtBuMEwNJcPge9k17hRgRQIDAQABo0swSTBHBgNVHQEEQDA+gBAS5AktBh0dTwCNYSHcFmRjoRgwFjEUMBIGA1UEAxMLUm9vdCBBZ2VuY3mCEAY3bACqAGSKEc+41KpcNfQwCQYFKw4DAh0FAANBAHl2M97QbpzdnwO5HoRBsiEExOcLTNg+GKCr7HUsbzfvrUivw+JLL7qjHAIc5phnK+F5bQ8HKe0L9YXBSKl+fvwxFTATBgkqhkiG9w0BCRUxBgQEAQAAADA7MB8wBwYFKw4DAhoEFGVtyGMqiBd32fGpzlGZQoRM6UQwBBTI0YHFFqTS4Go8CoLgswn29EiuUQICB9A=',
            certificate_format=batch.models.CertificateFormat.pfx,
            password='nodesdk')

        response = self.assertRuns(_e, _m, self.batch_client_sk.certificate.add, certificate)
        self.assertIsNone(_e, _m, response)

        _m = "Test List Certificates"
        LOG.debug(_m)
        certs = self.assertList(_e, _m, self.batch_client_sk.certificate.list)
        self.assertTrue(_e, _m, len(certs) > 0)

        test_cert = [c for c in certs if c.thumbprint == 'cff2ab63c8c955aaf71989efa641b906558d9fb7']
        self.assertEqual(_e, _m, len(test_cert), 1)

        _m = "Test Get Certificate"
        LOG.debug(_m)
        cert = self.assertRuns(_e, _m, self.batch_client_sk.certificate.get, 'sha1', 'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        self.assertTrue(_e, _m, isinstance(cert, batch.models.Certificate))
        if cert:
            self.assertEqual(_e, _m, cert.thumbprint, 'cff2ab63c8c955aaf71989efa641b906558d9fb7')
            self.assertEqual(_e, _m, cert.thumbprint_algorithm, 'sha1')
            self.assertIsNone(_e, _m, cert.delete_certificate_error)

        _m = "Test Cancel Certificate Delete"
        LOG.debug(_m)
        self.assertBatchError(_e, _m, 'CertificateStateActive',
                                self.batch_client_sk.certificate.cancel_deletion,
                                'sha1',
                                'cff2ab63c8c955aaf71989efa641b906558d9fb7')

        _m = "Test Delete Certificate"
        LOG.debug(_m)
        response = self.assertRuns(_e, _m, self.batch_client_sk.certificate.delete,
            'sha1',
            'cff2ab63c8c955aaf71989efa641b906558d9fb7')
        self.assertIsNone(_e, _m, response)
        self.assertSuccess(_e)

    @record
    def test_batch_pools(self):
        _e = {}

        _m = "Test List Node Agent SKUs"
        response = self.assertList(_e, _m, self.batch_client_sk.account.list_node_agent_skus)
        if response:
            self.assertTrue(_e, _m, len(response) > 1)
            self.assertEqual(_e, _m, response[-1].id, "batch.node.windows amd64")
            self.assertEqual(_e, _m, response[-1].os_type.value, "windows")
            self.assertTrue(_e, _m, len(response[-1].verified_image_references) > 1)

        users = [
            {'name': 'test-user-1', 'password': 'kt#_gahr!@aGERDXA'},
            {'name': 'test-user-2', 'password': 'kt#_gahr!@aGERDXA',
             'elevation_level': batch.models.ElevationLevel.admin}
        ]
        with BatchPool(self.live, self.batch_client_sk, 'python_test_pool_1', user_accounts=users) as pool_id:
            with BatchPool(self.live, self.batch_client_sk, 'python_test_pool_2',
                           target_low_priority_nodes=2) as pool_id_2:

                _m = "Test Create Pool with Network Configuration"
                LOG.debug(_m)
                pool_config = batch.models.CloudServiceConfiguration('4')
                network_config = batch.models.NetworkConfiguration('/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/test/providers/Microsoft.Network/virtualNetworks/vnet1/subnets/subnet1')
                pool = batch.models.PoolAddParameter('no_pool', 'small',
                                                     cloud_service_configuration=pool_config,
                                                     network_configuration=network_config)
                self.assertBatchError(_e, _m, 'Forbidden',
                                      self.batch_client_sk.pool.add,
                                      pool, batch.models.PoolAddOptions(timeout=45))

                _m = "Test Create Pool with Custom VHD"
                LOG.debug(_m)
                pool_config = batch.models.VirtualMachineConfiguration(
                    node_agent_sku_id="batch.node.ubuntu 16.04",
                    os_disk={'image_uris': ['http://image-A', 'http://image-B']})
                pool = batch.models.PoolAddParameter(
                    'no_pool', 'Standard_A1',
                    virtual_machine_configuration=pool_config)
                self.assertBatchError(_e, _m, 'InvalidPropertyValue',
                                      self.batch_client_sk.pool.add,
                                      pool, batch.models.PoolAddOptions(timeout=45))

                _m = "Test Create Pool with application licenses"
                LOG.debug(_m)
                pool_config = batch.models.CloudServiceConfiguration('4')
                pool = batch.models.PoolAddParameter('no_pool', 'small',
                    cloud_service_configuration=pool_config,
                    application_licenses=["maya"])
                self.assertBatchError(_e, _m, 'Forbidden',
                                      self.batch_client_sk.pool.add,
                                      pool, batch.models.PoolAddOptions(timeout=45))

                _m = "Test Upgrade Pool OS"
                LOG.debug(_m)
                response = self.assertBatchError(_e, _m, "PoolVersionEqualsUpgradeVersion",
                                                 self.batch_client_sk.pool.upgrade_os, pool_id, '*')
                self.assertIsNone(_e, _m, response)

                _m = "Test Update Pool Parameters"
                LOG.debug(_m)
                params = batch.models.PoolUpdatePropertiesParameter([], [], [batch.models.MetadataItem('foo', 'bar')])
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.update_properties, pool_id, params)
                self.assertIsNone(_e, _m, response)

                _m = "Test Patch Pool Parameters"
                LOG.debug(_m)
                params = batch.models.PoolPatchParameter(metadata=[batch.models.MetadataItem('foo2', 'bar2')])
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.patch, pool_id, params)
                self.assertIsNone(_e, _m, response)

                _m = "Test Get Pool"
                LOG.debug(_m)
                pool = self.assertRuns(_e, _m, self.batch_client_sk.pool.get, pool_id)
                self.assertTrue(_e, _m, isinstance(pool, batch.models.CloudPool))
                if pool:
                    self.assertEqual(_e, _m, pool.id, pool_id)
                    self.assertEqual(_e, _m, pool.state, batch.models.PoolState.active)
                    self.assertEqual(_e, _m, pool.allocation_state, batch.models.AllocationState.steady)
                    self.assertEqual(_e, _m, pool.cloud_service_configuration.os_family, '4')
                    self.assertEqual(_e, _m, pool.vm_size, 'small')
                    self.assertEqual(_e, _m, pool.metadata[0].name, 'foo2')
                    self.assertEqual(_e, _m, pool.metadata[0].value, 'bar2')
                    self.assertEqual(_e, _m, pool.user_accounts[0].name, 'test-user-1')
                    self.assertEqual(_e, _m, pool.user_accounts[0].elevation_level.value, 'nonAdmin')
                    self.assertEqual(_e, _m, pool.user_accounts[1].name, 'test-user-2')
                    self.assertEqual(_e, _m, pool.user_accounts[1].elevation_level.value, 'admin')

                _m = "Test Get Pool with OData Clauses"
                LOG.debug(_m)
                options = batch.models.PoolGetOptions(select='id,state', expand='stats')
                pool = self.assertRuns(_e, _m, self.batch_client_sk.pool.get, pool_id, options)
                self.assertTrue(_e, _m, isinstance(pool, batch.models.CloudPool))
                if pool:
                    self.assertEqual(_e, _m, pool.id, pool_id)
                    self.assertEqual(_e, _m, pool.state, batch.models.PoolState.active)
                    self.assertIsNone(_e, _m, pool.allocation_state)
                    self.assertIsNone(_e, _m, pool.vm_size)

                _m = "Test Enable Autoscale"
                LOG.debug(_m)
                interval = datetime.timedelta(minutes=6)
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.enable_auto_scale, pool_id,
                                           auto_scale_formula='$TargetDedicatedNodes=2',
                                           auto_scale_evaluation_interval=interval)
                self.assertIsNone(_e, _m, response)

                _m = "Test Evaluate Autoscale"
                LOG.debug(_m)
                result = self.assertRuns(_e, _m, self.batch_client_sk.pool.evaluate_auto_scale,
                                         pool_id, '$TargetDedicatedNodes=3')
                if result:
                    self.assertTrue(_e, _m, isinstance(result, batch.models.AutoScaleRun))
                    self.assertEqual(_e, _m, result.results, '$TargetDedicatedNodes=3;$TargetLowPriorityNodes=0;$NodeDeallocationOption=requeue')

                _m = "Test Disable Autoscale"
                LOG.debug(_m)
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.disable_auto_scale, pool_id)
                self.assertIsNone(_e, _m, response)            

                _m = "Test List Pools without Filters"
                LOG.debug(_m)
                pools = self.assertList(_e, _m, self.batch_client_sk.pool.list)
                self.assertTrue(_e, _m, len(pools) > 1)
                
                _m = "Test List Pools with Maximum"
                LOG.debug(_m)
                options = batch.models.PoolListOptions(max_results=1)
                pools = self.assertRuns(_e, _m, self.batch_client_sk.pool.list, options)
                if pools:
                    self.assertRuns(_e, _m, pools.next)
                    self.assertEqual(_e, _m, len(pools.current_page), 1)

                _m = "Test List Pools with Filter"
                LOG.debug(_m)
                options = batch.models.PoolListOptions(
                    filter='startswith(id,\'python_test_pool_1\')',
                    select='id,state',
                    expand='stats')
                pools = self.assertList(_e, _m, self.batch_client_sk.pool.list, options)
                self.assertEqual(_e, _m, len(pools), 1)

                _m = "Test Pool Exists"
                LOG.debug(_m)
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.exists, pool_id_2)
                self.assertTrue(_e, _m, response)

                _m = "Test Pool Resize"
                LOG.debug(_m)
                pool = self.assertRuns(_e, _m, self.batch_client_sk.pool.get, pool_id_2)
                self.assertTrue(_e, _m, isinstance(pool, batch.models.CloudPool))
                if pool:
                    self.assertEqual(_e, _m, pool.target_dedicated_nodes, 0)
                    self.assertEqual(_e, _m, pool.target_low_priority_nodes, 2)
                params = batch.models.PoolResizeParameter(target_dedicated_nodes=3, target_low_priority_nodes=0)
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.resize, pool_id_2, params)
                self.assertIsNone(_e, _m, response)

                _m = "Test Stop Pool Resize"
                LOG.debug(_m)
                response = self.assertRuns(_e, _m, self.batch_client_sk.pool.stop_resize, pool_id_2)
                self.assertIsNone(_e, _m, response)
                pool = self.assertRuns(_e, _m, self.batch_client_sk.pool.get, pool_id_2)
                self.assertTrue(_e, _m, isinstance(pool, batch.models.CloudPool))
                if pool:
                    self.assertEqual(_e, _m, pool.target_dedicated_nodes, 3)
                    self.assertEqual(_e, _m, pool.target_low_priority_nodes, 2)  # TODO: Why?

                _m = "Test Get All Pools Lifetime Statistics"
                LOG.debug(_m)
                stats = self.assertRuns(_e, _m, self.batch_client_sk.pool.get_all_lifetime_statistics)
                self.assertTrue(_e, _m, isinstance(stats, batch.models.PoolStatistics))
                if stats:
                    self.assertEqual(_e, _m, stats.url, "https://{}.{}.batch.azure.com/lifetimepoolstats".format(
                        AZURE_BATCH_ACCOUNT, AZURE_LOCATION))
                    self.assertEqual(_e, _m, stats.resource_stats.avg_cpu_percentage, 0.0)
                    self.assertEqual(_e, _m, stats.resource_stats.network_read_gi_b, 0.0)
                    self.assertEqual(_e, _m, stats.resource_stats.disk_write_gi_b, 0.0)
                    self.assertEqual(_e, _m, stats.resource_stats.peak_disk_gi_b, 0.0)

                _m = "Test Get Pool Usage Info"  #TODO: Test with real usage metrics
                LOG.debug('TODO: ' + _m)
                response = self.assertList(_e, _m, self.batch_client_sk.pool.list_usage_metrics)
                #TODO: Assert
        self.assertSuccess(_e)

    @record
    def test_batch_compute_nodes(self):
        _e = {}
        with BatchPool(self.live,
                       self.batch_client_sk,
                       'python_test_pool_3',
                       target_dedicated_nodes=2) as pool_id:

            _m = "Test List Compute Nodes"
            LOG.debug(_m)
            nodes = self.assertList(_e, _m, self.batch_client_sk.compute_node.list, pool_id)
            self.assertEqual(_e, _m, len(nodes), 2)
            node_ids = [n.id for n in nodes]

            _m = "Test Get Compute Node"
            LOG.debug(_m)
            node = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.get, pool_id, node_ids[0])
            self.assertTrue(_e, _m, isinstance(node, batch.models.ComputeNode))
            if node:
                self.assertEqual(_e, _m, node.state, batch.models.ComputeNodeState.idle)
                self.assertEqual(_e, _m, node.scheduling_state, batch.models.SchedulingState.enabled)
                self.assertTrue(_e, _m, node.is_dedicated)

            _m = "Test Add User"
            LOG.debug(_m)
            user = batch.models.ComputeNodeUser('BatchPythonSDKUser', password='kt#_gahr!@aGERDXA', is_admin=False)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.add_user, pool_id, node_ids[0], user)
            self.assertIsNone(_e, _m, response)

            _m = "Test Update User"
            LOG.debug(_m)
            user = batch.models.NodeUpdateUserParameter(password='liilef#$DdRGSa_ewkjh')
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.update_user,
                                       pool_id, node_ids[0], 'BatchPythonSDKUser', user)
            self.assertIsNone(_e, _m, response)

            _m = "Test Get RDP File"
            LOG.debug(_m)
            file_length = 0
            with io.BytesIO() as file_handle:
                response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.get_remote_desktop,
                                           pool_id, node_ids[0])
                if response:
                    for data in response:
                        file_length += len(data)
            self.assertTrue(_e, _m, file_length > 0)

            _m = "Test Delete User"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.delete_user,
                                       pool_id, node_ids[0], 'BatchPythonSDKUser')
            self.assertIsNone(_e, _m, response)

            _m = "Test Disable Scheduling"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.disable_scheduling,
                                      pool_id, node_ids[0])
            self.assertIsNone(_e, _m, response)

            _m = "Test Enable Scehduling"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.enable_scheduling, pool_id, node_ids[0])
            self.assertIsNone(_e, _m, response)

            _m = "Test List Files"
            LOG.debug(_m)
            files = self.assertList(_e, _m, self.batch_client_sk.file.list_from_compute_node, pool_id, node_ids[0])
            self.assertTrue(_e, _m, len(files) > 2)

            _m = "Test File Properties"
            LOG.debug('TODO: ' + _m)
            #props = self.batch_client_sk.file.get_properties_from_compute_node(pool_id, node_ids[0], '', raw=True)
            #self.assertTrue('Content-Length' in props.headers)
            #self.assertTrue('Content-Type'in props.headers)

            _m = "Test Get File"
            LOG.debug('TODO: ' + _m)
            #file_length = 0
            #with io.BytesIO() as file_handle:
            #    response = self.batch_client_sk.file.get_from_task(pool_id, node_ids[0], '')
            #    for data in response:
            #        file_length += len(data)
            #self.assertEqual(file_length, props.headers['Content-Length'])    

            _m = "Test Reboot Node"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.reboot,
                                       pool_id, node_ids[0])
            self.assertIsNone(_e, _m, response)

            _m = "Test Reimage Node"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.compute_node.reimage,
                                       pool_id, node_ids[1])
            self.assertIsNone(_e, _m, response)

            _m = "Test Remove Nodes"
            LOG.debug(_m)
            options = batch.models.NodeRemoveParameter(node_ids)
            response = self.assertRuns(_e, _m, self.batch_client_sk.pool.remove_nodes, pool_id, options)
            self.assertIsNone(_e, _m, response)
        self.assertSuccess(_e)

    @record
    def test_batch_jobs(self):
        _e = {}
        _m = "Test Add Application"
        LOG.debug(_m)
        application = self.assertRuns(_e, _m, self.batch_mgmt_client.application.create,
                                   AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id',
                                   allow_updated=True, display_name='my_application_name')
        self.assertTrue(_e, _m, isinstance(application, azure.mgmt.batch.models.Application))
        if application:
            self.assertEqual(_e, _m, application.id, 'my_application_id')
            self.assertEqual(_e, _m, application.display_name, 'my_application_name')
            self.assertEqual(_e, _m, application.allow_updates, True)

        _m = "Test Add Application Package"
        LOG.debug(_m)
        package_ref = self.assertRuns(_e, _m, self.batch_mgmt_client.application_package.create,
                                      AZURE_RESOURCE_GROUP, AZURE_BATCH_ACCOUNT, 'my_application_id', 'v1.0')
        self.assertTrue(_e, _m, isinstance(package_ref, azure.mgmt.batch.models.ApplicationPackage))

        users = [
            {'name': 'task-user', 'password': 'kt#_gahr!@aGERDXA',
             'elevation_level': batch.models.ElevationLevel.admin}
        ]
        image = batch.models.VirtualMachineConfiguration(
            node_agent_sku_id="batch.node.windows amd64",
            image_reference=batch.models.ImageReference(
                publisher="MicrosoftWindowsServer",
                offer="WindowsServer",
                sku="2016-Datacenter")
        )
        with BatchPool(self.live,
                       self.batch_client_sk,
                       'python_test_pool_4',
                       virtual_machine=image,
                       target_dedicated_nodes=1, user_accounts=users) as pool_id:

            _m = "Test Create Job"
            LOG.debug(_m)
            job = batch.models.JobAddParameter('python_test_job',
                                                batch.models.PoolInformation(pool_id=pool_id))
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.add, job)
            self.assertIsNone(_e, _m, response)

            LOG.debug("    wait for job to create...")
            self.sleep(10)

            _m = "Test Create Job with Auto Complete"
            LOG.debug(_m)
            job_with_auto_complete = batch.models.JobAddParameter(id='python_test_job_2',
                                                pool_info=batch.models.PoolInformation(pool_id=pool_id),
                                                on_all_tasks_complete='noAction',
                                                on_task_failure='performExitOptionsJobAction')
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.add, job_with_auto_complete)
            self.assertIsNone(_e, _m, response)


            LOG.debug("    wait for job to create...")
            self.sleep(10)

            _m = "Test Update Job"
            LOG.debug(_m)
            constraints = batch.models.JobConstraints(max_task_retry_count=3)
            options = batch.models.JobUpdateParameter(priority=500,
                                                        constraints=constraints,
                                                        pool_info=batch.models.PoolInformation(pool_id=pool_id))
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.update, 'python_test_job', options)
            self.assertIsNone(_e, _m, response)

            _m = "Test Patch Job"
            LOG.debug(_m)
            constraints = batch.models.JobConstraints(max_task_retry_count=1)
            options = batch.models.JobPatchParameter(priority=900,
                                                     constraints=constraints,
                                                     pool_info=batch.models.PoolInformation(pool_id=pool_id))
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.patch, 'python_test_job', options)
            self.assertIsNone(_e, _m, response)

            _m = "Test Get Job"
            LOG.debug(_m)
            job = self.assertRuns(_e, _m, self.batch_client_aad.job.get, 'python_test_job')
            self.assertTrue(_e, _m, isinstance(job, batch.models.CloudJob))
            if job:
                self.assertEqual(_e, _m, job.id, 'python_test_job')
                self.assertEqual(_e, _m, job.pool_info.pool_id, pool_id)
                self.assertEqual(_e, _m, job.constraints.max_task_retry_count, 1)

            _m = "Test List Jobs"
            LOG.debug(_m)
            jobs = self.assertList(_e, _m, self.batch_client_aad.job.list) 
            self.assertTrue(_e, _m, len(jobs) > 0)
            job_ids = [j.id for j in jobs]

            _m = "Test Job Disable"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.disable, 'python_test_job', 'requeue')
            self.assertIsNone(_e, _m, response)

            _m = "Test Job Enable"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.enable, 'python_test_job')
            self.assertIsNone(_e, _m, response)

            _m = "Test Create Task with Auto Complete and Auto User and Token Settings"
            LOG.debug(_m)
            auto_user = batch.models.AutoUserSpecification(
                scope=batch.models.AutoUserScope.task,
                elevation_level=batch.models.ElevationLevel.admin)
            conditions = batch.models.ExitConditions(default=batch.models.ExitOptions('terminate'),
                                                     exit_codes=[batch.models.ExitCodeMapping(code=1, exit_options=batch.models.ExitOptions('None'))])
            task = batch.models.TaskAddParameter(id='python_task_with_auto_complete',
                                                 command_line='cmd /c "echo hello world"',
                                                 user_identity={'auto_user': auto_user},
                                                 exit_conditions=conditions,
                                                 authentication_token_settings={'access': ['job']})
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job_2', task)
            self.assertIsNone(_e, _m, response)

            _m = "Test Get Task with Auto Complete and Auto User and Token Settings"
            LOG.debug(_m)
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job_2', 'python_task_with_auto_complete')
            self.assertTrue(_e, _m, isinstance(task, batch.models.CloudTask))
            if task:
                self.assertEqual(_e, _m, task.exit_conditions.default.job_action.value, 'terminate')
                self.assertEqual(_e, _m, task.exit_conditions.exit_codes[0].code, 1)
                self.assertEqual(_e, _m, task.user_identity.auto_user.scope.value, 'task')
                self.assertEqual(_e, _m, task.user_identity.auto_user.elevation_level.value, 'admin')
                self.assertEqual(_e, _m, task.authentication_token_settings.access[0].value, 'job')
                self.assertEqual(_e, _m, task.exit_conditions.exit_codes[0].exit_options.job_action.value, 'none')

            _m = "Test Create Task with Application Package and Run-As-User"
            LOG.debug(_m)
            task = batch.models.TaskAddParameter('python_task_with_app_package',
                                                 'cmd /c "echo hello world"',
                                                 user_identity={'user_name': 'task-user'},
                                                 application_package_references=[batch.models.ApplicationPackageReference('my_application_id')])
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job', task)
            self.assertIsNone(_e, _m, response)

            _m = "Test Get Task with Application Package and Run-As-User"
            LOG.debug(_m)
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job', 'python_task_with_app_package')

            self.assertTrue(_e, _m, isinstance(task, batch.models.CloudTask))
            if task:
                self.assertEqual(_e, _m, task.id, 'python_task_with_app_package')
                self.assertEqual(_e, _m, task.user_identity.user_name, 'task-user')
                self.assertEqual(_e, _m, task.application_package_references[0].application_id, 'my_application_id')

            response = self.assertRuns(_e, _m, self.batch_client_sk.task.delete, 'python_test_job', 'python_task_with_app_package')
            self.assertIsNone(_e, _m, response)

            _m = "Test Create Task with Output Files"
            LOG.debug(_m)
            container_url = self._generate_container_sas_token()
            outputs = [
                batch.models.OutputFile(
                    file_pattern="../stdout.txt",
                    destination=batch.models.OutputFileDestination(
                        container=batch.models.OutputFileBlobContainerDestination(
                            container_url=container_url, path="taskLogs/output.txt")),
                    upload_options=batch.models.OutputFileUploadOptions(
                        upload_condition=batch.models.OutputFileUploadCondition.task_completion)),
                batch.models.OutputFile(
                    file_pattern="../stderr.txt",
                    destination=batch.models.OutputFileDestination(
                        container=batch.models.OutputFileBlobContainerDestination(
                            container_url=container_url, path="taskLogs/error.txt")),
                    upload_options=batch.models.OutputFileUploadOptions(
                        upload_condition=batch.models.OutputFileUploadCondition.task_failure)),
            ]

            task = batch.models.TaskAddParameter('python_task_1', 'cmd /c "echo hello world"',
                                                 output_files=outputs)
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job_2', task)
            self.assertIsNone(_e, _m, response)

            _m = "Test for Complete Output Files"
            LOG.debug(_m)
            task = self.batch_client_sk.task.get('python_test_job_2', 'python_task_1')
            if self.live and task:
                while task.state.value != 'completed':
                    time.sleep(5)
                    task = self.batch_client_sk.task.get('python_test_job_2', 'python_task_1')
                outputs = list(self.storage_data_client.list_blobs(OUTPUT_CONTAINER))
                self.assertEqual(_e, _m, len(outputs), 1)
                if outputs:
                    self.assertEqual(_e, _m, outputs[0].name, "taskLogs/output.txt")

            _m = "Test Terminate Task"
            LOG.debug(_m)
            task = batch.models.TaskAddParameter('python_task_1', 'cmd /c "echo hello world"')
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job', task)
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.terminate, 
                                       'python_test_job', 'python_task_1')
            self.assertIsNone(_e, _m, response)
            
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job', 'python_task_1')
            self.assertTrue(_e, _m, isinstance(task, batch.models.CloudTask))
            if task:
                self.assertEqual(_e, _m, task.state.value, 'completed')

            _m = "Test Reactivate Task"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.reactivate,
                                       'python_test_job', 'python_task_1')
            self.assertIsNone(_e, _m, response)
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job', 'python_task_1')

            self.assertTrue(_e, _m, isinstance(task, batch.models.CloudTask))
            if task:
                self.assertEqual(_e, _m, task.state.value, 'active')

            _m = "Test Task Failure"
            LOG.debug(_m)
            task = batch.models.TaskAddParameter('python_task_bad', 'bad command')
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job_2', task)
            self.assertIsNone(_e, _m, response)
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job_2', 'python_task_bad')
            if self.live and task:
                while task.state.value != 'completed':
                    time.sleep(5)
                    task = self.batch_client_sk.task.get('python_test_job_2', 'python_task_bad')
                self.assertEqual(_e, _m, task.execution_info.result, batch.models.TaskExecutionResult.failure)
                self.assertEqual(_e, _m, task.execution_info.failure_info.category, batch.models.ErrorCategory.user_error)
                self.assertEqual(_e, _m, task.execution_info.failure_info.code, 'CommandProgramNotFound')

            _m = "Test Update Task"
            LOG.debug(_m)
            task = batch.models.TaskAddParameter('python_task_2', 'cmd /c "echo hello world"')
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add, 'python_test_job', task)
            constraints = batch.models.TaskConstraints(max_task_retry_count=1)
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.update,
                                       'python_test_job', 'python_task_2', constraints=constraints)
            self.assertIsNone(_e, _m, response)

            _m = "Test Add Task Collection"
            LOG.debug(_m)
            tasks = []
            for i in range(3, 6):
                tasks.append(batch.models.TaskAddParameter('python_task_{}'.format(i), 'cmd /c "echo hello world"'))
            response = self.assertRuns(_e, _m, self.batch_client_sk.task.add_collection, 'python_test_job', tasks)
            self.assertTrue(_e, _m, isinstance(response, batch.models.TaskAddCollectionResult))

            _m = "Test List Tasks"
            LOG.debug(_m)
            tasks = self.assertList(_e, _m, self.batch_client_sk.task.list, 'python_test_job')
            self.assertEqual(_e, _m, len(tasks), 5)
            task_ids = [t.id for t in tasks]

            _m = "Test Get Task"
            LOG.debug(_m)
            task = self.assertRuns(_e, _m, self.batch_client_sk.task.get, 'python_test_job', 'python_task_2')
            self.assertTrue(_e, _m, isinstance(task, batch.models.CloudTask))
            if task:
                self.assertEqual(_e, _m, task.constraints.max_task_retry_count, 1)
                self.assertEqual(_e, _m, task.id, 'python_task_2')
                self.assertEqual(_e, _m, task.command_line, 'cmd /c "echo hello world"')

            _m = "Test Get Subtasks"  #TODO: Test with actual subtasks
            LOG.debug('TODO: ' + _m)
            subtasks = self.assertRuns(_e, _m, self.batch_client_sk.task.list_subtasks,
                                       'python_test_job', 'python_task_2')
            #TODO: Assert

            LOG.debug("    wait for job to finish...")
            self.sleep(30)

            _m = "Test List Files"
            LOG.debug(_m)
            files = self.assertList(_e, _m, self.batch_client_sk.file.list_from_task,
                                    'python_test_job', 'python_task_2')
            self.assertTrue(_e, _m, len(files) > 2)

            _m = "Test Get File Properties"
            LOG.debug(_m)
            props = self.assertRuns(_e, _m, self.batch_client_sk.file.get_properties_from_task,
                                    'python_test_job', 'python_task_2', 'stdout.txt', raw=True)
            if props:
                self.assertTrue(_e, _m, 'Content-Length' in props.headers)
                self.assertTrue(_e, _m, 'Content-Type'in props.headers)

            _m = "Test Task File"
            LOG.debug(_m)
            file_length = 0
            with io.BytesIO() as file_handle:
                response = self.assertRuns(_e, _m, self.batch_client_sk.file.get_from_task,
                                           'python_test_job', 'python_task_2', 'stdout.txt')
                if response:
                    for data in response:
                        file_length += len(data)
            self.assertTrue(_e, _m, file_length > 0)

            _m = "Test Prep and Release Task"  #TODO: Test with actual prep and release tasks
            LOG.debug('TODO: ' + _m)
            response = self.assertRuns(_e, _m, self.batch_client_aad.job.list_preparation_and_release_task_status,
                                       'python_test_job')
            #TODO: Assert

            _m = "Test Delete File"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.file.delete_from_task,
                                       'python_test_job', 'python_task_2', 'stdout.txt')
            self.assertIsNone(_e, _m, response)
            
            _m = "Test Delete Task"
            LOG.debug(_m)
            for id in task_ids:
                response = self.assertRuns(_e, _m, self.batch_client_sk.task.delete, 'python_test_job', id)
                self.assertIsNone(_e, _m, response)

            _m = "Test Terminate Job"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job.terminate, 'python_test_job')
            self.assertIsNone(_e, _m, response)

            _m = "Test Delete Job"
            LOG.debug(_m)
            for id in job_ids:
                response = self.assertRuns(_e, _m, self.batch_client_sk.job.delete, id)
                self.assertIsNone(_e, _m, response)

            _m = "Test Job Lifetime Statistics"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job.get_all_lifetime_statistics)
        self.assertSuccess(_e)

    @record
    def test_batch_job_schedules(self):
        _e = {}
        with BatchPool(self.live,
                       self.batch_client_sk,
                       'python_test_pool_5',
                       target_dedicated_nodes=2) as pool_id:

            _m = "Test Create Job Schedule"
            LOG.debug(_m)
            job_spec = batch.models.JobSpecification(pool_info=batch.models.PoolInformation(pool_id))
            schedule = batch.models.Schedule(start_window=datetime.timedelta(hours=1),
                                             recurrence_interval=datetime.timedelta(days=1))
            params = batch.models.JobScheduleAddParameter('python_test_schedule', schedule, job_spec)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.add, params)
            self.assertIsNone(_e, _m, response)

            _m = "Test List Job Schedules"
            LOG.debug(_m)
            schedules = self.assertList(_e, _m, self.batch_client_sk.job_schedule.list)
            self.assertTrue(_e, _m, len(schedules) > 0)

            _m = "Test Get Job Schedule"
            LOG.debug(_m)
            schedule = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.get, 'python_test_schedule')
            self.assertTrue(_e, _m, isinstance(schedule, batch.models.CloudJobSchedule))
            if schedule:
                self.assertEqual(_e, _m, schedule.id, 'python_test_schedule')
                self.assertEqual(_e, _m, schedule.state, batch.models.JobScheduleState.active)

            _m = "Test Job Schedule Exists"
            LOG.debug(_m)
            exists = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.exists, 'python_test_schedule')
            self.assertTrue(_e, _m, exists)

            _m = "Test List Jobs from Schedule"
            LOG.debug(_m)
            jobs = self.assertList(_e, _m, self.batch_client_sk.job.list_from_job_schedule, 'python_test_schedule')
            self.assertTrue(_e, _m, len(jobs) > 0)
            if jobs:
                self.assertRuns(_e, _m, self.batch_client_sk.job.delete, jobs[0].id)

            _m = "Test Disable Job Schedule"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.disable, 'python_test_schedule')
            self.assertIsNone(_e, _m, response)

            _m = "Test Enable Job Schedule"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.enable, 'python_test_schedule')
            self.assertIsNone(_e, _m, response)

            _m = "Test Update Job Schedule"
            LOG.debug(_m)
            job_spec = batch.models.JobSpecification(pool_info=batch.models.PoolInformation(pool_id))
            schedule = batch.models.Schedule(recurrence_interval=datetime.timedelta(hours=10))
            params = batch.models.JobScheduleUpdateParameter(schedule, job_spec)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.update, 'python_test_schedule', params)
            self.assertIsNone(_e, _m, response)

            _m = "Test Patch Job Schedule"
            LOG.debug(_m)
            schedule = batch.models.Schedule(recurrence_interval=datetime.timedelta(hours=5))
            params = batch.models.JobSchedulePatchParameter(schedule)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.patch, 'python_test_schedule', params)
            self.assertIsNone(_e, _m, response)

            _m = "Test Terminate Job Schedule"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.terminate, 'python_test_schedule')
            self.assertIsNone(_e, _m, response)

            _m = "Test Delete Job Schedule"
            LOG.debug(_m)
            response = self.assertRuns(_e, _m, self.batch_client_sk.job_schedule.delete, 'python_test_schedule')
            self.assertIsNone(_e, _m, response)
        self.assertSuccess(_e)


class BatchPool(object):

    def __init__(self, live, client, id, **kwargs):
        self.live = live
        self.client = client
        self.id = id
        self.kwargs = kwargs
        self.nodes = kwargs.get('target_dedicated_nodes', 0)
        self.timeout = datetime.datetime.now() + datetime.timedelta(minutes=20)

    def __enter__(self):
        response = None
        if self.live:
            try:
                try:
                    pool_config = self.kwargs.pop("virtual_machine")
                    pool = batch.models.PoolAddParameter(self.id, 'standard_a1', virtual_machine_configuration=pool_config, **self.kwargs)
                except KeyError:
                    pool_config = batch.models.CloudServiceConfiguration('4')
                    pool = batch.models.PoolAddParameter(self.id, 'small', cloud_service_configuration=pool_config, **self.kwargs)
                response = self.client.pool.add(pool)
                if self.live:
                    LOG.debug("    waiting for pool to be ready...")
                    time.sleep(30)

                    ready_nodes = []
                    options = batch.models.ComputeNodeListOptions(select='id,state')
                    while len(ready_nodes) != self.nodes:
                        if datetime.datetime.now() > self.timeout:
                            raise AssertionError("Nodes failed to become idle in 15 minutes")

                        LOG.debug("    waiting for {} nodes to be ready...".format(self.nodes))
                        nodes = self.client.compute_node.list(self.id, options)
                        ready_nodes = [n for n in nodes if n.state == batch.models.ComputeNodeState.idle]
                        time.sleep(30)

            except Exception as err:
                try:
                    self.client.pool.delete(self.id)
                except:
                    pass
                raise AssertionError("Failed to create test pool: {}".format(err))
           
        if response is None:
            return self.id
        else:
            raise AssertionError('Failed to create test pool') 

    def __exit__(self, type, value, traceback):
        if self.live:
            try:
                self.client.pool.delete(self.id)
            except:
                pass


if __name__ == '__main__':
    unittest.main()
