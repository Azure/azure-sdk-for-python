# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.containerregistry.v2018_02_01_preview.models import (
    Registry,
    RegistryUpdateParameters,
    StorageAccountProperties,
    Sku,
    SkuName,
    SkuTier,
    ProvisioningState,
    PasswordName,
    WebhookCreateParameters,
    WebhookUpdateParameters,
    WebhookAction,
    WebhookStatus,
    BuildTask,
    SourceRepositoryProperties,
    SourceControlAuthInfo,
    PlatformProperties,
    DockerBuildStep,
    BuildTaskBuildRequest,
    BuildTaskUpdateParameters,
    SourceRepositoryUpdateParameters,
    DockerBuildStepUpdateParameters,
    SourceControlType,
    TokenType,
    OsType,
    BuildTaskStatus,
    BaseImageTriggerType,
    BuildArgument,
    QuickBuildRequest,
    BuildType
)
import azure.mgmt.storage

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


DEFAULT_LOCATION = 'eastus'
DEFAULT_REPLICATION_LOCATION = 'southcentralus'
DEFAULT_WEBHOOK_SERVICE_URI = 'http://www.microsoft.com'
DEFAULT_WEBHOOK_SCOPE = 'hello-world'
DEFAULT_KEY_VALUE_PAIR = {
    'key': 'value'
}
# This token requires 'admin:repo_hook' access. Recycle the token after recording tests.
DEFAULT_GIT_ACCESS_TOKEN = 'f431834b9161510c40d49f0626f975a962a3c856'
DEFAULT_REPOSITORY_URL = 'https://github.com/djyou/BuildTest'


