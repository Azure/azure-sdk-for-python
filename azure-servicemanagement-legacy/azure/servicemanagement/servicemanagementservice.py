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
    OSImageDetails,
    PersistentVMRole,
    ResourceExtensions,
    ReservedIP,
    ReservedIPs,
    ReplicationProgress,
    ReplicationProgressElement,
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

class ServiceManagementService(_ServiceManagementClient):

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
        super(ServiceManagementService, self).__init__(
            subscription_id, cert_file, host, request_session, timeout)

    #--Operations for subscriptions --------------------------------------
    def list_role_sizes(self):
        '''
        Lists the role sizes that are available under the specified
        subscription.
        '''
        return self._perform_get(self._get_role_sizes_path(),
                                 RoleSizes)

    def list_subscriptions(self):
        '''
        Returns a list of subscriptions that you can access.

        You must make sure that the request that is made to the management
        service is secure using an Active Directory access token.
        '''
        return self._perform_get(self._get_subscriptions_path(),
                                 Subscriptions)

    #--Operations for storage accounts -----------------------------------
    def list_storage_accounts(self):
        '''
        Lists the storage accounts available under the current subscription.
        '''
        return self._perform_get(self._get_storage_service_path(),
                                 StorageServices)

    def get_storage_account_properties(self, service_name):
        '''
        Returns system properties for the specified storage account.

        service_name:
            Name of the storage service account.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_get(self._get_storage_service_path(service_name),
                                 StorageService)

    def get_storage_account_keys(self, service_name):
        '''
        Returns the primary and secondary access keys for the specified
        storage account.

        service_name:
            Name of the storage service account.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_get(
            self._get_storage_service_path(service_name) + '/keys',
            StorageService)

    def regenerate_storage_account_keys(self, service_name, key_type):
        '''
        Regenerates the primary or secondary access key for the specified
        storage account.

        service_name:
            Name of the storage service account.
        key_type:
            Specifies which key to regenerate. Valid values are:
            Primary, Secondary
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('key_type', key_type)
        return self._perform_post(
            self._get_storage_service_path(
                service_name) + '/keys?action=regenerate',
            _XmlSerializer.regenerate_keys_to_xml(
                key_type),
            StorageService)

    def create_storage_account(self, service_name, description, label,
                               affinity_group=None, location=None,
                               geo_replication_enabled=None,
                               extended_properties=None,
                               account_type='Standard_GRS'):
        '''
        Creates a new storage account in Windows Azure.

        service_name:
            A name for the storage account that is unique within Windows Azure.
            Storage account names must be between 3 and 24 characters in length
            and use numbers and lower-case letters only.
        description:
            A description for the storage account. The description may be up
            to 1024 characters in length.
        label:
            A name for the storage account. The name may be up to 100
            characters in length. The name can be used to identify the storage
            account for your tracking purposes.
        affinity_group:
            The name of an existing affinity group in the specified
            subscription. You can specify either a location or affinity_group,
            but not both.
        location:
            The location where the storage account is created. You can specify
            either a location or affinity_group, but not both.
        geo_replication_enabled:
            Deprecated. Replaced by the account_type parameter.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        account_type:
            Specifies whether the account supports locally-redundant storage,
            geo-redundant storage, zone-redundant storage, or read access
            geo-redundant storage.
            Possible values are:
                Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('description', description)
        _validate_not_none('label', label)
        if affinity_group is None and location is None:
            raise ValueError(
                'location or affinity_group must be specified')
        if affinity_group is not None and location is not None:
            raise ValueError(
                'Only one of location or affinity_group needs to be specified')
        if geo_replication_enabled == False:
            account_type = 'Standard_LRS'
        return self._perform_post(
            self._get_storage_service_path(),
            _XmlSerializer.create_storage_service_input_to_xml(
                service_name,
                description,
                label,
                affinity_group,
                location,
                account_type,
                extended_properties),
            async=True)

    def update_storage_account(self, service_name, description=None,
                               label=None, geo_replication_enabled=None,
                               extended_properties=None,
                               account_type='Standard_GRS'):
        '''
        Updates the label, the description, and enables or disables the
        geo-replication status for a storage account in Windows Azure.

        service_name:
            Name of the storage service account.
        description:
            A description for the storage account. The description may be up
            to 1024 characters in length.
        label:
            A name for the storage account. The name may be up to 100
            characters in length. The name can be used to identify the storage
            account for your tracking purposes.
        geo_replication_enabled:
            Deprecated. Replaced by the account_type parameter.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        account_type:
            Specifies whether the account supports locally-redundant storage,
            geo-redundant storage, zone-redundant storage, or read access
            geo-redundant storage.
            Possible values are:
                Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS
        '''
        _validate_not_none('service_name', service_name)
        if geo_replication_enabled == False:
            account_type = 'Standard_LRS'
        return self._perform_put(
            self._get_storage_service_path(service_name),
            _XmlSerializer.update_storage_service_input_to_xml(
                description,
                label,
                account_type,
                extended_properties))

    def delete_storage_account(self, service_name):
        '''
        Deletes the specified storage account from Windows Azure.

        service_name:
            Name of the storage service account.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_delete(
            self._get_storage_service_path(service_name),
            async=True)

    def check_storage_account_name_availability(self, service_name):
        '''
        Checks to see if the specified storage account name is available, or
        if it has already been taken.

        service_name:
            Name of the storage service account.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_get(
            self._get_storage_service_path() +
            '/operations/isavailable/' +
            _str(service_name) + '',
            AvailabilityResponse)

    #--Operations for hosted services ------------------------------------
    def list_hosted_services(self):
        '''
        Lists the hosted services available under the current subscription.

        Note that you will receive a list of HostedService instances, without
        all details inside. For instance, deployments will be None. If you
        want deployments information for a specific host service, you have to
        call get_hosted_service_properties with embed_detail=True.
        '''
        return self._perform_get(self._get_hosted_service_path(),
                                 HostedServices)

    def get_hosted_service_properties(self, service_name, embed_detail=False):
        '''
        Retrieves system properties for the specified hosted service. These
        properties include the service name and service type; the name of the
        affinity group to which the service belongs, or its location if it is
        not part of an affinity group; and optionally, information on the
        service's deployments.

        service_name:
            Name of the hosted service.
        embed_detail:
            When True, the management service returns properties for all
            deployments of the service, as well as for the service itself.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('embed_detail', embed_detail)
        return self._perform_get(
            self._get_hosted_service_path(service_name) +
            '?embed-detail=' +
            _str(embed_detail).lower(),
            HostedService)

    def create_hosted_service(self, service_name, label, description=None,
                              location=None, affinity_group=None,
                              extended_properties=None):
        '''
        Creates a new hosted service in Windows Azure.

        service_name:
            A name for the hosted service that is unique within Windows Azure.
            This name is the DNS prefix name and can be used to access the
            hosted service.
        label:
            A name for the hosted service. The name can be up to 100 characters
            in length. The name can be used to identify the storage account for
            your tracking purposes.
        description:
            A description for the hosted service. The description can be up to
            1024 characters in length.
        location:
            The location where the hosted service will be created. You can
            specify either a location or affinity_group, but not both.
        affinity_group:
            The name of an existing affinity group associated with this
            subscription. This name is a GUID and can be retrieved by examining
            the name element of the response body returned by
            list_affinity_groups. You can specify either a location or
            affinity_group, but not both.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('label', label)
        if affinity_group is None and location is None:
            raise ValueError(
                'location or affinity_group must be specified')
        if affinity_group is not None and location is not None:
            raise ValueError(
                'Only one of location or affinity_group needs to be specified')
        return self._perform_post(self._get_hosted_service_path(),
                                  _XmlSerializer.create_hosted_service_to_xml(
                                      service_name,
                                      label,
                                      description,
                                      location,
                                      affinity_group,
                                      extended_properties),
                                  async=True)

    def update_hosted_service(self, service_name, label=None, description=None,
                              extended_properties=None):
        '''
        Updates the label and/or the description for a hosted service in
        Windows Azure.

        service_name:
            Name of the hosted service.
        label:
            A name for the hosted service. The name may be up to 100 characters
            in length. You must specify a value for either Label or
            Description, or for both. It is recommended that the label be
            unique within the subscription. The name can be used
            identify the hosted service for your tracking purposes.
        description:
            A description for the hosted service. The description may be up to
            1024 characters in length. You must specify a value for either
            Label or Description, or for both.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_put(self._get_hosted_service_path(service_name),
                                 _XmlSerializer.update_hosted_service_to_xml(
                                     label,
                                     description,
                                     extended_properties))

    def delete_hosted_service(self, service_name, complete=False):
        '''
        Deletes the specified hosted service from Windows Azure.

        service_name:
            Name of the hosted service.
        complete:
            True if all OS/data disks and the source blobs for the disks should
            also be deleted from storage.
        '''

        _validate_not_none('service_name', service_name)

        path = self._get_hosted_service_path(service_name)

        if complete == True:
            path = path +'?comp=media'

        return self._perform_delete(path, async=True)

    def get_deployment_by_slot(self, service_name, deployment_slot):
        '''
        Returns configuration information, status, and system properties for
        a deployment.

        service_name:
            Name of the hosted service.
        deployment_slot:
            The environment to which the hosted service is deployed. Valid
            values are: staging, production
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_slot', deployment_slot)
        return self._perform_get(
            self._get_deployment_path_using_slot(
                service_name, deployment_slot),
            Deployment)

    def get_deployment_by_name(self, service_name, deployment_name):
        '''
        Returns configuration information, status, and system properties for a
        deployment.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        return self._perform_get(
            self._get_deployment_path_using_name(
                service_name, deployment_name),
            Deployment)

    def create_deployment(self, service_name, deployment_slot, name,
                          package_url, label, configuration,
                          start_deployment=False,
                          treat_warnings_as_error=False,
                          extended_properties=None):
        '''
        Uploads a new service package and creates a new deployment on staging
        or production.

        service_name:
            Name of the hosted service.
        deployment_slot:
            The environment to which the hosted service is deployed. Valid
            values are: staging, production
        name:
            The name for the deployment. The deployment name must be unique
            among other deployments for the hosted service.
        package_url:
            A URL that refers to the location of the service package in the
            Blob service. The service package can be located either in a
            storage account beneath the same subscription or a Shared Access
            Signature (SAS) URI from any storage account.
        label:
            A name for the hosted service. The name can be up to 100 characters
            in length. It is recommended that the label be unique within the
            subscription. The name can be used to identify the hosted service
            for your tracking purposes.
        configuration:
            The base-64 encoded service configuration file for the deployment.
        start_deployment:
            Indicates whether to start the deployment immediately after it is
            created. If false, the service model is still deployed to the
            virtual machines but the code is not run immediately. Instead, the
            service is Suspended until you call Update Deployment Status and
            set the status to Running, at which time the service will be
            started. A deployed service still incurs charges, even if it is
            suspended.
        treat_warnings_as_error:
            Indicates whether to treat package validation warnings as errors.
            If set to true, the Created Deployment operation fails if there
            are validation warnings on the service package.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_slot', deployment_slot)
        _validate_not_none('name', name)
        _validate_not_none('package_url', package_url)
        _validate_not_none('label', label)
        _validate_not_none('configuration', configuration)
        return self._perform_post(
            self._get_deployment_path_using_slot(
                service_name, deployment_slot),
            _XmlSerializer.create_deployment_to_xml(
                name,
                package_url,
                label,
                configuration,
                start_deployment,
                treat_warnings_as_error,
                extended_properties),
            async=True)

    def delete_deployment(self, service_name, deployment_name,delete_vhd=False):
        '''
        Deletes the specified deployment.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        path= self._get_deployment_path_using_name(service_name, deployment_name)
        if delete_vhd:
            path += '?comp=media'
        return self._perform_delete(
                path,
            async=True)

    def swap_deployment(self, service_name, production, source_deployment):
        '''
        Initiates a virtual IP swap between the staging and production
        deployment environments for a service. If the service is currently
        running in the staging environment, it will be swapped to the
        production environment. If it is running in the production
        environment, it will be swapped to staging.

        service_name:
            Name of the hosted service.
        production:
            The name of the production deployment.
        source_deployment:
            The name of the source deployment.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('production', production)
        _validate_not_none('source_deployment', source_deployment)
        return self._perform_post(self._get_hosted_service_path(service_name),
                                  _XmlSerializer.swap_deployment_to_xml(
                                      production, source_deployment),
                                  async=True)

    def change_deployment_configuration(self, service_name, deployment_name,
                                        configuration,
                                        treat_warnings_as_error=False,
                                        mode='Auto', extended_properties=None):
        '''
        Initiates a change to the deployment configuration.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        configuration:
            The base-64 encoded service configuration file for the deployment.
        treat_warnings_as_error:
            Indicates whether to treat package validation warnings as errors.
            If set to true, the Created Deployment operation fails if there
            are validation warnings on the service package.
        mode:
            If set to Manual, WalkUpgradeDomain must be called to apply the
            update. If set to Auto, the Windows Azure platform will
            automatically apply the update To each upgrade domain for the
            service. Possible values are: Auto, Manual
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('configuration', configuration)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/?comp=config',
            _XmlSerializer.change_deployment_to_xml(
                configuration,
                treat_warnings_as_error,
                mode,
                extended_properties),
            async=True)

    def update_deployment_status(self, service_name, deployment_name, status):
        '''
        Initiates a change in deployment status.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        status:
            The change to initiate to the deployment status. Possible values
            include:
                Running, Suspended
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('status', status)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/?comp=status',
            _XmlSerializer.update_deployment_status_to_xml(
                status),
            async=True)

    def upgrade_deployment(self, service_name, deployment_name, mode,
                           package_url, configuration, label, force,
                           role_to_upgrade=None, extended_properties=None):
        '''
        Initiates an upgrade.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        mode:
            If set to Manual, WalkUpgradeDomain must be called to apply the
            update. If set to Auto, the Windows Azure platform will
            automatically apply the update To each upgrade domain for the
            service. Possible values are: Auto, Manual
        package_url:
            A URL that refers to the location of the service package in the
            Blob service. The service package can be located either in a
            storage account beneath the same subscription or a Shared Access
            Signature (SAS) URI from any storage account.
        configuration:
            The base-64 encoded service configuration file for the deployment.
        label:
            A name for the hosted service. The name can be up to 100 characters
            in length. It is recommended that the label be unique within the
            subscription. The name can be used to identify the hosted service
            for your tracking purposes.
        force:
            Specifies whether the rollback should proceed even when it will
            cause local data to be lost from some role instances. True if the
            rollback should proceed; otherwise false if the rollback should
            fail.
        role_to_upgrade:
            The name of the specific role to upgrade.
        extended_properties:
            Dictionary containing name/value pairs of storage account
            properties. You can have a maximum of 50 extended property
            name/value pairs. The maximum length of the Name element is 64
            characters, only alphanumeric characters and underscores are valid
            in the Name, and the name must start with a letter. The value has
            a maximum length of 255 characters.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('mode', mode)
        _validate_not_none('package_url', package_url)
        _validate_not_none('configuration', configuration)
        _validate_not_none('label', label)
        _validate_not_none('force', force)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/?comp=upgrade',
            _XmlSerializer.upgrade_deployment_to_xml(
                mode,
                package_url,
                configuration,
                label,
                role_to_upgrade,
                force,
                extended_properties),
            async=True)

    def walk_upgrade_domain(self, service_name, deployment_name,
                            upgrade_domain):
        '''
        Specifies the next upgrade domain to be walked during manual in-place
        upgrade or configuration change.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        upgrade_domain:
            An integer value that identifies the upgrade domain to walk.
            Upgrade domains are identified with a zero-based index: the first
            upgrade domain has an ID of 0, the second has an ID of 1, and so on.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('upgrade_domain', upgrade_domain)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/?comp=walkupgradedomain',
            _XmlSerializer.walk_upgrade_domain_to_xml(
                upgrade_domain),
            async=True)

    def rollback_update_or_upgrade(self, service_name, deployment_name, mode,
                                   force):
        '''
        Cancels an in progress configuration change (update) or upgrade and
        returns the deployment to its state before the upgrade or
        configuration change was started.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        mode:
            Specifies whether the rollback should proceed automatically.
                auto - The rollback proceeds without further user input.
                manual - You must call the Walk Upgrade Domain operation to
                         apply the rollback to each upgrade domain.
        force:
            Specifies whether the rollback should proceed even when it will
            cause local data to be lost from some role instances. True if the
            rollback should proceed; otherwise false if the rollback should
            fail.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('mode', mode)
        _validate_not_none('force', force)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/?comp=rollback',
            _XmlSerializer.rollback_upgrade_to_xml(
                mode, force),
            async=True)

    def reboot_role_instance(self, service_name, deployment_name,
                             role_instance_name):
        '''
        Requests a reboot of a role instance that is running in a deployment.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        role_instance_name:
            The name of the role instance.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_instance_name', role_instance_name)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + \
                    '/roleinstances/' + _str(role_instance_name) + \
                    '?comp=reboot',
            '',
            async=True)

    def reimage_role_instance(self, service_name, deployment_name,
                              role_instance_name):
        '''
        Requests a reimage of a role instance that is running in a deployment.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        role_instance_name:
            The name of the role instance.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_instance_name', role_instance_name)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + \
                    '/roleinstances/' + _str(role_instance_name) + \
                    '?comp=reimage',
            '',
            async=True)

    def rebuild_role_instance(self, service_name, deployment_name,
                             role_instance_name):
        '''
        Reinstalls the operating system on instances of web roles or worker
        roles and initializes the storage resources that are used by them. If
        you do not want to initialize storage resources, you can use
        reimage_role_instance.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        role_instance_name:
            The name of the role instance.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_instance_name', role_instance_name)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + \
                    '/roleinstances/' + _str(role_instance_name) + \
                    '?comp=rebuild&resources=allLocalDrives',
            '',
            async=True)

    def delete_role_instances(self, service_name, deployment_name,
                             role_instance_names):
        '''
        Reinstalls the operating system on instances of web roles or worker
        roles and initializes the storage resources that are used by them. If
        you do not want to initialize storage resources, you can use
        reimage_role_instance.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name of the deployment.
        role_instance_names:
            List of role instance names.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_instance_names', role_instance_names)
        return self._perform_post(
            self._get_deployment_path_using_name(
                service_name, deployment_name) + '/roleinstances/?comp=delete',
            _XmlSerializer.role_instances_to_xml(role_instance_names),
            async=True)

    def check_hosted_service_name_availability(self, service_name):
        '''
        Checks to see if the specified hosted service name is available, or if
        it has already been taken.

        service_name:
            Name of the hosted service.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_get(
            '/' + self.subscription_id +
            '/services/hostedservices/operations/isavailable/' +
            _str(service_name) + '',
            AvailabilityResponse)

    #--Operations for service certificates -------------------------------
    def list_service_certificates(self, service_name):
        '''
        Lists all of the service certificates associated with the specified
        hosted service.

        service_name:
            Name of the hosted service.
        '''
        _validate_not_none('service_name', service_name)
        return self._perform_get(
            '/' + self.subscription_id + '/services/hostedservices/' +
            _str(service_name) + '/certificates',
            Certificates)

    def get_service_certificate(self, service_name, thumbalgorithm, thumbprint):
        '''
        Returns the public data for the specified X.509 certificate associated
        with a hosted service.

        service_name:
            Name of the hosted service.
        thumbalgorithm:
            The algorithm for the certificate's thumbprint.
        thumbprint:
            The hexadecimal representation of the thumbprint.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('thumbalgorithm', thumbalgorithm)
        _validate_not_none('thumbprint', thumbprint)
        return self._perform_get(
            '/' + self.subscription_id + '/services/hostedservices/' +
            _str(service_name) + '/certificates/' +
            _str(thumbalgorithm) + '-' + _str(thumbprint) + '',
            Certificate)

    def add_service_certificate(self, service_name, data, certificate_format,
                                password=None):
        '''
        Adds a certificate to a hosted service.

        service_name:
            Name of the hosted service.
        data:
            The base-64 encoded form of the pfx/cer file.
        certificate_format:
            The service certificate format.
        password:
            The certificate password. Default to None when using cer format.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('data', data)
        _validate_not_none('certificate_format', certificate_format)
        _validate_not_none('password', password)

        return self._perform_post(
            '/' + self.subscription_id + '/services/hostedservices/' +
            _str(service_name) + '/certificates',
            _XmlSerializer.certificate_file_to_xml(
                data, certificate_format, password),
            async=True)

    def delete_service_certificate(self, service_name, thumbalgorithm,
                                   thumbprint):
        '''
        Deletes a service certificate from the certificate store of a hosted
        service.

        service_name:
            Name of the hosted service.
        thumbalgorithm:
            The algorithm for the certificate's thumbprint.
        thumbprint:
            The hexadecimal representation of the thumbprint.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('thumbalgorithm', thumbalgorithm)
        _validate_not_none('thumbprint', thumbprint)
        return self._perform_delete(
            '/' + self.subscription_id + '/services/hostedservices/' +
            _str(service_name) + '/certificates/' +
            _str(thumbalgorithm) + '-' + _str(thumbprint),
            async=True)

    #--Operations for management certificates ----------------------------
    def list_management_certificates(self):
        '''
        The List Management Certificates operation lists and returns basic
        information about all of the management certificates associated with
        the specified subscription. Management certificates, which are also
        known as subscription certificates, authenticate clients attempting to
        connect to resources associated with your Windows Azure subscription.
        '''
        return self._perform_get('/' + self.subscription_id + '/certificates',
                                 SubscriptionCertificates)

    def get_management_certificate(self, thumbprint):
        '''
        The Get Management Certificate operation retrieves information about
        the management certificate with the specified thumbprint. Management
        certificates, which are also known as subscription certificates,
        authenticate clients attempting to connect to resources associated
        with your Windows Azure subscription.

        thumbprint:
            The thumbprint value of the certificate.
        '''
        _validate_not_none('thumbprint', thumbprint)
        return self._perform_get(
            '/' + self.subscription_id + '/certificates/' + _str(thumbprint),
            SubscriptionCertificate)

    def add_management_certificate(self, public_key, thumbprint, data):
        '''
        The Add Management Certificate operation adds a certificate to the
        list of management certificates. Management certificates, which are
        also known as subscription certificates, authenticate clients
        attempting to connect to resources associated with your Windows Azure
        subscription.

        public_key:
            A base64 representation of the management certificate public key.
        thumbprint:
            The thumb print that uniquely identifies the management
            certificate.
        data:
            The certificate's raw data in base-64 encoded .cer format.
        '''
        _validate_not_none('public_key', public_key)
        _validate_not_none('thumbprint', thumbprint)
        _validate_not_none('data', data)
        return self._perform_post(
            '/' + self.subscription_id + '/certificates',
            _XmlSerializer.subscription_certificate_to_xml(
                public_key, thumbprint, data))

    def delete_management_certificate(self, thumbprint):
        '''
        The Delete Management Certificate operation deletes a certificate from
        the list of management certificates. Management certificates, which
        are also known as subscription certificates, authenticate clients
        attempting to connect to resources associated with your Windows Azure
        subscription.

        thumbprint:
            The thumb print that uniquely identifies the management
            certificate.
        '''
        _validate_not_none('thumbprint', thumbprint)
        return self._perform_delete(
            '/' + self.subscription_id + '/certificates/' + _str(thumbprint))

    #--Operations for affinity groups ------------------------------------
    def list_affinity_groups(self):
        '''
        Lists the affinity groups associated with the specified subscription.
        '''
        return self._perform_get(
            '/' + self.subscription_id + '/affinitygroups',
            AffinityGroups)

    def get_affinity_group_properties(self, affinity_group_name):
        '''
        Returns the system properties associated with the specified affinity
        group.

        affinity_group_name:
            The name of the affinity group.
        '''
        _validate_not_none('affinity_group_name', affinity_group_name)
        return self._perform_get(
            '/' + self.subscription_id + '/affinitygroups/' +
            _str(affinity_group_name) + '',
            AffinityGroup)

    def create_affinity_group(self, name, label, location, description=None):
        '''
        Creates a new affinity group for the specified subscription.

        name:
            A name for the affinity group that is unique to the subscription.
        label:
            A name for the affinity group. The name can be up to 100 characters
            in length.
        location:
            The data center location where the affinity group will be created.
            To list available locations, use the list_location function.
        description:
            A description for the affinity group. The description can be up to
            1024 characters in length.
        '''
        _validate_not_none('name', name)
        _validate_not_none('label', label)
        _validate_not_none('location', location)
        return self._perform_post(
            '/' + self.subscription_id + '/affinitygroups',
            _XmlSerializer.create_affinity_group_to_xml(name,
                                                        label,
                                                        description,
                                                        location))

    def update_affinity_group(self, affinity_group_name, label,
                              description=None):
        '''
        Updates the label and/or the description for an affinity group for the
        specified subscription.

        affinity_group_name:
            The name of the affinity group.
        label:
            A name for the affinity group. The name can be up to 100 characters
            in length.
        description:
            A description for the affinity group. The description can be up to
            1024 characters in length.
        '''
        _validate_not_none('affinity_group_name', affinity_group_name)
        _validate_not_none('label', label)
        return self._perform_put(
            '/' + self.subscription_id + '/affinitygroups/' +
            _str(affinity_group_name),
            _XmlSerializer.update_affinity_group_to_xml(label, description))

    def delete_affinity_group(self, affinity_group_name):
        '''
        Deletes an affinity group in the specified subscription.

        affinity_group_name:
            The name of the affinity group.
        '''
        _validate_not_none('affinity_group_name', affinity_group_name)
        return self._perform_delete('/' + self.subscription_id + \
                                    '/affinitygroups/' + \
                                    _str(affinity_group_name))

    #--Operations for locations ------------------------------------------
    def list_locations(self):
        '''
        Lists all of the data center locations that are valid for your
        subscription.
        '''
        return self._perform_get('/' + self.subscription_id + '/locations',
                                 Locations)


    #--Operations for retrieving operating system information ------------
    def list_operating_systems(self):
        '''
        Lists the versions of the guest operating system that are currently
        available in Windows Azure.
        '''
        return self._perform_get(
            '/' + self.subscription_id + '/operatingsystems',
            OperatingSystems)

    def list_operating_system_families(self):
        '''
        Lists the guest operating system families available in Windows Azure,
        and also lists the operating system versions available for each family.
        '''
        return self._perform_get(
            '/' + self.subscription_id + '/operatingsystemfamilies',
            OperatingSystemFamilies)

    #--Operations for retrieving subscription history --------------------
    def get_subscription(self):
        '''
        Returns account and resource allocation information on the specified
        subscription.
        '''
        return self._perform_get('/' + self.subscription_id + '',
                                 Subscription)

    # Operations for retrieving subscription operations ------------------
    def list_subscription_operations(self, start_time=None, end_time=None, object_id_filter=None,
                                     operation_result_filter=None, continuation_token=None):
        '''
        List subscription operations.

        start_time: Required. An ISO8601 date.
        end_time: Required. An ISO8601 date.
        object_id_filter: Optional. Returns subscription operations only for the specified object type and object ID
        operation_result_filter: Optional. Returns subscription operations only for the specified result status, either Succeeded, Failed, or InProgress.
        continuation_token: Optional.
        More information at:
        https://msdn.microsoft.com/en-us/library/azure/gg715318.aspx
        '''
        start_time = ('StartTime=' + start_time) if start_time else ''
        end_time = ('EndTime=' + end_time) if end_time else ''
        object_id_filter = ('ObjectIdFilter=' + object_id_filter) if object_id_filter else ''
        operation_result_filter = ('OperationResultFilter=' + operation_result_filter) if operation_result_filter else ''
        continuation_token = ('ContinuationToken=' + continuation_token) if continuation_token else ''

        parameters = ('&'.join(v for v in (start_time, end_time, object_id_filter, operation_result_filter, continuation_token) if v))
        parameters = '?' + parameters if parameters else ''

        return self._perform_get(self._get_list_subscription_operations_path() + parameters,
                                 SubscriptionOperationCollection)

    #--Operations for reserved ip addresses  -----------------------------
    def create_reserved_ip_address(self, name, label=None, location=None):
        '''
        Reserves an IPv4 address for the specified subscription.

        name:
            Required. Specifies the name for the reserved IP address.
        label:
            Optional. Specifies a label for the reserved IP address. The label
            can be up to 100 characters long and can be used for your tracking
            purposes.
        location:
            Required. Specifies the location of the reserved IP address. This
            should be the same location that is assigned to the cloud service
            containing the deployment that will use the reserved IP address.
            To see the available locations, you can use list_locations.
        '''
        _validate_not_none('name', name)
        return self._perform_post(
            self._get_reserved_ip_path(),
            _XmlSerializer.create_reserved_ip_to_xml(name, label, location),
            async=True)

    def delete_reserved_ip_address(self, name):
        '''
        Deletes a reserved IP address from the specified subscription.

        name:
            Required. Name of the reserved IP address.
        '''
        _validate_not_none('name', name)
        return self._perform_delete(self._get_reserved_ip_path(name),
                                    async=True)

    def associate_reserved_ip_address(
        self, name, service_name, deployment_name, virtual_ip_name=None
    ):
        '''
        Associate an existing reservedIP to a deployment.

        name:
            Required. Name of the reserved IP address.

        service_name:
            Required. Name of the hosted service.

        deployment_name:
            Required. Name of the deployment.

        virtual_ip_name:
            Optional. Name of the VirtualIP in case of multi Vip tenant.
            If this value is not specified default virtualIP is used
            for this operation.
        '''
        _validate_not_none('name', name)
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        return self._perform_post(
            self._get_reserved_ip_path_for_association(name),
            _XmlSerializer.associate_reserved_ip_to_xml(
                service_name, deployment_name, virtual_ip_name
            ),
            async=True,
            x_ms_version='2015-02-01'
        )

    def disassociate_reserved_ip_address(
        self, name, service_name, deployment_name, virtual_ip_name=None
    ):
        '''
        Disassociate an existing reservedIP from the given deployment.

        name:
            Required. Name of the reserved IP address.

        service_name:
            Required. Name of the hosted service.

        deployment_name:
            Required. Name of the deployment.

        virtual_ip_name:
            Optional. Name of the VirtualIP in case of multi Vip tenant.
            If this value is not specified default virtualIP is used
            for this operation.
        '''
        _validate_not_none('name', name)
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        return self._perform_post(
            self._get_reserved_ip_path_for_disassociation(name),
            _XmlSerializer.associate_reserved_ip_to_xml(
                service_name, deployment_name, virtual_ip_name
            ),
            async=True,
            x_ms_version='2015-02-01'
        )

    def get_reserved_ip_address(self, name):
        '''
        Retrieves information about the specified reserved IP address.

        name:
            Required. Name of the reserved IP address.
        '''
        _validate_not_none('name', name)
        return self._perform_get(self._get_reserved_ip_path(name), ReservedIP)

    def list_reserved_ip_addresses(self):
        '''
        Lists the IP addresses that have been reserved for the specified
        subscription.
        '''
        return self._perform_get(self._get_reserved_ip_path(), ReservedIPs)

    #--Operations for virtual machines -----------------------------------
    def get_role(self, service_name, deployment_name, role_name):
        '''
        Retrieves the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        return self._perform_get(
            self._get_role_path(service_name, deployment_name, role_name),
            PersistentVMRole)

    def create_virtual_machine_deployment(self, service_name, deployment_name,
                                          deployment_slot, label, role_name,
                                          system_config, os_virtual_hard_disk,
                                          network_config=None,
                                          availability_set_name=None,
                                          data_virtual_hard_disks=None,
                                          role_size=None,
                                          role_type='PersistentVMRole',
                                          virtual_network_name=None,
                                          resource_extension_references=None,
                                          provision_guest_agent=None,
                                          vm_image_name=None,
                                          media_location=None,
                                          dns_servers=None,
                                          reserved_ip_name=None):
        '''
        Provisions a virtual machine based on the supplied configuration.

        service_name:
            Name of the hosted service.
        deployment_name:
            The name for the deployment. The deployment name must be unique
            among other deployments for the hosted service.
        deployment_slot:
            The environment to which the hosted service is deployed. Valid
            values are: staging, production
        label:
            Specifies an identifier for the deployment. The label can be up to
            100 characters long. The label can be used for tracking purposes.
        role_name:
            The name of the role.
        system_config:
            Contains the metadata required to provision a virtual machine from
            a Windows or Linux OS image.  Use an instance of
            WindowsConfigurationSet or LinuxConfigurationSet.
        os_virtual_hard_disk:
            Contains the parameters Windows Azure uses to create the operating
            system disk for the virtual machine. If you are creating a Virtual
            Machine by using a VM Image, this parameter is not used.
        network_config:
            Encapsulates the metadata required to create the virtual network
            configuration for a virtual machine. If you do not include a
            network configuration set you will not be able to access the VM
            through VIPs over the internet. If your virtual machine belongs to
            a virtual network you can not specify which subnet address space
            it resides under. Use an instance of ConfigurationSet.
        availability_set_name:
            Specifies the name of an availability set to which to add the
            virtual machine. This value controls the virtual machine
            allocation in the Windows Azure environment. Virtual machines
            specified in the same availability set are allocated to different
            nodes to maximize availability.
        data_virtual_hard_disks:
            Contains the parameters Windows Azure uses to create a data disk
            for a virtual machine.
        role_size:
            The size of the virtual machine to allocate. The default value is
            Small. Possible values are: ExtraSmall,Small,Medium,Large,
            ExtraLarge,A5,A6,A7,A8,A9,Basic_A0,Basic_A1,Basic_A2,Basic_A3,
            Basic_A4,Standard_D1,Standard_D2,Standard_D3,Standard_D4,
            Standard_D11,Standard_D12,Standard_D13,Standard_D14,Standard_G1,
            Standard_G2,Sandard_G3,Standard_G4,Standard_G5. The specified
            value must be compatible with the disk selected in the 
            OSVirtualHardDisk values.
        role_type:
            The type of the role for the virtual machine. The only supported
            value is PersistentVMRole.
        virtual_network_name:
            Specifies the name of an existing virtual network to which the
            deployment will belong.
        resource_extension_references:
            Optional. Contains a collection of resource extensions that are to
            be installed on the Virtual Machine. This element is used if
            provision_guest_agent is set to True. Use an iterable of instances
            of ResourceExtensionReference.
        provision_guest_agent:
            Optional. Indicates whether the VM Agent is installed on the
            Virtual Machine. To run a resource extension in a Virtual Machine,
            this service must be installed.
        vm_image_name:
            Optional. Specifies the name of the VM Image that is to be used to
            create the Virtual Machine. If this is specified, the
            system_config and network_config parameters are not used.
        media_location:
            Optional. Required if the Virtual Machine is being created from a
            published VM Image. Specifies the location of the VHD file that is
            created when VMImageName specifies a published VM Image.
        dns_servers:
            Optional. List of DNS servers (use DnsServer class) to associate
            with the Virtual Machine.
        reserved_ip_name:
            Optional. Specifies the name of a reserved IP address that is to be
            assigned to the deployment. You must run create_reserved_ip_address
            before you can assign the address to the deployment using this
            element.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('deployment_slot', deployment_slot)
        _validate_not_none('label', label)
        _validate_not_none('role_name', role_name)
        return self._perform_post(
            self._get_deployment_path_using_name(service_name),
            _XmlSerializer.virtual_machine_deployment_to_xml(
                deployment_name,
                deployment_slot,
                label,
                role_name,
                system_config,
                os_virtual_hard_disk,
                role_type,
                network_config,
                availability_set_name,
                data_virtual_hard_disks,
                role_size,
                virtual_network_name,
                resource_extension_references,
                provision_guest_agent,
                vm_image_name,
                media_location,
                dns_servers,
                reserved_ip_name),
            async=True)

    def add_role(self, service_name, deployment_name, role_name, system_config,
                 os_virtual_hard_disk, network_config=None,
                 availability_set_name=None, data_virtual_hard_disks=None,
                 role_size=None, role_type='PersistentVMRole',
                 resource_extension_references=None,
                 provision_guest_agent=None, vm_image_name=None,
                 media_location=None):
        '''
        Adds a virtual machine to an existing deployment.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        system_config:
            Contains the metadata required to provision a virtual machine from
            a Windows or Linux OS image.  Use an instance of
            WindowsConfigurationSet or LinuxConfigurationSet.
        os_virtual_hard_disk:
            Contains the parameters Windows Azure uses to create the operating
            system disk for the virtual machine. If you are creating a Virtual
            Machine by using a VM Image, this parameter is not used.
        network_config:
            Encapsulates the metadata required to create the virtual network
            configuration for a virtual machine. If you do not include a
            network configuration set you will not be able to access the VM
            through VIPs over the internet. If your virtual machine belongs to
            a virtual network you can not specify which subnet address space
            it resides under.
        availability_set_name:
            Specifies the name of an availability set to which to add the
            virtual machine. This value controls the virtual machine allocation
            in the Windows Azure environment. Virtual machines specified in the
            same availability set are allocated to different nodes to maximize
            availability.
        data_virtual_hard_disks:
            Contains the parameters Windows Azure uses to create a data disk
            for a virtual machine.
        role_size:
            The size of the virtual machine to allocate. The default value is
            Small. Possible values are: ExtraSmall, Small, Medium, Large,
            ExtraLarge. The specified value must be compatible with the disk
            selected in the OSVirtualHardDisk values.
        role_type:
            The type of the role for the virtual machine. The only supported
            value is PersistentVMRole.
        resource_extension_references:
            Optional. Contains a collection of resource extensions that are to
            be installed on the Virtual Machine. This element is used if
            provision_guest_agent is set to True.
        provision_guest_agent:
            Optional. Indicates whether the VM Agent is installed on the
            Virtual Machine. To run a resource extension in a Virtual Machine,
            this service must be installed.
        vm_image_name:
            Optional. Specifies the name of the VM Image that is to be used to
            create the Virtual Machine. If this is specified, the
            system_config and network_config parameters are not used.
        media_location:
            Optional. Required if the Virtual Machine is being created from a
            published VM Image. Specifies the location of the VHD file that is
            created when VMImageName specifies a published VM Image.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        return self._perform_post(
            self._get_role_path(service_name, deployment_name),
            _XmlSerializer.add_role_to_xml(
                role_name,
                system_config,
                os_virtual_hard_disk,
                role_type,
                network_config,
                availability_set_name,
                data_virtual_hard_disks,
                role_size,
                resource_extension_references,
                provision_guest_agent,
                vm_image_name,
                media_location),
            async=True)

    def update_role(self, service_name, deployment_name, role_name,
                    os_virtual_hard_disk=None, network_config=None,
                    availability_set_name=None, data_virtual_hard_disks=None,
                    role_size=None, role_type='PersistentVMRole',
                    resource_extension_references=None,
                    provision_guest_agent=None):
        '''
        Updates the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        os_virtual_hard_disk:
            Contains the parameters Windows Azure uses to create the operating
            system disk for the virtual machine.
        network_config:
            Encapsulates the metadata required to create the virtual network
            configuration for a virtual machine. If you do not include a
            network configuration set you will not be able to access the VM
            through VIPs over the internet. If your virtual machine belongs to
            a virtual network you can not specify which subnet address space
            it resides under.
        availability_set_name:
            Specifies the name of an availability set to which to add the
            virtual machine. This value controls the virtual machine allocation
            in the Windows Azure environment. Virtual machines specified in the
            same availability set are allocated to different nodes to maximize
            availability.
        data_virtual_hard_disks:
            Contains the parameters Windows Azure uses to create a data disk
            for a virtual machine.
        role_size:
            The size of the virtual machine to allocate. The default value is
            Small. Possible values are: ExtraSmall, Small, Medium, Large,
            ExtraLarge. The specified value must be compatible with the disk
            selected in the OSVirtualHardDisk values.
        role_type:
            The type of the role for the virtual machine. The only supported
            value is PersistentVMRole.
        resource_extension_references:
            Optional. Contains a collection of resource extensions that are to
            be installed on the Virtual Machine. This element is used if
            provision_guest_agent is set to True.
        provision_guest_agent:
            Optional. Indicates whether the VM Agent is installed on the
            Virtual Machine. To run a resource extension in a Virtual Machine,
            this service must be installed.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        return self._perform_put(
            self._get_role_path(service_name, deployment_name, role_name),
            _XmlSerializer.update_role_to_xml(
                role_name,
                os_virtual_hard_disk,
                role_type,
                network_config,
                availability_set_name,
                data_virtual_hard_disks,
                role_size,
                resource_extension_references,
                provision_guest_agent),
            async=True)

    def delete_role(self, service_name, deployment_name, role_name, complete = False):
        '''
        Deletes the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        complete:
            True if all OS/data disks and the source blobs for the disks should
            also be deleted from storage.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)

        path = self._get_role_path(service_name, deployment_name, role_name)
        
        if complete == True:
            path = path +'?comp=media'

        return self._perform_delete(path,
                                    async=True)

    def capture_role(self, service_name, deployment_name, role_name,
                     post_capture_action, target_image_name,
                     target_image_label, provisioning_configuration=None):
        '''
        The Capture Role operation captures a virtual machine image to your
        image gallery. From the captured image, you can create additional
        customized virtual machines.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        post_capture_action:
            Specifies the action after capture operation completes. Possible
            values are: Delete, Reprovision.
        target_image_name:
            Specifies the image name of the captured virtual machine.
        target_image_label:
            Specifies the friendly name of the captured virtual machine.
        provisioning_configuration:
            Use an instance of WindowsConfigurationSet or LinuxConfigurationSet.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('post_capture_action', post_capture_action)
        _validate_not_none('target_image_name', target_image_name)
        _validate_not_none('target_image_label', target_image_label)
        return self._perform_post(
            self._get_role_instance_operations_path(
                service_name, deployment_name, role_name),
            _XmlSerializer.capture_role_to_xml(
                post_capture_action,
                target_image_name,
                target_image_label,
                provisioning_configuration),
            async=True)

    def start_role(self, service_name, deployment_name, role_name):
        '''
        Starts the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        return self._perform_post(
            self._get_role_instance_operations_path(
                service_name, deployment_name, role_name),
            _XmlSerializer.start_role_operation_to_xml(),
            async=True)

    def start_roles(self, service_name, deployment_name, role_names):
        '''
        Starts the specified virtual machines.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_names:
            The names of the roles, as an enumerable of strings.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_names', role_names)
        return self._perform_post(
            self._get_roles_operations_path(service_name, deployment_name),
            _XmlSerializer.start_roles_operation_to_xml(role_names),
            async=True)

    def restart_role(self, service_name, deployment_name, role_name):
        '''
        Restarts the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        return self._perform_post(
            self._get_role_instance_operations_path(
                service_name, deployment_name, role_name),
            _XmlSerializer.restart_role_operation_to_xml(
            ),
            async=True)

    def shutdown_role(self, service_name, deployment_name, role_name,
                      post_shutdown_action='Stopped'):
        '''
        Shuts down the specified virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        post_shutdown_action:
            Specifies how the Virtual Machine should be shut down. Values are:
                Stopped
                    Shuts down the Virtual Machine but retains the compute
                    resources. You will continue to be billed for the resources
                    that the stopped machine uses.
                StoppedDeallocated
                    Shuts down the Virtual Machine and releases the compute
                    resources. You are not billed for the compute resources that
                    this Virtual Machine uses. If a static Virtual Network IP
                    address is assigned to the Virtual Machine, it is reserved.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('post_shutdown_action', post_shutdown_action)
        return self._perform_post(
            self._get_role_instance_operations_path(
                service_name, deployment_name, role_name),
            _XmlSerializer.shutdown_role_operation_to_xml(post_shutdown_action),
            async=True)

    def shutdown_roles(self, service_name, deployment_name, role_names,
                       post_shutdown_action='Stopped'):
        '''
        Shuts down the specified virtual machines.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_names:
            The names of the roles, as an enumerable of strings.
        post_shutdown_action:
            Specifies how the Virtual Machine should be shut down. Values are:
                Stopped
                    Shuts down the Virtual Machine but retains the compute
                    resources. You will continue to be billed for the resources
                    that the stopped machine uses.
                StoppedDeallocated
                    Shuts down the Virtual Machine and releases the compute
                    resources. You are not billed for the compute resources that
                    this Virtual Machine uses. If a static Virtual Network IP
                    address is assigned to the Virtual Machine, it is reserved.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_names', role_names)
        _validate_not_none('post_shutdown_action', post_shutdown_action)
        return self._perform_post(
            self._get_roles_operations_path(service_name, deployment_name),
            _XmlSerializer.shutdown_roles_operation_to_xml(
                role_names, post_shutdown_action),
            async=True)

    def add_dns_server(self, service_name, deployment_name, dns_server_name, address):
        '''
        Adds a DNS server definition to an existing deployment.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        dns_server_name:
            Specifies the name of the DNS server.
        address:
            Specifies the IP address of the DNS server.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('dns_server_name', dns_server_name)
        _validate_not_none('address', address)
        return self._perform_post(
            self._get_dns_server_path(service_name, deployment_name),
            _XmlSerializer.dns_server_to_xml(dns_server_name, address),
            async=True)

    def update_dns_server(self, service_name, deployment_name, dns_server_name, address):
        '''
        Updates the ip address of a DNS server.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        dns_server_name:
            Specifies the name of the DNS server.
        address:
            Specifies the IP address of the DNS server.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('dns_server_name', dns_server_name)
        _validate_not_none('address', address)
        return self._perform_put(
            self._get_dns_server_path(service_name,
                                      deployment_name,
                                      dns_server_name),
            _XmlSerializer.dns_server_to_xml(dns_server_name, address),
            async=True)

    def delete_dns_server(self, service_name, deployment_name, dns_server_name):
        '''
        Deletes a DNS server from a deployment.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        dns_server_name:
            Name of the DNS server that you want to delete.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('dns_server_name', dns_server_name)
        return self._perform_delete(
            self._get_dns_server_path(service_name,
                                      deployment_name,
                                      dns_server_name),
            async=True)

    def list_resource_extensions(self):
        '''
        Lists the resource extensions that are available to add to a
        Virtual Machine.
        '''
        return self._perform_get(self._get_resource_extensions_path(),
                                 ResourceExtensions)

    def list_resource_extension_versions(self, publisher_name, extension_name):
        '''
        Lists the versions of a resource extension that are available to add
        to a Virtual Machine.

        publisher_name:
            Name of the resource extension publisher.
        extension_name:
            Name of the resource extension.
        '''
        return self._perform_get(self._get_resource_extension_versions_path(
                                    publisher_name, extension_name),
                                 ResourceExtensions)

    #--Operations for virtual machine images -----------------------------
    def replicate_vm_image(self, vm_image_name, regions, offer, sku, version):
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

    def unreplicate_vm_image(self, vm_image_name):
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

    def share_vm_image(self, vm_image_name, permission):
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

    def capture_vm_image(self, service_name, deployment_name, role_name, options):
        '''
        Creates a copy of the operating system virtual hard disk (VHD) and all
        of the data VHDs that are associated with the Virtual Machine, saves
        the VHD copies in the same storage location as the original VHDs, and
        registers the copies as a VM Image in the image repository that is
        associated with the specified subscription.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        options:
            An instance of CaptureRoleAsVMImage class.
        options.os_state:
            Required. Specifies the state of the operating system in the image.
            Possible values are: Generalized, Specialized 
            A Virtual Machine that is fully configured and running contains a
            Specialized operating system. A Virtual Machine on which the
            Sysprep command has been run with the generalize option contains a
            Generalized operating system. If you capture an image from a
            generalized Virtual Machine, the machine is deleted after the image
            is captured. It is recommended that all Virtual Machines are shut
            down before capturing an image.
        options.vm_image_name:
            Required. Specifies the name of the VM Image.
        options.vm_image_label:
            Required. Specifies the label of the VM Image.
        options.description:
            Optional. Specifies the description of the VM Image.
        options.language:
            Optional. Specifies the language of the VM Image.
        options.image_family:
            Optional. Specifies a value that can be used to group VM Images.
        options.recommended_vm_size:
            Optional. Specifies the size to use for the Virtual Machine that
            is created from the VM Image.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('options', options)
        _validate_not_none('options.os_state', options.os_state)
        _validate_not_none('options.vm_image_name', options.vm_image_name)
        _validate_not_none('options.vm_image_label', options.vm_image_label)
        return self._perform_post(
            self._get_capture_vm_image_path(service_name, deployment_name, role_name),
            _XmlSerializer.capture_vm_image_to_xml(options),
            async=True)

    def create_vm_image(self, vm_image):
        '''
        Creates a VM Image in the image repository that is associated with the
        specified subscription using a specified set of virtual hard disks.

        vm_image:
            An instance of VMImage class.
        vm_image.name: Required. Specifies the name of the image.
        vm_image.label: Required. Specifies an identifier for the image.
        vm_image.description: Optional. Specifies the description of the image.
        vm_image.os_disk_configuration:
            Required. Specifies configuration information for the operating 
            system disk that is associated with the image.
        vm_image.os_disk_configuration.host_caching:
            Optional. Specifies the caching behavior of the operating system disk.
            Possible values are: None, ReadOnly, ReadWrite 
        vm_image.os_disk_configuration.os_state:
            Required. Specifies the state of the operating system in the image.
            Possible values are: Generalized, Specialized
            A Virtual Machine that is fully configured and running contains a
            Specialized operating system. A Virtual Machine on which the
            Sysprep command has been run with the generalize option contains a
            Generalized operating system.
        vm_image.os_disk_configuration.os:
            Required. Specifies the operating system type of the image.
        vm_image.os_disk_configuration.media_link:
            Required. Specifies the location of the blob in Windows Azure
            storage. The blob location belongs to a storage account in the
            subscription specified by the <subscription-id> value in the
            operation call.
        vm_image.data_disk_configurations:
            Optional. Specifies configuration information for the data disks
            that are associated with the image. A VM Image might not have data
            disks associated with it.
        vm_image.data_disk_configurations[].host_caching:
            Optional. Specifies the caching behavior of the data disk.
            Possible values are: None, ReadOnly, ReadWrite 
        vm_image.data_disk_configurations[].lun:
            Optional if the lun for the disk is 0. Specifies the Logical Unit
            Number (LUN) for the data disk.
        vm_image.data_disk_configurations[].media_link:
            Required. Specifies the location of the blob in Windows Azure
            storage. The blob location belongs to a storage account in the
            subscription specified by the <subscription-id> value in the
            operation call.
        vm_image.data_disk_configurations[].logical_size_in_gb:
            Required. Specifies the size, in GB, of the data disk.
        vm_image.language: Optional. Specifies the language of the image.
        vm_image.image_family:
            Optional. Specifies a value that can be used to group VM Images.
        vm_image.recommended_vm_size:
            Optional. Specifies the size to use for the Virtual Machine that
            is created from the VM Image.
        vm_image.eula:
            Optional. Specifies the End User License Agreement that is
            associated with the image. The value for this element is a string,
            but it is recommended that the value be a URL that points to a EULA.
        vm_image.icon_uri:
            Optional. Specifies the URI to the icon that is displayed for the
            image in the Management Portal.
        vm_image.small_icon_uri:
            Optional. Specifies the URI to the small icon that is displayed for
            the image in the Management Portal.
        vm_image.privacy_uri:
            Optional. Specifies the URI that points to a document that contains
            the privacy policy related to the image.
        vm_image.published_date:
            Optional. Specifies the date when the image was added to the image
            repository.
        vm_image.show_in_gui:
            Optional. Indicates whether the VM Images should be listed in the
            portal.
        '''
        _validate_not_none('vm_image', vm_image)
        _validate_not_none('vm_image.name', vm_image.name)
        _validate_not_none('vm_image.label', vm_image.label)
        _validate_not_none('vm_image.os_disk_configuration.os_state',
                           vm_image.os_disk_configuration.os_state)
        _validate_not_none('vm_image.os_disk_configuration.os',
                           vm_image.os_disk_configuration.os)
        _validate_not_none('vm_image.os_disk_configuration.media_link',
                           vm_image.os_disk_configuration.media_link)
        return self._perform_post(
            self._get_vm_image_path(),
            _XmlSerializer.create_vm_image_to_xml(vm_image),
            async=True)

    def delete_vm_image(self, vm_image_name, delete_vhd=False):
        '''
        Deletes the specified VM Image from the image repository that is
        associated with the specified subscription.

        vm_image_name:
            The name of the image.
        delete_vhd:
            Deletes the underlying vhd blob in Azure storage.
        '''
        _validate_not_none('vm_image_name', vm_image_name)
        path = self._get_vm_image_path(vm_image_name)
        if delete_vhd:
            path += '?comp=media'
        return self._perform_delete(path, async=True)

    def list_vm_images(self, location=None, publisher=None, category=None):
        '''
        Retrieves a list of the VM Images from the image repository that is
        associated with the specified subscription.
        '''
        path = self._get_vm_image_path()
        query = ''
        if location:
            query += '&location=' + location
        if publisher:
            query += '&publisher=' + publisher
        if category:
            query += '&category=' + category
        if query:
            path = path + '?' + query.lstrip('&')
        return self._perform_get(path, VMImages)

    def update_vm_image(self, vm_image_name, vm_image):
        '''
        Updates a VM Image in the image repository that is associated with the
        specified subscription.

        vm_image_name:
            Name of image to update.
        vm_image:
            An instance of VMImage class.
        vm_image.label: Optional. Specifies an identifier for the image.
        vm_image.os_disk_configuration:
            Required. Specifies configuration information for the operating 
            system disk that is associated with the image.
        vm_image.os_disk_configuration.host_caching:
            Optional. Specifies the caching behavior of the operating system disk.
            Possible values are: None, ReadOnly, ReadWrite 
        vm_image.data_disk_configurations:
            Optional. Specifies configuration information for the data disks
            that are associated with the image. A VM Image might not have data
            disks associated with it.
        vm_image.data_disk_configurations[].name:
            Required. Specifies the name of the data disk.
        vm_image.data_disk_configurations[].host_caching:
            Optional. Specifies the caching behavior of the data disk.
            Possible values are: None, ReadOnly, ReadWrite 
        vm_image.data_disk_configurations[].lun:
            Optional if the lun for the disk is 0. Specifies the Logical Unit
            Number (LUN) for the data disk.
        vm_image.description: Optional. Specifies the description of the image.
        vm_image.language: Optional. Specifies the language of the image.
        vm_image.image_family:
            Optional. Specifies a value that can be used to group VM Images.
        vm_image.recommended_vm_size:
            Optional. Specifies the size to use for the Virtual Machine that
            is created from the VM Image.
        vm_image.eula:
            Optional. Specifies the End User License Agreement that is
            associated with the image. The value for this element is a string,
            but it is recommended that the value be a URL that points to a EULA.
        vm_image.icon_uri:
            Optional. Specifies the URI to the icon that is displayed for the
            image in the Management Portal.
        vm_image.small_icon_uri:
            Optional. Specifies the URI to the small icon that is displayed for
            the image in the Management Portal.
        vm_image.privacy_uri:
            Optional. Specifies the URI that points to a document that contains
            the privacy policy related to the image.
        vm_image.published_date:
            Optional. Specifies the date when the image was added to the image
            repository.
        vm_image.show_in_gui:
            Optional. Indicates whether the VM Images should be listed in the
            portal.
        '''
        _validate_not_none('vm_image_name', vm_image_name)
        _validate_not_none('vm_image', vm_image)
        return self._perform_put(self._get_vm_image_path(vm_image_name),
                                 _XmlSerializer.update_vm_image_to_xml(vm_image),
                                 async=True)

    #--Operations for operating system images ----------------------------
    def list_os_images(self):
        '''
        Retrieves a list of the OS images from the image repository.
        '''
        return self._perform_get(self._get_image_path(),
                                 Images)

    def get_os_image(self, image_name):
        '''
        Retrieves an OS image from the image repository.
        '''
        return self._perform_get(self._get_image_path(image_name),
                                 OSImage)

    def get_os_image_details(self, image_name):
        '''
        Retrieves an OS image from the image repository, including replication
        progress.
        '''
        return self._perform_get(self._get_image_details_path(image_name),
                                 OSImageDetails)

    def add_os_image(self, label, media_link, name, os):
        '''
        Adds an OS image that is currently stored in a storage account in your
        subscription to the image repository.

        label:
            Specifies the friendly name of the image.
        media_link:
            Specifies the location of the blob in Windows Azure blob store
            where the media for the image is located. The blob location must
            belong to a storage account in the subscription specified by the
            <subscription-id> value in the operation call. Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        name:
            Specifies a name for the OS image that Windows Azure uses to
            identify the image when creating one or more virtual machines.
        os:
            The operating system type of the OS image. Possible values are:
            Linux, Windows
        '''
        _validate_not_none('label', label)
        _validate_not_none('media_link', media_link)
        _validate_not_none('name', name)
        _validate_not_none('os', os)
        return self._perform_post(self._get_image_path(),
                                  _XmlSerializer.os_image_to_xml(
                                      label, media_link, name, os),
                                  async=True)

    def update_os_image(self, image_name, label, media_link, name, os):
        '''
        Updates an OS image that in your image repository.

        image_name:
            The name of the image to update.
        label:
            Specifies the friendly name of the image to be updated. You cannot
            use this operation to update images provided by the Windows Azure
            platform.
        media_link:
            Specifies the location of the blob in Windows Azure blob store
            where the media for the image is located. The blob location must
            belong to a storage account in the subscription specified by the
            <subscription-id> value in the operation call. Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        name:
            Specifies a name for the OS image that Windows Azure uses to
            identify the image when creating one or more VM Roles.
        os:
            The operating system type of the OS image. Possible values are:
            Linux, Windows
        '''
        _validate_not_none('image_name', image_name)
        _validate_not_none('label', label)
        _validate_not_none('media_link', media_link)
        _validate_not_none('name', name)
        _validate_not_none('os', os)
        return self._perform_put(self._get_image_path(image_name),
                                 _XmlSerializer.os_image_to_xml(
                                     label, media_link, name, os),
                                 async=True)

    def update_os_image_from_image_reference(self, image_name, os_image):
        '''
        Updates metadata elements from a given OS image reference.

        image_name:
            The name of the image to update.
        os_image:
            An instance of OSImage class.
        os_image.label: Optional. Specifies an identifier for the image.
        os_image.description: Optional. Specifies the description of the image.
        os_image.language: Optional. Specifies the language of the image.
        os_image.image_family:
            Optional. Specifies a value that can be used to group VM Images.
        os_image.recommended_vm_size:
            Optional. Specifies the size to use for the Virtual Machine that
            is created from the VM Image.
        os_image.eula:
            Optional. Specifies the End User License Agreement that is
            associated with the image. The value for this element is a string,
            but it is recommended that the value be a URL that points to a EULA.
        os_image.icon_uri:
            Optional. Specifies the URI to the icon that is displayed for the
            image in the Management Portal.
        os_image.small_icon_uri:
            Optional. Specifies the URI to the small icon that is displayed for
            the image in the Management Portal.
        os_image.privacy_uri:
            Optional. Specifies the URI that points to a document that contains
            the privacy policy related to the image.
        os_image.published_date:
            Optional. Specifies the date when the image was added to the image
            repository.
        os.image.media_link:
            Required: Specifies the location of the blob in Windows Azure
            blob store where the media for the image is located. The blob
            location must belong to a storage account in the subscription
            specified by the <subscription-id> value in the operation call.
            Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        os_image.name:
            Specifies a name for the OS image that Windows Azure uses to
            identify the image when creating one or more VM Roles.
        os_image.os:
            The operating system type of the OS image. Possible values are:
            Linux, Windows
        '''
        _validate_not_none('image_name', image_name)
        _validate_not_none('os_image', os_image)
        return self._perform_put(self._get_image_path(image_name),
            _XmlSerializer.update_os_image_to_xml(os_image), async=True
        )

    def delete_os_image(self, image_name, delete_vhd=False):
        '''
        Deletes the specified OS image from your image repository.

        image_name:
            The name of the image.
        delete_vhd:
            Deletes the underlying vhd blob in Azure storage.
        '''
        _validate_not_none('image_name', image_name)
        path = self._get_image_path(image_name)
        if delete_vhd:
            path += '?comp=media'
        return self._perform_delete(path, async=True)

    #--Operations for virtual machine disks ------------------------------
    def get_data_disk(self, service_name, deployment_name, role_name, lun):
        '''
        Retrieves the specified data disk from a virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        lun:
            The Logical Unit Number (LUN) for the disk.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('lun', lun)
        return self._perform_get(
            self._get_data_disk_path(
                service_name, deployment_name, role_name, lun),
            DataVirtualHardDisk)

    def add_data_disk(self, service_name, deployment_name, role_name, lun,
                      host_caching=None, media_link=None, disk_label=None,
                      disk_name=None, logical_disk_size_in_gb=None,
                      source_media_link=None):
        '''
        Adds a data disk to a virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        lun:
            Specifies the Logical Unit Number (LUN) for the disk. The LUN
            specifies the slot in which the data drive appears when mounted
            for usage by the virtual machine. Valid LUN values are 0 through 15.
        host_caching:
            Specifies the platform caching behavior of data disk blob for
            read/write efficiency. The default vault is ReadOnly. Possible
            values are: None, ReadOnly, ReadWrite
        media_link:
            Specifies the location of the blob in Windows Azure blob store
            where the media for the disk is located. The blob location must
            belong to the storage account in the subscription specified by the
            <subscription-id> value in the operation call. Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        disk_label:
            Specifies the description of the data disk. When you attach a disk,
            either by directly referencing a media using the MediaLink element
            or specifying the target disk size, you can use the DiskLabel
            element to customize the name property of the target data disk.
        disk_name:
            Specifies the name of the disk. Windows Azure uses the specified
            disk to create the data disk for the machine and populates this
            field with the disk name.
        logical_disk_size_in_gb:
            Specifies the size, in GB, of an empty disk to be attached to the
            role. The disk can be created as part of disk attach or create VM
            role call by specifying the value for this property. Windows Azure
            creates the empty disk based on size preference and attaches the
            newly created disk to the Role.
        source_media_link:
            Specifies the location of a blob in account storage which is
            mounted as a data disk when the virtual machine is created.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('lun', lun)
        return self._perform_post(
            self._get_data_disk_path(service_name, deployment_name, role_name),
            _XmlSerializer.data_virtual_hard_disk_to_xml(
                host_caching,
                disk_label,
                disk_name,
                lun,
                logical_disk_size_in_gb,
                media_link,
                source_media_link),
            async=True)

    def update_data_disk(self, service_name, deployment_name, role_name, lun,
                         host_caching=None, media_link=None, updated_lun=None,
                         disk_label=None, disk_name=None,
                         logical_disk_size_in_gb=None):
        '''
        Updates the specified data disk attached to the specified virtual
        machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        lun:
            Specifies the Logical Unit Number (LUN) for the disk. The LUN
            specifies the slot in which the data drive appears when mounted
            for usage by the virtual machine. Valid LUN values are 0 through
            15.
        host_caching:
            Specifies the platform caching behavior of data disk blob for
            read/write efficiency. The default vault is ReadOnly. Possible
            values are: None, ReadOnly, ReadWrite
        media_link:
            Specifies the location of the blob in Windows Azure blob store
            where the media for the disk is located. The blob location must
            belong to the storage account in the subscription specified by
            the <subscription-id> value in the operation call. Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        updated_lun:
            Specifies the Logical Unit Number (LUN) for the disk. The LUN
            specifies the slot in which the data drive appears when mounted
            for usage by the virtual machine. Valid LUN values are 0 through 15.
        disk_label:
            Specifies the description of the data disk. When you attach a disk,
            either by directly referencing a media using the MediaLink element
            or specifying the target disk size, you can use the DiskLabel
            element to customize the name property of the target data disk.
        disk_name:
            Specifies the name of the disk. Windows Azure uses the specified
            disk to create the data disk for the machine and populates this
            field with the disk name.
        logical_disk_size_in_gb:
            Specifies the size, in GB, of an empty disk to be attached to the
            role. The disk can be created as part of disk attach or create VM
            role call by specifying the value for this property. Windows Azure
            creates the empty disk based on size preference and attaches the
            newly created disk to the Role.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('lun', lun)
        return self._perform_put(
            self._get_data_disk_path(
                service_name, deployment_name, role_name, lun),
            _XmlSerializer.data_virtual_hard_disk_to_xml(
                host_caching,
                disk_label,
                disk_name,
                updated_lun,
                logical_disk_size_in_gb,
                media_link,
                None),
            async=True)

    def delete_data_disk(self, service_name, deployment_name, role_name, lun, delete_vhd=False):
        '''
        Removes the specified data disk from a virtual machine.

        service_name:
            The name of the service.
        deployment_name:
            The name of the deployment.
        role_name:
            The name of the role.
        lun:
            The Logical Unit Number (LUN) for the disk.
        delete_vhd:
            Deletes the underlying vhd blob in Azure storage.
        '''
        _validate_not_none('service_name', service_name)
        _validate_not_none('deployment_name', deployment_name)
        _validate_not_none('role_name', role_name)
        _validate_not_none('lun', lun)
        path = self._get_data_disk_path(service_name, deployment_name, role_name, lun)
        if delete_vhd:
            path += '?comp=media'
        return self._perform_delete(path, async=True)

    #--Operations for virtual machine disks ------------------------------
    def list_disks(self):
        '''
        Retrieves a list of the disks in your image repository.
        '''
        return self._perform_get(self._get_disk_path(),
                                 Disks)

    def get_disk(self, disk_name):
        '''
        Retrieves a disk from your image repository.
        '''
        return self._perform_get(self._get_disk_path(disk_name),
                                 Disk)

    def add_disk(self, has_operating_system, label, media_link, name, os):
        '''
        Adds a disk to the user image repository. The disk can be an OS disk
        or a data disk.

        has_operating_system:
            Deprecated.
        label:
            Specifies the description of the disk.
        media_link:
            Specifies the location of the blob in Windows Azure blob store
            where the media for the disk is located. The blob location must
            belong to the storage account in the current subscription specified
            by the <subscription-id> value in the operation call. Example:
            http://example.blob.core.windows.net/disks/mydisk.vhd
        name:
            Specifies a name for the disk. Windows Azure uses the name to
            identify the disk when creating virtual machines from the disk.
        os:
            The OS type of the disk. Possible values are: Linux, Windows
        '''
        _validate_not_none('label', label)
        _validate_not_none('media_link', media_link)
        _validate_not_none('name', name)
        _validate_not_none('os', os)
        return self._perform_post(self._get_disk_path(),
                                  _XmlSerializer.disk_to_xml(
                                      label,
                                      media_link,
                                      name,
                                      os))

    def update_disk(self, disk_name, has_operating_system=None, label=None, media_link=None,
                    name=None, os=None):
        '''
        Updates an existing disk in your image repository.

        disk_name:
            The name of the disk to update.
        has_operating_system:
            Deprecated.
        label:
            Specifies the description of the disk.
        media_link:
            Deprecated.
        name:
            Deprecated.
        os:
            Deprecated.
        '''
        _validate_not_none('disk_name', disk_name)
        _validate_not_none('label', label)
        return self._perform_put(self._get_disk_path(disk_name),
                                 _XmlSerializer.disk_to_xml(
                                     label,
                                     None,
                                     None,
                                     None))

    def delete_disk(self, disk_name, delete_vhd=False):
        '''
        Deletes the specified data or operating system disk from your image
        repository.

        disk_name:
            The name of the disk to delete.
        delete_vhd:
            Deletes the underlying vhd blob in Azure storage.
        '''
        _validate_not_none('disk_name', disk_name)
        path = self._get_disk_path(disk_name)
        if delete_vhd:
            path += '?comp=media'
        return self._perform_delete(path)

    #--Operations for virtual networks  ------------------------------
    def list_virtual_network_sites(self):
        '''
        Retrieves a list of the virtual networks.
        '''
        return self._perform_get(self._get_virtual_network_site_path(), VirtualNetworkSites)
  
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

    def _get_role_sizes_path(self):
        return self._get_path('rolesizes', None)

    def _get_subscriptions_path(self):
        return '/subscriptions'

    def _get_list_subscription_operations_path(self):
        return self._get_path('operations', None)

    def _get_virtual_network_site_path(self):
        return self._get_path('services/networking/virtualnetwork', None)

    def _get_storage_service_path(self, service_name=None):
        return self._get_path('services/storageservices', service_name)

    def _get_hosted_service_path(self, service_name=None):
        return self._get_path('services/hostedservices', service_name)

    def _get_deployment_path_using_slot(self, service_name, slot=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deploymentslots', slot)

    def _get_deployment_path_using_name(self, service_name,
                                        deployment_name=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments', deployment_name)

    def _get_role_path(self, service_name, deployment_name, role_name=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + deployment_name +
                              '/roles', role_name)

    def _get_role_instance_operations_path(self, service_name, deployment_name,
                                           role_name=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + deployment_name +
                              '/roleinstances', role_name) + '/Operations'

    def _get_roles_operations_path(self, service_name, deployment_name):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + deployment_name +
                              '/roles/Operations', None)

    def _get_resource_extensions_path(self):
        return self._get_path('services/resourceextensions', None)

    def _get_resource_extension_versions_path(self, publisher_name, extension_name):
        return self._get_path('services/resourceextensions',
                              publisher_name + '/' + extension_name)

    def _get_dns_server_path(self, service_name, deployment_name,
                             dns_server_name=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + deployment_name +
                              '/dnsservers', dns_server_name)

    def _get_capture_vm_image_path(self, service_name, deployment_name, role_name):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + _str(deployment_name) +
                              '/roleinstances/' + _str(role_name) + '/Operations',
                              None)

    def _get_vm_image_path(self, image_name=None):
        return self._get_path('services/vmimages', image_name)

    def _get_reserved_ip_path(self, name=None):
        return self._get_path('services/networking/reservedips', name)

    def _get_reserved_ip_path_for_association(self, name):
        return self._get_path('services/networking/reservedips', name) + \
            '/operations/associate'

    def _get_reserved_ip_path_for_disassociation(self, name):
        return self._get_path('services/networking/reservedips', name) + \
            '/operations/disassociate'

    def _get_data_disk_path(self, service_name, deployment_name, role_name,
                            lun=None):
        return self._get_path('services/hostedservices/' + _str(service_name) +
                              '/deployments/' + _str(deployment_name) +
                              '/roles/' + _str(role_name) + '/DataDisks', lun)

    def _get_disk_path(self, disk_name=None):
        return self._get_path('services/disks', disk_name)

    def _get_image_path(self, image_name=None):
        return self._get_path('services/images', image_name)

    def _get_image_details_path(self, image_name=None):
        return self._get_path('services/images', image_name, 'details')
