#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from .constants import (
    DEFAULT_HTTP_TIMEOUT,
    MANAGEMENT_HOST,
)
from .models import (
    AffinityGroups,
    AffinityGroup,
    AvailabilityResponse,
    Certificate,
    Certificates,
    DataVirtualHardDisk,
    Deployment,
    Disk,
    Disks,
    Locations,
    HostedService,
    HostedServices,
    Images,
    OperatingSystems,
    OperatingSystemFamilies,
    OSImage,
    PersistentVMRole,
    ResourceExtensions,
    ReservedIP,
    ReservedIPs,
    RoleSize,
    RoleSizes,
    StorageService,
    StorageServices,
    Subscription,
    Subscriptions,
    SubscriptionCertificate,
    SubscriptionCertificates,
    SubscriptionOperationCollection,
    VirtualNetworkSites,
    VMImages,
)
from ._common_conversion import (
    _str,
)
from ._common_error import (
    _validate_not_none,
)
from .servicemanagementclient import (
    _ServiceManagementClient,
)
from ._serialization import (
    _XmlSerializer,
)

class ComputeManagementService(_ServiceManagementClient):

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST, request_session=None,
                 timeout=DEFAULT_HTTP_TIMEOUT):
        '''
        Initializes the management service.

        subscription_id:
            Subscription to manage.
        cert_file:
            Path to .pem certificate file (httplib), or location of the
            certificate in your Personal certificate store (winhttp) in the
            CURRENT_USER\my\CertificateName format.
            If a request_session is specified, then this is unused.
        host:
            Live ServiceClient URL. Defaults to Azure public cloud.
        request_session:
            Session object to use for http requests. If this is specified, it
            replaces the default use of httplib or winhttp. Also, the cert_file
            parameter is unused when a session is passed in.
            The session object handles authentication, and as such can support
            multiple types of authentication: .pem certificate, oauth.
            For example, you can pass in a Session instance from the requests
            library. To use .pem certificate authentication with requests
            library, set the path to the .pem file on the session.cert
            attribute.
        timeout:
            Optional. Timeout for the http request, in seconds.
        '''
        super(ComputeManagementService, self).__init__(
            subscription_id, cert_file, host, request_session, timeout)

    def replicate(self, vm_image_name, regions, offer, sku, version):
        '''
        Replicate a VM image to multiple target locations. This operation
        is only for publishers. You have to be registered as image publisher
        with Microsoft Azure to be able to call this.

        vm_image_name:
            Specifies the name of the VM Image that is to be used for
            replication
        regions:
            Specified a list of regions to replicate the image to
            Note: The regions in the request body are not additive. If a VM
            Image has already been replicated to Regions A, B, and C, and
            a request is made to replicate to Regions A and D, the VM
            Image will remain in Region A, will be replicated in Region D,
            and will be unreplicated from Regions B and C
        offer:
            Specifies the publisher defined name of the offer. The allowed
            characters are uppercase or lowercase letters, digit,
            hypen(-), period (.).The maximum allowed length is 64 characters.
        sku:
            Specifies the publisher defined name of the Sku. The allowed
            characters are uppercase or lowercase letters, digit,
            hypen(-), period (.). The maximum allowed length is 64 characters.
        version:
            Specifies the publisher defined version of the image.
            The allowed characters are digit and period.
            Format: <MajorVersion>.<MinorVersion>.<Patch>
            Example: '1.0.0' or '1.1.0' The 3 version number to
            follow standard of most of the RPs. See http://semver.org
        '''
        _validate_not_none('vm_image_name', vm_image_name)
        _validate_not_none('regions', regions)
        _validate_not_none('offer', offer)
        _validate_not_none('sku', sku)
        _validate_not_none('version', version)

        return self._perform_put(
            self._get_replication_path_using_vm_image_name(vm_image_name),
            _XmlSerializer.replicate_image_to_xml(
                regions,
                offer,
                sku,
                version
            ),
            async=True,
            x_ms_version='2015-04-01'
        )

    def unreplicate(self, vm_image_name):
        '''
        Unreplicate a VM image from all regions This operation
        is only for publishers. You have to be registered as image publisher
        with Microsoft Azure to be able to call this

        vm_image_name:
            Specifies the name of the VM Image that is to be used for
            unreplication. The VM Image Name should be the user VM Image,
            not the published name of the VM Image.

        '''
        _validate_not_none('vm_image_name', vm_image_name)

        return self._perform_put(
            self._get_unreplication_path_using_vm_image_name(vm_image_name),
            None,
            async=True,
            x_ms_version='2015-04-01'
        )

    def share(self, vm_image_name, permission):
        '''
        Share an already replicated OS image. This operation is only for
        publishers. You have to be registered as image publisher with Windows
        Azure to be able to call this.

        vm_image_name:
            The name of the virtual machine image to share
        permission:
            The sharing permission: public, msdn, or private
        '''
        _validate_not_none('vm_image_name', vm_image_name)
        _validate_not_none('permission', permission)

        path = self._get_sharing_path_using_vm_image_name(vm_image_name)
        query = '&permission=' + permission
        path = path + '?' + query.lstrip('&')

        return self._perform_put(
            path, None, async=True, x_ms_version='2015-04-01'
        )

    #--Helper functions --------------------------------------------------
    def _get_replication_path_using_vm_image_name(self, vm_image_name):
        return self._get_path(
            'services/images/' + _str(vm_image_name) + '/replicate', None
        )

    def _get_unreplication_path_using_vm_image_name(self, vm_image_name):
        return self._get_path(
            'services/images/' + _str(vm_image_name) + '/unreplicate', None
        )

    def _get_sharing_path_using_vm_image_name(self, vm_image_name):
        return self._get_path(
            'services/images/' + _str(vm_image_name) + '/shareasync', None
        )