class MgmtACRTest20180201Preview(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtACRTest20180201Preview, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient,
            api_version='2018-02-01-preview'
        )


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_managed_registry(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')

        name_status = self.client.registries.check_name_availability(registry_name)
        self.assertTrue(name_status.name_available)

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)
        self._core_registry_scenario(registry_name, resource_group.name)


    def _core_registry_scenario(self, registry_name, resource_group_name):
        registries = list(self.client.registries.list_by_resource_group(resource_group_name))
        self.assertEqual(len(registries), 1)

        # Update the registry with new tags and enable admin user
        registry = self.client.registries.update(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            registry_update_parameters=RegistryUpdateParameters(
                tags=DEFAULT_KEY_VALUE_PAIR,
                admin_user_enabled=True
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        registry = self.client.registries.get(resource_group_name, registry_name)
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(registry.admin_user_enabled, True)

        credentials = self.client.registries.list_credentials(resource_group_name, registry_name)
        self.assertEqual(len(credentials.passwords), 2)

        credentials = self.client.registries.regenerate_credential(
            resource_group_name, registry_name, PasswordName.password)
        self.assertEqual(len(credentials.passwords), 2)

        if registry.sku.name == SkuName.premium.value:
            usages = self.client.registries.list_usages(resource_group_name, registry_name)
            self.assertTrue(len(usages.value) > 1)

        self.client.registries.delete(resource_group_name, registry_name).wait()


    def _create_managed_registry(self, registry_name, resource_group_name, location):
        registry = self.client.registries.create(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            registry=Registry(
                location=location,
                sku=Sku(
                    name=SkuName.premium
                )
            )
        ).result()
        self.assertEqual(registry.name, registry_name)
        self.assertEqual(registry.location, location)
        self.assertEqual(registry.sku.name, SkuName.premium.value)
        self.assertEqual(registry.sku.tier, SkuTier.premium.value)
        self.assertEqual(registry.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(registry.admin_user_enabled, False)
        self.assertEqual(registry.storage_account, None)


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_webhook(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        webhook_name = self.get_resource_name('pyacr')

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a webhook
        webhook = self.client.webhooks.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            webhook_name=webhook_name,
            webhook_create_parameters=WebhookCreateParameters(
                location=location,
                service_uri=DEFAULT_WEBHOOK_SERVICE_URI,
                actions=[WebhookAction.push]
            )
        ).result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.location, location)
        self.assertEqual(webhook.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(webhook.actions, [WebhookAction.push.value])
        self.assertEqual(webhook.status, WebhookStatus.enabled.value)

        webhooks = list(self.client.webhooks.list(resource_group.name, registry_name))
        self.assertEqual(len(webhooks), 1)

        # Update the webhook with custom headers, scope, and new tags
        webhook = self.client.webhooks.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            webhook_name=webhook_name,
            webhook_update_parameters=WebhookUpdateParameters(
                tags=DEFAULT_KEY_VALUE_PAIR,
                custom_headers=DEFAULT_KEY_VALUE_PAIR,
                scope=DEFAULT_WEBHOOK_SCOPE
            )
        ).result()
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(webhook.scope, DEFAULT_WEBHOOK_SCOPE)

        webhook = self.client.webhooks.get(resource_group.name, registry_name, webhook_name)
        self.assertEqual(webhook.name, webhook_name)
        self.assertEqual(webhook.tags, DEFAULT_KEY_VALUE_PAIR)
        self.assertEqual(webhook.scope, DEFAULT_WEBHOOK_SCOPE)

        webhook_config = self.client.webhooks.get_callback_config(
            resource_group.name,
            registry_name,
            webhook_name
        )
        self.assertEqual(webhook_config.service_uri, DEFAULT_WEBHOOK_SERVICE_URI)
        self.assertEqual(webhook_config.custom_headers, DEFAULT_KEY_VALUE_PAIR)

        self.client.webhooks.ping(resource_group.name, registry_name, webhook_name)
        self.client.webhooks.list_events(resource_group.name, registry_name, webhook_name)

        self.client.webhooks.delete(resource_group.name, registry_name, webhook_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_replication(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        replication_name = DEFAULT_REPLICATION_LOCATION

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a replication
        replication = self.client.replications.create(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            replication_name=replication_name,
            location=DEFAULT_REPLICATION_LOCATION
        ).result()
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.location, DEFAULT_REPLICATION_LOCATION)
        self.assertEqual(replication.provisioning_state, ProvisioningState.succeeded.value)

        replications = list(self.client.replications.list(resource_group.name, registry_name))
        self.assertEqual(len(replications), 2) # 2 because a replication in home region is auto created

        # Update the replication with new tags
        replication = self.client.replications.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            replication_name=replication_name,
            tags=DEFAULT_KEY_VALUE_PAIR
        ).result()
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.tags, DEFAULT_KEY_VALUE_PAIR)

        replication = self.client.replications.get(resource_group.name, registry_name, replication_name)
        self.assertEqual(replication.name, replication_name)
        self.assertEqual(replication.tags, DEFAULT_KEY_VALUE_PAIR)

        self.client.replications.delete(resource_group.name, registry_name, replication_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


    def _create_build_task(self, build_task_name, registry_name, resource_group_name, location):
        build_task_create_parameters = BuildTask(
            location=location,
            alias=build_task_name,
            source_repository=SourceRepositoryProperties(
                source_control_type=SourceControlType.github,
                repository_url=DEFAULT_REPOSITORY_URL,
                is_commit_trigger_enabled=True,
                source_control_auth_properties=SourceControlAuthInfo(
                    token=DEFAULT_GIT_ACCESS_TOKEN,
                    token_type=TokenType.pat,
                    refresh_token='',
                    scope='repo',
                    expires_in=1313141
                )
            ),
            platform=PlatformProperties(os_type=OsType.linux, cpu=1),
            status=BuildTaskStatus.enabled
        )

        build_task = self.client.build_tasks.create(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            build_task_create_parameters=build_task_create_parameters
        ).result()

        self.assertEqual(build_task.name, build_task_name)
        self.assertEqual(build_task.location, location)
        self.assertEqual(build_task.platform.os_type, OsType.linux.value)
        self.assertEqual(build_task.platform.cpu, 1)
        self.assertEqual(build_task.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(build_task.status, BuildTaskStatus.enabled.value)
        self.assertEqual(build_task.source_repository.repository_url, DEFAULT_REPOSITORY_URL)
        self.assertEqual(build_task.source_repository.source_control_type, SourceControlType.github.value)
        self.assertEqual(build_task.source_repository.is_commit_trigger_enabled, True)


    def _create_build_step(self, build_step_name, build_task_name, registry_name, resource_group_name, location):
        docker_build_step = DockerBuildStep(
            branch='master',
            image_names=['repo:tag'],
            is_push_enabled=True,
            no_cache=False,
            docker_file_path='Dockerfile',
            build_arguments=[],
            base_image_trigger=BaseImageTriggerType.runtime
        )

        build_step = self.client.build_steps.create(
            resource_group_name=resource_group_name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            step_name=build_step_name,
            properties=docker_build_step
        ).result()

        self.assertEqual(build_step.name, build_step_name)
        self.assertEqual(build_step.properties.branch, 'master')
        self.assertEqual(build_step.properties.image_names, ['repo:tag'])
        self.assertEqual(build_step.properties.is_push_enabled, True)
        self.assertEqual(build_step.properties.no_cache, False)
        self.assertEqual(build_step.properties.docker_file_path, 'Dockerfile')
        self.assertEqual(build_step.properties.build_arguments, [])
        self.assertEqual(build_step.properties.base_image_trigger, BaseImageTriggerType.runtime.value)
        self.assertEqual(build_step.properties.provisioning_state, ProvisioningState.succeeded.value)


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def _disabled_test_build_task(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        build_task_name = self.get_resource_name('pyacr')

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a build task
        self._create_build_task(build_task_name, registry_name, resource_group.name, location)

        # List build tasks
        build_tasks = list(self.client.build_tasks.list(resource_group.name, registry_name))
        self.assertEqual(len(build_tasks), 1)

        # Get the build task source repository properties
        source_repository_properties = self.client.build_tasks.list_source_repository_properties(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name)

        self.assertEqual(source_repository_properties.repository_url, DEFAULT_REPOSITORY_URL)
        self.assertEqual(source_repository_properties.source_control_type, SourceControlType.github.value)
        self.assertEqual(source_repository_properties.is_commit_trigger_enabled, True)
        self.assertEqual(source_repository_properties.source_control_type, SourceControlType.github.value)
        self.assertEqual(source_repository_properties.source_control_auth_properties.token, DEFAULT_GIT_ACCESS_TOKEN)
        self.assertEqual(source_repository_properties.source_control_auth_properties.token_type, TokenType.pat)

        # Update the build task
        build_task_update_parameters = BuildTaskUpdateParameters(
            alias=build_task_name,
            source_repository=SourceRepositoryUpdateParameters(
                is_commit_trigger_enabled=False
            ),
            platform=PlatformProperties(os_type=OsType.windows, cpu=1),
            status=BuildTaskStatus.disabled,
            timeout=10000
        )

        build_task = self.client.build_tasks.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            build_task_update_parameters=build_task_update_parameters
        ).result()

        self.assertEqual(build_task.name, build_task_name)
        self.assertEqual(build_task.location, location)
        self.assertEqual(build_task.platform.os_type, OsType.windows.value)
        self.assertEqual(build_task.platform.cpu, 1)
        self.assertEqual(build_task.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(build_task.status, BuildTaskStatus.disabled.value)
        self.assertEqual(build_task.timeout, 10000)
        self.assertEqual(build_task.source_repository.repository_url, DEFAULT_REPOSITORY_URL)
        self.assertEqual(build_task.source_repository.source_control_type, SourceControlType.github.value)
        self.assertEqual(build_task.source_repository.is_commit_trigger_enabled, False)

        # Get the build task
        build_task = self.client.build_tasks.get(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name)

        self.assertEqual(build_task.name, build_task_name)
        self.assertEqual(build_task.location, location)
        self.assertEqual(build_task.platform.os_type, OsType.windows.value)
        self.assertEqual(build_task.platform.cpu, 1)
        self.assertEqual(build_task.provisioning_state, ProvisioningState.succeeded.value)
        self.assertEqual(build_task.status, BuildTaskStatus.disabled.value)
        self.assertEqual(build_task.timeout, 10000)
        self.assertEqual(build_task.source_repository.repository_url, DEFAULT_REPOSITORY_URL)
        self.assertEqual(build_task.source_repository.source_control_type, SourceControlType.github.value)
        self.assertEqual(build_task.source_repository.is_commit_trigger_enabled, False)

        # Delete the build task
        self.client.build_tasks.delete(resource_group.name, registry_name, build_task_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def _disabled_test_build_step(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')
        build_task_name = self.get_resource_name('pyacr')
        build_step_name = self.get_resource_name('pyacr')

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        # Create a build task
        self._create_build_task(build_task_name, registry_name, resource_group.name, location)

        # Create a build step
        self._create_build_step(build_step_name, build_task_name, registry_name, resource_group.name, location)

        # List build steps
        build_steps = list(self.client.build_steps.list(resource_group.name, registry_name, build_task_name))
        self.assertEqual(len(build_steps), 1)

        # Update the build step
        build_step_update_parameters = DockerBuildStepUpdateParameters(
            branch='dev',
            image_names=['repo1:tag1', 'repo2:tag2'],
            is_push_enabled=False,
            no_cache=True,
            docker_file_path='src\Dockerfile',
            build_arguments=[
                BuildArgument(name='key1', value='value1', is_secret=False),
                BuildArgument(name='key2', value='value2', is_secret=True)
            ],
            base_image_trigger=BaseImageTriggerType.none
        )

        build_step = self.client.build_steps.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            step_name=build_step_name,
            properties=build_step_update_parameters
        ).result()

        self.assertEqual(build_step.name, build_step_name)
        self.assertEqual(build_step.properties.branch, 'dev')
        self.assertEqual(build_step.properties.image_names, ['repo1:tag1', 'repo2:tag2'])
        self.assertEqual(build_step.properties.is_push_enabled, False)
        self.assertEqual(build_step.properties.no_cache, True)
        self.assertEqual(build_step.properties.docker_file_path, 'src\Dockerfile')
        self.assertEqual(build_step.properties.build_arguments[0].name, 'key1')
        self.assertEqual(build_step.properties.build_arguments[0].value, 'value1')
        self.assertEqual(build_step.properties.build_arguments[0].is_secret, False)
        self.assertEqual(build_step.properties.base_image_trigger, BaseImageTriggerType.none.value)
        self.assertEqual(build_step.properties.provisioning_state, ProvisioningState.succeeded.value)

        # Get the build step
        build_step = self.client.build_steps.get(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            step_name=build_step_name)

        self.assertEqual(build_step.name, build_step_name)
        self.assertEqual(build_step.properties.branch, 'dev')
        self.assertEqual(build_step.properties.image_names, ['repo1:tag1', 'repo2:tag2'])
        self.assertEqual(build_step.properties.is_push_enabled, False)
        self.assertEqual(build_step.properties.no_cache, True)
        self.assertEqual(build_step.properties.docker_file_path, 'src\Dockerfile')
        self.assertEqual(build_step.properties.build_arguments[0].name, 'key1')
        self.assertEqual(build_step.properties.build_arguments[0].value, 'value1')
        self.assertEqual(build_step.properties.build_arguments[0].is_secret, False)
        self.assertEqual(build_step.properties.base_image_trigger, BaseImageTriggerType.none.value)
        self.assertEqual(build_step.properties.provisioning_state, ProvisioningState.succeeded.value)

        # Get the build step build arguments
        build_arguments = list(self.client.build_steps.list_build_arguments(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_task_name=build_task_name,
            step_name=build_step_name))

        self.assertEqual(len(build_arguments), 2)

        # Delete the build step
        self.client.build_steps.delete(resource_group.name, registry_name, build_task_name, build_step_name).wait()
        self.client.build_tasks.delete(resource_group.name, registry_name, build_task_name).wait()
        self.client.registries.delete(resource_group.name, registry_name).wait()


    @ResourceGroupPreparer(location=DEFAULT_LOCATION)
    def test_build(self, resource_group, location):
        registry_name = self.get_resource_name('pyacr')

        # Create a managed registry
        self._create_managed_registry(registry_name, resource_group.name, location)

        build_request = QuickBuildRequest(
            source_location=DEFAULT_REPOSITORY_URL,
            platform=PlatformProperties(os_type='Linux'),
            docker_file_path='Dockerfile',
            image_names=['repo:tag'],
            is_push_enabled=True,
            timeout=3600,
            build_arguments=[])

        # Get build source upload url
        self.client.registries.get_build_source_upload_url(
            resource_group_name=resource_group.name,
            registry_name=registry_name)

        # Queue a build
        queued_build = self.client.registries.queue_build(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_request=build_request).result()

        build_id = queued_build.build_id

        # List builds
        builds = list(self.client.builds.list(
            resource_group_name=resource_group.name,
            registry_name=registry_name))

        self.assertEqual(len(builds), 1)
        self.assertEqual(builds[0].build_id, build_id)
        self.assertEqual(builds[0].build_type, BuildType.quick_build.value)

        # Get the build
        build = self.client.builds.get(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_id=build_id)

        self.assertEqual(build.build_id, build_id)
        self.assertEqual(build.build_type, BuildType.quick_build.value)
        self.assertEqual(build.is_archive_enabled, False)

        # Update the build
        build = self.client.builds.update(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_id=build_id,
            is_archive_enabled=True).result()

        self.assertEqual(build.build_id, build_id)
        self.assertEqual(build.build_type, BuildType.quick_build.value)
        self.assertEqual(build.is_archive_enabled, True)

        # Get log link
        self.client.builds.get_log_link(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_id=build_id)

        # Cancel a build
        self.client.builds.cancel(
            resource_group_name=resource_group.name,
            registry_name=registry_name,
            build_id=build_id).wait()

        # Delete the registry
        self.client.registries.delete(resource_group.name, registry_name).wait()


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
