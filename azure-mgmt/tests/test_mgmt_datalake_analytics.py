# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.datalake.analytics import account, job, catalog
import azure.mgmt.datalake.store
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase
import uuid


class MgmtDataLakeAnalyticsTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtDataLakeAnalyticsTest, self).setUp()
        self.region = 'East US 2' # this is the ADL produciton region for now.
        self.adls_account_client = self.create_mgmt_client(
            azure.mgmt.datalake.store.DataLakeStoreAccountManagementClient
        )
        self.adla_account_client = self.create_mgmt_client(
            azure.mgmt.datalake.analytics.account.DataLakeAnalyticsAccountManagementClient
        )
        # use create_basic_client for job and catalog because they don't take a subscriptionId as a parameter.
        self.adla_job_client = self.create_basic_client(
            azure.mgmt.datalake.analytics.job.DataLakeAnalyticsJobManagementClient,
            adla_job_dns_suffix = 'azuredatalakeanalytics.net'
        )
        self.adla_catalog_client = self.create_basic_client(
            azure.mgmt.datalake.analytics.catalog.DataLakeAnalyticsCatalogManagementClient,
            adla_catalog_dns_suffix = 'azuredatalakeanalytics.net'
        )

        # define all names
        self.adls_account_name = self.get_resource_name('pyarmadls2')
        self.job_account_name = self.get_resource_name('pyarmadla2')

        # construct the catalog script
        self.db_name = self.get_resource_name('adladb')
        self.table_name = self.get_resource_name('adlatable')
        self.tvf_name = self.get_resource_name('adlatvf')
        self.proc_name = self.get_resource_name('adlaproc')
        self.view_name = self.get_resource_name('adlaview')
        self.secret_name = self.get_resource_name('adlasecret')
        self.secret_pwd = self.get_resource_name('adlapwd')
        self.credential_name = self.get_resource_name('adlacredential')
        self.secret_cred_name = self.get_resource_name('adlasecretcred')
        self.credential_id = self.get_resource_name('adlacredid')
        self.schema_name = 'dbo'
        
        self.catalog_script = """DROP DATABASE IF EXISTS {0}; CREATE DATABASE {0}; 
CREATE TABLE {0}.dbo.{1}
(
        //Define schema of table
        UserId          int, 
        Start           DateTime, 
        Region          string, 
        Query           string, 
        Duration        int, 
        Urls            string, 
        ClickedUrls     string,
    INDEX idx1 
    CLUSTERED (Region ASC) 
    PARTITIONED BY (UserId) HASH (Region)
);

ALTER TABLE {0}.dbo.{1} ADD IF NOT EXISTS PARTITION (1);

DROP FUNCTION IF EXISTS {0}.dbo.{2};

CREATE FUNCTION {0}.dbo.{2}()
RETURNS @result TABLE
(
    s_date DateTime,
    s_time string,
    s_sitename string,
    cs_method string, 
    cs_uristem string,
    cs_uriquery string,
    s_port int,
    cs_username string, 
    c_ip string,
    cs_useragent string,
    cs_cookie string,
    cs_referer string, 
    cs_host string,
    sc_status int,
    sc_substatus int,
    sc_win32status int, 
    sc_bytes int,
    cs_bytes int,
    s_timetaken int
) 
AS
BEGIN

    @result = EXTRACT
        s_date DateTime,
        s_time string,
        s_sitename string,
        cs_method string,
        cs_uristem string,
        cs_uriquery string,
        s_port int,
        cs_username string,
        c_ip string,
        cs_useragent string,
        cs_cookie string,
        cs_referer string,
        cs_host string,
        sc_status int,
        sc_substatus int,
        sc_win32status int,
        sc_bytes int,
        cs_bytes int,
        s_timetaken int
    FROM @"/Samples/Data/WebLog.log"
    USING Extractors.Text(delimiter:' ');

RETURN;
END;
CREATE VIEW {0}.dbo.{3} 
AS 
    SELECT * FROM 
    (
        VALUES(1,2),(2,4)
    ) 
AS 
T(a, b);
CREATE PROCEDURE {0}.dbo.{4}()
AS BEGIN
  CREATE VIEW {0}.dbo.{3} 
  AS 
    SELECT * FROM 
    (
        VALUES(1,2),(2,4)
    ) 
  AS 
  T(a, b);
END;""".format(self.db_name, self.table_name, self.tvf_name, self.view_name, self.proc_name)

        # define all the job IDs to be used during execution
        if self.is_playback():
            self.cancel_id = self.fake_settings.ADLA_JOB_ID
            self.run_id = self.fake_settings.ADLA_JOB_ID
            self.catalog_id = self.fake_settings.ADLA_JOB_ID
            self.cred_create_id = self.fake_settings.ADLA_JOB_ID
            self.cred_drop_id = self.fake_settings.ADLA_JOB_ID
        else:
            self.cancel_id = str(uuid.uuid1())
            self.run_id = str(uuid.uuid1())
            self.catalog_id = str(uuid.uuid1())
            self.cred_create_id = str(uuid.uuid1())
            self.cred_drop_id = str(uuid.uuid1())

    def _scrub(self, val):
        val = super(MgmtDataLakeAnalyticsTest, self)._scrub(val)
        real_to_fake_dict = {
            self.cancel_id: self.fake_settings.ADLA_JOB_ID,
            self.run_id:  self.fake_settings.ADLA_JOB_ID,
            self.catalog_id:  self.fake_settings.ADLA_JOB_ID,
            self.cred_create_id: self.fake_settings.ADLA_JOB_ID,
            self.cred_drop_id: self.fake_settings.ADLA_JOB_ID
        }
        val = self._scrub_using_dict(val, real_to_fake_dict)
        return val

    def run_prereqs(self, create_job_acct = False, create_catalog = False):
        if not self.is_playback():
            self.create_resource_group()

        # construct ADLS account for use with the ADLA tests.
        params_create = azure.mgmt.datalake.store.models.DataLakeStoreAccount(
            location = self.region
        )
        result_create = self.adls_account_client.account.create(
            self.group_name,
            self.adls_account_name,
            params_create,
        )

        adls_account = result_create.result()
        
        # validation of the create
        self.assertEqual(adls_account.name, self.adls_account_name)

        # construct an ADLA account for use with catalog and job tests
        if(create_job_acct):
            params_create = azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccount(
                location = self.region,
                default_data_lake_store_account = self.adls_account_name,
                data_lake_store_accounts = [azure.mgmt.datalake.analytics.account.models.DataLakeStoreAccountInfo(name = self.adls_account_name)]
            )

            result_create = self.adla_account_client.account.create(
                self.group_name,
                self.job_account_name,
                params_create,
            )

            adla_account = result_create.result()
        
            # full validation of the create
            self.assertEqual(adla_account.name, self.job_account_name)

            # wait two minutes for the account to be fully provisioned with a queue.
            self.sleep(120)
    
            if(create_catalog):
                self.run_job_to_completion(self.job_account_name, self.catalog_id, self.catalog_script)

    def run_job_to_completion(self, adla_account_name, job_id, script_to_run):
        job_params = azure.mgmt.datalake.analytics.job.models.JobInformation(
            name = self.get_resource_name('testjob'),
            type = azure.mgmt.datalake.analytics.job.models.JobType.usql,
            degree_of_parallelism = 2,
            properties = azure.mgmt.datalake.analytics.job.models.USqlJobProperties(
                script = script_to_run,
            )
        )
        create_response = self.adla_job_client.job.create(
            adla_account_name,
            job_id,
            job_params
        )
        self.assertIsNotNone(create_response)
        max_wait_in_seconds = 180
        cur_wait_in_seconds = 0
        adla_job = self.adla_job_client.job.get(
            adla_account_name,
            job_id
        )
        self.assertIsNotNone(adla_job)
        while (adla_job.state != azure.mgmt.datalake.analytics.job.models.JobState.ended and cur_wait_in_seconds < max_wait_in_seconds):
            self.sleep(5)
            cur_wait_in_seconds += 5
            adla_job = self.adla_job_client.job.get(
                adla_account_name,
                job_id
            )
            self.assertIsNotNone(adla_job)

        self.assertTrue(cur_wait_in_seconds <= max_wait_in_seconds)
        self.assertTrue(adla_job.state == azure.mgmt.datalake.analytics.job.models.JobState.ended and adla_job.result == azure.mgmt.datalake.analytics.job.models.JobResult.succeeded,
                        'Job: {0} did not return success. Current job state: {1}. Actual result: {2}. Error (if any): {3}'.format(adla_job.job_id, adla_job.state, adla_job.result, adla_job.error_message))

    @record
    def test_adla_jobs(self):
        self.run_prereqs(create_job_acct= True, create_catalog = False)
        # define some static GUIDs
        job_to_submit = azure.mgmt.datalake.analytics.job.models.JobInformation(
            name = 'azure python sdk job test',
            degree_of_parallelism = 2,
            type = azure.mgmt.datalake.analytics.job.models.JobType.usql,
            properties = azure.mgmt.datalake.analytics.job.models.USqlJobProperties(
                script = 'DROP DATABASE IF EXISTS testdb; CREATE DATABASE testdb;'
            )
        )

        # submit a job
        create_response = self.adla_job_client.job.create(
            self.job_account_name,
            self.cancel_id,
            job_to_submit
        )
        
        self.assertIsNotNone(create_response)

        # cancel it right away
        self.adla_job_client.job.cancel(
            self.job_account_name,
            self.cancel_id
        )

        # validate that it was cancelled
        adla_job = self.adla_job_client.job.get(
            self.job_account_name,
            self.cancel_id
        )
        self.assertEqual(azure.mgmt.datalake.analytics.job.models.JobResult.cancelled, adla_job.result)
        self.assertIsNotNone(adla_job.error_message)

        # resubmit and allow to run to completion.
        self.run_job_to_completion(self.job_account_name, self.run_id, job_to_submit.properties.script)

        # list the jobs that have been submitted
        list_of_jobs = self.adla_job_client.job.list(self.job_account_name)
        self.assertIsNotNone(list_of_jobs)
        list_of_jobs = list(list_of_jobs)
        self.assertGreater(len(list_of_jobs), 1)

        # compile a job
        compile_response = self.adla_job_client.job.build(self.job_account_name, job_to_submit)
        self.assertIsNotNone(compile_response)

        # now compile a broken job and validate diagnostics.
        job_to_submit.properties.script = 'DROP DATABASE IF EXIST FOO; CREATE DATABASE FOO;'
        compile_response = self.adla_job_client.job.build(self.job_account_name, job_to_submit)
        self.assertIsNotNone(compile_response)

        self.assertEqual(1, len(list(compile_response.properties.diagnostics)))
        self.assertEqual(azure.mgmt.datalake.analytics.job.models.SeverityTypes.error, list(compile_response.properties.diagnostics)[0].severity)
        self.assertEqual(18, list(compile_response.properties.diagnostics)[0].column_number)
        self.assertEqual(22, list(compile_response.properties.diagnostics)[0].end)
        self.assertEqual(17, list(compile_response.properties.diagnostics)[0].start)
        self.assertEqual(1, list(compile_response.properties.diagnostics)[0].line_number)
        self.assertIn("E_CSC_USER_SYNTAXERROR", list(compile_response.properties.diagnostics)[0].message)

    @record
    def test_adla_catalog_items(self):
        self.run_prereqs(create_job_acct= True, create_catalog = True)
        
        # get all databases, there should be at least 2 and the specific database
        dbList = list(self.adla_catalog_client.catalog.list_databases(self.job_account_name))
        self.assertGreater(len(dbList), 1)
        dbMatch = [item for item in dbList if item.name == self.db_name]
        self.assertIsNotNone(dbMatch)
        self.assertEqual(len(dbMatch), 1)
        specific_db = self.adla_catalog_client.catalog.get_database(self.job_account_name, self.db_name)
        self.assertEqual(specific_db.name, dbMatch[0].name)

        # get the table list, table list from within a DB and specific table
        table_list = list(self.adla_catalog_client.catalog.list_tables(self.job_account_name, self.db_name, self.schema_name))
        self.assertGreater(len(table_list), 0)
        table_match = [item for item in table_list if item.name == self.table_name]
        self.assertIsNotNone(table_match)
        self.assertEqual(len(table_match), 1)
        
        # get table list in database
        table_list = list(self.adla_catalog_client.catalog.list_tables_by_database(self.job_account_name, self.db_name))
        self.assertGreater(len(table_list), 0)
        table_match = [item for item in table_list if item.name == self.table_name]
        self.assertIsNotNone(table_match)
        self.assertEqual(len(table_match), 1)

        # get specific table
        specific_table = self.adla_catalog_client.catalog.get_table(self.job_account_name, self.db_name, self.schema_name, self.table_name)
        self.assertEqual(specific_table.name, table_match[0].name)

        # get the TVF list and specific tvf
        tvf_list = list(self.adla_catalog_client.catalog.list_table_valued_functions(self.job_account_name, self.db_name, self.schema_name))
        self.assertGreater(len(tvf_list), 0)
        tvf_match = [item for item in tvf_list if item.name == self.tvf_name]
        self.assertIsNotNone(tvf_list)
        self.assertEqual(len(tvf_list), 1)
        
        # get tvf list by database
        tvf_list = list(self.adla_catalog_client.catalog.list_table_valued_functions_by_database(self.job_account_name, self.db_name))
        self.assertGreater(len(tvf_list), 0)
        tvf_match = [item for item in tvf_list if item.name == self.tvf_name]
        self.assertIsNotNone(tvf_list)
        self.assertEqual(len(tvf_list), 1)
        
        # get specific tvf
        specific_tvf = self.adla_catalog_client.catalog.get_table_valued_function(self.job_account_name, self.db_name, self.schema_name, self.tvf_name)
        self.assertEqual(specific_tvf.name, tvf_match[0].name)

        # get the views and specific view
        view_list = list(self.adla_catalog_client.catalog.list_views(self.job_account_name, self.db_name, self.schema_name))
        self.assertGreater(len(view_list), 0)
        view_match = [item for item in view_list if item.name == self.view_name]
        self.assertIsNotNone(view_match)
        self.assertEqual(len(view_match), 1)

        # get the views by database
        view_list = list(self.adla_catalog_client.catalog.list_views_by_database(self.job_account_name, self.db_name))
        self.assertGreater(len(view_list), 0)
        view_match = [item for item in view_list if item.name == self.view_name]
        self.assertIsNotNone(view_match)
        self.assertEqual(len(view_match), 1)

        # get specific view
        specific_view = self.adla_catalog_client.catalog.get_view(self.job_account_name, self.db_name, self.schema_name, self.view_name)
        self.assertEqual(specific_view.name, view_match[0].name)

        # get the list of procedures and the specific procedure we created
        proc_list = list(self.adla_catalog_client.catalog.list_procedures(self.job_account_name, self.db_name, self.schema_name))
        self.assertGreater(len(proc_list), 0)
        proc_match = [item for item in proc_list if item.name == self.proc_name]
        self.assertIsNotNone(proc_match)
        self.assertEqual(len(proc_match), 1)
        specific_proc = self.adla_catalog_client.catalog.get_procedure(self.job_account_name, self.db_name, self.schema_name, self.proc_name)
        self.assertEqual(specific_proc.name, proc_match[0].name)

        # get the partition list and a specific partition
        partition_list = list(self.adla_catalog_client.catalog.list_table_partitions(self.job_account_name, self.db_name, self.schema_name, self.table_name))
        self.assertGreater(len(partition_list), 0)
        partition_to_get = partition_list[0]
        specific_partition= self.adla_catalog_client.catalog.get_table_partition(self.job_account_name, self.db_name, self.schema_name, self.table_name, partition_to_get.name)
        self.assertEqual(specific_partition.name, partition_to_get.name)

        # get all the types
        type_list = list(self.adla_catalog_client.catalog.list_types(self.job_account_name, self.db_name, self.schema_name))
        self.assertIsNotNone(type_list)
        self.assertGreater(len(type_list), 0)
    
    @record
    def test_adla_catalog_credentials(self):
        self.run_prereqs(create_job_acct= True, create_catalog = True)
        self.adla_catalog_client.catalog.create_credential(
            self.job_account_name,
            self.db_name,
            self.credential_name,
            azure.mgmt.datalake.analytics.catalog.models.DataLakeAnalyticsCatalogCredentialCreateParameters(
                password = self.secret_pwd,
                uri = 'https://pyadlacredtest.contoso.com:443',
                user_id = self.credential_id
            )
        )
        
        # try to create the credential again.
        try:
            self.adla_catalog_client.catalog.create_credential(
                self.job_account_name,
                self.db_name,
                self.credential_name,
                azure.mgmt.datalake.analytics.catalog.models.DataLakeAnalyticsCatalogCredentialCreateParameters(
                    password = self.secret_pwd,
                    uri = 'https://pyadlacredtest.contoso.com:443',
                    user_id = self.generate_resource_name('newcredid')
                )
            )
            self.assertTrue(False, 'should not have made it here')
        except Exception as e:
            self.assertTrue(True)
        
        # get credential and ensure the response is not null
        cred_response = self.adla_catalog_client.catalog.get_credential(
            self.job_account_name,
            self.db_name,
            self.credential_name
        )
        self.assertIsNotNone(cred_response)
        self.assertIsNotNone(cred_response.name)

        # list credentials
        cred_list = list(self.adla_catalog_client.catalog.list_credentials(
            self.job_account_name,
            self.db_name
        ))
        
        self.assertIsNotNone(cred_list)
        self.assertGreater(len(cred_list), 0)
        specific_cred = [item for item in cred_list if item.name == self.credential_name]
        self.assertIsNotNone(specific_cred)
        self.assertEqual(specific_cred[0].name, cred_response.name)

        # delete the credential
        self.adla_catalog_client.catalog.delete_credential(
            self.job_account_name,
            self.db_name,
            self.credential_name
        )

        # try to get the credential and ensure it throws
        try:
            cred_response = self.adla_catalog_client.catalog.get_credential(
                self.job_account_name,
                self.db_name,
                self.credential_name
            )
            self.assertTrue(False, 'should not have made it here')
        except Exception as e:
            self.assertTrue(True)

    @record
    def test_adla_catalog_secret(self):
        self.run_prereqs(create_job_acct= True, create_catalog = True)

        self.adla_catalog_client.catalog.create_secret(
            self.job_account_name,
            self.db_name,
            self.secret_name,
            azure.mgmt.datalake.analytics.catalog.models.DataLakeAnalyticsCatalogSecretCreateOrUpdateParameters(
                password = self.secret_pwd,
                uri = 'https://adlapysecrettest.contoso.com:443'
            )
        )

        # try to create the secret again
        try:
            self.adla_catalog_client.catalog.create_secret(
                self.job_account_name,
                self.db_name,
                self.secret_name,
                azure.mgmt.datalake.analytics.catalog.models.DataLakeAnalyticsCatalogSecretCreateOrUpdateParameters(
                    password = self.secret_pwd,
                    uri = 'https://adlapysecrettest.contoso.com:443'
                )
            )
            self.assertTrue(False, 'should not have made it here')
        except Exception as e:
            self.assertTrue(True)

        # get the secret
        secret_response = self.adla_catalog_client.catalog.get_secret(
            self.job_account_name,
            self.db_name,
            self.secret_name
        )
        self.assertIsNotNone(secret_response)
        self.assertIsNotNone(secret_response.creation_time)

        # create a credential with the secret
        cred_script = 'USE {0}; CREATE CREDENTIAL {1} WITH USER_NAME = "scope@rkm4grspxa", IDENTITY = "{2}";'.format(self.db_name, self.secret_cred_name, self.secret_name)
        self.run_job_to_completion(self.job_account_name, self.cred_create_id, cred_script)

        # get the credential just created
        cred_response = self.adla_catalog_client.catalog.get_credential(
            self.job_account_name,
            self.db_name,
            self.secret_cred_name
        )
        self.assertIsNotNone(cred_response)
        self.assertIsNotNone(cred_response.name)

        # list credentials
        cred_list = list(self.adla_catalog_client.catalog.list_credentials(
            self.job_account_name,
            self.db_name
        ))
        
        self.assertIsNotNone(cred_list)
        self.assertGreater(len(cred_list), 0)
        specific_cred = [item for item in cred_list if item.name == self.secret_cred_name]
        self.assertIsNotNone(specific_cred)
        self.assertEqual(specific_cred[0].name, cred_response.name)

        # drop the credential using a job
        cred_script = 'USE {0}; DROP CREDENTIAL {1};'.format(self.db_name, self.secret_cred_name)
        self.run_job_to_completion(self.job_account_name, self.cred_drop_id, cred_script)

        # delete the secret
        self.adla_catalog_client.catalog.delete_secret(
            self.job_account_name,
            self.db_name,
            self.secret_name
        )

        # try to get the secret again which should fail
        try:
            self.adla_catalog_client.catalog.get_secret(
                self.job_account_name,
                self.db_name,
                self.secret_name
            )
            self.assertTrue(False, 'should not have made it here')
        except Exception as e:
            self.assertTrue(True)

        # delete all secrets in the db, which should just be a no-op
        self.adla_catalog_client.catalog.delete_all_secrets(
            self.job_account_name,
            self.db_name
        )

    @record
    def test_adla_accounts(self):
        
        # create resource group and store account
        self.run_prereqs()

        # define account params
        account_name = self.get_resource_name('pyarmadla')
        params_create = azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccount(
            location = self.region,
            default_data_lake_store_account = self.adls_account_name,
            data_lake_store_accounts = [azure.mgmt.datalake.analytics.account.models.DataLakeStoreAccountInfo(name = self.adls_account_name)],
            tags={
                'tag1': 'value1'
            }
        )

        # create and validate an ADLA account
        result_create = self.adla_account_client.account.create(
            self.group_name,
            account_name,
            params_create,
        )

        adla_account = result_create.result()
        
        # full validation of the create
        self.assertEqual(adla_account.name, account_name)
        
        # TODO: re-enable once it is determined why this property is still in "creating" state.
        # self.assertEqual(azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountStatus.succeeded, adla_account.provisioning_state)
        self.assertIsNotNone(adla_account.id)
        self.assertIn(account_name, adla_account.id)
        self.assertEqual(self.region, adla_account.location)
        self.assertEqual('Microsoft.DataLakeAnalytics/accounts', adla_account.type)
        self.assertEqual(adla_account.tags['tag1'], 'value1')
        self.assertEqual(1, len(adla_account.data_lake_store_accounts))
        self.assertEqual(self.adls_account_name, adla_account.default_data_lake_store_account)

        # get the account and do the same checks
        adla_account = self.adla_account_client.account.get(
            self.group_name,
            account_name
        )

        # full validation
        self.assertEqual(adla_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountStatus.succeeded, adla_account.provisioning_state)
        self.assertIsNotNone(adla_account.id)
        self.assertIn(account_name, adla_account.id)
        self.assertEqual(self.region, adla_account.location)
        self.assertEqual('Microsoft.DataLakeAnalytics/accounts', adla_account.type)
        self.assertEqual(adla_account.tags['tag1'], 'value1')
        self.assertEqual(1, len(adla_account.data_lake_store_accounts))
        self.assertEqual(self.adls_account_name, adla_account.default_data_lake_store_account)

        # list all the accounts (there should always be at least 2).
        result_list = self.adla_account_client.account.list_by_resource_group(
            self.group_name,
        )
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        result_list = self.adla_account_client.account.list()
        result_list = list(result_list)
        self.assertGreater(len(result_list), 0)

        
        # update the tags
        adla_account = self.adla_account_client.account.update(
            self.group_name,
            account_name,
            azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountUpdateParameters(
                tags = {
                    'tag2': 'value2'
                }
            )
        ).result()

        self.assertEqual(adla_account.tags['tag2'], 'value2')
        self.adla_account_client.account.delete(
            self.group_name,
            account_name
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
