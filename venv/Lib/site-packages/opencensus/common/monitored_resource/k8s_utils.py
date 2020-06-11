# Copyright 2019, OpenCensus Authors
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

import os

from opencensus.common.monitored_resource import gcp_metadata_config

# Env var that signals that we're in a kubernetes container
_KUBERNETES_SERVICE_HOST = 'KUBERNETES_SERVICE_HOST'

# Name of the cluster the container is running in
CLUSTER_NAME_KEY = 'k8s.io/cluster/name'

# ID of the instance the container is running on
NAMESPACE_NAME_KEY = 'k8s.io/namespace/name'

# Container pod ID
POD_NAME_KEY = 'k8s.io/pod/name'

# Container name
CONTAINER_NAME_KEY = 'k8s.io/container/name'

# Attributes set from environment variables
_K8S_ENV_ATTRIBUTES = {
    CONTAINER_NAME_KEY: 'CONTAINER_NAME',
    NAMESPACE_NAME_KEY: 'NAMESPACE',
    POD_NAME_KEY: 'HOSTNAME'
}


def is_k8s_environment():
    """Whether the environment is a kubernetes container.

    The KUBERNETES_SERVICE_HOST environment variable must be set.
    """
    return _KUBERNETES_SERVICE_HOST in os.environ


def get_k8s_metadata():
    """Get kubernetes container metadata, as on GCP GKE."""
    k8s_metadata = {}

    gcp_cluster = (gcp_metadata_config.GcpMetadataConfig
                   .get_attribute(gcp_metadata_config.CLUSTER_NAME_KEY))
    if gcp_cluster is not None:
        k8s_metadata[CLUSTER_NAME_KEY] = gcp_cluster

    for attribute_key, attribute_env in _K8S_ENV_ATTRIBUTES.items():
        attribute_value = os.environ.get(attribute_env)
        if attribute_value is not None:
            k8s_metadata[attribute_key] = attribute_value

    return k8s_metadata
