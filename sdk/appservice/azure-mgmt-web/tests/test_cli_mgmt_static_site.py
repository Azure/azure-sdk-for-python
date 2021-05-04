# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# Current Operation Coverage:
#   StaticSites: 12/26

import unittest

import azure.mgmt.web
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

AZURE_LOCATION = 'eastus2'

class MgmtWebSiteTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtWebSiteTest, self).setUp()
        self.mgmt_client = self.create_mgmt_client(
            azure.mgmt.web.WebSiteManagementClient
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    def test_static_site(self, resource_group):

        GITHUB_TOKEN = self.settings.GITHUB_TOKEN if self.is_live else "xxx"
        TENANT_ID = self.settings.TENANT_ID
        RESOURCE_GROUP = resource_group.name
        NAME = "myname"
        PR_ID = "1"
        DOMAIN_NAME = "mydomain"

#--------------------------------------------------------------------------
        # /StaticSites/put/Create or update a static site[put]
#--------------------------------------------------------------------------
        BODY = {
          "location": AZURE_LOCATION,
          "sku": {
            "name": "Free",
        #     "tier": "Free"
          },
        #   "repository_url": "https://github.com/username/RepoName",
          "repository_url": "https://github.com/00Kai0/html-docs-hello-world",
          "branch": "master",
        #   "repository_token": "repoToken123",
          "repository_token": GITHUB_TOKEN,
          "build_properties": {
            "app_location": "app",
            "api_location": "api",
            "app_artifact_location": "build"
          }
        }
        result = self.mgmt_client.static_sites.create_or_update_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/put/Creates or updates the function app settings of a static site.[put]
#--------------------------------------------------------------------------
        BODY = {
          "properties": {
            "setting1": "someval",
            "setting2": "someval2"
          }
        }
        # result = self.mgmt_client.static_sites.create_or_update_static_site_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, app_settings=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/put/Create or update a custom domain for a static site[put]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.create_or_update_static_site_custom_domain(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/put/Creates or updates the function app settings of a static site build.[put]
#--------------------------------------------------------------------------
        BODY = {
          "setting1": "someval",
          "setting2": "someval2"
        }
        # result = self.mgmt_client.static_sites.create_or_update_static_site_build_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID, app_settings=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/get/Gets the functions of a particular static site build[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_build_functions(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get a static site build[get]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.get_static_site_build(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /StaticSites/get/List custom domains for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_custom_domains(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Gets the functions of a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_functions(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get all builds for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_site_builds(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get details for a static site[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get static sites for a resource group[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.get_static_sites_by_resource_group(resource_group_name=RESOURCE_GROUP)

#--------------------------------------------------------------------------
        # /StaticSites/get/Get all static sites in a subscription[get]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list()

#--------------------------------------------------------------------------
        # /StaticSites/patch/Create or update a user for a static site[patch]
#--------------------------------------------------------------------------
        BODY = {
          "roles": "contributor"
        }
        # result = self.mgmt_client.static_sites.update_static_site_user(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER, userid=USERID, static_site_user_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/post/List users for a static site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.list_static_site_users(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER)

#--------------------------------------------------------------------------
        # /StaticSites/post/Get function app settings of a static site build[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.list_static_site_build_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /StaticSites/post/Validate a custom domain for a static site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.validate_custom_domain_can_be_added_to_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Get function app settings of a static site[post]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.list_static_site_function_app_settings(resource_group_name=RESOURCE_GROUP, name=NAME)

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
        # result = self.mgmt_client.static_sites.create_user_roles_invitation_link(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_user_roles_invitation_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/post/List secrets for a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.list_static_site_secrets(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/post/Reset the api key for a static site[post]
#--------------------------------------------------------------------------
        BODY = {
          "should_update_repository": True,
          "repository_token": GITHUB_TOKEN
        }
        result = self.mgmt_client.static_sites.reset_static_site_api_key(resource_group_name=RESOURCE_GROUP, name=NAME, reset_properties_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/post/Detach a static site[post]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.detach_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)

#--------------------------------------------------------------------------
        # /StaticSites/patch/Patch a static site[patch]
#--------------------------------------------------------------------------
        BODY = {}
        # result = self.mgmt_client.static_sites.update_static_site(resource_group_name=RESOURCE_GROUP, name=NAME, static_site_envelope=BODY)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a user for a static site[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.delete_static_site_user(resource_group_name=RESOURCE_GROUP, name=NAME, authprovider=AUTHPROVIDER, userid=USERID)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a custom domain for a static site[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.delete_static_site_custom_domain(resource_group_name=RESOURCE_GROUP, name=NAME, domain_name=DOMAIN_NAME)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a static site build[delete]
#--------------------------------------------------------------------------
        # result = self.mgmt_client.static_sites.delete_static_site_build(resource_group_name=RESOURCE_GROUP, name=NAME, pr_id=PR_ID)

#--------------------------------------------------------------------------
        # /StaticSites/delete/Delete a static site[delete]
#--------------------------------------------------------------------------
        result = self.mgmt_client.static_sites.delete_static_site(resource_group_name=RESOURCE_GROUP, name=NAME)
