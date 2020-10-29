# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


# TEST SCENARIO COVERAGE
# ----------------------
# Methods Total   : 572
# Methods Covered : 111
# Examples Total  : 131
# Examples Tested : 131
# Coverage %      : 19
# ----------------------

# Current Operation Coverage:
#   AppServiceCertificateOrders: 0/20
#   CertificateRegistrationProvider: 1/1
#   Domains: 1/15
#   TopLevelDomains: 3/3
#   DomainRegistrationProvider: 1/1
#   Certificates: 6/6
#   DeletedWebApps: 2/3
#   Diagnostics: 22/22
#   Provider: 1/3
#   Recommendations: 0/15
#   : 1/16
#   WebApps: 33/372
#   StaticSites: 26/26
#   AppServiceEnvironments: 2/36
#   AppServicePlans: 6/27
#   ResourceHealthMetadata: 6/6

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )
    
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_web(self, resource_group):

        SUBSCRIPTION_ID = self.settings.SUBSCRIPTION_ID
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        DOMAIN_NAME = "myDomain"
        NAME = "my"
        DELETED_SITE_ID = "myDeletedSiteId"
        DETECTOR_NAME = "myDetector"
        SITE_NAME = "mySite"
        DIAGNOSTIC_CATEGORY = "myDiagnosticCategory"
        ANALYSIS_NAME = "myAnalysis"
        SLOT = "mySlot"
        BASIC_PUBLISHING_CREDENTIALS_POLICY_NAME = "myBasicPublishingCredentialsPolicy"
        CONFIG_NAME = "myConfig"
        APP_SETTING_KEY = "myAppSettingKey"
        INSTANCE_ID = "myInstanceId"
        NETWORK_TRACE_NAME = "myNetworkTrace"
        OPERATION_ID = "myOperationId"
        PRIVATE_ENDPOINT_CONNECTION_NAME = "myPrivateEndpointConnection"
        AUTHPROVIDER = "myAuthprovider"
        USERID = "myUserid"
        PR_ID = "myPrId"
        RESOURCE_HEALTH_METADATA_NAME = "myResourceHealthMetadata"

#--------------------------------------------------------------------------
        # /AppServicePlans/put/Create Or Update App Service plan[put]
#--------------------------------------------------------------------------
        BODY = {
          "kind": "app",
          "location": AZURE_LOCATION,
          "sku": {
            "name": "P1",
            "tier": "Premium",
            "size": "P1",
            "family": "P",
            "capacity": "1"
          }
        }
        result = self.mgmt_client.app_service_plans.begin_create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, app_service_plan=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /StaticSites/put/Create or update a static site[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "Basic",
            "tier": "Basic"
          },
          "repository_url": "https://github.com/username/RepoName",
          "branch": "master",
          "repository_token": "repoToken123",
          "build_properties": {
            "app_location": "app",
            "api_location": "api",
            "app_artifact_location": "build"
          }
        }
        result = self.mgmt_client.static_sites.create_or_update_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_envelope=BODY)

#--------------------------------------------------------------------------
        # /Certificates/put/Create Or Update Certificate[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "host_names": [
            "ServerCert"
          ],
          "password": "SWsSsd__233$Sdsds#%Sd!"
        }
        result = self.mgmt_client.certificates.create_or_update(resource_group_name=RESOURCE_GROUP, name=NAME, certificate_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/put/Creates or updates the function app settings of a static site.[put]
#--------------------------------------------------------------------------
        BODY = {
          "setting1": "someval",
          "setting2": "someval2"
        }
        result = self.mgmt_client.static_sites.create_or_update_static_site_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, config_name=CONFIG_NAME, app_settings=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/put/Create or update a custom domain for a static site[put]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.create_or_update_static_site_custom_domain(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/put/Creates or updates the function app settings of a static site build.[put]
#--------------------------------------------------------------------------
        BODY = {
          "setting1": "someval",
          "setting2": "someval2"
        }
        result = self.mgmt_client.static_sites.create_or_update_static_site_build_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID, config_name=CONFIG_NAME, app_settings=BODY)

#--------------------------------------------------------------------------
        # /WebApps/put/Approves or rejects a private endpoint connection for a site.[put]
#--------------------------------------------------------------------------
        BODY = {
          "private_link_service_connection_state": {
            "status": "Approved",
            "description": "Approved by admin.",
            "actions_required": ""
          }
        }
        result = self.mgmt_client.web_apps.begin_approve_or_reject_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME, private_endpoint_wrapper=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/put/Update SCM Allowed[put]
#--------------------------------------------------------------------------
        BODY = {
          "allow": True
        }
        result = self.mgmt_client.web_apps.update_scm_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, basic_publishing_credentials_policy_name=BASIC_PUBLISHING_CREDENTIALS_POLICY_NAME, csm_publishing_access_policies_entity=BODY)

