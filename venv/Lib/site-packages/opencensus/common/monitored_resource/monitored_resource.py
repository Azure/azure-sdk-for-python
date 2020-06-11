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

from opencensus.common import resource
from opencensus.common.monitored_resource import aws_identity_doc_utils
from opencensus.common.monitored_resource import gcp_metadata_config
from opencensus.common.monitored_resource import k8s_utils


# Supported environments (resource types)
_GCE_INSTANCE = "gce_instance"
_K8S_CONTAINER = "k8s_container"
_AWS_EC2_INSTANCE = "aws_ec2_instance"


def is_gce_environment():
    """Whether the environment is a virtual machine on GCE."""
    return gcp_metadata_config.GcpMetadataConfig.is_running_on_gcp()


def is_aws_environment():
    """Whether the environment is a virtual machine instance on EC2."""
    return aws_identity_doc_utils.AwsIdentityDocumentUtils.is_running_on_aws()


def get_instance():
    """Get a resource based on the application environment.

    Returns a `Resource` configured for the current environment, or None if the
    environment is unknown or unsupported.

    :rtype: :class:`opencensus.common.resource.Resource` or None
    :return: A `Resource` configured for the current environment.
    """
    resources = []
    env_resource = resource.get_from_env()
    if env_resource is not None:
        resources.append(env_resource)

    if k8s_utils.is_k8s_environment():
        resources.append(resource.Resource(
            _K8S_CONTAINER, k8s_utils.get_k8s_metadata()))

    if is_gce_environment():
        resources.append(resource.Resource(
            _GCE_INSTANCE,
            gcp_metadata_config.GcpMetadataConfig().get_gce_metadata()))
    elif is_aws_environment():
        resources.append(resource.Resource(
            _AWS_EC2_INSTANCE,
            (aws_identity_doc_utils.AwsIdentityDocumentUtils()
             .get_aws_metadata())))

    if not resources:
        return None
    return resource.merge_resources(resources)
