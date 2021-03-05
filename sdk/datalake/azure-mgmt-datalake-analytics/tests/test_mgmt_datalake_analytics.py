# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import time
import unittest
import uuid

from azure.mgmt.datalake.analytics import account, job, catalog
import azure.mgmt.datalake.store
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

# 'East US 2' is the ADL production region for now
_REGION = 'East US 2'

# this is used explicitly for ADLA job id replacement in recordings.
ADLA_JOB_ID = "00000000-0000-0000-0000-000000000000"

class MgmtDataLakeAnalyticsTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtDataLakeAnalyticsTest, self).setUp()

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
        self.pipeline_name = self.get_resource_name('pipeline')
        self.recurrence_name = self.get_resource_name('recurrence')
        self.pipeline_uri = 'https://{}.contoso.com/myJob'.format(self.get_resource_name('pipelineuri'))

        # construct the catalog script
        self.db_name = self.get_resource_name('adladb')
        self.table_name = self.get_resource_name('adlatable')
        self.tvf_name = self.get_resource_name('adlatvf')
        self.proc_name = self.get_resource_name('adlaproc')
        self.view_name = self.get_resource_name('adlaview')
        self.secret_pwd = self.get_resource_name('adlapwd')
        self.credential_name = self.get_resource_name('adlacredential')
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

