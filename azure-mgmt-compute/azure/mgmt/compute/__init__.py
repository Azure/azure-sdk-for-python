# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from msrest.service_client import ServiceClient
from msrest import Serializer, Deserializer
from msrestazure import AzureConfiguration
from .version import VERSION


def models(api_version=None):
    if api_version == '2015-06-15':
        from .v2015_06_15 import models
        return models
    elif api_version == '2016-04-30-preview':
        from .v2016_04_30_preview import models
        return models
    elif api_version == '2017-01-31':
        from .v2017_01_31 import models
        return models
    raise NotImplementedError("APIVersion {} is not available".format(api_version))

class ClientConfiguration(AzureConfiguration):
    """Configuration for ComputeManagementClient
    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param api_version: Client Api Version.
    :type api_version: str
    :param str base_url: Service URL
    """

    def __init__(
            self, credentials, subscription_id=None, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")
        if not base_url:
            base_url = 'https://management.azure.com'

        super(ClientConfiguration, self).__init__(base_url)

        self.add_user_agent('computemanagementclient/{}'.format(VERSION))
        self.add_user_agent('Azure-SDK-For-Python')

        self.credentials = credentials
        self.subscription_id = subscription_id


class Client(object):
    """The Compute Management Client.

    :ivar config: Configuration for client.
    :vartype config: ResourceManagementClientConfiguration

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`
    :param subscription_id: Gets subscription credentials which uniquely
     identify Microsoft Azure subscription. The subscription ID forms part of
     the URI for every service call.
    :type subscription_id: str
    :param str base_url: Service URL
    """

    def __init__(self, credentials, subscription_id=None, base_url=None):

        if credentials is None:
            raise ValueError("Parameter 'credentials' must not be None.")
        if subscription_id is None:
            raise ValueError("Parameter 'subscription_id' must not be None.")
        if not isinstance(subscription_id, str):
            raise TypeError("Parameter 'subscription_id' must be str.")

        self.credentials = credentials
        self.subscription_id = subscription_id
        self.base_url = base_url

        self.config = ClientConfiguration(self.credentials, self.subscription_id, self.base_url)
        self.client = ServiceClient(self.credentials, self.config)

    def _instantiate_operation_class(self, api_version, local_models, operation_class):
        client_models = {k: v for k, v in local_models.__dict__.items() if isinstance(v, type)}
        serialize = Serializer(client_models)
        deserialize = Deserializer(client_models)
        return operation_class(self.client, self.config, serialize, deserialize)

    def availability_sets(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.availability_sets_operations import AvailabilitySetsOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.availability_sets_operations import AvailabilitySetsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_extension_images(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_extension_images_operations import VirtualMachineExtensionImagesOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_extension_images_operations import VirtualMachineExtensionImagesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_extensions(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_extensions_operations import VirtualMachineExtensionsOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_extensions_operations import VirtualMachineExtensionsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_images(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_images_operations import VirtualMachineImagesOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_images_operations import VirtualMachineImagesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def usage(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.usage_operations import UsageOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.usage_operations import UsageOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_sizes(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_sizes_operations import VirtualMachineSizesOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_sizes_operations import VirtualMachineSizesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def images(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.images_operations import ImagesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machines(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machines_operations import VirtualMachinesOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machines_operations import VirtualMachinesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_scale_sets(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_scale_sets_operations import VirtualMachineScaleSetsOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_scale_sets_operations import VirtualMachineScaleSetsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def virtual_machine_scale_set_vms(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.virtual_machine_scale_set_vms_operations import VirtualMachineScaleSetVMsOperations as OperationClass
        elif api_version =='2015-06-15':
            from .v2015_06_15.operations.virtual_machine_scale_set_vms_operations import VirtualMachineScaleSetVMsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def disks(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.disks_operations import DisksOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def snapshots(self, api_version='2016-04-30-preview'):
        if api_version =='2016-04-30-preview':
            from .v2016_04_30_preview.operations.snapshots_operations import SnapshotsOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

    def container_services(self, api_version='2017-01-31'):
        if api_version =='2017-01-31':
            from .v2017_01_31.operations.container_services_operations import ContainerServicesOperations as OperationClass
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return self._instantiate_operation_class(api_version, models(api_version), OperationClass)

