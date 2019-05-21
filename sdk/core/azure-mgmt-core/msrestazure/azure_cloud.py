# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
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
import os
import logging
from pprint import pformat


_LOGGER = logging.getLogger(__name__)


# The exact API version doesn't matter too much right now. It just has to be YYYY-MM-DD format.
METADATA_ENDPOINT_SUFFIX = '/metadata/endpoints?api-version=2015-01-01'

class CloudEndpointNotSetException(Exception):
    pass


class CloudSuffixNotSetException(Exception):
    pass


class MetadataEndpointError(Exception):
    pass


class CloudEndpoints(object):  # pylint: disable=too-few-public-methods,too-many-instance-attributes

    def __init__(self,
                 management=None,
                 resource_manager=None,
                 sql_management=None,
                 batch_resource_id=None,
                 gallery=None,
                 active_directory=None,
                 active_directory_resource_id=None,
                 active_directory_graph_resource_id=None):
        # Attribute names are significant. They are used when storing/retrieving clouds from config
        self.management = management
        self.resource_manager = resource_manager
        self.sql_management = sql_management
        self.batch_resource_id = batch_resource_id
        self.gallery = gallery
        self.active_directory = active_directory
        self.active_directory_resource_id = active_directory_resource_id
        self.active_directory_graph_resource_id = active_directory_graph_resource_id

    def has_endpoint_set(self, endpoint_name):
        try:
            # Can't simply use hasattr here as we override __getattribute__ below.
            # Python 3 hasattr() only returns False if an AttributeError is raised but we raise
            # CloudEndpointNotSetException. This exception is not a subclass of AttributeError.
            getattr(self, endpoint_name)
            return True
        except Exception:  # pylint: disable=broad-except
            return False

    def __getattribute__(self, name):
        val = object.__getattribute__(self, name)
        if val is None:
            raise CloudEndpointNotSetException("The endpoint '{}' for this cloud "
                                               "is not set but is used.".format(name))
        return val


class CloudSuffixes(object):  # pylint: disable=too-few-public-methods

    def __init__(self,
                 storage_endpoint=None,
                 keyvault_dns=None,
                 sql_server_hostname=None,
                 azure_datalake_store_file_system_endpoint=None,
                 azure_datalake_analytics_catalog_and_job_endpoint=None):
        # Attribute names are significant. They are used when storing/retrieving clouds from config
        self.storage_endpoint = storage_endpoint
        self.keyvault_dns = keyvault_dns
        self.sql_server_hostname = sql_server_hostname
        self.azure_datalake_store_file_system_endpoint = azure_datalake_store_file_system_endpoint
        self.azure_datalake_analytics_catalog_and_job_endpoint = azure_datalake_analytics_catalog_and_job_endpoint  # pylint: disable=line-too-long

    def __getattribute__(self, name):
        val = object.__getattribute__(self, name)
        if val is None:
            raise CloudSuffixNotSetException("The suffix '{}' for this cloud "
                                             "is not set but is used.".format(name))
        return val


class Cloud(object):  # pylint: disable=too-few-public-methods
    """ Represents an Azure Cloud instance """

    def __init__(self,
                 name,
                 endpoints=None,
                 suffixes=None):
        self.name = name
        self.endpoints = endpoints or CloudEndpoints()
        self.suffixes = suffixes or CloudSuffixes()

    def __str__(self):
        o = {
            'name': self.name,
            'endpoints': vars(self.endpoints),
            'suffixes': vars(self.suffixes),
        }
        return pformat(o)


AZURE_PUBLIC_CLOUD = Cloud(
    'AzureCloud',
    endpoints=CloudEndpoints(
        management='https://management.core.windows.net/',
        resource_manager='https://management.azure.com/',
        sql_management='https://management.core.windows.net:8443/',
        batch_resource_id='https://batch.core.windows.net/',
        gallery='https://gallery.azure.com/',
        active_directory='https://login.microsoftonline.com',
        active_directory_resource_id='https://management.core.windows.net/',
        active_directory_graph_resource_id='https://graph.windows.net/'),
    suffixes=CloudSuffixes(
        storage_endpoint='core.windows.net',
        keyvault_dns='.vault.azure.net',
        sql_server_hostname='.database.windows.net',
        azure_datalake_store_file_system_endpoint='azuredatalakestore.net',
        azure_datalake_analytics_catalog_and_job_endpoint='azuredatalakeanalytics.net'))

AZURE_CHINA_CLOUD = Cloud(
    'AzureChinaCloud',
    endpoints=CloudEndpoints(
        management='https://management.core.chinacloudapi.cn/',
        resource_manager='https://management.chinacloudapi.cn',
        sql_management='https://management.core.chinacloudapi.cn:8443/',
        batch_resource_id='https://batch.chinacloudapi.cn/',
        gallery='https://gallery.chinacloudapi.cn/',
        active_directory='https://login.chinacloudapi.cn',
        active_directory_resource_id='https://management.core.chinacloudapi.cn/',
        active_directory_graph_resource_id='https://graph.chinacloudapi.cn/'),
    suffixes=CloudSuffixes(
        storage_endpoint='core.chinacloudapi.cn',
        keyvault_dns='.vault.azure.cn',
        sql_server_hostname='.database.chinacloudapi.cn'))

