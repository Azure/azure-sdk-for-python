from dotenv import load_dotenv, find_dotenv
import unittest

from .azure_testcase import get_resource_name, get_qualified_method_name

class AzureUnitTest(unittest.TestCase):
    def __init__(self, method_name):
        load_dotenv(find_dotenv())
        super(AzureUnitTest, self).__init__(method_name)
        self.qualified_test_name = get_qualified_method_name(self, method_name)

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

