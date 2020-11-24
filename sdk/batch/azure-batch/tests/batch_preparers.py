from collections import namedtuple
import io
import os
import requests
import time

import azure.mgmt.batch
from azure.mgmt.batch import models
import azure.batch
from azure.batch.batch_auth import SharedKeyCredentials

from azure_devtools.scenario_tests.preparers import (
    AbstractPreparer,
    SingleValueReplacer,
)
from azure_devtools.scenario_tests.exceptions import AzureTestError

from devtools_testutils import AzureMgmtPreparer, ResourceGroupPreparer, FakeResource
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

BATCH_ACCOUNT_PARAM = 'batch_account'
STORAGE_ACCOUNT_PARAM = 'storage_account'
FakeAccount = namedtuple(
    'FakeResource',
    ['name', 'account_endpoint']
)

class AccountPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='batch',
                 location='westus',
                 parameter_name=BATCH_ACCOUNT_PARAM,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None):
        super(AccountPreparer, self).__init__(name_prefix, 24,
                                              disable_recording=disable_recording,
                                              playback_fake_resource=playback_fake_resource,
                                              client_kwargs=client_kwargs)
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.creds_parameter = 'credentials'
        self.parameter_name_for_location='location'
        self.resource_moniker=name_prefix

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = 'To create a batch account a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_storage_account(self, **kwargs):
        return kwargs.get(STORAGE_ACCOUNT_PARAM)

    def _add_app_package(self, group_name, batch_name):
        self.client.application.create(
            group_name, batch_name, 'application_id')
        package_ref = self.client.application_package.create(
            group_name, batch_name, 'application_id', 'v1.0')
        try:
            with io.BytesIO(b'Hello World') as f:
                headers = {'x-ms-blob-type': 'BlockBlob'}
                upload = requests.put(package_ref.storage_url, headers=headers, data=f.read())
                if not upload:
                    raise ValueError('Upload failed: {!r}'.format(upload))
        except Exception as err:
            raise AzureTestError('Failed to upload test package: {}'.format(err))
        else:
            self.client.application_package.activate(group_name, batch_name, 'application_id', 'v1.0', 'zip')

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(
                azure.mgmt.batch.BatchManagementClient)
            group = self._get_resource_group(**kwargs)
            batch_account = models.BatchAccountCreateParameters(
                location=self.location,
            )
            storage = self._get_storage_account(**kwargs)
            if storage:
                storage_resource = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}'.format(
                    self.test_class_instance.settings.SUBSCRIPTION_ID,
                    group.name,
                    storage.name
                )
                batch_account.auto_storage=models.AutoStorageBaseProperties(storage_account_id=storage_resource)
            account_setup = self.client.batch_account.create(
                group.name,
                name,
                batch_account)
            self.resource = account_setup.result()
            keys = self.client.batch_account.get_keys(
                group.name,
                name
            )
            credentials = SharedKeyCredentials(
                keys.account_name,
                keys.primary)
            if storage:
                self._add_app_package(group.name, name)
            self.test_class_instance.scrubber.register_name_pair(
                name,
                self.resource_moniker
            )
        else:
            self.resource = FakeAccount(
                name=name,
                account_endpoint="https://{}.{}.batch.azure.com".format(name, self.location))
            credentials = SharedKeyCredentials(
                name,
                'ZmFrZV9hY29jdW50X2tleQ==')
        return {
            self.parameter_name: self.resource,
            self.creds_parameter: credentials
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            deleting = self.client.batch_account.delete(group.name, name)
            try:
                deleting.wait()
            except:
                pass


class PoolPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='',
                 size=0,
                 os='Linux',
                 config='iaas',
                 parameter_name='batch_pool',
                 location=None,
                 resource_group_parameter_name=RESOURCE_GROUP_PARAM,
                 batch_account_parameter_name=BATCH_ACCOUNT_PARAM,
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None):
        super(PoolPreparer, self).__init__(name_prefix, 24,
                                           disable_recording=disable_recording,
                                           playback_fake_resource=playback_fake_resource,
                                           client_kwargs=client_kwargs)
        self.size = size
        self.os = os
        self.config = config
        self.resource_group_parameter_name = resource_group_parameter_name
        self.batch_account_parameter_name = batch_account_parameter_name
        self.parameter_name = parameter_name

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError:
            template = 'To create a batch account a resource group is required. Please add ' \
                       'decorator @{} in front of this storage account preparer.'
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__))

    def _get_batch_account(self, **kwargs):
        try:
            return kwargs[self.batch_account_parameter_name]
        except KeyError:
            template = 'To create a batch poool, a batch account is required. Please add ' \
                       'decorator @AccountPreparer in front of this pool preparer.'
            raise AzureTestError(template)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(
                azure.mgmt.batch.BatchManagementClient)
            group = self._get_resource_group(**kwargs)
            batch_account = self._get_batch_account(**kwargs)
            user = models.UserAccount(name='task-user', password='kt#_gahr!@aGERDXA', elevation_level=models.ElevationLevel.admin)
            vm_size = 'Standard_A1'

            if self.config == 'paas':
                vm_size = 'small'
                deployment = models.DeploymentConfiguration(
                    cloud_service_configuration=models.CloudServiceConfiguration(
                        os_family='5'))
            elif self.os == 'Windows':
                deployment = models.DeploymentConfiguration(
                    virtual_machine_configuration=models.VirtualMachineConfiguration(
                        image_reference=models.ImageReference(
                            publisher='MicrosoftWindowsServer',
                            offer='WindowsServer',
                            sku='2016-Datacenter-smalldisk'
                        ),
                        node_agent_sku_id='batch.node.windows amd64'))
            else:
                deployment = models.DeploymentConfiguration(
                    virtual_machine_configuration=models.VirtualMachineConfiguration(
                        image_reference=models.ImageReference(
                            publisher='Canonical',
                            offer='UbuntuServer',
                            sku='16.04-LTS'
                        ),
                        node_agent_sku_id='batch.node.ubuntu 16.04'))
            parameters = models.Pool(
                display_name="test_pool",
                vm_size=vm_size,
                user_accounts=[user],
                deployment_configuration=deployment,
                scale_settings=models.ScaleSettings(
                    fixed_scale=models.FixedScaleSettings(
                        target_dedicated_nodes=self.size
                    )
                )
            )

            pool_setup = self.client.pool.create(
                group.name, batch_account.name, name, parameters)
            self.resource = pool_setup.result()
            while (self.resource.allocation_state != models.AllocationState.steady 
                    and self.resource.current_dedicated_nodes < self.size):
                time.sleep(10)
                self.resource = self.client.pool.get(group.name, batch_account.name, name)
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            account = self._get_batch_account(**kwargs)
            self.client.pool.delete(group.name, account.name, name)


