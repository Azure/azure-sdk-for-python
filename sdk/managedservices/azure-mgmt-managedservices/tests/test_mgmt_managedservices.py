# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import time
import json
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.managedservices import ManagedServicesClient


@unittest.skip("skip test")
class MgmtManagedServicesTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtManagedServicesTest, self).setUp()
        self.client = self.create_basic_client(ManagedServicesClient)

    def test_managedservices_crud(self):
        scope = 'subscriptions/00000000-0000-0000-0000-000000000000'
        assignmentid = 'c0d5f994-63a1-484d-8c1e-a2ac825efd60'
        definitionid = '8daec8c7-7567-47ff-9009-f0a4ec429a3c'
        regdef_string='{"registrationDefinitionName":"Registration Test","description":"dpp","managedByTenantId":"bab3375b-6197-4a15-a44b-16c41faa91d7","authorizations":[{"principalId":"d6f6c88a-5b7a-455e-ba40-ce146d4d3671","roleDefinitionId":"acdd72a7-3385-48ef-bd42-f606fba81ae7"}]}'
        properties = json.loads((regdef_string))

        #create definition
        poller = self.client.registration_definitions.create_or_update(definitionid, scope, properties)
        response = poller.result()
        self.assertIsNotNone(response)
        self.assertEqual(definitionid, response.name)

        #create assignment
        definition = scope + "/providers/Microsoft.ManagedServices/registrationDefinitions/" + definitionid
        assignmentproperties = {"registrationDefinitionId":definition}
        poller = self.client.registration_assignments.create_or_update(scope, assignmentid, assignmentproperties)
        response = poller.result()
        self.assertIsNotNone(response)
        self.assertEqual(assignmentid, response.name)

        #get definition
        response = self.client.registration_definitions.get(scope = scope, registration_definition_id = definitionid)
        self.assertEqual(definitionid, response.name)

        #get assignment
        response = self.client.registration_assignments.get(scope = scope, registration_assignment_id = assignmentid)
        self.assertEqual(assignmentid, response.name)

        #remove assignment
        self.client.registration_assignments.delete(scope, assignmentid).wait()

        #remove definition
        self.client.registration_definitions.delete(definitionid, scope)

        #list assignments
        assignments = self.client.registration_assignments.list(scope)
        for assignment in assignments:
            self.assertNotEqual(assignmentid, assignment.name)

        #list definitions
        definitions = self.client.registration_definitions.list(scope)
        for definition in definitions:
            self.assertNotEqual(definitionid, definition.name)


if __name__ == '__main__':
    unittest.main()
