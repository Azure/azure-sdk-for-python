# Testing Azure Packages has some additional complication/reading required.
# Reference https://github.com/Azure/azure-sdk-for-python/wiki/Contributing-to-the-tests
# Pytest should be leveraged to test your project.

from devtools_testutils import AzureMgmtTestCase
from azure.ai.ml import template_main

# this test case highlights that there are some additional Test capabilities present in devtools_testutils
# as a package owner you are not required to use these. Standard PyTest implementation will work.
class TemplateTest(AzureMgmtTestCase):
    def setUp(self):
        super(TemplateTest, self).setUp()

    def test_case_default(self):
        self.assertEqual(template_main(), True)