INSERT INTO {0}.dbo.{1}
(UserId, Start, Region, Query, Duration, Urls, ClickedUrls)
ON INTEGRITY VIOLATION MOVE TO PARTITION (1)
VALUES
(1, new DateTime(2018, 04, 25), "US", @"fake query", 34, "http://url1.fake.com", "http://clickedUrl1.fake.com"),
(1, new DateTime(2018, 04, 26), "EN", @"fake query", 23, "http://url2.fake.com", "http://clickedUrl2.fake.com");

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
END;""".format(self.db_name, self.table_name, self.tvf_name, self.view_name, self.proc_name)    # nosec

        # define all the job IDs to be used during execution
        if self.is_playback():
            self.cancel_id = ADLA_JOB_ID
            self.run_id = ADLA_JOB_ID
            self.catalog_id = ADLA_JOB_ID
            self.cred_create_id = ADLA_JOB_ID
            self.cred_drop_id = ADLA_JOB_ID
            self.pipeline_id = ADLA_JOB_ID
            self.recurrence_id = ADLA_JOB_ID
            self.run_id_2 = ADLA_JOB_ID
            self.run_id_3 = ADLA_JOB_ID
            self.principal_id = ADLA_JOB_ID
        else:
            self.cancel_id = str(uuid.uuid1())
            self.run_id = str(uuid.uuid1())
            self.catalog_id = str(uuid.uuid1())
            self.cred_create_id = str(uuid.uuid1())
            self.cred_drop_id = str(uuid.uuid1())
            self.pipeline_id = str(uuid.uuid1())
            self.recurrence_id = str(uuid.uuid1())
            self.run_id_2 = str(uuid.uuid1())
            self.run_id_3 = str(uuid.uuid1())
            self.principal_id = str(uuid.uuid1())

            real_to_fake_dict = {
                self.cancel_id: ADLA_JOB_ID,
                self.run_id:  ADLA_JOB_ID,
                self.catalog_id:  ADLA_JOB_ID,
                self.cred_create_id: ADLA_JOB_ID,
                self.cred_drop_id: ADLA_JOB_ID,
                self.pipeline_id: ADLA_JOB_ID,
                self.recurrence_id: ADLA_JOB_ID,
                self.run_id_2: ADLA_JOB_ID,
                self.run_id_3: ADLA_JOB_ID,
                self.principal_id: ADLA_JOB_ID
            }

            for key in real_to_fake_dict:
                self.scrubber.register_name_pair(key, real_to_fake_dict[key])

    def run_prereqs(self, resource_group, location, create_job_acct = False, create_catalog = False):

        # construct ADLS account for use with the ADLA tests.
        params_create = azure.mgmt.datalake.store.models.CreateDataLakeStoreAccountParameters(
            location = location
        )

        adls_account = self.adls_account_client.accounts.begin_create(
            resource_group.name,
            self.adls_account_name,
            params_create,
        ).result()

        # validation of the create
        self.assertEqual(adls_account.name, self.adls_account_name)

        # construct an ADLA account for use with catalog and job tests
        if create_job_acct:
            params_create = azure.mgmt.datalake.analytics.account.models.CreateDataLakeAnalyticsAccountParameters(
                location = location,
                default_data_lake_store_account = self.adls_account_name,
                data_lake_store_accounts = [
                    azure.mgmt.datalake.analytics.account.models.AddDataLakeStoreWithAccountParameters(
                        name = self.adls_account_name
                    )
                ]
            )

            adla_account = self.adla_account_client.accounts.create(
                resource_group.name,
                self.job_account_name,
                params_create,
            ).result()

            # full validation of the create
            self.assertEqual(adla_account.name, self.job_account_name)

            # wait five minutes for the account to be fully provisioned with a queue.
            if self.is_live:
                time.sleep(300)

            if create_catalog:
                self.run_job_to_completion(self.job_account_name, self.catalog_id, self.catalog_script)

    def run_job_to_completion(self, adla_account_name, job_id, script_to_run, job_params=None):
        if not job_params:
            job_params = azure.mgmt.datalake.analytics.job.models.CreateJobParameters(
                name = self.get_resource_name('testjob'),
                type = azure.mgmt.datalake.analytics.job.models.JobType.usql,
                degree_of_parallelism = 2,
                properties = azure.mgmt.datalake.analytics.job.models.CreateUSqlJobProperties(
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

        while adla_job.state != azure.mgmt.datalake.analytics.job.models.JobState.ended and cur_wait_in_seconds < max_wait_in_seconds:
            if self.is_live:
                time.sleep(5)
            cur_wait_in_seconds += 5
            adla_job = self.adla_job_client.job.get(
                adla_account_name,
                job_id
            )
            self.assertIsNotNone(adla_job)

        self.assertTrue(cur_wait_in_seconds <= max_wait_in_seconds)
        self.assertTrue(adla_job.state == azure.mgmt.datalake.analytics.job.models.JobState.ended and adla_job.result == azure.mgmt.datalake.analytics.job.models.JobResult.succeeded,
                        'Job: {0} did not return success. Current job state: {1}. Actual result: {2}. Error (if any): {3}'.format(
                            adla_job.job_id,
                            adla_job.state,
                            adla_job.result,
                            adla_job.error_message
                        ))

    @ResourceGroupPreparer(location=_REGION)
    def test_adla_jobs(self, resource_group, location):
        self.run_prereqs(resource_group, location, create_job_acct= True, create_catalog = False)

        # define some static GUIDs
        job_to_submit = azure.mgmt.datalake.analytics.job.models.CreateJobParameters(
            name = 'azure python sdk job test',
            degree_of_parallelism = 2,
            type = azure.mgmt.datalake.analytics.job.models.JobType.usql,
            properties = azure.mgmt.datalake.analytics.job.models.CreateUSqlJobProperties(
                script = 'DROP DATABASE IF EXISTS testdb; CREATE DATABASE testdb;'
            ),
            related = azure.mgmt.datalake.analytics.job.models.JobRelationshipProperties(
                pipeline_id = self.pipeline_id,
                pipeline_name = self.pipeline_name,
                pipeline_uri = self.pipeline_uri,
                recurrence_id = self.recurrence_id,
                recurrence_name = self.recurrence_name,
                run_id = self.run_id_2
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

        # resubmit and allow to run to completion -- update the runId beforehand
        job_to_submit.related.run_id = self.run_id_3
        self.run_job_to_completion(self.job_account_name, self.run_id, job_to_submit.properties.script, job_params=job_to_submit)

        # list the jobs that have been submitted
        list_of_jobs = self.adla_job_client.job.list(self.job_account_name)
        self.assertIsNotNone(list_of_jobs)

        list_of_jobs = list(list_of_jobs)
        self.assertGreater(len(list_of_jobs), 1)

        # get the specific job and validate the job relationship properties
        adla_job = self.adla_job_client.job.get(
            self.job_account_name,
            self.run_id
        )
        self.assertEqual(self.run_id_3, adla_job.related.run_id)
        self.assertEqual(self.recurrence_id, adla_job.related.recurrence_id)
        self.assertEqual(self.pipeline_id, adla_job.related.pipeline_id)
        self.assertEqual(self.pipeline_name, adla_job.related.pipeline_name)
        self.assertEqual(self.recurrence_name, adla_job.related.recurrence_name)
        self.assertEqual(self.pipeline_uri, adla_job.related.pipeline_uri)

        # validate job relationship APIs
        recurrence_get =  self.adla_job_client.recurrence.get(self.job_account_name, self.recurrence_id)
        self.assertEqual(self.recurrence_id, recurrence_get.recurrence_id)
        self.assertEqual(self.recurrence_name, recurrence_get.recurrence_name)

        recurrence_list =  self.adla_job_client.recurrence.list(self.job_account_name)
        self.assertIsNotNone(recurrence_list)

        recurrence_list = list(recurrence_list)
        self.assertEqual(1, len(recurrence_list))

        pipeline_get =  self.adla_job_client.pipeline.get(self.job_account_name, self.pipeline_id)
        self.assertEqual(self.pipeline_id, pipeline_get.pipeline_id)
        self.assertEqual(self.pipeline_name, pipeline_get.pipeline_name)
        self.assertEqual(self.pipeline_uri, pipeline_get.pipeline_uri)
        self.assertGreater(len(pipeline_get.runs), 1)

        pipeline_list =  self.adla_job_client.pipeline.list(self.job_account_name)
        self.assertIsNotNone(pipeline_list)

        pipeline_list = list(pipeline_list)
        self.assertEqual(1, len(pipeline_list))

        # create a job to build
        job_to_build = azure.mgmt.datalake.analytics.job.models.BuildJobParameters(
            name = 'azure python sdk job test',
            type = azure.mgmt.datalake.analytics.job.models.JobType.usql,
            properties = azure.mgmt.datalake.analytics.job.models.CreateUSqlJobProperties(
                script = 'DROP DATABASE IF EXISTS testdb; CREATE DATABASE testdb;'
            )
        )

        # compile a job
        compile_response = self.adla_job_client.job.build(self.job_account_name, job_to_build)
        self.assertIsNotNone(compile_response)

        # now compile a broken job and validate diagnostics.
        job_to_build.properties.script = 'DROP DATABASE IF EXIST FOO; CREATE DATABASE FOO;'
        compile_response = self.adla_job_client.job.build(self.job_account_name, job_to_build)
        self.assertIsNotNone(compile_response)

        self.assertEqual(1, len(list(compile_response.properties.diagnostics)))
        self.assertEqual(azure.mgmt.datalake.analytics.job.models.SeverityTypes.error, list(compile_response.properties.diagnostics)[0].severity)
        self.assertEqual(18, list(compile_response.properties.diagnostics)[0].column_number)
        self.assertEqual(22, list(compile_response.properties.diagnostics)[0].end)
        self.assertEqual(17, list(compile_response.properties.diagnostics)[0].start)
        self.assertEqual(1, list(compile_response.properties.diagnostics)[0].line_number)
        self.assertIn("E_CSC_USER_SYNTAXERROR", list(compile_response.properties.diagnostics)[0].message)

    @ResourceGroupPreparer(location=_REGION)
    def test_adla_catalog_items(self, resource_group, location):
        self.run_prereqs(resource_group, location, create_job_acct = True, create_catalog = True)

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
        self.assertIsNotNone(table_match[0].column_list)

        # get the tabe list with only basic info and verify that extended properties are empty
        table_list = list(self.adla_catalog_client.catalog.list_tables(self.job_account_name, self.db_name, self.schema_name, basic=True))
        self.assertGreater(len(table_list), 0)
        table_match = [item for item in table_list if item.name == self.table_name]
        self.assertIsNotNone(table_match)
        self.assertEqual(len(table_match), 1)
        self.assertEqual(len(table_match[0].column_list), 0)
        self.assertEqual(len(table_match[0].index_list), 0)
        self.assertEqual(len(table_match[0].partition_key_list), 0)
        self.assertIsNone(table_match[0].external_table)
        self.assertIsNone(table_match[0].distribution_info)

        # get table list in database and verify that at least one extended property is populated.
        table_list = list(self.adla_catalog_client.catalog.list_tables_by_database(self.job_account_name, self.db_name))
        self.assertGreater(len(table_list), 0)
        table_match = [item for item in table_list if item.name == self.table_name]
        self.assertIsNotNone(table_match)
        self.assertEqual(len(table_match), 1)
        self.assertIsNotNone(table_match[0].column_list)

        # get the tabe list by database with only basic info and verify that extended properties are empty
        table_list = list(self.adla_catalog_client.catalog.list_tables_by_database(self.job_account_name, self.db_name, basic=True))
        self.assertGreater(len(table_list), 0)
        table_match = [item for item in table_list if item.name == self.table_name]
        self.assertIsNotNone(table_match)
        self.assertEqual(len(table_match), 1)
        self.assertEqual(len(table_match[0].column_list), 0)
        self.assertEqual(len(table_match[0].index_list), 0)
        self.assertEqual(len(table_match[0].partition_key_list), 0)
        self.assertIsNone(table_match[0].external_table)
        self.assertIsNone(table_match[0].distribution_info)

        # get the preview of the specific table
        specific_table_preview = self.adla_catalog_client.catalog.preview_table(self.job_account_name, self.db_name, self.schema_name, self.table_name)
        self.assertGreater(specific_table_preview.total_row_count, 0)
        self.assertGreater(specific_table_preview.total_column_count, 0)
        self.assertIsNotNone(specific_table_preview.rows)
        self.assertGreater(len(specific_table_preview.rows), 0)
        self.assertIsNotNone(specific_table_preview.schema)
        self.assertGreater(len(specific_table_preview.schema), 0)
        self.assertIsNotNone(specific_table_preview.schema[0].name)
        self.assertIsNotNone(specific_table_preview.schema[0].type)

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

        # get the preview of the specific partition
        specific_partition_preview = self.adla_catalog_client.catalog.preview_table_partition(self.job_account_name, self.db_name, self.schema_name, self.table_name, partition_to_get.name)
        self.assertGreater(specific_partition_preview.total_row_count, 0)
        self.assertGreater(specific_partition_preview.total_column_count, 0)
        self.assertIsNotNone(specific_partition_preview.rows)
        self.assertGreater(len(specific_partition_preview.rows), 0)
        self.assertIsNotNone(specific_partition_preview.schema)
        self.assertGreater(len(specific_partition_preview.schema), 0)
        self.assertIsNotNone(specific_partition_preview.schema[0].name)
        self.assertIsNotNone(specific_partition_preview.schema[0].type)

        # get the table fragment list
        fragment_list = list(self.adla_catalog_client.catalog.list_table_fragments(self.job_account_name, self.db_name, self.schema_name, self.table_name))
        self.assertIsNotNone(fragment_list)
        self.assertGreater(len(fragment_list), 0)

        # get all the types
        type_list = list(self.adla_catalog_client.catalog.list_types(self.job_account_name, self.db_name, self.schema_name))
        self.assertIsNotNone(type_list)
        self.assertGreater(len(type_list), 0)

        # prepare to grant/revoke ACLs
        grant_acl_param = azure.mgmt.datalake.analytics.catalog.models.AclCreateOrUpdateParameters(
            ace_type = azure.mgmt.datalake.analytics.catalog.models.AclType.user,
            principal_id = self.principal_id,
            permission = azure.mgmt.datalake.analytics.catalog.models.PermissionType.use
        )

        revoke_ace_type = azure.mgmt.datalake.analytics.catalog.models.AclType.user
        revoke_principal_id = self.principal_id

        # get the initial number of ACLs by db
        acl_by_db_list = list(
            self.adla_catalog_client.catalog.list_acls_by_database(
                self.job_account_name,
                self.db_name
            )
        )

        acl_by_db_count = len(acl_by_db_list)

        # get the initial number of ACLs by catalog
        acl_list = list(self.adla_catalog_client.catalog.list_acls(self.job_account_name))
        acl_count = len(acl_list)

        # grant ACL to the db
        self.adla_catalog_client.catalog.grant_acl_to_database(
            self.job_account_name,
            self.db_name,
            grant_acl_param
        )

        acl_by_db_list = list(
            self.adla_catalog_client.catalog.list_acls_by_database(
                self.job_account_name,
                self.db_name
            )
        )

        granted_acl = acl_by_db_list[-1]

        # confirm the ACL's information
        self.assertEqual(acl_by_db_count + 1, len(acl_by_db_list))
        self.assertEqual(azure.mgmt.datalake.analytics.catalog.models.AclType.user.value, granted_acl.ace_type)
        self.assertEqual(self.principal_id, granted_acl.principal_id)
        self.assertEqual(azure.mgmt.datalake.analytics.catalog.models.PermissionType.use.value, granted_acl.permission)

        # revoke ACL from the db
        self.adla_catalog_client.catalog.revoke_acl_from_database(
            self.job_account_name,
            self.db_name,
            revoke_ace_type,
            revoke_principal_id
        )

        acl_by_db_list = list(
            self.adla_catalog_client.catalog.list_acls_by_database(
                self.job_account_name,
                self.db_name
            )
        )

        self.assertEqual(acl_by_db_count, len(acl_by_db_list))

        # grant ACL to the catalog
        self.adla_catalog_client.catalog.grant_acl(
            self.job_account_name,
            grant_acl_param
        )

        acl_list = list(self.adla_catalog_client.catalog.list_acls(self.job_account_name))
        granted_acl = acl_list[-1]

        # confirm the ACL's information
        self.assertEqual(acl_count + 1, len(acl_list))
        self.assertEqual(azure.mgmt.datalake.analytics.catalog.models.AclType.user.value, granted_acl.ace_type)
        self.assertEqual(self.principal_id, granted_acl.principal_id)
        self.assertEqual(azure.mgmt.datalake.analytics.catalog.models.PermissionType.use.value, granted_acl.permission)

        # revoke ACL from the catalog
        self.adla_catalog_client.catalog.revoke_acl(
            self.job_account_name,
            revoke_ace_type,
            revoke_principal_id
        )

        acl_list = list(self.adla_catalog_client.catalog.list_acls(self.job_account_name))

        self.assertEqual(acl_count, len(acl_list))

    @ResourceGroupPreparer(location=_REGION)
    def test_adla_catalog_credentials(self, resource_group, location):
        self.run_prereqs(resource_group, location, create_job_acct= True, create_catalog = True)

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
                    user_id = self.get_resource_name('newcredid')
                )
            )
            self.assertTrue(False, 'should not have made it here')
        except Exception:
            pass

        # get credential and ensure the response is not null
        cred_response = self.adla_catalog_client.catalog.get_credential(
            self.job_account_name,
            self.db_name,
            self.credential_name
        )
        self.assertIsNotNone(cred_response)
        self.assertIsNotNone(cred_response.name)

        # list credentials
        cred_list = list(
            self.adla_catalog_client.catalog.list_credentials(
                self.job_account_name,
                self.db_name
            )
        )

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
        except Exception:
            pass

    @ResourceGroupPreparer(location=_REGION)
    def test_adla_compute_policies(self, resource_group, location):
        self.run_prereqs(resource_group, location)

        # define account params
        account_name = self.get_resource_name('pyarmadla')
        user_id = '8ce05900-7a9e-4895-b3f0-0fbcee507803'
        user_policy_name = self.get_resource_name('adlapolicy1')
        group_id = '0583cfd7-60f5-43f0-9597-68b85591fc69'
        group_policy_name = self.get_resource_name('adlapolicy2')

        params_create = azure.mgmt.datalake.analytics.account.models.CreateDataLakeAnalyticsAccountParameters(
            location = location,
            default_data_lake_store_account = self.adls_account_name,
            data_lake_store_accounts = [
                azure.mgmt.datalake.analytics.account.models.AddDataLakeStoreWithAccountParameters(
                    name = self.adls_account_name
                )
            ],
            compute_policies = [
                azure.mgmt.datalake.analytics.account.models.CreateComputePolicyWithAccountParameters(
                    name = user_policy_name,
                    object_id = user_id,
                    object_type = azure.mgmt.datalake.analytics.account.models.AADObjectType.user,
                    max_degree_of_parallelism_per_job = 1,
                    min_priority_per_job = 1
                )
            ]
        )

        # create and validate an ADLA account
        adla_account = self.adla_account_client.accounts.create(
            resource_group.name,
            account_name,
            params_create,
        ).result()

        # full validation of the create
        self.assertEqual(adla_account.name, account_name)
        self.assertIsNotNone(adla_account.id)
        self.assertIn(account_name, adla_account.id)
        self.assertEqual(location, adla_account.location)
        self.assertEqual('Microsoft.DataLakeAnalytics/accounts', adla_account.type)
        self.assertEqual(1, len(adla_account.data_lake_store_accounts))
        self.assertEqual(self.adls_account_name, adla_account.default_data_lake_store_account)

        # get the account and validate compute policy exists
        adla_account = self.adla_account_client.accounts.get(
            resource_group.name,
            account_name
        )

        self.assertEqual(user_policy_name, list(adla_account.compute_policies)[0].name)
        self.assertEqual(1, len(list(adla_account.compute_policies)))

        # validate compute policy CRUD
        new_policy = self.adla_account_client.compute_policies.create_or_update(
            resource_group.name,
            account_name,
            group_policy_name,
            azure.mgmt.datalake.analytics.account.models.CreateOrUpdateComputePolicyParameters(
                object_id = group_id,
                object_type = azure.mgmt.datalake.analytics.account.models.AADObjectType.group,
                max_degree_of_parallelism_per_job = 1,
                min_priority_per_job = 1
            )
        )

        self.assertEqual(group_id, new_policy.object_id)
        self.assertEqual(azure.mgmt.datalake.analytics.account.models.AADObjectType.group.value, new_policy.object_type)
        self.assertEqual(1, new_policy.max_degree_of_parallelism_per_job)
        self.assertEqual(1, new_policy.min_priority_per_job)

        # get policy
        new_policy = self.adla_account_client.compute_policies.get(
            resource_group.name,
            account_name,
            group_policy_name
        )

        self.assertEqual(group_id, new_policy.object_id)
        self.assertEqual(azure.mgmt.datalake.analytics.account.models.AADObjectType.group.value, new_policy.object_type)
        self.assertEqual(1, new_policy.max_degree_of_parallelism_per_job)
        self.assertEqual(1, new_policy.min_priority_per_job)

        # list all policies
        list_policy = list(
            self.adla_account_client.compute_policies.list_by_account(
                resource_group.name,
                account_name
            )
        )

        self.assertEqual(2, len(list_policy))

        # remove the group policy and verify list length is 1
        self.adla_account_client.compute_policies.delete(
            resource_group.name,
            account_name,
            group_policy_name
        )

        list_policy = list(
            self.adla_account_client.compute_policies.list_by_account(
                resource_group.name,
                account_name
            )
        )

        self.assertEqual(1, len(list_policy))

        # delete account
        self.adla_account_client.accounts.delete(
            resource_group.name,
            account_name
        ).wait()

    @ResourceGroupPreparer(location=_REGION)
    def test_adla_accounts(self, resource_group, location):
        self.run_prereqs(resource_group, location)

        # define account params
        account_name = self.get_resource_name('pyarmadla')

        params_create = azure.mgmt.datalake.analytics.account.models.CreateDataLakeAnalyticsAccountParameters(
            location = location,
            default_data_lake_store_account = self.adls_account_name,
            data_lake_store_accounts = [
                azure.mgmt.datalake.analytics.account.models.AddDataLakeStoreWithAccountParameters(
                    name = self.adls_account_name
                )
            ],
            tags = {
                'tag1' : 'value1'
            }
        )

        # ensure that the account name is available
        name_availability = self.adla_account_client.accounts.check_name_availability(
            location.replace(" ", ""),
            account_name
        )
        self.assertTrue(name_availability.name_available)

        # create and validate an ADLA account
        adla_account = self.adla_account_client.accounts.create(
            resource_group.name,
            account_name,
            params_create
        ).result()

        # ensure that the account name is no longer available
        name_availability = self.adla_account_client.accounts.check_name_availability(
            location.replace(" ", ""),
            account_name
        )
        self.assertFalse(name_availability.name_available)

        # full validation of the create
        self.assertEqual(adla_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountStatus.succeeded, adla_account.provisioning_state)
        self.assertIsNotNone(adla_account.id)
        self.assertIn(account_name, adla_account.id)
        self.assertEqual(location, adla_account.location)
        self.assertEqual('Microsoft.DataLakeAnalytics/accounts', adla_account.type)
        self.assertEqual(adla_account.tags['tag1'], 'value1')
        self.assertEqual(1, len(adla_account.data_lake_store_accounts))
        self.assertEqual(self.adls_account_name, adla_account.default_data_lake_store_account)

        # get the account and do the same checks
        adla_account = self.adla_account_client.accounts.get(
            resource_group.name,
            account_name
        )

        # full validation of the create
        self.assertEqual(adla_account.name, account_name)
        self.assertEqual(azure.mgmt.datalake.analytics.account.models.DataLakeAnalyticsAccountStatus.succeeded, adla_account.provisioning_state)
        self.assertIsNotNone(adla_account.id)
        self.assertIn(account_name, adla_account.id)
        self.assertEqual(location, adla_account.location)
        self.assertEqual('Microsoft.DataLakeAnalytics/accounts', adla_account.type)
        self.assertEqual(adla_account.tags['tag1'], 'value1')
        self.assertEqual(1, len(adla_account.data_lake_store_accounts))
        self.assertEqual(self.adls_account_name, adla_account.default_data_lake_store_account)

        # list all the accounts (there should always be at least 2)
        account_list_by_rg = list(self.adla_account_client.accounts.list_by_resource_group(resource_group.name))
        self.assertGreater(len(account_list_by_rg), 0)

        account_list = list(self.adla_account_client.accounts.list())
        self.assertGreater(len(account_list), 0)

        # update the tags
        adla_account = self.adla_account_client.accounts.update(
            resource_group.name,
            account_name,
            azure.mgmt.datalake.analytics.account.models.UpdateDataLakeAnalyticsAccountParameters(
                tags = {
                    'tag2' : 'value2'
                }
            )
        ).result()

        self.assertEqual(adla_account.tags['tag2'], 'value2')

        # confirm that 'locations.get_capability' is functional
        get_capability = self.adla_account_client.locations.get_capability(location.replace(" ", ""))
        self.assertIsNotNone(get_capability)

        # confirm that 'operations.list' is functional
        operations_list = self.adla_account_client.operations.list()
        self.assertIsNotNone(operations_list)

        self.adla_account_client.accounts.delete(
            resource_group.name,
            account_name
        ).wait()

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
