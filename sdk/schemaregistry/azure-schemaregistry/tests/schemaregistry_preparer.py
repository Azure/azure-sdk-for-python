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


SCHEMA_REGISTRY_ENDPOINT_PARAM = "schemaregistry_endpoint"
SCHEMA_REGISTRY_GROUP_PARAM = "schemaregistry_group"
SCHEMA_REGISTRY_ENDPOINT_ENV_KEY_NAME = 'SCHEMA_REGISTRY_ENDPOINT'
SCHEMA_REGISTRY_GROUP_ENV_KEY_NAME = 'SCHEMA_REGISTRY_GROUP'


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
                "SCHEMAREGISTRY_CLIENT_ID": os.environ["SCHEMAREGISTRY_CLIENT_ID"],
                "SCHEMAREGISTRY_RESOURCE_MANAGER_URL": os.environ["SCHEMAREGISTRY_RESOURCE_MANAGER_URL"],
                "SCHEMAREGISTRY_CLIENT_SECRET": os.environ["SCHEMAREGISTRY_CLIENT_SECRET"],
                "schemaregistry_endpoint": os.environ["SCHEMAREGISTRY_ENDPOINT"],
                "SCHEMAREGISTRY_RESOURCE_GROUP": os.environ["SCHEMAREGISTRY_RESOURCE_GROUP"],
                "SCHEMAREGISTRY_TENANT_ID": os.environ["SCHEMAREGISTRY_TENANT_ID"],
                "SCHEMAREGISTRY_LOCATION": os.environ["SCHEMAREGISTRY_LOCATION"],
                "schemaregistry_group": os.environ["SCHEMAREGISTRY_GROUP"],
                "SCHEMAREGISTRY_AZURE_AUTHORITY_HOST": os.environ["SCHEMAREGISTRY_AZURE_AUTHORITY_HOST"],
                "SCHEMAREGISTRY_SUBSCRIPTION_ID": os.environ["SCHEMAREGISTRY_SUBSCRIPTION_ID"],
                "SCHEMAREGISTRY_ENVIRONMENT": os.environ["SCHEMAREGISTRY_ENVIRONMENT"],
                "SCHEMAREGISTRY_SERVICE_MANAGEMENT_URL": os.environ["SCHEMAREGISTRY_SERVICE_MANAGEMENT_URL"]
            }
            # return {
            #     SCHEMA_REGISTRY_ENDPOINT_PARAM: os.environ[SCHEMA_REGISTRY_ENDPOINT_ENV_KEY_NAME],
            #     SCHEMA_REGISTRY_GROUP_PARAM: os.environ[SCHEMA_REGISTRY_GROUP_ENV_KEY_NAME]
            # }
        else:
            return {
                SCHEMA_REGISTRY_ENDPOINT_PARAM: "sr-playground.servicebus.windows.net",
                SCHEMA_REGISTRY_GROUP_PARAM: "azsdk_python_test_group"
            }

    def remove_resource(self, name, **kwargs):
        pass
