# This file describes data-plane and management-plane library tests, which can differ slightly.
# Test requirements are documented at https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md.
# SDK tests should use `pytest`, and tests that send service requests should be recorded with the Azure SDK test proxy.

from devtools_testutils import AzureRecordedTestCase, AzureMgmtRecordedTestCase
from azure.template import template_main


# The `devtools_testutils` package in the SDK repository provides test capabilities.
# `AzureRecordedTestCase` provides methods for client creation, resource naming, and more.
# Tools from `devtools_testutils` are not required; plain `pytest` unit tests can be sufficient in some scenarios.
class TestDataPlane(AzureRecordedTestCase):
    def setup_method(self, method):
        # Code in this optional method will be executed before each test in the class runs.
        # Fixtures can also perform test-specific setup: https://docs.pytest.org/latest/explanation/fixtures.html
        pass

    def test_case_default(self):
        assert template_main() == True


# `AzureMgmtRecordedTestCase` inherits from `AzureRecordedTestCase` and also includes a `create_mgmt_client` method.
# This class should only be used by management-plane libraries in most cases. `azure-mgmt-*` libraries have their own
# reference material for testing: https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md.
class TestMgmtPlane(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        pass

    def test_case_default(self):
        assert template_main() == True
