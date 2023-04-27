# Testing Azure Packages has some additional complication/reading required.
# Reference https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md
# Pytest should be leveraged to test your project.

from devtools_testutils import AzureMgmtRecordedTestCase
from azure.template import template_main

# This test case highlights that there are some additional test capabilities present in devtools_testutils
# AzureMgmtRecordedTestCase provides methods for client creation, resource naming, and more. 
# As a package owner you are not required to use these. Standard pytest implementation will work.
class TestTemplate(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        # Code in this optional method will be executed before each test in the class runs.
        # Fixtures can perform test-specific setup: https://docs.pytest.org/latest/explanation/fixtures.html
        pass

    def test_case_default(self):
        assert template_main() == True
