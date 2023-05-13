# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import os
import pytest
import logging
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.identity import InteractiveBrowserCredential 
from azure.developer.devcenter import DevCenterClient
from azure.core.exceptions import HttpResponseError
from testcase import DevcenterPowerShellPreparer
from datetime import datetime, timedelta, timezone

class TestDevcenter(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint, credential=credential)

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_devbox_operations(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")
        user = kwargs.pop("devcenter_test_user_id")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        time_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        client = self.create_client(endpoint)

        # Pools
        pool_response = client.dev_boxes.get_pool(project_name, pool_name)
        assert pool_response['name'] == pool_name

        pools_response = client.dev_boxes.list_pools(project_name)
        assert pools_response.next()['name'] == pool_response['name']

        # Schedules
        schedule_response = client.dev_boxes.get_schedule(project_name, pool_name, "default")
        assert schedule_response['name'] == "default"

        schedules_response = client.dev_boxes.list_schedules(project_name, pool_name)
        assert schedules_response.next()['name'] == schedule_response['name']

        # Create DevBox
        create_devbox_response = client.dev_boxes.begin_create_dev_box(project_name, devbox_name, {"poolName": pool_name}, user_id=user)
        devbox_result = create_devbox_response.result()
        assert devbox_result['provisioningState'] in ["Succeeded", "ProvisionedWithWarning"]

        # Actions
        action_response = client.dev_boxes.get_action(project_name, devbox_name, "schedule-default")
        next_time_str = action_response['next']['scheduledTime']
        next_time_date = datetime.strptime(next_time_str, time_format)
        assert action_response['name'] == "schedule-default"

        actions_response = client.dev_boxes.list_actions(project_name, devbox_name, user)
        assert actions_response.next()['name'] == action_response['name']

        next_time_date = next_time_date + timedelta(hours=1)
        delay_all_response = client.dev_boxes.delay_all_actions(project_name, devbox_name, until=next_time_date)
        assert delay_all_response.next()['action']['next']['scheduledTime'] == next_time_date.strftime(time_format)

        # Failing with a 400 saying the date range isn't valid, even though the delay_all works just fine.
        next_time_date = next_time_date + timedelta(hours=1)
        delay_response = client.dev_boxes.delay_action(project_name, devbox_name, "schedule-default", until=next_time_date)
        assert delay_response['next']['scheduledTime'] == next_time_date.strftime(time_format)


        client.dev_boxes.skip_action(project_name, devbox_name, "schedule-default")

        # Dev Box:
        # list_all_dev_boxes, get_dev_box, list_dev_boxes, list_all_dev_boxes_by_user

        devbox_response = client.dev_boxes.get_dev_box(project_name, devbox_name)
        assert devbox_response['name'] == devbox_name

        devboxes_response = client.dev_boxes.list_dev_boxes(project_name)
        filtered_devbox_response = filter(lambda x: x['name'] == devbox_name, devboxes_response)
        assert len(list(filtered_devbox_response)) == 1

        devboxes_response = client.dev_boxes.list_all_dev_boxes()
        filtered_devbox_response = filter(lambda x: x['name'] == devbox_name and x['projectName'] == project_name, devboxes_response)
        assert len(list(filtered_devbox_response)) == 1

        devboxes_response = client.dev_boxes.list_all_dev_boxes_by_user()
        filtered_devbox_response = filter(lambda x: x['name'] == devbox_name and x['projectName'] == project_name, devboxes_response)
        assert len(list(filtered_devbox_response)) == 1

        # get_remote_connection
        connection_response = client.dev_boxes.get_remote_connection(project_name, devbox_name)
        assert connection_response['webUrl'] != None

        # begin_stop_dev_box, begin_start_dev_box, begin_delete_dev_box, begin_restart_dev_box
        restart_response = client.dev_boxes.begin_restart_dev_box(project_name, devbox_name)
        restart_result = restart_response.result()
        assert restart_result['status'] == "Succeeded"

        stop_response = client.dev_boxes.begin_stop_dev_box(project_name, devbox_name)
        stop_result = stop_response.result()
        assert stop_result['status'] == "Succeeded"

        start_response = client.dev_boxes.begin_start_dev_box(project_name, devbox_name)
        start_result = start_response.result()
        assert start_result['status'] == "Succeeded"

        delete_response = client.dev_boxes.begin_delete_dev_box(project_name, devbox_name)
        delete_result = delete_response.result()
        assert delete_result['status'] == "Succeeded"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_environment_operations(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        environment_type_name = kwargs.pop("devcenter_environment_type_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")
        env_name = kwargs.pop("devcenter_environment_name")

        client = self.create_client(endpoint)

        # Catalogs
        catalog_response = client.deployment_environments.get_catalog(project_name, catalog_name)
        assert catalog_response['name'] == catalog_name

        catalogs_response = client.deployment_environments.list_catalogs(project_name)
        catalogs_response = list(catalogs_response)
        filtered_catalog_response = filter(lambda x: x['name'] == catalog_name, catalogs_response)
        filtered_catalog_response = list(filtered_catalog_response)
        assert len(filtered_catalog_response) == 1
        assert filtered_catalog_response[0]['name'] == catalog_response['name']

        # Environment Definitions
        env_definition_response = client.deployment_environments.get_environment_definition(project_name, catalog_name, env_definition_name)
        assert env_definition_response['name'] == env_definition_name

        all_env_definition_response = client.deployment_environments.list_environment_definitions(project_name)
        filtered_all_env_definition_response = filter(lambda x: x['name'] == env_definition_name, all_env_definition_response)
        filtered_all_env_definition_response = list(filtered_all_env_definition_response)
        assert len(filtered_all_env_definition_response) == 1 and filtered_all_env_definition_response[0]['name'] == env_definition_response['name']

        env_definitions_response = client.deployment_environments.list_environment_definitions_by_catalog(project_name, catalog_name)
        filtered_env_definitions_response = filter(lambda x: x['name'] == env_definition_name, env_definitions_response)
        filtered_env_definitions_response = list(filtered_env_definitions_response)
        assert len(filtered_env_definitions_response) == 1 and filtered_env_definitions_response[0]['name'] == env_definition_response['name']

        # Environment Types
        env_types_response = client.deployment_environments.list_environment_types(project_name)
        filtered_env_types_response = filter(lambda x: x['name'] == environment_type_name, env_types_response)
        filtered_env_types_response = list(filtered_env_types_response)
        assert len(filtered_env_types_response) == 1 and filtered_env_types_response[0]['name'] == environment_type_name

        # Environments
        environment = {
            "catalogName": catalog_name,
            "environmentDefinitionName": env_definition_name,
            "environmentType": environment_type_name
        }
        create_env_response = client.deployment_environments.begin_create_or_update_environment(project_name, env_name, environment)
        create_env_result = create_env_response.result()
        assert create_env_result['provisioningState'] == "Succeeded"

        env_response = client.deployment_environments.get_environment(project_name, env_name)
        assert env_response['name'] == env_name

        envs_response = client.deployment_environments.list_environments(project_name)
        envs_response = filter(lambda x: x['name'] == env_name, envs_response)
        envs_response = list(envs_response)
        assert len(envs_response) == 1 and envs_response[0]['name'] == env_response['name']

        all_envs_response = client.deployment_environments.list_all_environments(project_name)
        all_envs_response = filter(lambda x: x['name'] == env_name, all_envs_response)
        all_envs_response = list(all_envs_response)
        assert len(all_envs_response) == 1 and all_envs_response[0]['name'] == env_response['name']

        delete_response = client.deployment_environments.begin_delete_environment(project_name, env_name)
        delete_result = delete_response.result()
        assert delete_result['status'] == "Succeeded"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_devcenter_operations(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")

        client = self.create_client(endpoint)

        # Projects
        project_response = client.dev_center.get_project(project_name)
        assert project_response['name'] == project_name

        projects_response = client.dev_center.list_projects()
        projects_response = filter(lambda x: x['name'] == project_name, projects_response)
        projects_response = list(projects_response)
        assert len(projects_response) == 1 and projects_response[0]['name'] == project_response['name']
