# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
import json
import uuid
from devtools_testutils import AzureMgmtTestCase
from azure.mgmt.managedservices import ManagedServicesClient


class MgmtManagedServicesTest(AzureMgmtTestCase):
    def setUp(self):
        super(MgmtManagedServicesTest, self).setUp()
        self.client = self.create_basic_client(ManagedServicesClient)

    def test_managedservices_crud(self):
        scope = 'subscriptions/38bd4bef-41ff-45b5-b3af-d03e55a4ca15'
        assignmentid = '367257d7-b69a-4b76-9c18-6dd3e9ae33ce'
        api_version = '2018-06-01-preview'
        definitionid = '1cf1704a-f8a8-4082-a8be-457d3f68e812'
        regdef_string='{"registrationDefinitionName":"Registration Test","description":"dpp","managedByTenantId":"bab3375b-6197-4a15-a44b-16c41faa91d7","authorizations":[{"principalId":"d6f6c88a-5b7a-455e-ba40-ce146d4d3671","roleDefinitionId":"acdd72a7-3385-48ef-bd42-f606fba81ae7"}]}'
        properties = json.loads((regdef_string))

        #create definition
        defresponse = self.client.registration_definitions.create_or_update(
                    definitionid, api_version, scope, properties)
        definitionresourceid = defresponse.id
        self.assertIsNotNone(defresponse)
        self.assertEqual(definitionid, defresponse.name)

        #create assignment
        assignmentproperties ={"registrationDefinitionId":definitionresourceid}
        assignmentresponse = self.client.registration_assignments.create_or_update(
            scope, assignmentid, api_version,assignmentproperties)
        self.assertIsNotNone(assignmentresponse)
        self.assertEqual(assignmentid, assignmentresponse.name)

        #get definition
        getdefresponse = self.client.registration_definitions.get(
            scope,definitionid,api_version)
        self.assertIsNotNone(getdefresponse)
        self.assertEqual(definitionid, getdefresponse.name)

        #get assingment
        getassignmentresponse = self.client.registration_assignments.get(
            scope, assignmentid, api_version)

        self.assertIsNotNone(getassignmentresponse)
        self.assertEqual(assignmentid, getassignmentresponse.name)

        #remove assignment
        removeassignmentresponse = self.client.registration_assignments.delete(
            scope, assignmentid, api_version)
        self.assertIsNotNone(removeassignmentresponse)
        self.assertEqual(assignmentid, removeassignmentresponse.name)

        #remove definition
        removedefinitionresponse = self.client.registration_definitions.delete(
            definitionid, api_version, scope)
        self.assertIsNotNone(removedefinitionresponse)
        self.assertEqual(definitionid, removedefinitionresponse.name)

if __name__ == '__main__':
    unittest.main()
