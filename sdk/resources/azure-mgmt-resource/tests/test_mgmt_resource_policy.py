# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

# covered ops:
#   policy_definitions: 10/10
#   policy_assignments: 10/10
#   policy_set_definitions: 10/10

import unittest

# import azure.mgmt.managementgroups
import azure.mgmt.resource
from devtools_testutils import AzureMgmtTestCase, RandomNameResourceGroupPreparer

class MgmtResourcePolicyTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourcePolicyTest, self).setUp()
        self.policy_client = self.create_mgmt_client(
            azure.mgmt.resource.PolicyClient
        )

        if self.is_live:
            # special client
            from azure.mgmt.managementgroups import ManagementGroupsAPI
            self.mgmtgroup_client = ManagementGroupsAPI(
                credentials=self.settings.get_credentials()
            )

    @unittest.skip("(InvalidAuthenticationToken) The access token is invalid.")
    @RandomNameResourceGroupPreparer()
    def test_policy_definition_at_management_group(self, resource_group, location):
        policy_name = self.get_resource_name('pypolicy')
        policy_assignment_name = self.get_resource_name('passignment')
        policy_set_name = self.get_resource_name('pypolicy')

        # create management group use track 1 version
        group_id = "20000000-0001-0000-0000-000000000123"

        if self.is_live:
            result = self.mgmtgroup_client.management_groups.create_or_update(
                group_id,
                {
                "name": group_id,
                }
            )
            result = result.result()

        definition = self.policy_client.policy_definitions.create_or_update_at_management_group(
            policy_name,
            group_id,
            {
                'policy_type':'Custom',
                'description':'Don\'t create a VM anywhere',
                'policy_rule':{
                    'if':{
                      'allOf':[
                        {
                          'source':'action',
                          'equals':'Microsoft.Compute/virtualMachines/write'
                        },
                        {
                          'field':'location',
                          'in':[
                            'eastus',
                            'eastus2',
                            'centralus'
                          ]
                        }
                      ]
                    },
                    'then':{
                      'effect':'deny'
                    }
                }
            }
        )

        definition = self.policy_client.policy_definitions.get_at_management_group(
            policy_name,
            group_id
        )

        policies = list(self.policy_client.policy_definitions.list_by_management_group(
            group_id
        ))

        result = list(self.policy_client.policy_definitions.list_built_in())

        self.policy_client.policy_definitions.get_built_in(
            result[0].name
        )

        result = self.policy_client.policy_definitions.list()

        result = self.policy_client.policy_assignments.list_for_management_group(
            group_id,
            None
        )

        # Policy Assignement - By Name
        scope = '/providers/Microsoft.Management/managementgroups/{group_id}/'.format(
            group_id=group_id
        )
        assignment = self.policy_client.policy_assignments.create(
            scope,
            policy_assignment_name,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = self.policy_client.policy_assignments.get(
            assignment.scope,
            assignment.name
        )

        assignments = list(self.policy_client.policy_assignments.list())
        assert len(assignments) > 0

        assignments = list(self.policy_client.policy_assignments.list_for_resource_group(
            resource_group.name
        ))
        # assert len(assignments) >= 1  # At least mine, could be more

        assignments = self.policy_client.policy_assignments.list_for_resource(
            resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name="pytestavset123",
        )

        self.policy_client.policy_assignments.delete(
            scope,
            policy_assignment_name
        )

        # Policy Assignement - By Id
        policy_id = '{}/providers/Microsoft.Authorization/policyAssignments/{}'.format(
            scope,
            policy_assignment_name
        )
        assignment = self.policy_client.policy_assignments.create_by_id(
            policy_id,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = self.policy_client.policy_assignments.get_by_id(
            assignment.id,
        )

        self.policy_client.policy_assignments.delete_by_id(
            assignment.id
        )

        BODY = {
            "properties": {
                "displayName": "Cost Management",
                "description": "Policies to enforce low cost storage SKUs",
                "metadata": {
                "category": "Cost Management"
                },
                "policyDefinitions": [
                {
                    "policyDefinitionId": definition.id,
                    "parameters": {
                    }
                }
                ]
            }
        }
        self.policy_client.policy_set_definitions.create_or_update_at_management_group(
            policy_set_name,
            group_id,
            BODY
        )

        self.policy_client.policy_set_definitions.get_at_management_group(
            policy_set_name,
            group_id
        )

        self.policy_client.policy_set_definitions.list_by_management_group(
            group_id
        )

        result = list(self.policy_client.policy_set_definitions.list_built_in())

        self.policy_client.policy_set_definitions.list()

        self.policy_client.policy_set_definitions.get_built_in(
            result[0].name
        )

        self.policy_client.policy_set_definitions.delete_at_management_group(
            policy_set_name,
            group_id
        )

        self.policy_client.policy_definitions.delete_at_management_group(
            policy_name,
            group_id
        )

        if self.is_live:
            # delete management group with track 1 version
            result = self.mgmtgroup_client.management_groups.delete(group_id)
            result = result.result()

    # @unittest.skip("Forbidden")
    @RandomNameResourceGroupPreparer()
    def test_policy_definition(self, resource_group, location):
        policy_name = self.get_resource_name('pypolicy')
        policy_assignment_name = self.get_resource_name('pypolicyassignment')
        policy_set_name = self.get_resource_name('pypolicy')

        definition = self.policy_client.policy_definitions.create_or_update(
            policy_name,
            {
                'policy_type':'Custom',
                'description':'Don\'t create a VM anywhere',
                'policy_rule':{
                    'if':{
                      'allOf':[
                        {
                          'source':'action',
                          'equals':'Microsoft.Compute/virtualMachines/read'
                        },
                        {
                          'field':'location',
                          'in':[
                            'eastus',
                            'eastus2',
                            'centralus'
                          ]
                        }
                      ]
                    },
                    'then':{
                      'effect':'deny'
                    }
                }
            }
        )

        definition = self.policy_client.policy_definitions.get(
            definition.name
        )

        policies = list(self.policy_client.policy_definitions.list())
        assert len(policies) > 0

        # Policy Assignement - By Name
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            resource_group.name
        )
        assignment = self.policy_client.policy_assignments.create(
            scope,
            policy_assignment_name,
            {
                'policy_definition_id': definition.id,
            }
        )

        BODY = {
            "properties": {
                "displayName": "Cost Management",
                "description": "Policies to enforce low cost storage SKUs",
                "metadata": {
                "category": "Cost Management"
                },
                "policyDefinitions": [
                {
                    "policyDefinitionId": definition.id,
                    "parameters": {
                    }
                }
                ]
            }
        }
        self.policy_client.policy_set_definitions.create_or_update(
            policy_set_name,
            BODY
        )

        assignment = self.policy_client.policy_assignments.get(
            assignment.scope,
            assignment.name
        )

        assignments = list(self.policy_client.policy_assignments.list())
        assert len(assignments) > 0

        assignments = list(self.policy_client.policy_assignments.list_for_resource_group(
            resource_group.name
        ))
        assert len(assignments) >= 1  # At least mine, could be more

        assignments = self.policy_client.policy_assignments.list_for_resource(
            resource_group.name,
            resource_provider_namespace="Microsoft.Compute",
            parent_resource_path="",
            resource_type="availabilitySets",
            resource_name="pytestavset123",
        )

        self.policy_client.policy_assignments.delete(
            scope,
            policy_assignment_name
        )

        # Policy Assignement - By Id
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            resource_group.name
        )
        policy_id = '{}/providers/Microsoft.Authorization/policyAssignments/{}'.format(
            scope,
            policy_assignment_name
        )
        assignment = self.policy_client.policy_assignments.create_by_id(
            policy_id,
            {
                'policy_definition_id': definition.id,
            }
        )

        self.policy_client.policy_set_definitions.get(
            policy_set_name
        )

        assignment = self.policy_client.policy_assignments.get_by_id(
            assignment.id,
        )

        self.policy_client.policy_assignments.delete_by_id(
            assignment.id
        )

        self.policy_client.policy_set_definitions.delete(
            policy_set_name
        )

        # Delete definitions
        self.policy_client.policy_definitions.delete(
            definition.name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
