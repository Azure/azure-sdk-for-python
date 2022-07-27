# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   Runs: 5/5
#   Tasks: 6/6
#   TaskRuns: 6/6
#   PipelineRuns: 1/4
#   ImportPipelines: 4/4
#   ExportPipelines: 4/4

import unittest

import azure.mgmt.containerregistry
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'


class MgmtRegistryTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRegistryTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.containerregistry.ContainerRegistryManagementClient,
            api_version="2019-12-01-preview"  # test the latest version
        )

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_pipelines(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        PIPELINE_RUN_NAME = "myPipelineRun"
        IMPORT_PIPELINE_NAME = "myImportPipeline"
        EXPORT_PIPELINE_NAME = "myExportPipeline"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Premium"  # Pipelineruns need Premium
          },
          "admin_user_enabled": False
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ImportPipelines/put/ImportPipelineCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "identity": {
            "type": "SystemAssigned"
            # "user_assigned_identities": {}
          },
          "source": {
            "type": "AzureStorageBlobContainer",
            "uri": "https://accountname.blob.core.windows.net/containername",
            "key_vault_uri": "https://myvault.vault.azure.net/secrets/acrimportsas"
          },
          "options": [
            "OverwriteTags",
            "DeleteSourceBlobOnSuccess",
            "ContinueOnErrors"
          ]
        }
        result = self.mgmt_client.import_pipelines.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, import_pipeline_name=IMPORT_PIPELINE_NAME, import_pipeline_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExportPipelines/put/ExportPipelineCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "identity": {
            "type": "SystemAssigned"
          },
          "target": {
            "type": "AzureStorageBlobContainer",
            "uri": "https://accountname.blob.core.windows.net/containername",
            "key_vault_uri": "https://myvault.vault.azure.net/secrets/acrexportsas"
          },
          "options": [
            "OverwriteBlobs"
          ]
        }
        result = self.mgmt_client.export_pipelines.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, export_pipeline_name=EXPORT_PIPELINE_NAME, export_pipeline_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /PipelineRuns/put/PipelineRunCreate_Import[put]
#--------------------------------------------------------------------------
        BODY = {
          "request": {
            "pipeline_resource_id": "/subscriptions/" + SUBSCRIPTION_ID + "/resourceGroups/" + RESOURCE_GROUP + "/providers/Microsoft.ContainerRegistry/registries/" + REGISTRY_NAME + "/importPipelines/" + IMPORT_PIPELINE_NAME,
            "source": {
              "type": "AzureStorageBlob",
              "name": "myblob.tar.gz"
            },
            "catalog_digest": "sha256@"
          },
          "force_update_tag": "2020-03-04T17:23:21.9261521+00:00"
        }
        # result = self.mgmt_client.pipeline_runs.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, pipeline_run_name=PIPELINE_RUN_NAME, pipeline_run_create_parameters=BODY)
        # result = result.result()

#--------------------------------------------------------------------------
        # /PipelineRuns/get/PipelineRunGet[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.pipeline_runs.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, pipeline_run_name=PIPELINE_RUN_NAME)

#--------------------------------------------------------------------------
        # /ImportPipelines/get/ImportPipelineGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.import_pipelines.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, import_pipeline_name=IMPORT_PIPELINE_NAME)

#--------------------------------------------------------------------------
        # /ExportPipelines/get/ExportPipelineGet[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.export_pipelines.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, export_pipeline_name=EXPORT_PIPELINE_NAME)

#--------------------------------------------------------------------------
        # /PipelineRuns/get/PipelineRunList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.pipeline_runs.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /ImportPipelines/get/ImportPipelineList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.import_pipelines.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /ExportPipelines/get/ExportPipelineList[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.export_pipelines.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /PipelineRuns/delete/PipelineRunDelete[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.pipeline_runs.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, pipeline_run_name=PIPELINE_RUN_NAME)
        # result = result.result()

