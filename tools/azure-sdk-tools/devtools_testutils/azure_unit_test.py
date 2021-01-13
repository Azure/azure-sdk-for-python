from dotenv import load_dotenv, find_dotenv
import os
import unittest

from azure_devtools.scenario_tests import GeneralNameReplacer
from azure_devtools.scenario_tests.config import TestConfig

from .azure_testcase import get_resource_name, get_qualified_method_name
from .config import TEST_SETTING_FILENAME

class AzureUnitTest(unittest.TestCase):
    def __init__(self, method_name, config_file=None):
        load_dotenv(find_dotenv())
        self.qualified_test_name = get_qualified_method_name(self, method_name)

        self.working_folder = os.path.dirname(__file__)
        self.scrubber = GeneralNameReplacer()
        config_file = config_file or os.path.join(
            self.working_folder, TEST_SETTING_FILENAME
        )


        self.config = TestConfig(config_file=config_file)

        # These two should always be false, these tests don't generate live traffic
        self.is_live = False
        self.in_recording = False
        super(AzureUnitTest, self).__init__(method_name)

    def setUp(self):
        # Incorporating this for leftover unittest dependent
        # tests. Will test without as well
        pass

    def get_resource_name(self):
        pass

    def create_client_from_credential(self):
        pass


    def get_resource_name(self, name):
        """Alias to create_random_name for back compatibility."""
        return get_resource_name(name, self.qualified_test_name.encode())

    def get_preparer_resource_name(self, prefix):
        """Random name generation for use by preparers.

        If prefix is a blank string, use the fully qualified test name instead.
        This is what legacy tests do for resource groups."""
        return self.get_resource_name(
            prefix or self.qualified_test_name.replace(".", "_")
        )