#--------------------------------------------------------------------------
        # /WebApps/put/Update FTP Allowed[put]
#--------------------------------------------------------------------------
        BODY = {
          "allow": True
        }
        result = self.mgmt_client.web_apps.update_ftp_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, basic_publishing_credentials_policy_name=BASIC_PUBLISHING_CREDENTIALS_POLICY_NAME, csm_publishing_access_policies_entity=BODY)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Analysis[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Analysis[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get FTP Allowed[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_ftp_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, basic_publishing_credentials_policy_name=BASIC_PUBLISHING_CREDENTIALS_POLICY_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get SCM Allowed[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_scm_allowed(resource_group_name=RESOURCE_GROUP, name=NAME, basic_publishing_credentials_policy_name=BASIC_PUBLISHING_CREDENTIALS_POLICY_NAME)

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/Get ResourceHealthMetadata[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.get_by_site(resource_group_name=RESOURCE_GROUP, name=NAME, resource_health_metadata_name=RESOURCE_HEALTH_METADATA_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Analysis[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Analysis[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Detectors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detectors(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Detectors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detectors(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Analyses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_analyses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Analyses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_analyses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get a private endpoint connection for a site.[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Diagnostic Category[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_diagnostic_category(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Diagnostic Category[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_diagnostic_category(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /WebApps/get/Get Azure Key Vault app setting reference[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_app_setting_key_vault_reference(resource_group_name=RESOURCE_GROUP, name=NAME, config_name=CONFIG_NAME, app_setting_key=APP_SETTING_KEY)

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/Get ResourceHealthMetadata[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.get_by_site(resource_group_name=RESOURCE_GROUP, name=NAME, resource_health_metadata_name=RESOURCE_HEALTH_METADATA_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Detectors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detectors(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Detectors[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detectors(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Analyses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_analyses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Analyses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_analyses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector Response[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector_response(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector Response[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector_response(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get the current status of a network trace operation for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /AppServiceEnvironments/get/Get Outbound Network Dependencies Endpoints[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_environments.get_outbound_network_dependencies_endpoints(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /AppServiceEnvironments/get/Get Inbound Network Dependencies Endpoints[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_environments.get_inbound_network_dependencies_endpoints(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get site instance info[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_instance_info(resource_group_name=RESOURCE_GROUP, name=NAME, instance_id=INSTANCE_ID)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Service Environment Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_hosting_environment_detector_responses(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Diagnostic Category[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_diagnostic_category(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Diagnostic Category[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_diagnostic_category(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY)

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/List ResourceHealthMetadata for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.list_by_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get Azure Key Vault references for app settings[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_app_settings_key_vault_references(resource_group_name=RESOURCE_GROUP, name=NAME, config_name=CONFIG_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector Response[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector_response(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector Response[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.get_site_detector_response(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/List Publishing Credentials Policies[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_basic_publishing_credentials_policies(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Gets the functions of a particular static site build[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_build_functions(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Diagnostic Categories[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_diagnostic_categories(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Diagnostic Categories[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_diagnostic_categories(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detector_responses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detector_responses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get NetworkTraces for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_network_traces(resource_group_name=RESOURCE_GROUP, name=NAME, operation_id=OPERATION_ID)

#--------------------------------------------------------------------------
        # /WebApps/get/Get site instance info[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_instance_info(resource_group_name=RESOURCE_GROUP, name=NAME, instance_id=INSTANCE_ID)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get a static site build[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_site_build(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Service Environment Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_hosting_environment_detector_responses(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/List ResourceHealthMetadata for a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.list_by_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/get/Get private link resources of a site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.get_private_link_resources(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/List custom domains for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_custom_domains(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Diagnostic Categories[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_diagnostic_categories(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/List App Slot Diagnostic Categories[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_diagnostic_categories(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Gets the functions of a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_functions(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detector_responses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/get/Get App Slot Detector Responses[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.list_site_detector_responses(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME)

#--------------------------------------------------------------------------
        # /DeletedWebApps/get/Get Deleted Web App by Location[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deleted_web_apps.get_deleted_web_app_by_location(azure_location=AZURE_LOCATION, deleted_site_id=DELETED_SITE_ID)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get all builds for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_site_builds(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /Certificates/get/Get Certificate[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get details for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /AppServicePlans/get/Get App Service plan[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.get(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/List ResourceHealthMetadata for a resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /Certificates/get/List Certificates by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get static sites for a resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_sites_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /AppServicePlans/get/List App Service plans by resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.list_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /DeletedWebApps/get/List Deleted Web App by Location[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.deleted_web_apps.list_by_location(azure_location=AZURE_LOCATION)

#--------------------------------------------------------------------------
        # /TopLevelDomains/get/Get Top Level Domain[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.top_level_domains.get(name=NAME)

#--------------------------------------------------------------------------
        # /TopLevelDomains/get/List Top Level Domains[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.top_level_domains.list()

#--------------------------------------------------------------------------
        # /ResourceHealthMetadata/get/List ResourceHealthMetadata for a subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.resource_health_metadata.list()

#--------------------------------------------------------------------------
        # /Certificates/get/List Certificates for subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.list()

#--------------------------------------------------------------------------
        # /StaticSites/get/Get all static sites in a subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list()

#--------------------------------------------------------------------------
        # /AppServicePlans/get/List App Service plans[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.list()

#--------------------------------------------------------------------------
        # /CertificateRegistrationProvider/get/List operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificate_registration_provider.list_operations()

#--------------------------------------------------------------------------
        # /DomainRegistrationProvider/get/List operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.domain_registration_provider.list_operations()

#--------------------------------------------------------------------------
        # /Provider/get/List operations[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.provider.list_operations()

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site detector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site slot detector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site slot analysis[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site analysis[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site detector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site slot detector[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_detector(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, detector_name=DETECTOR_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site slot analysis[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /Diagnostics/post/Execute site analysis[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.diagnostics.execute_site_analysis(resource_group_name=RESOURCE_GROUP, site_name=SITE_NAME, diagnostic_category=DIAGNOSTIC_CATEGORY, analysis_name=ANALYSIS_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/patch/Create or update a user for a static site[patch]
#--------------------------------------------------------------------------
        BODY = {
          "roles": "contributor"
        }
        result = self.mgmt_client.static_sites.update_static_site_user(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER, userid=USERID, static_site_user_envelope=BODY)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/List users for a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_users(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER)

#--------------------------------------------------------------------------
        # /StaticSites/post/Get function app settings of a static site build[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_build_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /StaticSites/post/Validate a custom domain for a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.validate_custom_domain_can_be_added_to_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /Domains/post/Renew an existing domain[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.domains.renew(resource_group_name=RESOURCE_GROUP, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Get function app settings of a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/List backups[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_site_backups(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Create an invitation link for a user for a static site[post]
#--------------------------------------------------------------------------
        BODY = {
          "domain": "happy-sea-15afae3e.azurestaticwebsites.net",
          "provider": "aad",
          "user_details": "username",
          "roles": "admin,contributor",
          "num_hours_to_expiration": "1"
        }
        result = self.mgmt_client.static_sites.create_user_roles_invitation_link(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_user_roles_invitation_envelope=BODY)

#--------------------------------------------------------------------------
        # /WebApps/post/Copy slot[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_slot": "staging",
          "site_config": {
            "number_of_workers": "1",
            "http_logging_enabled": True
          }
        }
        result = self.mgmt_client.web_apps.begin_copy_production_slot(resource_group_name=RESOURCE_GROUP, name=NAME, copy_slot_entity=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /WebApps/post/Start a new network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_start_web_site_network_trace_operation(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME, duration_in_seconds="60")
        result = result.result()

#--------------------------------------------------------------------------
        # /StaticSites/post/List secrets for a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_secrets(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Reset the api key for a static site[post]
#--------------------------------------------------------------------------
        BODY = {
          "should_update_repository": True,
          "repository_token": "repoToken123"
        }
        result = self.mgmt_client.static_sites.reset_static_site_api_key(resource_group_name=RESOURCE_GROUP, name=NAME, reset_properties_envelope=BODY)

#--------------------------------------------------------------------------
        # /WebApps/post/Stop a currently running network trace operation for a site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.stop_web_site_network_trace(resource_group_name=RESOURCE_GROUP, name=NAME, network_trace_name=NETWORK_TRACE_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Detach a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.detach_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/List backups[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.list_site_backups(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /WebApps/post/Copy slot[post]
#--------------------------------------------------------------------------
        BODY = {
          "target_slot": "staging",
          "site_config": {
            "number_of_workers": "1",
            "http_logging_enabled": True
          }
        }
        result = self.mgmt_client.web_apps.begin_copy_production_slot(resource_group_name=RESOURCE_GROUP, name=NAME, copy_slot_entity=BODY)
        result = result.result()

#--------------------------------------------------------------------------
        # /Certificates/patch/Patch Certificate[patch]
#--------------------------------------------------------------------------
        BODY = {
          "password": "SWsSsd__233$Sdsds#%Sd!"
        }
        result = self.mgmt_client.certificates.update(resource_group_name=RESOURCE_GROUP, name=NAME, certificate_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/patch/Patch a static site[patch]
#--------------------------------------------------------------------------
        BODY = {}
        result = self.mgmt_client.static_sites.update_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_envelope=BODY)

#--------------------------------------------------------------------------
        # /AppServicePlans/patch/Patch Service plan[patch]
#--------------------------------------------------------------------------
        BODY = {
          "kind": "app"
        }
        result = self.mgmt_client.app_service_plans.update(resource_group_name=RESOURCE_GROUP, name=NAME, app_service_plan=BODY)

#--------------------------------------------------------------------------
        # /TopLevelDomains/post/List Top Level Domain Agreements[post]
#--------------------------------------------------------------------------
        BODY = {
          "include_privacy": True,
          "for_transfer": False
        }
        result = self.mgmt_client.top_level_domains.list_agreements(name=NAME, agreement_option=BODY)

#--------------------------------------------------------------------------
        # //post/VerifyHostingEnvironmentVnet[post]
#--------------------------------------------------------------------------
        BODY = {
          "vnet_resource_group": "vNet123rg",
          "vnet_name": "vNet123",
          "vnet_subnet_name": "vNet123SubNet"
        }
        result = self.mgmt_client.verify_hosting_environment_vnet(parameters=BODY)

#--------------------------------------------------------------------------
        # /WebApps/delete/Delete a private endpoint connection for a site.[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.web_apps.begin_delete_private_endpoint_connection(resource_group_name=RESOURCE_GROUP, name=NAME, private_endpoint_connection_name=PRIVATE_ENDPOINT_CONNECTION_NAME)
        result = result.result()

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a user for a static site[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.delete_static_site_user(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER, userid=USERID)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a custom domain for a static site[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.delete_static_site_custom_domain(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a static site build[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.delete_static_site_build(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /Certificates/delete/Delete Certificate[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.certificates.delete(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a static site[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.delete_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /AppServicePlans/delete/Delete App Service plan[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.app_service_plans.delete(resource_group_name=RESOURCE_GROUP, name=NAME)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
