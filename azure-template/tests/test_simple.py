# Testing Azure Packages has some additional complication/reading required.
# Reference https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests

from devtools_testutils import AzureMgmtTestCase
from azure.template import template_main

class TemplateTest(AzureMgmtTestCase):
    def setUp(self):
        super(TemplateTest, self).setUp()

    def test_case_default(self):
        self.assertEqual(template_main(), True)
