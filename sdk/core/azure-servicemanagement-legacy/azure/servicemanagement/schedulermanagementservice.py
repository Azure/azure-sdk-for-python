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
import json

from .constants import (
    DEFAULT_HTTP_TIMEOUT,
    MANAGEMENT_HOST,
)
from .models import (
    AvailabilityResponse,
    CloudService,
    CloudServices,
    Resource,
)
from ._common_conversion import (
    _str,
)
from ._common_error import (
    _validate_not_none
)
from .servicemanagementclient import (
    _ServiceManagementClient,
)
from ._serialization import (
    JSONEncoder,
    _SchedulerManagementXmlSerializer,
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
        The Create Cloud Service request creates a new cloud service. When job
        collections are created, they are hosted within a cloud service.
        A cloud service groups job collections together in a given region.
        Once a cloud service has been created, job collections can then be
        created and contained within it.

        cloud_service_id:
            The cloud service id
        label:
            The name of the cloud service.
        description:
            The description of the cloud service.
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

        return self._perform_put(path, body, as_async=True)

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
        return self._perform_delete(path, as_async=True)

    def check_job_collection_name(self, cloud_service_id, job_collection_id):
        '''
        The Check Name Availability operation checks if a new job collection with
        the given name may be created, or if it is unavailable. The result of the
        operation is a Boolean true or false.

        cloud_service_id:
            The cloud service id
        job_collection_id:
            The name of the job_collection_id.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)

        path = self._get_cloud_services_path(
            cloud_service_id, "scheduler", "jobCollections")
        path += "?op=checknameavailability&resourceName=" + job_collection_id
        return self._perform_post(path, None, AvailabilityResponse)

    def create_job_collection(self, cloud_service_id, job_collection_id, plan="Standard"):
        '''
        The Create Job Collection request is specified as follows. Replace <subscription-id>
        with your subscription ID, <cloud-service-id> with your cloud service ID, and
        <job-collection-id> with the ID of the job collection you\'d like to create.
        There are no "default" pre-existing job collections every job collection
        must be manually created.

        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)

        path = self._get_cloud_services_path(
            cloud_service_id, "scheduler", "jobCollections")

        path += '/' + _str(job_collection_id)
        body = _SchedulerManagementXmlSerializer.create_job_collection_to_xml(
            plan)

        return self._perform_put(path, body, as_async=True)

    def delete_job_collection(self, cloud_service_id, job_collection_id):
        '''
        The Delete Job Collection request is specified as follows. Replace <subscription-id>
        with your subscription ID, <cloud-service-id> with your cloud service ID, and
        <job-collection-id> with the ID of the job collection you\'d like to delete.

        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)

        path = self._get_cloud_services_path(
            cloud_service_id, "scheduler", "jobCollections")

        path += '/' + _str(job_collection_id)

        return self._perform_delete(path, as_async=True)

    def get_job_collection(self, cloud_service_id, job_collection_id):
        '''
        The Get Job Collection operation gets the details of a job collection

        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)

        path = self._get_job_collection_path(
            cloud_service_id, job_collection_id)

        return self._perform_get(path, Resource)

    def create_job(self, cloud_service_id, job_collection_id, job_id, job):
        '''
        The Create Job request creates a new job.
        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        job_id:
            The job id you wish to create.
        job:
            A dictionary of the payload
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)
        _validate_not_none('job_id', job_id)
        _validate_not_none('job', job)

        path = self._get_job_collection_path(
            cloud_service_id, job_collection_id, job_id)

        self.content_type = "application/json"
        return self._perform_put(path, JSONEncoder().encode(job), as_async=True)

    def delete_job(self, cloud_service_id, job_collection_id, job_id):
        '''
        The Delete Job request creates a new job.
        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        job_id:
            The job id you wish to create.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)
        _validate_not_none('job_id', job_id)

        path = self._get_job_collection_path(
            cloud_service_id, job_collection_id, job_id)
        return self._perform_delete(path, as_async=True)

    def get_job(self, cloud_service_id, job_collection_id, job_id):
        '''
        The Get Job operation gets the details (including the current job status)
        of the specified job from the specified job collection.

        The return type is

        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        job_id:
            The job id you wish to create.
        '''
        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)
        _validate_not_none('job_id', job_id)

        path = self._get_job_collection_path(
            cloud_service_id, job_collection_id, job_id)

        self.content_type = "application/json"
        payload = self._perform_get(path).body.decode()
        return json.loads(payload)

    def get_all_jobs(self, cloud_service_id, job_collection_id):
        '''
        The Get All Jobs operation gets all the jobs in a job collection.
        The full list of jobs can be accessed by excluding any job ID in the
        GET call (i.e. /jobs.)

        The return type is

        cloud_service_id:
            The cloud service id
        job_collection_id:
            Name of the hosted service.
        '''

        _validate_not_none('cloud_service_id', cloud_service_id)
        _validate_not_none('job_collection_id', job_collection_id)

        path = self._get_job_collection_path(cloud_service_id, job_collection_id,"")


        self.content_type = "application/json"
        payload = self._perform_get(path).body.decode()
        return json.loads(payload)

    #--Helper functions --------------------------------------------------

    def _get_job_collection_path(self, cloud_service_id, job_collection_id, job_id=None):
        path = self._get_cloud_services_path(
            cloud_service_id, "scheduler", "~/jobCollections")

        path += '/' + _str(job_collection_id)
        if job_id is not None:
            path += '/jobs/' + job_id

        path += '?api-version=2014-04-01'
        return path

    def _get_list_cloud_services_path(self):
        return self._get_path('cloudservices', None)
