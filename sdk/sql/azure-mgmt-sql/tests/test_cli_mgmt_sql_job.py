# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   JobAgents: 5/5
#   JobCredentials: 4/4
#   JobExecutions: 6/6
#   JobStepExecutions: 2/2
#   JobSteps: 6/6
#   JobTargetExecutions: 2/3
#   JobTargetGroups: 4/4
#   Jobs: 4/4
#   JobVersions: 2/2

import unittest

import azure.mgmt.sql
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtSqlTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtSqlTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.sql.SqlManagementClient
        )

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_job(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        SERVER_NAME = "myserverxpxyz"
        DATABASE_NAME = "mydatabase"
        JOB_AGENT_NAME = "myjobagent"
        JOB_NAME = "myjob"
        CREDENTIAL_NAME = "mycredential"
        JOB_EXECUTION_ID = "622ffff7-c4be-4c62-8098-3867c5db6427"
        TARGET_GROUP_NAME = "mytargetgroup"
        STEP_NAME = "mystep"
        JOB_VERSION = 1

#--------------------------------------------------------------------------
        # /Servers/put/Create server[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "administrator_login": "dummylogin",
          "administrator_login_password": "Un53cuRE!"
        }
        result = self.mgmt_client.servers.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/put/Creates a database [put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION
        }
        result = self.mgmt_client.databases.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/put/Create or update a job agent with minimum properties[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "database_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/databases/" + DATABASE_NAME
        }
        result = self.mgmt_client.job_agents.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobCredentials/put/Create or update a credential[put]
#--------------------------------------------------------------------------
        BODY = {
          "username": "myuser",
          "password": "<password>"
        }
        result = self.mgmt_client.job_credentials.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobTargetGroups/put/Create or update a target group with minimal properties.[put]
#--------------------------------------------------------------------------
        BODY = {
          "members": []
        }
        result = self.mgmt_client.job_target_groups.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /Jobs/put/Create a job with all properties specified[put]
#--------------------------------------------------------------------------
        BODY = {
          "description": "my favourite job",
          "schedule": {
            "start_time": "2020-09-24T18:30:01Z",
            "end_time": "2020-09-24T23:59:59Z",
            "type": "Recurring",
            "interval": "PT5M",
            "enabled": True
          }
        }
        result = self.mgmt_client.jobs.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobSteps/put/Create or update a job step with minimal properties specified.[put]
#--------------------------------------------------------------------------
        BODY = {
          "target_group": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/targetGroups/" + TARGET_GROUP_NAME,
          "credential": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.Sql/servers/" + SERVER_NAME + "/jobAgents/" + JOB_AGENT_NAME + "/credentials/" + CREDENTIAL_NAME,
          "action": {
            "value": "select 1"
          }
        }
        result = self.mgmt_client.job_steps.create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME, parameters=BODY)

#--------------------------------------------------------------------------
        # /JobExecutions/put/Create job execution.[put]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.begin_create_or_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobAgents/get/Get a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobCredentials/get/Get a credential[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME)

#--------------------------------------------------------------------------
        # /JobTargetGroups/get/Get a target group.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/Get the latest version of a job step.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/Get a job execution.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /JobStepExecutions/get/List job step executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_step_executions.list_by_job_execution(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /Jobs/get/Get a job[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/List job step target executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_executions.list_by_job_execution(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)
        # TARGET_ID = result.next().value[0].name

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/Get a job step target execution[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.job_target_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID, step_name=STEP_NAME, target_id=TARGET_ID)

#--------------------------------------------------------------------------
        # /JobTargetExecutions/get/List job step target executions[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_executions.list_by_step(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /JobStepExecutions/get/Get a job step execution[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_step_executions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/Get the specified version of a job step.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.get_by_version(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION, step_name=STEP_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/List job steps for the specified version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.list_by_version(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION)

#--------------------------------------------------------------------------
        # /Jobs/get/List jobs in a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobSteps/get/List job steps for the latest version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_steps.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/List a job's executions.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /JobExecutions/get/List all job executions in a job agent.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobCredentials/get/List credentials in a job agent[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobTargetGroups/get/Get all target groups in an agent.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.list_by_agent(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)

#--------------------------------------------------------------------------
        # /JobAgents/get/List job agents in a server[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.list_by_server(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)

#--------------------------------------------------------------------------
        # /JobVersions/get/Get all versions of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_versions.list_by_job(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)
        # JOB_VERSION = result.next().name

#--------------------------------------------------------------------------
        # /JobVersions/get/Get a version of a job.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_versions.get(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_version=JOB_VERSION)

#--------------------------------------------------------------------------
        # /JobExecutions/post/Start a job execution.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.begin_create(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobExecutions/post/Cancel a job execution.[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_executions.cancel(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, job_execution_id=JOB_EXECUTION_ID)

#--------------------------------------------------------------------------
        # /Jobs/delete/Delete a job[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.jobs.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME)

#--------------------------------------------------------------------------
        # /JobAgents/patch/Update a job agent's tags.[patch]
#--------------------------------------------------------------------------
        BODY = {
          "tags": {
            "mytag1": "myvalue1"
          }
        }
        result = self.mgmt_client.job_agents.begin_update(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /JobSteps/delete/Delete a job step.[delete]
#--------------------------------------------------------------------------
        try:
            result = self.mgmt_client.job_steps.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, job_name=JOB_NAME, step_name=STEP_NAME)
        except ResourceNotFoundError:
            pass

#--------------------------------------------------------------------------
        # /JobTargetGroups/delete/Delete a target group.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_target_groups.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, target_group_name=TARGET_GROUP_NAME)

#--------------------------------------------------------------------------
        # /JobCredentials/delete/Delete a credential[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_credentials.delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME, credential_name=CREDENTIAL_NAME)

#--------------------------------------------------------------------------
        # /JobAgents/delete/Delete a job agent[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.job_agents.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, job_agent_name=JOB_AGENT_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Databases/delete/Deletes a database.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.databases.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME, database_name=DATABASE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Servers/delete/Delete server[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.servers.begin_delete(resource_group_name=RESOURCE_GROUP, server_name=SERVER_NAME)
        result = result.result()
