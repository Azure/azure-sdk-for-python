# Copyright 2018, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from opencensus.common.http_handler import get_request
import json

REGION_KEY = 'region'
ACCOUNT_ID_KEY = 'aws_account'
INSTANCE_ID_KEY = 'instance_id'

# AWS provides Instance Metadata via below url
_AWS_INSTANCE_IDENTITY_DOCUMENT_URI = \
    "http://169.254.169.254/latest/dynamic/instance-identity/document"

_AWS_ATTRIBUTES = {
    # Region is the AWS region for the VM. The format of this field is
    # "aws:{region}", where supported values for {region} are listed at
    # http://docs.aws.amazon.com/general/latest/gr/rande.html.
    'region': REGION_KEY,

    # accountId is the AWS account number for the VM.
    'accountId': ACCOUNT_ID_KEY,

    # instanceId is the instance id of the instance.
    'instanceId': INSTANCE_ID_KEY
}

# inited is used to make sure AWS initialize executes only once.
inited = False

# Detects if the application is running on EC2 by making a connection to AWS
# instance identity document URI.If connection is successful, application
# should be on an EC2 instance.
is_running_on_aws = False

aws_metadata_map = {}


class AwsIdentityDocumentUtils(object):
    """Util methods for getting and parsing AWS instance identity document."""

    inited = False
    is_running = False

    @classmethod
    def _initialize_aws_identity_document(cls):
        """This method, tries to establish an HTTP connection to AWS instance
        identity document url. If the application is running on an EC2
        instance, we should be able to get back a valid JSON document. Make a
        http get request call and store data in local map.
        This method should only be called once.
        """

        if cls.inited:
            return

        content = get_request(_AWS_INSTANCE_IDENTITY_DOCUMENT_URI)
        if content is not None:
            content = json.loads(content)
            for env_var, attribute_key in _AWS_ATTRIBUTES.items():
                attribute_value = content.get(env_var)
                if attribute_value is not None:
                    aws_metadata_map[attribute_key] = attribute_value

            cls.is_running = True

        cls.inited = True

    @classmethod
    def is_running_on_aws(cls):
        cls._initialize_aws_identity_document()
        return cls.is_running

    def get_aws_metadata(self):
        """AWS Instance Identity Document is a JSON file.
        See docs.aws.amazon.com/AWSEC2/latest/UserGuide/
        instance-identity-documents.html.
        :return:
        """
        if self.is_running_on_aws():
            return aws_metadata_map

        return dict()