#--------------------------------------------------------------------------
        # /ImportPipelines/delete/ImportPipelineDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.import_pipelines.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, import_pipeline_name=IMPORT_PIPELINE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /ExportPipelines/delete/ExportPipelineDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.export_pipelines.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, export_pipeline_name=EXPORT_PIPELINE_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_task_run(self, resource_group):

        # UNIQUE = resource_group.name[-4:]
        RESOURCE_GROUP = resource_group.name
        REGISTRY_NAME = "myRegistry"
        TASK_RUN_NAME = "myTaskRun"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Premium"  # Taskruns need Premium
          },
          "admin_user_enabled": False
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TaskRuns/put/TaskRuns_Create[put] (TODO: add to swagger)
#--------------------------------------------------------------------------
        BODY = {
          "force_update_tag": "test",
          "run_request": {
            "type": "DockerBuildRequest",
            "image_names": ["testtaskrun:v1"],
            "is_push_enabled": True,
            "no_cache": False,
            "docker_file_path": "Dockerfile",
            "platform": {
              "os": "linux",
              "architecture": "amd64"
            },
            "source_location": "https://github.com/Azure-Samples/acr-build-helloworld-node.git",
            "is_archive_enabled": True
          }
        }
        result = self.mgmt_client.task_runs.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_run_name=TASK_RUN_NAME, task_run=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /TaskRuns/get/TaskRuns_Get[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.task_runs.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_run_name=TASK_RUN_NAME)

        RUN_ID = result.run_result.run_id

#--------------------------------------------------------------------------
        # /Runs/get/Runs_Get[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.runs.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_id=RUN_ID)

#--------------------------------------------------------------------------
        # /TaskRuns/get/TaskRuns_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.task_runs.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Runs/get/Runs_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.runs.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, top="10")

#--------------------------------------------------------------------------
        # /TaskRuns/post/TaskRuns_GetDetails[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.task_runs.get_details(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_run_name=TASK_RUN_NAME)

#--------------------------------------------------------------------------
        # /Runs/post/Runs_GetLogSasUrl[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.runs.get_log_sas_url(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_id=RUN_ID)

#--------------------------------------------------------------------------
        # /Runs/post/Runs_Cancel[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.runs.begin_cancel(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_id=RUN_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /TaskRuns/patch/TaskRuns_Update[patch] (TODO: add to swagger)
