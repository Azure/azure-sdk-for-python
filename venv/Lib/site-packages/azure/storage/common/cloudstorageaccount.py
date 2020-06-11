# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# Note that we import BlobService/QueueService/FileService on demand
# because this module is imported by azure/storage/__init__
# ie. we don't want 'import azure.storage' to trigger an automatic import
# of blob/queue/file packages.

from azure.storage.common._error import _validate_not_none
from azure.storage.common.models import (
    ResourceTypes,
    Services,
    AccountPermissions,
)
from azure.storage.common.sharedaccesssignature import (
    SharedAccessSignature,
)


class CloudStorageAccount(object):
    """
    Provides a factory for creating the blob, queue, and file services
    with a common account name and account key or sas token.  Users can either 
    use the factory or can construct the appropriate service directly.
    """

    def __init__(self, account_name=None, account_key=None, sas_token=None,
                 is_emulated=None, endpoint_suffix=None):
        '''
        :param str account_name:
            The storage account name. This is used to authenticate requests 
            signed with an account key and to construct the storage endpoint. It 
            is required unless is_emulated is used.
        :param str account_key:
            The storage account key. This is used for shared key authentication. 
        :param str sas_token:
             A shared access signature token to use to authenticate requests 
             instead of the account key. If account key and sas token are both 
             specified, account key will be used to sign.
        :param bool is_emulated:
            Whether to use the emulator. Defaults to False. If specified, will
            override all other parameters.
        :param str endpoint_suffix:
            The host base component of the url, minus the account name. Defaults
            to Azure (core.windows.net). Override this to use a sovereign cloud.
        '''
        self.account_name = account_name
        self.account_key = account_key
        self.sas_token = sas_token
        self.is_emulated = is_emulated
        self.endpoint_suffix = endpoint_suffix

    def create_block_blob_service(self):
        '''
        Creates a BlockBlobService object with the settings specified in the 
        CloudStorageAccount.

        :return: A service object.
        :rtype: :class:`~azure.storage.blob.blockblobservice.BlockBlobService`
        '''
        try:
            from azure.storage.blob.blockblobservice import BlockBlobService
            return BlockBlobService(self.account_name, self.account_key,
                                    sas_token=self.sas_token,
                                    is_emulated=self.is_emulated,
                                    endpoint_suffix=self.endpoint_suffix)
        except ImportError:
            raise Exception('The package azure-storage-blob is required. '
                            + 'Please install it using "pip install azure-storage-blob"')

    def create_page_blob_service(self):
        '''
        Creates a PageBlobService object with the settings specified in the 
        CloudStorageAccount.

        :return: A service object.
        :rtype: :class:`~azure.storage.blob.pageblobservice.PageBlobService`
        '''
        try:
            from azure.storage.blob.pageblobservice import PageBlobService
            return PageBlobService(self.account_name, self.account_key,
                                   sas_token=self.sas_token,
                                   is_emulated=self.is_emulated,
                                   endpoint_suffix=self.endpoint_suffix)
        except ImportError:
            raise Exception('The package azure-storage-blob is required. '
                            + 'Please install it using "pip install azure-storage-blob"')

    def create_append_blob_service(self):
        '''
        Creates a AppendBlobService object with the settings specified in the 
        CloudStorageAccount.

        :return: A service object.
        :rtype: :class:`~azure.storage.blob.appendblobservice.AppendBlobService`
        '''
        try:
            from azure.storage.blob.appendblobservice import AppendBlobService
            return AppendBlobService(self.account_name, self.account_key,
                                     sas_token=self.sas_token,
                                     is_emulated=self.is_emulated,
                                     endpoint_suffix=self.endpoint_suffix)
        except ImportError:
            raise Exception('The package azure-storage-blob is required. '
                            + 'Please install it using "pip install azure-storage-blob"')

    def create_queue_service(self):
        '''
        Creates a QueueService object with the settings specified in the 
        CloudStorageAccount.

        :return: A service object.
        :rtype: :class:`~azure.storage.queue.queueservice.QueueService`
        '''
        try:
            from azure.storage.queue.queueservice import QueueService
            return QueueService(self.account_name, self.account_key,
                                sas_token=self.sas_token,
                                is_emulated=self.is_emulated,
                                endpoint_suffix=self.endpoint_suffix)
        except ImportError:
            raise Exception('The package azure-storage-queue is required. '
                            + 'Please install it using "pip install azure-storage-queue"')

    def create_file_service(self):
        '''
        Creates a FileService object with the settings specified in the 
        CloudStorageAccount.

        :return: A service object.
        :rtype: :class:`~azure.storage.file.fileservice.FileService`
        '''
        try:
            from azure.storage.file.fileservice import FileService
            return FileService(self.account_name, self.account_key,
                               sas_token=self.sas_token,
                               endpoint_suffix=self.endpoint_suffix)
        except ImportError:
            raise Exception('The package azure-storage-file is required. '
                            + 'Please install it using "pip install azure-storage-file"')

    def generate_shared_access_signature(self, services, resource_types,
                                         permission, expiry, start=None,
                                         ip=None, protocol=None):
        '''
        Generates a shared access signature for the account.
        Use the returned signature with the sas_token parameter of the service 
        or to create a new account object.

        :param Services services:
            Specifies the services accessible with the account SAS. You can 
            combine values to provide access to more than one service. 
        :param ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account 
            SAS. You can combine values to provide access to more than one 
            resource type. 
        :param AccountPermissions permission:
            The permissions associated with the shared access signature. The 
            user is restricted to operations allowed by the permissions. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has been 
            specified in an associated stored access policy. You can combine 
            values to provide more than one permission.
        :param expiry:
            The time at which the shared access signature becomes invalid. 
            Required unless an id is given referencing a stored access policy 
            which contains this field. This field must be omitted if it has 
            been specified in an associated stored access policy. Azure will always 
            convert values to UTC. If a date is passed in without timezone info, it 
            is assumed to be UTC.
        :type expiry: datetime or str
        :param start:
            The time at which the shared access signature becomes valid. If 
            omitted, start time for this call is assumed to be the time when the 
            storage service receives the request. Azure will always convert values 
            to UTC. If a date is passed in without timezone info, it is assumed to 
            be UTC.
        :type start: datetime or str
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. Possible values are
            both HTTPS and HTTP (https,http) or HTTPS only (https). The default value
            is https,http. Note that HTTP only is not a permitted value.
        '''
        _validate_not_none('self.account_name', self.account_name)
        _validate_not_none('self.account_key', self.account_key)

        sas = SharedAccessSignature(self.account_name, self.account_key)
        return sas.generate_account(services, resource_types, permission,
                                    expiry, start=start, ip=ip, protocol=protocol)
