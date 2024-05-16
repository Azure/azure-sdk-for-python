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
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async
from azure.developer.devcenter.aio import DevCenterClient
from azure.developer.devcenter.models import DevBoxProvisioningState
from azure.developer.devcenter.models import OperationStatus
from testcase import DevcenterPowerShellPreparer
from datetime import timedelta


class TestDevcenterAsync(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint, credential=credential)

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_project_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")

        client = self.create_client(endpoint)

        async with client:
            project = await client.get_project(project_name)
            assert project is not None
            assert project.name == project_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_projects_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")

        client = self.create_client(endpoint)

        async with client:
            projects = []

            async for project in client.list_projects():
                projects.append(project)

            assert projects is not None
            assert len(projects) == 1
            assert projects[0].name == project_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_pool_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        async with client:
            pool_response = await client.get_pool(project_name, pool_name)
            assert pool_response is not None
            assert pool_response.name == pool_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_pools_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        async with client:
            pools_response = []
            async for pool in client.list_pools(project_name):
                pools_response.append(pool)

            assert pools_response is not None
            assert len(pools_response) == 1
            assert pools_response[0].name == pool_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_schedule_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        async with client:
            # Schedule
            schedule_response = await client.get_schedule(project_name, pool_name, "default")
            assert schedule_response is not None
            assert schedule_response.name == "default"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_schedules_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        async with client:
            # Schedules
            schedules_response = []
            async for schedule in client.list_schedules(project_name, pool_name):
                schedules_response.append(schedule)

            assert schedules_response is not None
            assert len(schedules_response) == 1
            assert schedules_response[0].name == "default"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_dev_box_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")
        user = kwargs.pop("devcenter_test_user_id")
        devbox_name = kwargs.pop("devcenter_devbox_name")

        client = self.create_client(endpoint)

        async with client:
            # Create DevBox
            create_devbox_response = await client.begin_create_dev_box(project_name, user, devbox_name, {"poolName": pool_name})
            devbox_result = await create_devbox_response.result()
            assert devbox_result is not None
            assert devbox_result.provisioning_state in [
                DevBoxProvisioningState.SUCCEEDED,
                DevBoxProvisioningState.PROVISIONED_WITH_WARNING,
        ]

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_dev_box_action_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            # Actions
            action_response = await client.get_dev_box_action(project_name, default_user, devbox_name, "schedule-default")
            next_time_date = action_response.next.scheduled_time
            assert next_time_date is not None
            assert action_response.name == "schedule-default"

            actions_response = []
            async for action in client.list_dev_box_actions(project_name, default_user, devbox_name):
                actions_response.append(action)
            assert actions_response[0].name == action_response.name

            next_time_date = next_time_date + timedelta(hours=1)
            delay_all_response = []
            async for action in client.delay_all_dev_box_actions(project_name, default_user, devbox_name, delay_until=next_time_date):
                delay_all_response.append(action)
            assert delay_all_response[0].action.next.scheduled_time == next_time_date

            # Failing with a 400 saying the date range isn't valid, even though the delay_all works just fine.
            next_time_date = next_time_date + timedelta(hours=1)
            delay_response = await client.delay_dev_box_action(
                project_name, default_user, devbox_name, "schedule-default", delay_until=next_time_date
            )
            assert delay_response.next.scheduled_time == next_time_date

            await client.skip_dev_box_action(project_name, default_user, devbox_name, "schedule-default")

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_dev_box_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            devbox_response = await client.get_dev_box(project_name, default_user, devbox_name)
            assert devbox_response.name == devbox_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_dev_boxes_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            devboxes = []
            async for devbox in client.list_dev_boxes(project_name, default_user):
                if devbox.name == devbox_name:
                    devboxes.append(devbox)

            assert len(devboxes) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_all_dev_boxes_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")

        client = self.create_client(endpoint)

        async with client:
            devboxes = []
            async for devbox in client.list_all_dev_boxes():
                if devbox.name == devbox_name and devbox.project_name == project_name:
                    devboxes.append(devbox)

            assert len(devboxes) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_all_dev_boxes_by_user_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)
        
        async with client:
            devboxes = []
            async for devbox in client.list_all_dev_boxes_by_user(default_user):
                if devbox.name == devbox_name and devbox.project_name == project_name:
                    devboxes.append(devbox)

            assert len(devboxes) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_remote_connection_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            connection_response = await client.get_remote_connection(project_name, default_user, devbox_name)
            assert connection_response.web_url is not None

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_restart_dev_box_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            restart_response = await client.begin_restart_dev_box(project_name, default_user, devbox_name)
            restart_result = await restart_response.result()
            assert restart_result.status == OperationStatus.SUCCEEDED

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_stop_start_delete_dev_box_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        async with client:
            stop_response = await client.begin_stop_dev_box(project_name, default_user, devbox_name)
            stop_result = await stop_response.result()
            assert stop_result.status == OperationStatus.SUCCEEDED

            start_response = await client.begin_start_dev_box(project_name, default_user, devbox_name)
            start_result = await start_response.result()
            assert start_result.status == OperationStatus.SUCCEEDED

            delete_response = await client.begin_delete_dev_box(project_name, default_user, devbox_name)
            delete_result = await delete_response.result()
            assert delete_result.status == OperationStatus.SUCCEEDED

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_catalog_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")

        client = self.create_client(endpoint)
        
        async with client:
            catalog_response = await client.get_catalog(project_name, catalog_name)
            assert catalog_response.name == catalog_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_catalogs_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")

        client = self.create_client(endpoint)

        async with client:
            catalogs = []
            async for catalog in client.list_catalogs(project_name):
                if catalog.name == catalog_name:
                    catalogs.append(catalog)
            
            assert len(catalogs) == 1
            assert catalogs[0].name == catalog_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_environment_definition_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)

        async with client:
            env_definition_response = await client.get_environment_definition(project_name, catalog_name, env_definition_name)
            assert env_definition_response.name == env_definition_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_environment_definitions_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)
        
        async with client:
            env_definitions = []
            async for env_definition in client.list_environment_definitions(project_name):
                if env_definition.name == env_definition_name:
                    env_definitions.append(env_definition)
            
            assert len(env_definitions) == 1
            assert env_definitions[0].name == env_definition_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_environment_definitions_by_catalog_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)

        async with client:
            env_definitions = []
            async for env_definition in client.list_environment_definitions_by_catalog(project_name, catalog_name):
                if env_definition.name == env_definition_name:
                    env_definitions.append(env_definition)

            assert len(env_definitions) == 1
            assert env_definitions[0].name == env_definition_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_environment_types_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        environment_type_name = kwargs.pop("devcenter_environment_type_name")

        client = self.create_client(endpoint)

        async with client:
            env_types = []
            async for env_type in client.list_environment_types(project_name):
                if env_type.name == environment_type_name:
                    env_types.append(env_type)

            assert len(env_types) == 1
            assert env_types[0].name == environment_type_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_environments_async(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        environment_type_name = kwargs.pop("devcenter_environment_type_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")
        env_name = kwargs.pop("devcenter_environment_name")
        default_user = "me"

        client = self.create_client(endpoint)

        environment = {
            "environmentType": environment_type_name,
            "catalogName": catalog_name,
            "environmentDefinitionName": env_definition_name,
        }

        async with client:
            create_env_response = await client.begin_create_or_update_environment(
                project_name, default_user, env_name, environment
            )
            create_env_result = await create_env_response.result()
            assert create_env_result.provisioning_state == DevBoxProvisioningState.SUCCEEDED
    
            env_response = await client.get_environment(project_name, default_user, env_name)
            assert env_response.name == env_name
    
            envs = []
            async for env in client.list_environments(project_name, default_user):
                if env.name == env_name:
                    envs.append(env)
            
            assert len(envs) == 1
            assert envs[0].name == env_name
    
            all_envs = []
            async for env in client.list_all_environments(project_name):
                if env.name == env_name:
                    all_envs.append(env)
            
            assert len(all_envs) == 1
            assert all_envs[0].name == env_name
    
            delete_response = await client.begin_delete_environment(project_name, default_user, env_name)
            delete_result = await delete_response.result()
            assert delete_result.status == OperationStatus.SUCCEEDED