AZURE_US_GOV_CLOUD = Cloud(
    'AzureUSGovernment',
    endpoints=CloudEndpoints(
        management='https://management.core.usgovcloudapi.net/',
        resource_manager='https://management.usgovcloudapi.net/',
        sql_management='https://management.core.usgovcloudapi.net:8443/',
        batch_resource_id='https://batch.core.usgovcloudapi.net/',
        gallery='https://gallery.usgovcloudapi.net/',
        active_directory='https://login.microsoftonline.us',
        active_directory_resource_id='https://management.core.usgovcloudapi.net/',
        active_directory_graph_resource_id='https://graph.windows.net/'),
    suffixes=CloudSuffixes(
        storage_endpoint='core.usgovcloudapi.net',
        keyvault_dns='.vault.usgovcloudapi.net',
        sql_server_hostname='.database.usgovcloudapi.net'))

AZURE_GERMAN_CLOUD = Cloud(
    'AzureGermanCloud',
    endpoints=CloudEndpoints(
        management='https://management.core.cloudapi.de/',
        resource_manager='https://management.microsoftazure.de',
        sql_management='https://management.core.cloudapi.de:8443/',
        batch_resource_id='https://batch.cloudapi.de/',
        gallery='https://gallery.cloudapi.de/',
        active_directory='https://login.microsoftonline.de',
        active_directory_resource_id='https://management.core.cloudapi.de/',
        active_directory_graph_resource_id='https://graph.cloudapi.de/'),
    suffixes=CloudSuffixes(
        storage_endpoint='core.cloudapi.de',
        keyvault_dns='.vault.microsoftazure.de',
        sql_server_hostname='.database.cloudapi.de'))


def _populate_from_metadata_endpoint(cloud, arm_endpoint, session=None):
    endpoints_in_metadata = ['active_directory_graph_resource_id',
                             'active_directory_resource_id', 'active_directory']
    if not arm_endpoint or all([cloud.endpoints.has_endpoint_set(n) for n in endpoints_in_metadata]):
        return
    try:
        error_msg_fmt = "Unable to get endpoints from the cloud.\n{}"
        import requests
        session = requests.Session() if session is None else session
        metadata_endpoint = arm_endpoint + METADATA_ENDPOINT_SUFFIX
        response = session.get(metadata_endpoint)
        if response.status_code == 200:
            metadata = response.json()
            if not cloud.endpoints.has_endpoint_set('gallery'):
                setattr(cloud.endpoints, 'gallery', metadata.get('galleryEndpoint'))
            if not cloud.endpoints.has_endpoint_set('active_directory_graph_resource_id'):
                setattr(cloud.endpoints, 'active_directory_graph_resource_id', metadata.get('graphEndpoint'))
            if not cloud.endpoints.has_endpoint_set('active_directory'):
                setattr(cloud.endpoints, 'active_directory', metadata['authentication'].get('loginEndpoint'))
            if not cloud.endpoints.has_endpoint_set('active_directory_resource_id'):
                setattr(cloud.endpoints, 'active_directory_resource_id', metadata['authentication']['audiences'][0])
        else:
            msg = 'Server returned status code {} for {}'.format(response.status_code, metadata_endpoint)
            raise MetadataEndpointError(error_msg_fmt.format(msg))
    except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError) as err:
        msg = 'Please ensure you have network connection. Error detail: {}'.format(str(err))
        raise MetadataEndpointError(error_msg_fmt.format(msg))
    except ValueError as err:
        msg = 'Response body does not contain valid json. Error detail: {}'.format(str(err))
        raise MetadataEndpointError(error_msg_fmt.format(msg))

def get_cloud_from_metadata_endpoint(arm_endpoint, name=None, session=None):
    """Get a Cloud object from an ARM endpoint.

    .. versionadded:: 0.4.11

    :Example:

    .. code:: python

        get_cloud_from_metadata_endpoint(https://management.azure.com/, "Public Azure")

    :param str arm_endpoint: The ARM management endpoint
    :param str name: An optional name for the Cloud object. Otherwise it's the ARM endpoint
    :params requests.Session session: A requests session object if you need to configure proxy, cert, etc.
    :rtype Cloud:
    :returns: a Cloud object
    :raises: MetadataEndpointError if unable to build the Cloud object
    """
    cloud = Cloud(name or arm_endpoint)
    cloud.endpoints.management = arm_endpoint
    cloud.endpoints.resource_manager = arm_endpoint
    _populate_from_metadata_endpoint(cloud, arm_endpoint, session)
    return cloud
