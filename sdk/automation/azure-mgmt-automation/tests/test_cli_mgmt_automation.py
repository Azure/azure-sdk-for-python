# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 147
# Methods Covered : 146
# Examples Total  : 167
# Examples Tested : 166
# Coverage %      : 98.72499898162857
# ----------------------

# current coverage: 85

import time
import unittest

import azure.mgmt.automation
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtAutomationClientTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtAutomationClientTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.automation.AutomationClient
        )
    
    @ResourceGroupPreparer(location=AZURE_LOCATION)
    def test_automation(self, resource_group):

        SERVICE_NAME = "myapimrndxyz"
        AUTOMATION_ACCOUNT_NAME = 'myAutomationAccount9'
        JOB_NAME = "job1"
        MODULE_NAME = "module1"
        WEBHOOK_NAME = "webhook1"
        WATCHER_NAME = "MyTestWatcher"
        SCHEDULE_NAME = "mySchedule"

        # Create or update automation account[put]
        BODY = {
          "sku": {
            "name": "Free"
          },
          "name": "myAutomationAccount9",
          "location": "East US 2"
        }
        result = self.mgmt_client.automation_account.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, BODY)

        RUNBOOK_DRAFT_NAME =  "runbook_draft"
        # Create runbook as draft[put]
        BODY = {
          "log_verbose": False,
          "log_progress": False,
          "runbook_type": "PowerShellWorkflow",
          "draft": {},
          "description": "Description of the Runbook",
          "name": RUNBOOK_DRAFT_NAME,
          "location": "East US 2",
          "tags": {
            "tag01": "value01",
            "tag02": "value02",
          }
        }
        result = self.mgmt_client.runbook.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_DRAFT_NAME, BODY)

        # Create or update a module[put]
        BODY = {
          "content_link": {
            "uri": "https://teststorage.blob.core.windows.net/dsccomposite/OmsCompositeResources.zip",
            "content_hash": {
              "algorithm": "sha265",
              "value": "07E108A962B81DD9C9BAA89BB47C0F6EE52B29E83758B07795E408D258B2B87A"
            },
            "version": "1.0.0.0"
          }
        }
        result = self.mgmt_client.module.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, BODY)

        RUNBOOK_NAME =  "Get-AzureVMTutorial"
        # Create or update runbook and publish it[put]
        BODY = {
          "log_verbose": False,
          "log_progress": True,
          "runbook_type": "PowerShellWorkflow",
          "publish_content_link": {
            "uri": "https://raw.githubusercontent.com/Azure/azure-quickstart-templates/0.0.0.3/101-automation-runbook-getvms/Runbooks/Get-AzureVMTutorial.ps1",
            "content_hash": {
              "algorithm": "SHA256",
              "value": "4fab357cab33adbe9af72ae4b1203e601e30e44de271616e376c08218fd10d1c"
            },
          },
          "description": "Description of the Runbook",
          "log_activity_trace": "1",
          "name": RUNBOOK_NAME,
          "location": "East US 2",
          "tags": {
            "tag01": "value01",
            "tag02": "value02"
          }
        }
        result = self.mgmt_client.runbook.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, BODY)

        # Create job[put]
        BODY = {
          "runbook": {
            "name": RUNBOOK_NAME
          },
          "parameters": {
            "key01": "value01",
            "key02": "value02"
          },
          "run_on": ""
        }
        result = self.mgmt_client.job.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME, BODY)

        # Create or update webhook[put]
        BODY = {
          "name": "TestWebhook",
          "is_enabled": True,
          "uri": "https://s1events.azure-automation.net/webhooks?token=7u3KfQvM1vUPWaDMFRv2%2fAA4Jqx8QwS8aBuyO6Xsdcw%3d",
          "expiry_time": "2021-03-29T22:18:13.7002872Z",
          "runbook": {
            "name": RUNBOOK_NAME
          }
        }
        result = self.mgmt_client.webhook.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, WEBHOOK_NAME, BODY)

        """ TODO: response 500 error
        # Create or update watcher[put]
        BODY = {
          "name": "MyTestWatcher",
          "type": None,
          "location": None,
          "tags": {},
          "etag": None,
          "execution_frequency_in_seconds": "60",
          "script_name": RUNBOOK_NAME,
          "description": "This is a test watcher.",
          "script_run_on": "MyTestHybridWorkerGroup",
          "scriptParameters": None,
          "creation_time": "2020-03-01T11:22:47.7333333+00:00",
          "lastModifiedBy": None,
          "last_modified_time": "2020-03-01T11:22:47.7333333+00:00"
        }
        result = self.mgmt_client.watcher.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME, BODY)
        """

        # Create or update a schedule[put]
        BODY = {
          "name": "mySchedule",
          "description": "my description of schedule goes here",
          "start_time": "2021-06-27T17:28:57.2494819Z",
          "expiry_time": "2022-01-01T17:28:57.2494819Z",
          "interval": "1",
          "frequency": "Hour"
        }
        result = self.mgmt_client.schedule.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, SCHEDULE_NAME, BODY)

        VARIABLE_NAME = "sampleVariable"
        # Create or update a variable[put]
        BODY = {
          "name": "sampleVariable",
          "value": "\"ComputerName.domain.com\"",
          "description": "my description",
          "is_encrypted": False
        }
        result = self.mgmt_client.variable.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, VARIABLE_NAME, BODY)

        CREDENTIAL_NAME = "myCredential"
        # Create a credential[put]
        BODY = {
          "name": "myCredential",
          "user_name": "mylingaiah",
          "password": "myPassw0rd",
          "description": "my description goes here"
        }
        result = self.mgmt_client.credential.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CREDENTIAL_NAME, BODY)

        """
        CERTIFICATE_NAME = "testCert"
        # Create or update a certificate[put]
        BODY = {
          "name": "testCert",
          "base64value": "base 64 value of cert",
          "description": "Sample Cert",
          "thumbprint": "thumbprint of cert",
          "is_exportable": False
        }
        result = self.mgmt_client.certificate.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CERTIFICATE_NAME, BODY)

        CONNECTION_NAME = "mysConnection"
        # Create or update connection[put]
        BODY = {
          "name": "mysConnection",
          "description": "my description goes here",
          "connection_type": {
            "name": "Azure"
          },
          "field_definition_values": {
            "automation_certificate_name": CERTIFICATE_NAME,
            "subscription_id": "subid"
          }
        }
        result = self.mgmt_client.connection.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_NAME, BODY)

        JOB_SCHEDULE_NAME = "ScheduleNameGoesHere332204b5-debe-4348-a5c7-6357457189f2"
        # Create a job schedule[put]
        BODY = {
          "schedule": {
            "name": "ScheduleNameGoesHere332204b5-debe-4348-a5c7-6357457189f2"
          },
          "runbook": {
            "name": RUNBOOK_NAME
          },
          "parameters": {
            "jobscheduletag01": "jobschedulevalue01",
            "jobscheduletag02": "jobschedulevalue02"
          }
        }
        result = self.mgmt_client.job_schedule.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_SCHEDULE_NAME, BODY)

        CONFIGURATION_NAME = "SetupServer"
        # Create or Update Configuration[put]
        BODY = {
          "source": {
            "hash": {
              "algorithm": "sha256",
              "value": "A9E5DB56BA21513F61E0B3868816FDC6D4DF5131F5617D7FF0D769674BD5072F"
            },
            "type": "embeddedContent",
            "value": "Configuration SetupServer {\r\n    Node localhost {\r\n                               WindowsFeature IIS {\r\n                               Name = \"Web-Server\";\r\n            Ensure = \"Present\"\r\n        }\r\n    }\r\n}"
          },
          "description": "sample configuration"
          "name": "SetupServer",
          "location": "East US 2"
        }
        result = self.mgmt_client.dsc_configuration.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONFIGURATION_NAME, BODY)

        SOURCE_CONTROL_NAME = "sourceControl"
        # Create or update a source control[put]
        BODY = {
          "repo_url": "https://sampleUser.visualstudio.com/myProject/_git/myRepository",
          "branch": "master",
          "folder_path": "/folderOne/folderTwo",
          "auto_sync": True,
          "publish_runbook": True,
          "source_type": "VsoGit",
          "security_token": {
            "access_token": "3a326f7a0dcd343ea58fee21f2fd5fb4c1234567",
            "token_type": "PersonalAccessToken"
          },
          "description": "my description"
        }
        result = self.mgmt_client.source_control.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, BODY)

        PYTHON2PACKAGE_NAME = "pythonPackage"
        # Create or update a python 2 package[put]
        BODY = {
          "content_link": {
            "uri": "https://teststorage.blob.core.windows.net/dsccomposite/OmsCompositeResources.zip",
            "content_hash": {
              "algorithm": "sha265",
              "value": "07E108A962B81DD9C9BAA89BB47C0F6EE52B29E83758B07795E408D258B2B87A"
            },
            "version": "1.0.0.0"
          }
        }
        result = self.mgmt_client.python2package.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, PYTHON2PACKAGE_NAME, BODY)

        COMPILATIONJOB_NAME = "compilationJob"
        # Create or update a DSC Compilation job[put]
        BODY = {
          "configuration": {
            "name": "SetupServer"
          }
        }
        result = self.mgmt_client.dsc_compilation_job.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, COMPILATIONJOB_NAME, BODY)
        result = result.result()

        CONNECTION_TYPE_NAME = "myCT"
        # Create or update connection type[put]
        BODY = {
          "name": "myCT",
          "is_global": False,
          "field_definitions": {
            "my_string_field": {
              "is_encrypted": False,
              "is_optional": False,
              "type": "string"
            },
            "my_bool_field": {
              "is_encrypted": False,
              "is_optional": False,
              "type": "bool"
            },
            "my_string_field_encrypted": {
              "is_encrypted": True,
              "is_optional": False,
              "type": "string"
            }
          }
        }
        result = self.mgmt_client.connection_type.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_TYPE_NAME, BODY)

        NODE_CONFIGURATION_NAME = "configName.nodeConfigName"
        # Create node configuration[put]
        BODY = {
          "name": "configName.nodeConfigName",
          "source": {
            "hash": {
              "algorithm": "sha256",
              "value": "6DE256A57F01BFA29B88696D5E77A383D6E61484C7686E8DB955FA10ACE9FFE5"
            },
            "type": "embeddedContent",
            "value": "\r\ninstance of MSFT_RoleResource as $MSFT_RoleResource1ref\r\n{\r\nResourceID = \"[WindowsFeature]IIS\";\r\n Ensure = \"Present\";\r\n SourceInfo = \"::3::32::WindowsFeature\";\r\n Name = \"Web-Server\";\r\n ModuleName = \"PsDesiredStateConfiguration\";\r\n\r\nModuleVersion = \"1.0\";\r\r\n ConfigurationName = \"configName\";\r\r\n};\r\ninstance of OMI_ConfigurationDocument\r\n\r\r\n                    {\r\n Version=\"2.0.0\";\r\n \r\r\n                        MinimumCompatibleVersion = \"1.0.0\";\r\n \r\r\n                        CompatibleVersionAdditionalProperties= {\"Omi_BaseResource:ConfigurationName\"};\r\n \r\r\n                        Author=\"weijiel\";\r\n \r\r\n                        GenerationDate=\"03/30/2017 13:40:25\";\r\n \r\r\n                        GenerationHost=\"TEST-BACKEND\";\r\n \r\r\n                        Name=\"configName\";\r\n\r\r\n                    };\r\n",
            "version": "1.0"
          },
          "increment_node_configuration_build": True,
          "configuration": {
            "name": "configName"
          }
        }
        result = self.mgmt_client.dsc_node_configuration.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_CONFIGURATION_NAME, BODY)
        result = result.result()

        DRAFT_NAME = "Get-AzureVMTutorial"
        # Create or update runbook draft[put]
        result = self.mgmt_client.runbook_draft.replace_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)
        result = result.result()

        # Create test job[put]
        BODY = {
          "key01": "value01",
          "key02": "value02"
          "run_on": ""
        }
        result = self.mgmt_client.test_job.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME, BODY)

        
        SOFTWARE_UPDATE_CONFIGURATION_NAME = "softconfig"
        # Create software update configuration[put]
        BODY = {
          "update_configuration": {
            "operating_system": "Windows",
            "duration": "PT2H0M",
            "windows": {
              "excluded_kb_numbers": [
                "168934",
                "168973"
              ],
              "included_update_classifications": "Critical",
              "reboot_setting": "IfRequired"
            },
            "azure_virtual_machines": [
              "/subscriptions/5ae68d89-69a4-454f-b5ce-e443cc4e0067/resourceGroups/myresources/providers/Microsoft.Compute/virtualMachines/vm-01",
              "/subscriptions/5ae68d89-69a4-454f-b5ce-e443cc4e0067/resourceGroups/myresources/providers/Microsoft.Compute/virtualMachines/vm-02",
              "/subscriptions/5ae68d89-69a4-454f-b5ce-e443cc4e0067/resourceGroups/myresources/providers/Microsoft.Compute/virtualMachines/vm-03"
            ],
            "non_azure_computer_names": [
              "box1.contoso.com",
              "box2.contoso.com"
            ],
            "targets": {
              "azure_queries": [
                {
                  "scope": [
                    "/subscriptions/5ae68d89-69a4-454f-b5ce-e443cc4e0067/resourceGroups/myresources",
                    "/subscriptions/5ae68d89-69a4-454f-b5ce-e443cc4e0067"
                  ],
                  "tag_settings": {
                    "tags": [
                      {
                        "tag1": [
                          "tag1Value1",
                          "tag1Value2",
                          "tag1Value3"
                        ]
                      },
                      {
                        "tag2": [
                          "tag2Value1",
                          "tag2Value2",
                          "tag2Value3"
                        ]
                      }
                    ],
                    "filter_operator": "All"
                  },
                  "locations": [
                    "Japan East",
                    "UK South"
                  ]
                }
              ],
              "non_azure_queries": [
                {
                  "function_alias": "SavedSearch1",
                  "workspace_id": "WorkspaceId1"
                },
                {
                  "function_alias": "SavedSearch2",
                  "workspace_id": "WorkspaceId2"
                }
              ]
            }
          },
          "schedule_info": {
            "frequency": "Hour",
            "start_time": "2017-10-19T12:22:57+00:00",
            "time_zone": "America/Los_Angeles",
            "interval": "1",
            "expiry_time": "2018-11-09T11:22:57+00:00",
            "advanced_schedule": {
              "week_days": [
                "Monday",
                "Thursday"
              ]
            }
          },
          "tasks": {
            "pre_task": {
              "source": "HelloWorld",
              "parameters": {
                "computername": "Computer1"
              }
            },
            "post_task": {
              "source": "GetCache"
            }
          }
        }
        result = self.mgmt_client.software_update_configurations.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOFTWARE_UPDATE_CONFIGURATION_NAME, BODY)

        SOURCE_CONTROL_SYNC_JOB_NAME = "sourceControlJobName"
        # Create or update a source control sync job[put]
        BODY = {
          "commit_id": "9de0980bfb45026a3d97a1b0522d98a9f604226e"
        }
        result = self.mgmt_client.source_control_sync_job.create(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, SOURCE_CONTROL_SYNC_JOB_NAME, BODY)

        # # Get a sync job stream identified by sync job stream id.[get]
        # result = self.mgmt_client.source_control_sync_job_streams.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, SOURCE_CONTROL_SYNC_JOB_NAME, STREAM_NAME)

        # Get a list of sync job streams identified by sync job id[get]
        result = self.mgmt_client.source_control_sync_job_streams.list_by_sync_job(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, SOURCE_CONTROL_SYNC_JOB_NAME)

        # Get a source control sync job by job id[get]
        result = self.mgmt_client.source_control_sync_job.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, SOURCE_CONTROL_SYNC_JOB_NAME)

        # # Get software update configuration machine run[get]
        # result = self.mgmt_client.software_update_configuration_machine_runs.get_by_id(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOFTWARE_UPDATE_CONFIGURATION_MACHINE_RUN_NAME)

        # # Get test job stream[get]
        # result = self.mgmt_client.test_job_streams.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME, STREAM_NAME)

        # # Get software update configuration runs by Id[get]
        # result = self.mgmt_client.software_update_configuration_runs.get_by_id(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOFTWARE_UPDATE_CONFIGURATION_RUN_NAME)

        # # Get a list of fields of a given type[get]
        # result = self.mgmt_client.object_data_types.list_fields_by_module_and_type(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, OBJECT_DATA_TYPE_NAME)

        # Get software update configuration by name[get]
        result = self.mgmt_client.software_update_configurations.get_by_name(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOFTWARE_UPDATE_CONFIGURATION_NAME)

        # # Get a DSC Compilation job stream by job stream id[get]
        # result = self.mgmt_client.dsc_compilation_job.get_stream(resource_group.name, AUTOMATION_ACCOUNT_NAME, COMPILATIONJOB_NAME, STREAM_NAME)

        # # Get a hybrid worker group[get]
        # result = self.mgmt_client.hybrid_runbook_worker_group.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, HYBRID_RUNBOOK_WORKER_GROUP_NAME)

        # Get a list of source control sync jobs[get]
        result = self.mgmt_client.source_control_sync_job.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME)
        """

        # List job streams by job name[get]
        result = self.mgmt_client.job_stream.list_by_job(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        """
        # # Get Activity in a module[get]
        # result = self.mgmt_client.activity.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, ACTIVITY_NAME)

        # # Get content of node[get]
        # result = self.mgmt_client.node_reports.get_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_NAME, REPORT_NAME)

        # # Get a list of fields of a given type[get]
        # result = self.mgmt_client.object_data_types.list_fields_by_module_and_type(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, OBJECT_DATA_TYPE_NAME)

        # # Get a list of fields of a given type across all accessible modules[get]
        # result = self.mgmt_client.object_data_types.list_fields_by_type(resource_group.name, AUTOMATION_ACCOUNT_NAME, OBJECT_DATA_TYPE_NAME)

        # Get runbook draft content[get]
        result = self.mgmt_client.runbook_draft.get_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)

        # # Get test job[get]
        # result = self.mgmt_client.test_job.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)

        # List DSC Compilation job streams[get]
        result = self.mgmt_client.dsc_compilation_job_stream.list_by_job(resource_group.name, AUTOMATION_ACCOUNT_NAME, COMPILATIONJOB_NAME)

        # Get a DSC node configuration[get]
        result = self.mgmt_client.dsc_node_configuration.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_CONFIGURATION_NAME)

        # Get DSC Configuration content[get]
        result = self.mgmt_client.dsc_configuration.get_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONFIGURATION_NAME)

        # # Get job stream[get]
        # result = self.mgmt_client.job_stream.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME, STREAM_NAME)

        # Get connection type[get]
        result = self.mgmt_client.connection_type.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_TYPE_NAME)

        # Get a DSC Compilation job[get]
        result = self.mgmt_client.dsc_compilation_job.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, COMPILATIONJOB_NAME)

        # Get a python 2 package[get]
        result = self.mgmt_client.python2package.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, PYTHON2PACKAGE_NAME)

        # Get a source control[get]
        result = self.mgmt_client.source_control.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME)

        # Get a DSC Configuration[get]
        result = self.mgmt_client.dsc_configuration.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONFIGURATION_NAME)
        """

        # List software update configuration machine runs for a specific software update configuration run[get]
        result = self.mgmt_client.software_update_configuration_machine_runs.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List software update configuration machine runs[get]
        result = self.mgmt_client.software_update_configuration_runs.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List activities by a module[get]
        result = self.mgmt_client.activity.list_by_module(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME)

        """
        # Get a job schedule[get]
        result = self.mgmt_client.job_schedule.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_SCHEDULE_NAME)
        """

        # Get runbook content[get]
        # result = self.mgmt_client.runbook.get_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME)

        """
        # Get a certificate[get]
        result = self.mgmt_client.certificate.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, CERTIFICATE_NAME)
        """

        # Get Job Runbook Content[get]
        # result = self.mgmt_client.job.get_runbook_content(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        # Get runbook draft[get]
        result = self.mgmt_client.runbook_draft.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_DRAFT_NAME)

        """
        # Get a connection[get]
        result = self.mgmt_client.connection.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_NAME)
        """

        # Get a credential[get]
        result = self.mgmt_client.credential.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, CREDENTIAL_NAME)

        """
        # # Get node's status counts[get]
        # result = self.mgmt_client.node_count_information.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODECOUNT_NAME)

        # # Get node's node configuration counts[get]
        # result = self.mgmt_client.node_count_information.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODECOUNT_NAME)
        """

        # List software update configuration machine run with status equal to 'Failed'[get]
        result = self.mgmt_client.software_update_configuration_runs.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List software update configuration machine runs[get]
        result = self.mgmt_client.software_update_configuration_runs.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # # List DSC reports by node id.[get]
        # result = self.mgmt_client.node_reports.list_by_node(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_NAME)

        # Get a variable[get]
        result = self.mgmt_client.variable.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, VARIABLE_NAME)

        # Get a schedule[get]
        result = self.mgmt_client.schedule.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, SCHEDULE_NAME)

        """
        # Get the agent registration information[get]
        result = self.mgmt_client.agent_registration_information.get(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List software update configurations Targeting a specific azure virtual machine[get]
        result = self.mgmt_client.software_update_configurations.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List software update configurations[get]
        result = self.mgmt_client.software_update_configurations.list(resource_group.name, AUTOMATION_ACCOUNT_NAME)
        """

        # Get runbook[get]
        result = self.mgmt_client.runbook.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME)

        # List job streams by job name[get]
        result = self.mgmt_client.job_stream.list_by_job(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        """
        # Get watcher[get]
        result = self.mgmt_client.watcher.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME)
        """

        # Get webhook[get]
        result = self.mgmt_client.webhook.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, WEBHOOK_NAME)

        # Get Job Output[get]
        result = self.mgmt_client.job.get_output(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        """
        # List hybrid worker groups by Automation Account[get]
        result = self.mgmt_client.hybrid_runbook_worker_group.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)
        """

        # Get a module[get]
        result = self.mgmt_client.module.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME)

        """
        # # Get a node[get]
        # result = self.mgmt_client.dsc_node.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_NAME)
        """

        # Get job[get]
        result = self.mgmt_client.job.get(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        # List Paged DSC node configurations by Automation Account with name filter[get]
        result = self.mgmt_client.dsc_node_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List DSC node configurations by Automation Account[get]
        result = self.mgmt_client.dsc_node_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC node configurations by Automation Account with no filter[get]
        result = self.mgmt_client.dsc_node_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # TODO: AttributeError: 'AutomationClient' object has no attribute 'python2package'
        # # List python 2 packages by automation account[get]
        # result = self.mgmt_client.python2package.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get connection types, first 100[get]
        result = self.mgmt_client.connection_type.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List DSC Compilation job in Automation Account[get]
        result = self.mgmt_client.dsc_compilation_job.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get connection types, next 100[get]
        result = self.mgmt_client.connection_type.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get the linked workspace of an automation account[get]
        result = self.mgmt_client.linked_workspace.get(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get DSC Configuration[get]
        result = self.mgmt_client.dsc_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC Configurations with name filter[get]
        result = self.mgmt_client.dsc_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List sourceControls[get]
        result = self.mgmt_client.source_control.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC Configurations with no filter[get]
        result = self.mgmt_client.dsc_configuration.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List certificates[get]
        result = self.mgmt_client.certificate.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List all job schedules by automation account[get]
        result = self.mgmt_client.job_schedule.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List credentials by automation account, next 100[get]
        result = self.mgmt_client.credential.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List credentials by automation account, first 100[get]
        result = self.mgmt_client.credential.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List connections by automation account, next 100[get]
        result = self.mgmt_client.connection.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List connections by automation account, first 100[get]
        result = self.mgmt_client.connection.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get statistics of an automation account[get]
        result = self.mgmt_client.statistics.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List variables, First 100[get]
        result = self.mgmt_client.variable.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List variables, Next 100[get]
        result = self.mgmt_client.variable.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List schedules by automation account, first 100[get]
        result = self.mgmt_client.schedule.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List schedules by automation account, next 100[get]
        result = self.mgmt_client.schedule.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List watchers by Automation Account[get]
        result = self.mgmt_client.watcher.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List runbooks by automation account[get]
        result = self.mgmt_client.runbook.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List webhooks by Automation Account[get]
        result = self.mgmt_client.webhook.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List modules by automation account[get]
        result = self.mgmt_client.module.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get usages of an automation account[get]
        result = self.mgmt_client.usages.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account with version filter[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account with name filter[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account with no filters[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List DSC nodes by Automation Account[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account with node status filter[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account with Node Configuration Custom filter[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes by Automation Account where Node Configurations are not assigned filter[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List Paged DSC nodes with filters separated by 'and'[get]
        result = self.mgmt_client.dsc_node.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List jobs by automation account[get]
        result = self.mgmt_client.job.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Get automation account[get]
        result = self.mgmt_client.automation_account.get(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # List automation accounts by resource group[get]
        result = self.mgmt_client.automation_account.list_by_resource_group(resource_group.name)

        # List automation accounts by resource group[get]
        result = self.mgmt_client.automation_account.list_by_resource_group(resource_group.name)

        """
        # # Regenerate registration key[post]
        # BODY = {
        #   "key_name": "primary"
        # }
        # result = self.mgmt_client.agent_registration_information.regenerate_key(resource_group.name, AUTOMATION_ACCOUNT_NAME, AGENT_REGISTRATION_INFORMATION_NAME, BODY)

        # # Update hybrid worker group[patch]
        # BODY = {
        #   "credential": {
        #     "name": "myRunAsCredentialName"
        #   }
        # }
        # result = self.mgmt_client.hybrid_runbook_worker_group.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, HYBRID_RUNBOOK_WORKER_GROUP_NAME, BODY)

        # Suspend test job[post]
        result = self.mgmt_client.test_job.suspend(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)

        # Resume test job[post]
        result = self.mgmt_client.test_job.resume(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)

        # Stop test job[post]
        result = self.mgmt_client.test_job.stop(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)

        # Undo draft edit to last known published state[post]
        result = self.mgmt_client.runbook_draft.undo_edit(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, DRAFT_NAME)
        """

        # Update a module[patch]
        BODY = {
          "content_link": {
            "uri": "https://teststorage.blob.core.windows.net/mycontainer/MyModule.zip",
            "content_hash": {
              "algorithm": "sha265",
              "value": "07E108A962B81DD9C9BAA89BB47C0F6EE52B29E83758B07795E408D258B2B87A"
            },
            "version": "1.0.0.0"
          }
        }
        result = self.mgmt_client.module.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, BODY)

        """
        # Update a source control[patch]
        BODY = {
          "branch": "master",
          "folder_path": "/folderOne/folderTwo",
          "auto_sync": True,
          "publish_runbook": True,
          "security_token": {
            "access_token": "3a326f7a0dcd343ea58fee21f2fd5fb4c1234567",
            "token_type": "PersonalAccessToken"
          },
          "description": "my description"
        }
        result = self.mgmt_client.source_control.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME, BODY)

        # Create or Update Configuration[put]
        BODY = {
          "source": {
            "hash": {
              "algorithm": "sha256",
              "value": "A9E5DB56BA21513F61E0B3868816FDC6D4DF5131F5617D7FF0D769674BD5072F"
            },
            "type": "embeddedContent",
            "value": "Configuration SetupServer {\r\n    Node localhost {\r\n                               WindowsFeature IIS {\r\n                               Name = \"Web-Server\";\r\n            Ensure = \"Present\"\r\n        }\r\n    }\r\n}"
          },
          "description": "sample configuration",
          "name": "SetupServer",
          "location": "East US 2"
        }
        result = self.mgmt_client.dsc_configuration.create_or_update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONFIGURATION_NAME, BODY)

        # Update a certificate[patch]
        BODY = {
          "name": "testCert",
          "properties": {
            "description": "sample certificate. Description updated"
          }
        }
        result = self.mgmt_client.certificate.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CERTIFICATE_NAME, BODY)
        """

        # Publish runbook draft[post]
        result = self.mgmt_client.runbook.begin_publish(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_DRAFT_NAME)
        result = result.result()

        # Update a credential[patch]
        BODY = {
          "name": "myCredential",
          "user_name": "mylingaiah",
          "password": "myPassw0rd3",
          "description": "my description goes here"
        }
        result = self.mgmt_client.credential.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CREDENTIAL_NAME, BODY)

        """
        # Update a connection[patch]
        BODY = {
          "name": "myConnection",
          "description": "my description goes here",
          "field_definition_values": {
            "automation_certificate_name": "myCertificateName",
            "subscription_id": "b5e4748c-f69a-467c-8749-e2f9c8cd3009"
          }
        }
        result = self.mgmt_client.connection.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_NAME, BODY)

        # Start Watcher[post]
        result = self.mgmt_client.watcher.start(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME)

        # Start Watcher[post]
        result = self.mgmt_client.watcher.start(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME)
        """

        # Update a variable[patch]
        BODY = {
          "name": "sampleVariable",
          "properties": {
            "value": "\"ComputerName3.domain.com\""
          }
        }
        result = self.mgmt_client.variable.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, VARIABLE_NAME, BODY)

        # Update a schedule[patch]
        BODY = {
          "name": "mySchedule",
          "description": "my updated description of schedule goes here",
          "is_enabled": False
        }
        result = self.mgmt_client.schedule.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, SCHEDULE_NAME, BODY)

        # Update runbook[patch]
        BODY = {
          "description": "Updated Description of the Runbook",
          "log_verbose": False,
          "log_progress": True,
          "log_activity_trace": "1"
        }
        result = self.mgmt_client.runbook.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME, BODY)

        """
        # Update watcher[patch]
        BODY = {
          "name": "MyTestWatcher",
          "execution_frequency_in_seconds": "600"
        }
        result = self.mgmt_client.watcher.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME, BODY)
        """

        # Suspend job[post]
        result = self.mgmt_client.job.suspend(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        # Update webhook[patch]
        BODY = {
          "name": WEBHOOK_NAME,
          "is_enabled": False,
          "description": "updated webhook"
        }
        result = self.mgmt_client.webhook.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, WEBHOOK_NAME, BODY)

        """
        # Generate webhook uri[post]
        result = self.mgmt_client.webhook.generate_uri(resource_group.name, AUTOMATION_ACCOUNT_NAME, WEBHOOK_NAME)

        # Resume job[post]
        result = self.mgmt_client.job.resume(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)
        """

        # Update a module[patch]
        BODY = {
          "content_link": {
            "uri": "https://teststorage.blob.core.windows.net/mycontainer/MyModule.zip",
            "content_hash": {
              "algorithm": "sha265",
              "value": "07E108A962B81DD9C9BAA89BB47C0F6EE52B29E83758B07795E408D258B2B87A"
            },
            "version": "1.0.0.0"
          }
        }
        result = self.mgmt_client.module.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME, BODY)

        if self.is_live:
            time.sleep(60)

        # Stop job[post]
        result = self.mgmt_client.job.stop(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_NAME)

        """
        # Update a node[patch]
        BODY = {
          "node_id": "nodeId",
          "node_configuration": {
            "name": "SetupServer.localhost"
          }
        }
        result = self.mgmt_client.dsc_node.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_NAME, BODY)
        """

        # Get lists of an automation account[post]
        result = self.mgmt_client.keys.list_by_automation_account(resource_group.name, AUTOMATION_ACCOUNT_NAME)

        # Update an automation account[patch]
        BODY = {
          "sku": {
            "name": "Free"
          },
          "name": "myAutomationAccount9",
          "location": "East US 2"
        }
        result = self.mgmt_client.automation_account.update(resource_group.name, AUTOMATION_ACCOUNT_NAME, BODY)

        """
        # # Delete software update configuration[delete]
        # result = self.mgmt_client.software_update_configurations.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOFTWARE_UPDATE_CONFIGURATION_NAME)

        # # Delete a hybrid worker group[delete]
        # result = self.mgmt_client.hybrid_runbook_worker_group.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, HYBRID_RUNBOOK_WORKER_GROUP_NAME)

        # # Delete a DSC node configuration[delete]
        # result = self.mgmt_client.dsc_node_configuration.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_CONFIGURATION_NAME)

        # Delete an existing connection type[delete]
        result = self.mgmt_client.connection_type.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_TYPE_NAME)

        # Delete a python 2 package[delete]
        result = self.mgmt_client.python2package.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, PYTHON2PACKAGE_NAME)

        # Delete a source control[delete]
        result = self.mgmt_client.source_control.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, SOURCE_CONTROL_NAME)

        # Delete DSC Configuration[delete]
        result = self.mgmt_client.dsc_configuration.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONFIGURATION_NAME)

        # Delete a job schedule[delete]
        result = self.mgmt_client.job_schedule.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, JOB_SCHEDULE_NAME)

        # Delete an existing connection[delete]
        result = self.mgmt_client.connection.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, CONNECTION_NAME)

        # Delete a certificate[delete]
        result = self.mgmt_client.certificate.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, CERTIFICATE_NAME)
        """

        # Delete a credential[delete]
        result = self.mgmt_client.credential.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, CREDENTIAL_NAME)

        # Delete a variable[delete]
        result = self.mgmt_client.variable.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, VARIABLE_NAME)

        # Delete schedule[delete]
        result = self.mgmt_client.schedule.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, SCHEDULE_NAME)

        # Delete webhook[delete]
        result = self.mgmt_client.webhook.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, WEBHOOK_NAME)

        # Delete a runbook[delete]
        result = self.mgmt_client.runbook.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, RUNBOOK_NAME)

        # # Delete watcher[delete]
        # result = self.mgmt_client.watcher.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, WATCHER_NAME)

        # Delete a module[delete]
        result = self.mgmt_client.module.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, MODULE_NAME)

        # # Delete a DSC Node[delete]
        # result = self.mgmt_client.dsc_node.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME, NODE_NAME)

        # Delete automation account[delete]
        result = self.mgmt_client.automation_account.delete(resource_group.name, AUTOMATION_ACCOUNT_NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
