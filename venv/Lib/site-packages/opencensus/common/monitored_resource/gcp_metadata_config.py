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

_GCP_METADATA_URI = 'http://metadata.google.internal/computeMetadata/v1/'
_GCP_METADATA_URI_HEADER = {'Metadata-Flavor': 'Google'}

# ID of the GCP project associated with this resource, such as "my-project"
PROJECT_ID_KEY = 'project_id'

# Numeric VM instance identifier assigned by GCE
INSTANCE_ID_KEY = 'instance_id'

# The GCE zone in which the VM is running
ZONE_KEY = 'zone'

# GKE cluster name
CLUSTER_NAME_KEY = 'instance/attributes/cluster-name'

# GCE common attributes
# See: https://cloud.google.com/appengine/docs/flexible/python/runtime#environment_variables  # noqa
_GCE_ATTRIBUTES = {
    PROJECT_ID_KEY: 'project/project-id',
    INSTANCE_ID_KEY: 'instance/id',
    ZONE_KEY: 'instance/zone'
}

_ATTRIBUTE_URI_TRANSFORMATIONS = {
    _GCE_ATTRIBUTES[ZONE_KEY]:
        lambda v: v[v.rfind('/') + 1:] if '/' in v else v
}

_GCP_METADATA_MAP = {}


class GcpMetadataConfig(object):
    """GcpMetadata represents metadata retrieved from GCP (GKE and GCE)
    environment. Some attributes are retrieved from the system environment.
    see : <a href="https://cloud.google.com/compute/docs/
    storing-retrieving-metadata"> https://cloud.google.com/compute/docs/storing
    -retrieving-metadata</a>
    """
    inited = False
    is_running = False

    @classmethod
    def _initialize_metadata_service(cls):
        """Initialize metadata service once and load gcp metadata into map
        This method should only be called once.
        """
        if cls.inited:
            return

        instance_id = cls.get_attribute('instance/id')

        if instance_id is not None:
            cls.is_running = True

            _GCP_METADATA_MAP['instance_id'] = instance_id

            # fetch attributes from metadata request
            for attribute_key, attribute_uri in _GCE_ATTRIBUTES.items():
                if attribute_key not in _GCP_METADATA_MAP:
                    attribute_value = cls.get_attribute(attribute_uri)
                    if attribute_value is not None:  # pragma: NO COVER
                        _GCP_METADATA_MAP[attribute_key] = attribute_value

        cls.inited = True

    @classmethod
    def is_running_on_gcp(cls):
        cls._initialize_metadata_service()
        return cls.is_running

    def get_gce_metadata(self):
        """for GCP GCE instance"""
        if self.is_running_on_gcp():
            return _GCP_METADATA_MAP

        return dict()

    @staticmethod
    def get_attribute(attribute_uri):
        """
        Fetch the requested instance metadata entry.
        :param attribute_uri: attribute_uri: attribute name relative to the
        computeMetadata/v1 prefix
        :return:  The value read from the metadata service or None
        """
        attribute_value = get_request(_GCP_METADATA_URI + attribute_uri,
                                      _GCP_METADATA_URI_HEADER)

        if attribute_value is not None and isinstance(attribute_value, bytes):
            # At least in python3, bytes are are returned from
            # urllib (although the response is text), convert
            # to a normal string:
            attribute_value = attribute_value.decode('utf-8')

        transformation = _ATTRIBUTE_URI_TRANSFORMATIONS.get(attribute_uri)
        if transformation is not None:
            attribute_value = transformation(attribute_value)

        return attribute_value
