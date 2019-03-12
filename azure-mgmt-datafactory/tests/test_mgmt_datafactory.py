# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time
from datetime import datetime, date, timedelta

from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

raise unittest.SkipTest("Skipping all tests")

class MgmtAdfTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAdfTest, self).setUp()
        self._adf_client = self.create_mgmt_client(
            DataFactoryManagementClient,
            base_url='https://api-dogfood.resources.windows-int.net/'
        )

    def clean_datafactory(self, df_name, resource_group):
        self._adf_client.factories.delete(resource_group.name, df_name)

    def create_datafactory(self, df_name, resource_group, location):
        df_resource = Factory(location=location)
        return self._adf_client.factories.create_or_update(resource_group.name, df_name, df_resource)

    def create_azureblob_linkedservice(self, df_name, ls_name, resource_group):
        s = SecureString('some connection string')
        ls_as = AzureStorageLinkedService(connection_string=s)
        return self._adf_client.linked_services.create_or_update(resource_group.name, df_name, ls_name, ls_as)

    def create_azureblob_dataset(self, df_name, ls_name, ds_name, resource_group):
        tx_f = TextFormat()
        ls_for_ds = LinkedServiceReference(ls_name)
        ds_ab = AzureBlobDataset(ls_for_ds, format=tx_f)
        return self._adf_client.datasets.create_or_update(resource_group.name, df_name, ds_name, ds_ab)

    def create_output_dataset(self, df_name, ls_name, ds_name, resource_group):
        tx_f = TextFormat()
        fileName_expr=Expression("'OutputBlobName'")
        ls_for_ds = LinkedServiceReference(ls_name)
        ds_ab = AzureBlobDataset(ls_for_ds, folder_path='entitylogs', file_name='OutputBlobName', format=tx_f)
        return self._adf_client.datasets.create_or_update(resource_group.name, df_name, ds_name, ds_ab)

    def create_pipeline_with_run(self, df_name, p_name, ls_name, dsin_name, dsout_name, act_name, resource_group):
        ls = self.create_azureblob_linkedservice(df_name, ls_name, resource_group)
        dsin = self.create_azureblob_dataset(df_name, ls_name, dsin_name, resource_group)
        dsout = self.create_output_dataset(df_name, ls_name, dsout_name, resource_group)
        act = self.create_copyactivity_blobtoblob(act_name, dsin_name, dsout_name, resource_group)
        param = ParameterSpecification('String')
        p_params = {'OutputBlobName': param}
        self.create_pipeline(df_name, [act], p_name, p_params, resource_group)
        return self._adf_client.pipelines.create_run(resource_group.name, df_name, p_name,
            {
               "OutputBlobName": "adf1"
            }
        )

    def create_lookup_pipeline_with_run(self, df_name, p_name, ls_name, ds_name, act_name, resource_group):
        ls = self.create_azureblob_linkedservice(df_name, ls_name, resource_group)
        ds = self.create_azureblob_dataset(df_name, ls_name, ds_name, resource_group)
        act = self.create_lookupactivity_blob(act_name, ds_name)
        param = ParameterSpecification('String')
        p_params = {'Dummy': param}
        self.create_pipeline(df_name, [act], p_name, p_params, resource_group)
        return self._adf_client.pipelines.create_run(resource_group.name, df_name, p_name,
            {
               "Dummy": "dummy"
            }
        )

    def create_get_metadata_pipeline_with_run(self, df_name, p_name, ls_name, ds_name, act_name, resource_group):
        ls = self.create_azureblob_linkedservice(df_name, ls_name, resource_group)
        ds = self.create_azureblob_dataset(df_name, ls_name, ds_name, resource_group)
        act = self.create_getmetadataactivity_blob(act_name, ds_name)
        param = ParameterSpecification('String')
        p_params = {'Dummy': param}
        self.create_pipeline(df_name, [act], p_name, p_params, resource_group)
        return self._adf_client.pipelines.create_run(resource_group.name, df_name, p_name,
            {
               "Dummy": "dummy"
            }
        )

    def wait_for_factory(self, df, resource_group):
        if not self.is_playback():
            while df.provisioning_state != 'Succeeded':
                df = self._adf_client.factories.get(resource_group.name, df.name)
                time.sleep(1)

    def create_copyactivity_blobtoblob(self, act_name, dsin_name, dsout_name, resource_group):
        bso = BlobSource()
        bsi = BlobSink()
        dsin_ref = DatasetReference(dsin_name)
        dsOut_ref = DatasetReference(dsout_name)
        return CopyActivity(act_name, inputs=[dsin_ref], outputs=[dsOut_ref], source=bso, sink=bsi)

    def create_lookupactivity_blob(self, act_name, ds_name):
        bso = BlobSource()
        ds_ref = DatasetReference(ds_name)
        return LookupActivity(act_name, source=bso, dataset=ds_ref)

    def create_getmetadataactivity_blob(self, act_name, ds_name):
        ds_ref = DatasetReference(ds_name)
        return GetMetadataActivity(act_name, field_list = [], dataset=ds_ref)

    def create_pipeline(self, df_name, act, p_name, p_params, resource_group):
        p_obj = PipelineResource(activities=act, parameters=p_params)
        return self._adf_client.pipelines.create_or_update(resource_group.name, df_name, p_name, p_obj)

    def create_integrationruntime(self, df_name, ir_name, resource_group):
        ir_properties = SelfHostedIntegrationRuntime()
        return self._adf_client.integration_runtimes.create_or_update(resource_group.name, df_name, ir_name, ir_properties)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_datafactory_create(self, resource_group, location):
        df_name = 'testdfcreate'
        df = self.create_datafactory(df_name, resource_group, location)
        df1 = self._adf_client.factories.get(resource_group.name, df_name)
        self.assertTrue(df.id == df1.id)
        self.wait_for_factory(df, resource_group)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_get_nonexisitng_datafactory(self, resource_group, location):
        df_name = 'testdfnonexist'
        exceptionhappened = False
        try:
            df = self._adf_client.factories.get(resource_group.name, df_name)
        except ErrorResponseException:
            exceptionhappened = True
        self.assertTrue(exceptionhappened)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_dataset_create(self, resource_group, location):
        df_name = 'testdscreate'
        ls_name = 'ls1'
        ds_name = 'ds1'
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        ls = self.create_azureblob_linkedservice(df_name, ls_name, resource_group)
        ds = self.create_azureblob_dataset(df_name, ls_name, ds_name, resource_group)
        ds1 = self._adf_client.datasets.get(resource_group.name, df_name, ds_name)
        self.assertTrue(ds.id == ds1.id)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_pipeline_create(self, resource_group, location):
        df_name = 'testpipelinecreate'
        ls_name = 'ls1'
        dsin_name = 'dsin'
        dsout_name = 'dsout'
        act_name = 'act1'
        p_name = 'p1'
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        run = self.create_pipeline_with_run(df_name, p_name, ls_name, dsin_name, dsout_name, act_name, resource_group)
        self.assertTrue(run is not None)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_lookup_pipeline_create(self, resource_group, location):
        df_name = 'testlookuppipeline'
        ls_name = 'ls1'
        ds_name = 'ds1'
        act_name = 'act1'
        p_name = 'p1'
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        run = self.create_lookup_pipeline_with_run(df_name, p_name, ls_name, ds_name, act_name, resource_group)
        self.assertTrue(run is not None)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_get_metadata_pipeline_create(self, resource_group, location):
        df_name = 'testmetadatapipeline'
        ls_name = 'ls1'
        ds_name = 'ds1'
        act_name = 'act1'
        p_name = 'p1'
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        run = self.create_get_metadata_pipeline_with_run(df_name, p_name, ls_name, ds_name, act_name, resource_group)
        self.assertTrue(run is not None)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_run_monitoring(self, resource_group, location):
        df_name = 'testmonitoring'
        ls_name = 'ls'
        dsin_name = 'dsin'
        dsout_name = 'dsout'
        act_name = 'act1'
        p_name = 'p1'
        start_time = datetime(2017, 9, 10, 12, 0, 0)
        end_time = (start_time + timedelta(days=3600))
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        run = self.create_pipeline_with_run(df_name, p_name, ls_name, dsin_name, dsout_name, act_name, resource_group)
        query_max_count = 10
        i = 0
        while True and i < query_max_count:
            filter = PipelineRunFilterParameters(start_time.isoformat(), end_time.isoformat(), filters=[])
            pipeline_runs = self._adf_client.pipeline_runs.query_by_factory(resource_group.name, df_name, filter).value
            if pipeline_runs:
                break
            time.sleep(15)
            i += 1

        self.assertTrue(any(elt.run_id == run.run_id for elt in pipeline_runs))
        i = 0
        while True and i < query_max_count:
            act_runs = list(self._adf_client.activity_runs.list_by_pipeline_run(resource_group.name, df_name, run.run_id, start_time.isoformat(), end_time.isoformat()))
            if act_runs:
                break
            time.sleep(15)
            i += 1

        self.assertTrue(any(elt.pipeline_run_id == run.run_id for elt in act_runs))
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_integrationruntime_regeneratekey(self, resource_group, location):
        df_name = 'testirregeneratekey'
        ir_name = 'ir1'
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)
        ir = self.create_integrationruntime(df_name, ir_name, resource_group)
        oldkey = self._adf_client.integration_runtimes.list_auth_keys(resource_group.name, df_name, ir_name).auth_key1
        newkey = self._adf_client.integration_runtimes.regenerate_auth_key(resource_group.name, df_name, ir_name, key_name='authKey1').auth_key1
        self.assertTrue(oldkey != newkey)
        self.clean_datafactory(df_name, resource_group)

    @ResourceGroupPreparer(location='eastus2', name_prefix='adfpythontests')
    def test_integrationruntime_create(self, resource_group, location):
        df_name = "testircreate"
        ir_name = "ir1"
        df = self.create_datafactory(df_name, resource_group, location)
        self.wait_for_factory(df, resource_group)

        ir = self.create_integrationruntime(df_name, ir_name, resource_group)
        self.assertTrue(ir_name == ir.name)

        ir_status = self._adf_client.integration_runtimes.get_status(resource_group.name, df_name, ir_name)
        self.assertTrue(ir_name == ir_status.name)

        self.clean_datafactory(df_name, resource_group)

if __name__ == '__main__':
    unittest.main()