class JobPreparer(AzureMgmtPreparer):
    def __init__(self,
                 name_prefix='batch',
                 parameter_name='batch_job',
                 batch_account_parameter_name=BATCH_ACCOUNT_PARAM,
                 batch_credentials_parameter_name='credentials',
                 batch_pool_parameter_name='batch_pool',
                 disable_recording=True, playback_fake_resource=None,
                 client_kwargs=None, **extra_args):
        super(JobPreparer, self).__init__(name_prefix, 24,
                                          disable_recording=disable_recording,
                                          playback_fake_resource=playback_fake_resource,
                                          client_kwargs=client_kwargs)
        self.parameter_name = parameter_name
        self.batch_account_parameter_name = batch_account_parameter_name
        self.batch_credentials_parameter_name = batch_credentials_parameter_name
        self.batch_pool_parameter_name = batch_pool_parameter_name
        self.extra_args = extra_args
        self.resource_moniker=name_prefix

    def _get_batch_client(self, **kwargs):
        try:
            account = kwargs[self.batch_account_parameter_name]
            credentials = kwargs[self.batch_credentials_parameter_name]
            return azure.batch.BatchServiceClient(
                credentials, batch_url='https://' + account.account_endpoint)
        except KeyError:
            template = 'To create a batch job, a batch account is required. Please add ' \
                       'decorator @AccountPreparer in front of this job preparer.'
            raise AzureTestError(template)

    def _get_batch_pool_id(self, **kwargs):
        try:
            pool_id = kwargs[self.batch_pool_parameter_name].name
            return azure.batch.models.PoolInformation(pool_id=pool_id)
        except KeyError:
            auto_pool = azure.batch.models.AutoPoolSpecification(
                pool_lifetime_option=azure.batch.models.PoolLifetimeOption.job,
                pool=azure.batch.models.PoolSpecification(
                    vm_size='small',
                    cloud_service_configuration=azure.batch.models.CloudServiceConfiguration(
                        os_family='5'
                    )
                )
            )
            return azure.batch.models.PoolInformation(
                auto_pool_specification=auto_pool
            )

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self._get_batch_client(**kwargs)
            pool = self._get_batch_pool_id(**kwargs)
            self.resource = azure.batch.models.JobAddParameter(
                id=name,
                pool_info=pool,
                **self.extra_args
            )
            try:
                self.client.job.add(self.resource)
            except azure.batch.models.BatchErrorException as e:
                message = "{}:{} ".format(e.error.code, e.error.message)
                for v in e.error.values:
                    message += "\n{}: {}".format(v.key, v.value)
                raise AzureTestError(message)
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            self.client.job.delete(name)