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
from azure.identity import DefaultAzureCredential
from azure.developer.devcenter import DevCenterClient
from azure.developer.devcenter.models import DevBoxProvisioningState
from azure.developer.devcenter.models import OperationStatus
from testcase import DevcenterPowerShellPreparer
from datetime import timedelta


class TestDevcenter(AzureRecordedTestCase):
    def create_client(self, endpoint):
        credential = self.get_credential(DevCenterClient)
        return DevCenterClient(endpoint, credential=credential)

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_project(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")

        client = self.create_client(endpoint)

        project = client.get_project(project_name)
        assert project is not None
        assert project.name == project_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_projects(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")

        client = self.create_client(endpoint)

        projects = list(client.list_projects())
        assert projects is not None
        assert len(projects) == 1
        assert projects[0].name == project_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_pool(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        pool_response = client.get_pool(project_name, pool_name)
        assert pool_response is not None
        assert pool_response.name == pool_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_pools(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        pools_response = list(client.list_pools(project_name))
        assert pools_response is not None
        assert len(pools_response) == 1
        assert pools_response[0].name == pool_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_schedule(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        # Schedule
        schedule_response = client.get_schedule(project_name, pool_name, "default")
        assert schedule_response is not None
        assert schedule_response.name == "default"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_schedules(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")

        client = self.create_client(endpoint)

        # Schedules
        schedules_response = list(client.list_schedules(project_name, pool_name))
        assert schedules_response is not None
        assert len(schedules_response) == 1
        assert schedules_response[0].name == "default"

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_create_dev_box(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        pool_name = kwargs.pop("devcenter_pool_name")
        user = kwargs.pop("devcenter_test_user_id")
        devbox_name = kwargs.pop("devcenter_devbox_name")

        client = self.create_client(endpoint)

        # Create DevBox
        create_devbox_response = client.begin_create_dev_box(project_name, user, devbox_name, {"poolName": pool_name})
        devbox_result = create_devbox_response.result()
        assert devbox_result is not None
        assert devbox_result.provisioning_state in [
            DevBoxProvisioningState.SUCCEEDED,
            DevBoxProvisioningState.PROVISIONED_WITH_WARNING,
        ]

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_dev_box_action(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        # Actions
        action_response = client.get_dev_box_action(project_name, default_user, devbox_name, "schedule-default")
        next_time_date = action_response.next.scheduled_time
        assert next_time_date is not None
        assert action_response.name == "schedule-default"

        actions_response = list(client.list_dev_box_actions(project_name, default_user, devbox_name))
        assert actions_response[0].name == action_response.name

        next_time_date = next_time_date + timedelta(hours=1)
        delay_all_response = list(
            client.delay_all_dev_box_actions(project_name, default_user, devbox_name, delay_until=next_time_date)
        )
        assert delay_all_response[0].action.next.scheduled_time == next_time_date

        # Failing with a 400 saying the date range isn't valid, even though the delay_all works just fine.
        next_time_date = next_time_date + timedelta(hours=1)
        delay_response = client.delay_dev_box_action(
            project_name, default_user, devbox_name, "schedule-default", delay_until=next_time_date
        )
        assert delay_response.next.scheduled_time == next_time_date

        client.skip_dev_box_action(project_name, default_user, devbox_name, "schedule-default")

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_dev_box(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        devbox_response = client.get_dev_box(project_name, default_user, devbox_name)
        assert devbox_response.name == devbox_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_dev_boxes(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        devboxes_response = client.list_dev_boxes(project_name, default_user)
        filtered_devbox_response = filter(lambda x: x.name == devbox_name, devboxes_response)
        assert len(list(filtered_devbox_response)) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_all_dev_boxes(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        devboxes_response = client.list_all_dev_boxes()
        filtered_devbox_response = filter(
            lambda x: x.name == devbox_name and x.project_name == project_name, devboxes_response
        )
        assert len(list(filtered_devbox_response)) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_all_dev_boxes_by_user(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        devboxes_response = client.list_all_dev_boxes_by_user(default_user)
        filtered_devbox_response = filter(
            lambda x: x.name == devbox_name and x.project_name == project_name, devboxes_response
        )
        assert len(list(filtered_devbox_response)) == 1

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_remote_connection(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        connection_response = client.get_remote_connection(project_name, default_user, devbox_name)
        assert connection_response.web_url is not None

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_restart_dev_box(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        restart_response = client.begin_restart_dev_box(project_name, default_user, devbox_name)
        restart_result = restart_response.result()
        assert restart_result.status == OperationStatus.SUCCEEDED

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_stop_start_delete_dev_box(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        devbox_name = kwargs.pop("devcenter_devbox_name")
        default_user = "me"

        client = self.create_client(endpoint)

        stop_response = client.begin_stop_dev_box(project_name, default_user, devbox_name)
        stop_result = stop_response.result()
        assert stop_result.status == OperationStatus.SUCCEEDED

        start_response = client.begin_start_dev_box(project_name, default_user, devbox_name)
        start_result = start_response.result()
        assert start_result.status == OperationStatus.SUCCEEDED

        delete_response = client.begin_delete_dev_box(project_name, default_user, devbox_name)
        delete_result = delete_response.result()
        assert delete_result.status == OperationStatus.SUCCEEDED

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_catalog(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")

        client = self.create_client(endpoint)

        catalog_response = client.get_catalog(project_name, catalog_name)
        assert catalog_response.name == catalog_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_catalogs(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")

        client = self.create_client(endpoint)

        catalogs_response = client.list_catalogs(project_name)
        catalogs_response = list(catalogs_response)
        filtered_catalog_response = filter(lambda x: x.name == catalog_name, catalogs_response)
        filtered_catalog_response = list(filtered_catalog_response)
        assert len(filtered_catalog_response) == 1
        assert filtered_catalog_response[0].name == catalog_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_get_environment_definition(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)

        env_definition_response = client.get_environment_definition(project_name, catalog_name, env_definition_name)
        assert env_definition_response.name == env_definition_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_environment_definitions(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)

        all_env_definition_response = client.list_environment_definitions(project_name)
        filtered_all_env_definition_response = filter(
            lambda x: x.name == env_definition_name, all_env_definition_response
        )
        filtered_all_env_definition_response = list(filtered_all_env_definition_response)
        assert (
            len(filtered_all_env_definition_response) == 1
            and filtered_all_env_definition_response[0].name == env_definition_name
        )

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_environment_definitions_by_catalog(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        catalog_name = kwargs.pop("devcenter_catalog_name")
        env_definition_name = kwargs.pop("devcenter_environment_definition_name")

        client = self.create_client(endpoint)

        env_definitions_response = client.list_environment_definitions_by_catalog(project_name, catalog_name)
        filtered_env_definitions_response = filter(lambda x: x.name == env_definition_name, env_definitions_response)
        filtered_env_definitions_response = list(filtered_env_definitions_response)
        assert (
            len(filtered_env_definitions_response) == 1
            and filtered_env_definitions_response[0].name == env_definition_name
        )

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_list_environment_types(self, **kwargs):
        self.logger = logging.getLogger(__name__)
        endpoint = kwargs.pop("devcenter_endpoint")
        project_name = kwargs.pop("devcenter_project_name")
        environment_type_name = kwargs.pop("devcenter_environment_type_name")

        client = self.create_client(endpoint)

        env_types_response = client.list_environment_types(project_name)
        filtered_env_types_response = filter(lambda x: x.name == environment_type_name, env_types_response)
        filtered_env_types_response = list(filtered_env_types_response)
        assert len(filtered_env_types_response) == 1 and filtered_env_types_response[0].name == environment_type_name

    @DevcenterPowerShellPreparer()
    @recorded_by_proxy
    def test_environments(self, **kwargs):
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
        create_env_response = client.begin_create_or_update_environment(
            project_name, default_user, env_name, environment
        )
        create_env_result = create_env_response.result()
        assert create_env_result.provisioning_state == DevBoxProvisioningState.SUCCEEDED

        env_response = client.get_environment(project_name, default_user, env_name)
        assert env_response.name == env_name

        envs_response = client.list_environments(project_name, default_user)
        envs_response = filter(lambda x: x.name == env_name, envs_response)
        envs_response = list(envs_response)
        assert len(envs_response) == 1 and envs_response[0].name == env_response.name

        all_envs_response = client.list_all_environments(project_name)
        all_envs_response = filter(lambda x: x.name == env_name, all_envs_response)
        all_envs_response = list(all_envs_response)
        assert len(all_envs_response) == 1 and all_envs_response[0].name == env_response.name

        delete_response = client.begin_delete_environment(project_name, default_user, env_name)
        delete_result = delete_response.result()
        assert delete_result.status == OperationStatus.SUCCEEDED
