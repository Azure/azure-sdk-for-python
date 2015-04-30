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
from azure import (
    DEFAULT_HTTP_TIMEOUT,
    MANAGEMENT_HOST,
    _str,
    _validate_not_none
)
from azure.servicemanagement import (
    _SchedulerManagementXmlSerializer,
    CloudService,
    CloudServices,
    AvailabilityResponse,
)
from azure.servicemanagement.servicemanagementclient import (
    _ServiceManagementClient,
)


class SchedulerManagementService(_ServiceManagementClient):

    ''' Note that this class is a preliminary work on Scheduler
        management. Since it lack a lot a features, final version
        can be slightly different from the current one.
    '''

    def __init__(self, subscription_id=None, cert_file=None,
                 host=MANAGEMENT_HOST, request_session=None,
                 timeout=DEFAULT_HTTP_TIMEOUT):
        '''
        Initializes the scheduler management service.

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
        super(SchedulerManagementService, self).__init__(
            subscription_id, cert_file, host, request_session, timeout)

    #--Operations for scheduler ----------------------------------------
    def list_cloud_services(self):
        '''
        List the cloud services for scheduling defined on the account.
        '''
        return self._perform_get(self._get_list_cloud_services_path(),
                                 CloudServices)

    def create_cloud_service(self, cloud_service_id, label, description, geo_region):
        '''
        The Get Cloud Service operation gets all the resources (job collections)
        in the cloud service.

        cloud_service_id:
            The cloud service id
        geo_region:
            The geographical region of the webspace that will be created.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('label', label)
        _validate_not_none('description', description)
        _validate_not_none('geo_region', geo_region)

        path = self._get_cloud_services_path(cloud_service_id)
        body = _SchedulerManagementXmlSerializer.create_cloud_service_to_xml(
            label, description, geo_region)

        return self._perform_put(path, body)

    def get_cloud_service(self, cloud_service_id):
        '''
        The Get Cloud Service operation gets all the resources (job collections)
        in the cloud service.

        cloud_service_id:
            The cloud service id
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        path = self._get_cloud_services_path(cloud_service_id)
        return self._perform_get(path, CloudService)

    def delete_cloud_service(self, cloud_service_id):
        '''
        The Get Cloud Service operation gets all the resources (job collections)
        in the cloud service.

        cloud_service_id:
            The cloud service id
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        path = self._get_cloud_services_path(cloud_service_id)
        return self._perform_delete(path, CloudService)

    def check_job_collection_name(self, cloud_service_id, job_collection_name):
        '''
        The Check Name Availability operation checks if a new job collection with
        the given name may be created, or if it is unavailable. The result of the
        operation is a Boolean true or false.

        cloud_service_id:
            The cloud service id
        job_collection_name:
            Name of the hosted service.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_name', job_collection_name)

        path = self._get_cloud_services_path(
            cloud_service_id, "scheduler", "jobCollections")
        path += "?op=checknameavailability&resourceName=" + job_collection_name
        return self._perform_post(path, "", AvailabilityResponse)

    #--Helper functions --------------------------------------------------

    def _get_list_cloud_services_path(self):
        return self._get_path('cloudservices', None)
