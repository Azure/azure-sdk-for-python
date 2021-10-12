# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

import functools
import hashlib
import os
from collections import namedtuple

from azure.identity import ClientSecretCredential
from azure_devtools.scenario_tests.exceptions import AzureTestError
from devtools_testutils import (
    ResourceGroupPreparer, AzureMgmtPreparer, FakeResource
)


SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE_PARAM = "schemaregistry_fully_qualified_namespace"
SCHEMAREGISTRY_GROUP_PARAM = "schemaregistry_group"
SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE_ENV_KEY_NAME = 'SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE'
SCHEMAREGISTRY_GROUP_ENV_KEY_NAME = 'SCHEMAREGISTRY_GROUP'


class SchemaRegistryNamespacePreparer(AzureMgmtPreparer):
    # TODO: SR doesn't have mgmt package
    def __init__(self):
        pass

    def create_resource(self, name, **kwargs):
        pass

    def remove_resource(self, name, **kwargs):
        pass


class SchemaRegistryPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix=''
    ):
        super(SchemaRegistryPreparer, self).__init__(name_prefix, 24)

    def create_resource(self, name, **kwargs):
        # TODO: right now the endpoint/group is fixed, as there is no way to create/delete resources using api, in the future we should be able to dynamically create and remove resources
        if self.is_live:
            return {
                SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE_PARAM: os.environ[SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE_ENV_KEY_NAME],
                SCHEMAREGISTRY_GROUP_PARAM: os.environ[SCHEMAREGISTRY_GROUP_ENV_KEY_NAME]
            }
        else:
            return {
                SCHEMAREGISTRY_FULLY_QUALIFIED_NAMESPACE_PARAM: "sr-playground.servicebus.windows.net",
                SCHEMAREGISTRY_GROUP_PARAM: "azsdk_python_test_group"
            }

    def remove_resource(self, name, **kwargs):
        pass