#--------------------------------------------------------------------------
        BODY = {
          "force_update_tag": "test",
          "run_request": {
            "type": "DockerBuildRequest",
            "image_names": ["testtaskrun:v1"],
            "is_push_enabled": True,
            "no_cache": False,
            "docker_file_path": "Dockerfile",
            "platform": {
              "os": "linux",
              "architecture": "amd64"
            },
            "source_location": "https://github.com/Azure-Samples/acr-build-helloworld-node.git",
            "is_archive_enabled": True
          }
        }
        result = self.mgmt_client.task_runs.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_run_name=TASK_RUN_NAME, update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Runs/post/Runs_Cancel[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.runs.begin_cancel(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_id=RUN_ID)
        result = result.result()

#--------------------------------------------------------------------------
        # /TaskRuns/delete/TaskRuns_Delete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.task_runs.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_run_name=TASK_RUN_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Runs/patch/Runs_Update[patch]
#--------------------------------------------------------------------------
        BODY = {
          "is_archive_enabled": True
        }
        result = self.mgmt_client.runs.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, run_id=RUN_ID, run_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()

    @unittest.skip('hard to test')
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_tasks(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        # UNIQUE = resource_group.name[-4:]
        REGISTRY_NAME = "myRegistry"
        RESOURCE_GROUP = resource_group.name
        TASK_RUN_NAME = "myTaskRun"
        TASK_NAME = "myTask"

#--------------------------------------------------------------------------
# /Registries/put/RegistryCreate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "key": "value"
          },
          "sku": {
            "name": "Standard"
          },
          "admin_user_enabled": True
        }
        result = self.mgmt_client.registries.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, registry=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tasks/put/Tasks_Create[put] (TODO: add to swagger)
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
        #   "identity": {
        #     "type": "SystemAssigned"
        #   },
          "tags": {
            "testkey": "value"
          },
          "status": "Enabled",
          "platform": {
            "os": "Linux",
            "architecture": "amd64"
          },
          "agent_configuration": {
            "cpu": "2"
          },
          "step": {
            "type": "Docker",
            "context_path": "https://github.com/SteveLasker/node-helloworld",
            "image_names": [
                "testtask:v1"
            ],
            "docker_file_path": "DockerFile",
            # "image_names": [
            #   "azurerest:testtag"
            # ],
            # "docker_file_path": "src/DockerFile",
            # "context_path": "src",
            "is_push_enabled": True,
            "no_cache": False,
            # "arguments": [
            #   {
            #     "name": "mytestargument",
            #     "value": "mytestvalue",
            #     "is_secret": False
            #   },
            #   {
            #     "name": "mysecrettestargument",
            #     "value": "mysecrettestvalue",
            #     "is_secret": True
            #   }
            # ]
          },
          "trigger": {
            "base_image_trigger": {
              "name": "myBaseImageTrigger",
              "base_image_trigger_type": "Runtime",
              "update_trigger_payload_type": "Default",
              "status": "Enabled"
            }
            # "timer_triggers": [
            #   {
            #     "name": "myTimerTrigger",
            #     "schedule": "30 9 * * 1-5"
            #   }
            # ],
            # "source_triggers": [
            #   {
            #     "name": "mySourceTrigger",
            #     "source_repository": {
            #       "source_control_type": "Github",
            #       "repository_url": "https://github.com/Azure/azure-rest-api-specs",
            #       "branch": "master",
            #       "source_control_auth_properties": {
            #         "token_type": "PAT",
            #         "token": "xxxxx"
            #       }
            #     },
            #     "source_trigger_events": [
            #       "commit"
            #     ]
            #   }
            # ],
            # "base_image_trigger": {
            #   "name": "myBaseImageTrigger",
            #   "base_image_trigger_type": "Runtime",
            #   "update_trigger_endpoint": "https://user:pass@mycicd.webhook.com?token=foo",
            #   "update_trigger_payload_type": "Token"
            # }
          }
        }
        result = self.mgmt_client.tasks.begin_create(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_name=TASK_NAME, task_create_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Tasks/get/Tasks_Get[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tasks.get(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_name=TASK_NAME)

#--------------------------------------------------------------------------
        # /Tasks/get/Tasks_List[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tasks.list(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)

#--------------------------------------------------------------------------
        # /Tasks/post/Tasks_GetDetails[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tasks.get_details(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_name=TASK_NAME)

#--------------------------------------------------------------------------
        # /Tasks/patch/Tasks_Update[patch] (TODO: add to swagger)
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "tags": {
            "testkey": "value"
          },
          "status": "Enabled",
          "platform": {
            "os": "Linux",
            "architecture": "amd64"
          },
          "agent_configuration": {
            "cpu": "2"
          },
          "step": {
            "type": "Docker",
            "context_path": "https://github.com/SteveLasker/node-helloworld",
            "image_names": [
                "testtask:v1"
            ],
            "docker_file_path": "DockerFile",
            "is_push_enabled": True,
            "no_cache": False,
          },
          "trigger": {
            "base_image_trigger": {
              "name": "myBaseImageTrigger",
              "base_image_trigger_type": "Runtime",
              "update_trigger_payload_type": "Default",
              "status": "Enabled"
            }
          }
        }
        result = self.mgmt_client.tasks.begin_update(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_name=TASK_NAME, task_update_parameters=BODY)
        result = result.result()

#--------------------------------------------------------------------------
# /Tasks/delete/Tasks_Delete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.tasks.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME, task_name=TASK_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /Registries/delete/RegistryDelete[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.registries.begin_delete(resource_group_name=RESOURCE_GROUP, registry_name=REGISTRY_NAME)
        result = result.result()
