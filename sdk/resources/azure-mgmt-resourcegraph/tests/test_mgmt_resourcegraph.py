# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *
from devtools_testutils import AzureMgmtTestCase
import six


class MgmtResourceGraphTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourceGraphTest, self).setUp()
        self.resourcegraph_client = self.create_basic_client(
            ResourceGraphClient
        )

    def test_resources_basic_query(self):
        query = QueryRequest(
            query='project id, tags, properties | limit 2',
            subscriptions=[self.settings.SUBSCRIPTION_ID]
        )

        query_response = self.resourcegraph_client.resources(query)

        # Top-level response fields
        self.assertEqual(query_response.count, 2)
        self.assertEqual(query_response.total_records, 2)
        self.assertIsNone(query_response.skip_token)
        self.assertEqual(query_response.result_truncated, ResultTruncated.false)
        self.assertIsNotNone(query_response.data)
        self.assertIsNotNone(query_response.facets)
        self.assertEqual(len(query_response.facets), 0)

        # Data columns
        self.assertIsNotNone(query_response.data['columns'])
        self.assertEqual(len(query_response.data['columns']), 3)
        self.assertIsNotNone(query_response.data["columns"][0]["name"])
        self.assertIsNotNone(query_response.data["columns"][1]["name"])
        self.assertIsNotNone(query_response.data["columns"][2]["name"])
        self.assertEqual(query_response.data["columns"][0]["type"], ColumnDataType.STRING)
        self.assertEqual(query_response.data["columns"][1]["type"], ColumnDataType.OBJECT)
        self.assertEqual(query_response.data["columns"][2]["type"], ColumnDataType.OBJECT)

        # Data rows
        self.assertIsNotNone(query_response.data["rows"])
        self.assertEqual(len(query_response.data["rows"]), 2)
        self.assertEqual(len(query_response.data["rows"][0]), 3)
        self.assertIsInstance(query_response.data["rows"][0][0], six.string_types)
        # self.assertIsInstance(query_response.data["rows"][0][1], dict)
        # self.assertIsInstance(query_response.data["rows"][0][2], dict)

    def test_resources_basic_query_object_array(self):
        query = QueryRequest(
            query='project id, tags, properties | limit 2',
            subscriptions=[self.settings.SUBSCRIPTION_ID],
            options=QueryRequestOptions(
                result_format=ResultFormat.object_array
            )
        )

        query_response = self.resourcegraph_client.resources(query)

        # Top-level response fields
        self.assertEqual(query_response.count, 2)
        self.assertEqual(query_response.total_records, 2)
        self.assertIsNone(query_response.skip_token)
        self.assertEqual(query_response.result_truncated, ResultTruncated.false)
        self.assertIsNotNone(query_response.data)
        self.assertIsNotNone(query_response.facets)
        self.assertEqual(len(query_response.facets), 0)

        # Data
        self.assertIsNotNone(query_response.data)
        self.assertEqual(len(query_response.data), 2)
        self.assertEqual(len(query_response.data[0]), 3)
        self.assertIsInstance(query_response.data[0]['id'], six.string_types)
        if query_response.data[0]['tags']:
            self.assertIsInstance(query_response.data[0]['tags'], dict)
        self.assertIsInstance(query_response.data[0]['properties'], dict)

    def test_resources_query_options(self):
        raise unittest.SkipTest("Skipping resources_query_options")
        query = QueryRequest(
            query='project id',
            subscriptions=[self.settings.SUBSCRIPTION_ID],
            options=QueryRequestOptions(
                skip_token='82aw3vQlArEastJ24LABY8oPgQLesIyAyzYs2g6/aOOOmJHSYFj39fODurJV5e2tTFFebWcfxn7n5edicA8u6HgSJe1GCEk5HjxwLkeJiye2LVZDC7TaValkJbsk9JqY4yv5c7iRiLqgO34RbHEeVfLJpa56u4RZu0K+GpQvnBRPyAhy3KbwhZWpU5Nnqnud2whGb5WKdlL8xF7wnQaUnUN2lns8WwqwM4rc0VK4BbQt/WfWWcYJivSAyB3m4Z5g73df1KiU4C+K8auvUMpLPYVxxnKC/YZz42YslVAWXXUmuGOaM2SfLHRO6o4O9DgXlUgYjeFWqIbAkmMiVEqU',
                top=4,
                skip=8
            )
        )

        query_response = self.resourcegraph_client.resources(query)

        # Top-level response fields
        self.assertEqual(query_response.count, 4)
        self.assertEqual(query_response.total_records, 743)
        self.assertIsNotNone(query_response.skip_token)
        self.assertEqual(query_response.result_truncated, ResultTruncated.false)
        self.assertIsNotNone(query_response.data)
        self.assertIsNotNone(query_response.facets)
        self.assertEqual(len(query_response.facets), 0)

        # Data columns
        self.assertIsNotNone(query_response.data["columns"])
        self.assertEqual(len(query_response.data["columns"]), 1)
        self.assertIsNotNone(query_response.data["columns"][0]["name"])
        self.assertEqual(query_response.data["columns"][0]["type"], ColumnDataType.string)

        # Data rows
        self.assertIsNotNone(query_response.data["rows"])
        self.assertEqual(len(query_response.data["rows"]), 4)
        self.assertEqual(len(query_response.data["rows"][0]), 1)
        self.assertIsInstance(query_response.data["rows"][0][0], six.string_types)

    def test_resources_facet_query(self):
        facet_expression0 = 'location'
        facet_expression1 = 'nonExistingColumn'

        query = QueryRequest(
            query='project id, location | limit 10',
            subscriptions=[self.settings.SUBSCRIPTION_ID],
            facets=[
                FacetRequest(
                    expression=facet_expression0,
                    options=FacetRequestOptions(
                        sort_order='desc',
                        top=1
                    )
                ),
                FacetRequest(
                    expression=facet_expression1,
                    options=FacetRequestOptions(
                        sort_order='desc',
                        top=1
                    )
                )
            ]
        )

        query_response = self.resourcegraph_client.resources(query)

        # Top-level response fields
        self.assertEqual(query_response.count, 8)
        self.assertEqual(query_response.total_records, 8)
        self.assertIsNone(query_response.skip_token)
        self.assertEqual(query_response.result_truncated, ResultTruncated.false)
        self.assertIsNotNone(query_response.data)
        self.assertIsNotNone(query_response.facets)
        self.assertEqual(len(query_response.facets), 2)

        # Successful facet fields
        self.assertIsInstance(query_response.facets[0], FacetResult)
        self.assertEqual(query_response.facets[0].expression, facet_expression0)
        self.assertGreaterEqual(query_response.facets[0].total_records, 1)
        self.assertEqual(query_response.facets[0].count, 1)

        # Successful facet columns
        self.assertIsNotNone(query_response.facets[0].data["columns"])
        self.assertEqual(len(query_response.facets[0].data["columns"]), 2)
        self.assertIsNotNone(query_response.facets[0].data["columns"][0]["name"])
        self.assertIsNotNone(query_response.facets[0].data["columns"][1]["name"])
        self.assertEqual(query_response.facets[0].data["columns"][0]["type"], ColumnDataType.string)
        self.assertEqual(query_response.facets[0].data["columns"][1]["type"], ColumnDataType.integer)

        # Successful facet rows
        self.assertIsNotNone(query_response.facets[0].data["rows"])
        self.assertEqual(len(query_response.facets[0].data["rows"]), 1)
        self.assertEqual(len(query_response.facets[0].data["rows"][0]), 2)
        self.assertIsInstance(query_response.facets[0].data["rows"][0][0], six.string_types)
        self.assertIsInstance(query_response.facets[0].data["rows"][0][1], six.integer_types)

        # Failed facet
        self.assertIsInstance(query_response.facets[1], FacetError)
        self.assertEqual(query_response.facets[1].expression, facet_expression1)
        self.assertIsNotNone(query_response.facets[1].errors)
        self.assertGreater(len(query_response.facets[1].errors), 0)
        self.assertIsNotNone(query_response.facets[1].errors[0].code)
        self.assertIsNotNone(query_response.facets[1].errors[0].message)

    def test_resources_malformed_query(self):
        query = QueryRequest(
            query='project id, location | where where',
            subscriptions=[self.settings.SUBSCRIPTION_ID]
        )

        with self.assertRaises(Exception) as cm:
            self.resourcegraph_client.resources(query)

        error = cm.exception.error.error
        self.assertIsNotNone(error.code)
        self.assertIsNotNone(error.message)
        self.assertIsNotNone(error.details)
        self.assertGreater(len(error.details), 0)
        self.assertIsNotNone(error.details[0].code)
        self.assertIsNotNone(error.details[0].message)
        #self.assertIsNotNone(error.details[0].additional_properties)
        #self.assertEqual(len(error.details[0].additional_properties), 4)


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
