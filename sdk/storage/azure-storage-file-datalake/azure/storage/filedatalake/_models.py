# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines
from enum import Enum

from azure.core.paging import PageIterator
from azure.storage.blob import LeaseProperties as BlobLeaseProperties
from azure.storage.blob import AccountSasPermissions as BlobAccountSasPermissions
from azure.storage.blob import ResourceTypes as BlobResourceTypes
from azure.storage.blob import UserDelegationKey as BlobUserDelegationKey
from azure.storage.blob import ContentSettings as BlobContentSettings
from azure.storage.blob import ContainerSasPermissions, BlobSasPermissions
from azure.storage.blob._generated.models import StorageErrorException
from azure.storage.blob._models import ContainerPropertiesPaged
from ._deserialize import return_headers_and_deserialized_path_list
from ._generated.models import Path
from ._shared.models import DictMixin
from ._shared.response_handlers import process_storage_error


class FileSystemProperties(object):
    """File System properties class.

    :ivar ~datetime.datetime last_modified:
        A datetime object representing the last time the file system was modified.
    :ivar str etag:
        The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar ~azure.storage.filedatalake.LeaseProperties lease:
        Stores all the lease information for the file system.
    :ivar str public_access: Specifies whether data in the file system may be accessed
        publicly and the level of access.
    :ivar bool has_immutability_policy:
        Represents whether the file system has an immutability policy.
    :ivar bool has_legal_hold:
        Represents whether the file system has a legal hold.
    :ivar dict metadata: A dict with name-value pairs to associate with the
        file system as metadata.

    Returned ``FileSystemProperties`` instances expose these values through a
    dictionary interface, for example: ``file_system_props["last_modified"]``.
    Additionally, the file system name is available as ``file_system_props["name"]``.
    """
    def __init__(self):
        self.name = None
        self.last_modified = None
        self.etag = None
        self.lease = None
        self.public_access = None
        self.has_immutability_policy = None
        self.has_legal_hold = None
        self.metadata = None

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.etag = generated.properties.etag
        props.lease = LeaseProperties._from_generated(generated)  # pylint: disable=protected-access
        props.public_access = PublicAccess._from_generated(  # pylint: disable=protected-access
            generated.properties.public_access)
        props.has_immutability_policy = generated.properties.has_immutability_policy
        props.has_legal_hold = generated.properties.has_legal_hold
        props.metadata = generated.metadata
        return props

    @classmethod
    def _convert_from_container_props(cls, container_properties):
        container_properties.__class__ = cls
        container_properties.public_access = PublicAccess._from_generated(  # pylint: disable=protected-access
            container_properties.public_access)
        container_properties.lease.__class__ = LeaseProperties
        return container_properties


class FileSystemPropertiesPaged(ContainerPropertiesPaged):
    """An Iterable of File System properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A file system name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :ivar current_page: The current page of listed results.
    :vartype current_page: list(~azure.storage.filedatalake.FileSystemProperties)

    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only file systems whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of file system names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """

    def __init__(self, *args, **kwargs):
        super(FileSystemPropertiesPaged, self).__init__(
            *args,
            **kwargs
        )

    @staticmethod
    def _build_item(item):
        return FileSystemProperties._from_generated(item)  # pylint: disable=protected-access


class DirectoryProperties(DictMixin):
    """
    :ivar str name: name of the directory
    :ivar str etag: The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar bool deleted: if the current directory marked as deleted
    :ivar dict metadata: Name-value pairs associated with the blob as metadata.
    :ivar ~azure.storage.filedatalake.LeaseProperties lease:
        Stores all the lease information for the directory.
    :ivar ~datetime.datetime last_modified:
        A datetime object representing the last time the directory was modified.
    :ivar ~datetime.datetime creation_time:
        Indicates when the directory was created, in UTC.
    :ivar int remaining_retention_days: The number of days that the directory will be retained
        before being permanently deleted by the service.
    :var ~azure.storage.filedatalake.ContentSettings content_settings:
    """
    def __init__(self, **kwargs):
        super(DirectoryProperties, self).__init__(
            **kwargs
        )
        self.name = None
        self.etag = None
        self.deleted = None
        self.metadata = None
        self.lease = None
        self.last_modified = None
        self.creation_time = None
        self.deleted_time = None
        self.remaining_retention_days = None

    @classmethod
    def _from_blob_properties(cls, blob_properties):
        directory_props = DirectoryProperties()
        directory_props.name = blob_properties.name
        directory_props.etag = blob_properties.etag
        directory_props.deleted = blob_properties.deleted
        directory_props.metadata = blob_properties.metadata
        directory_props.lease = blob_properties.lease
        directory_props.lease.__class__ = LeaseProperties
        directory_props.last_modified = blob_properties.last_modified
        directory_props.creation_time = blob_properties.creation_time
        directory_props.deleted_time = blob_properties.deleted_time
        directory_props.remaining_retention_days = blob_properties.remaining_retention_days
        return directory_props


class FileProperties(DictMixin):
    """
    :ivar str name: name of the file
    :ivar str etag: The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar bool deleted: if the current file marked as deleted
    :ivar dict metadata: Name-value pairs associated with the blob as metadata.
    :ivar ~azure.storage.filedatalake.LeaseProperties lease:
        Stores all the lease information for the file.
    :ivar ~datetime.datetime last_modified:
        A datetime object representing the last time the file was modified.
    :ivar ~datetime.datetime creation_time:
        Indicates when the file was created, in UTC.
    :ivar int size: size of the file
    :ivar int remaining_retention_days: The number of days that the file will be retained
        before being permanently deleted by the service.
    :var ~azure.storage.filedatalake.ContentSettings content_settings:
    """
    def __init__(self, **kwargs):
        super(FileProperties, self).__init__(
            **kwargs
        )
        self.name = None
        self.etag = None
        self.deleted = None
        self.metadata = None
        self.lease = None
        self.last_modified = None
        self.creation_time = None
        self.size = None
        self.deleted_time = None
        self.remaining_retention_days = None
        self.content_settings = None

    @classmethod
    def _from_blob_properties(cls, blob_properties):
        file_props = FileProperties()
        file_props.name = blob_properties.name
        file_props.etag = blob_properties.etag
        file_props.deleted = blob_properties.deleted
        file_props.metadata = blob_properties.metadata
        file_props.lease = blob_properties.lease
        file_props.lease.__class__ = LeaseProperties
        file_props.last_modified = blob_properties.last_modified
        file_props.creation_time = blob_properties.creation_time
        file_props.size = blob_properties.size
        file_props.deleted_time = blob_properties.deleted_time
        file_props.remaining_retention_days = blob_properties.remaining_retention_days
        file_props.content_settings = blob_properties.content_settings
        return file_props


class PathProperties(object):
    """Path properties listed by get_paths api.

    :ivar str name: the full path for a file or directory.
    :ivar str owner: The owner of the file or directory.
    :ivar str group: he owning group of the file or directory.
    :ivar str permissions: Sets POSIX access permissions for the file
         owner, the file owning group, and others. Each class may be granted
         read, write, or execute permission.  The sticky bit is also supported.
         Both symbolic (rwxrw-rw-) and 4-digit octal notation (e.g. 0766) are
         supported.
    :ivar datetime last_modified:  A datetime object representing the last time the blob was modified.
    :ivar bool is_directory: is the path a directory or not.
    :ivar str etag: The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar content_length: the size of file if the path is a file.
    """
    def __init__(self, **kwargs):
        super(PathProperties, self).__init__(
            **kwargs
        )
        self.name = kwargs.pop('name', None)
        self.owner = kwargs.get('owner', None)
        self.group = kwargs.get('group', None)
        self.permissions = kwargs.get('permissions', None)
        self.last_modified = kwargs.get('last_modified', None)
        self.is_directory = kwargs.get('is_directory', False)
        self.etag = kwargs.get('etag', None)
        self.content_length = kwargs.get('content_length', None)

    @classmethod
    def _from_generated(cls, generated):
        path_prop = PathProperties()
        path_prop.name = generated.name
        path_prop.owner = generated.owner
        path_prop.group = generated.group
        path_prop.permissions = generated.permissions
        path_prop.last_modified = generated.last_modified
        path_prop.is_directory = bool(generated.is_directory)
        path_prop.etag = generated.additional_properties.get('etag')
        path_prop.content_length = generated.content_length
        return path_prop


class PathPropertiesPaged(PageIterator):
    """An Iterable of Path properties.

    :ivar str path: Filters the results to return only paths under the specified path.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str continuation_token: The continuation token to retrieve the next page of results.
    :ivar list(~azure.storage.filedatalake.PathProperties) current_page: The current page of listed results.

    :param callable command: Function to retrieve the next page of items.
    :param str path: Filters the results to return only paths under the specified path.
    :param int max_results: The maximum number of psths to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(
            self, command,
            recursive,
            path=None,
            max_results=None,
            continuation_token=None,
            upn=None):
        super(PathPropertiesPaged, self).__init__(
            get_next=self._get_next_cb,
            extract_data=self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.recursive = recursive
        self.results_per_page = max_results
        self.path = path
        self.upn = upn
        self.current_page = None
        self.path_list = None

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                self.recursive,
                continuation=continuation_token or None,
                path=self.path,
                max_results=self.results_per_page,
                upn=self.upn,
                cls=return_headers_and_deserialized_path_list)
        except StorageErrorException as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.path_list, self._response = get_next_return
        self.current_page = [self._build_item(item) for item in self.path_list]

        return self._response['continuation'] or None, self.current_page

    @staticmethod
    def _build_item(item):
        if isinstance(item, PathProperties):
            return item
        if isinstance(item, Path):
            path = PathProperties._from_generated(item)  # pylint: disable=protected-access
            return path
        return item


class LeaseProperties(BlobLeaseProperties):
    """DataLake Lease Properties.

    :ivar str status:
        The lease status of the file. Possible values: locked|unlocked
    :ivar str state:
        Lease state of the file. Possible values: available|leased|expired|breaking|broken
    :ivar str duration:
        When a file is leased, specifies whether the lease is of infinite or fixed duration.
    """
    def __init__(self):
        self.status = None
        self.state = None
        self.duration = None


class ContentSettings(BlobContentSettings):
    """The content settings of a file or directory.

    :ivar str content_type:
        The content type specified for the file or directory. If no content type was
        specified, the default content type is application/octet-stream.
    :ivar str content_encoding:
        If the content_encoding has previously been set
        for the file, that value is stored.
    :ivar str content_language:
        If the content_language has previously been set
        for the file, that value is stored.
    :ivar str content_disposition:
        content_disposition conveys additional information about how to
        process the response payload, and also can be used to attach
        additional metadata. If content_disposition has previously been set
        for the file, that value is stored.
    :ivar str cache_control:
        If the cache_control has previously been set for
        the file, that value is stored.
    :ivar str content_md5:
        If the content_md5 has been set for the file, this response
        header is stored so that the client can check for message content
        integrity.
    """
    def __init__(
            self, content_type=None, content_encoding=None,
            content_language=None, content_disposition=None,
            cache_control=None, content_md5=None, **kwargs):
        super(ContentSettings, self).__init__(
            content_type=content_type,
            content_encoding=content_encoding,
            content_language=content_language,
            content_disposition=content_disposition,
            cache_control=cache_control,
            content_md5=content_md5,
            **kwargs
        )


class AccountSasPermissions(BlobAccountSasPermissions):
    def __init__(self, read=False, write=False, delete=False, list=False,  # pylint: disable=redefined-builtin
                 create=False):
        super(AccountSasPermissions, self).__init__(
            read=read, create=create, write=write, list=list,
            delete=delete
        )


class FileSystemSasPermissions(ContainerSasPermissions):
    """FileSystemSasPermissions class to be used with the
    :func:`~azure.storage.filedatalake.generate_file_system_sas` function.

    :param bool read:
        Read the content, properties, metadata etc.
    :param bool write:
        Create or write content, properties, metadata. Lease the file system.
    :param bool delete:
        Delete the file system.
    :param bool list:
        List paths in the file system.
    """
    def __init__(self, read=False, write=False, delete=False, list=False  # pylint: disable=redefined-builtin
                 ):
        super(FileSystemSasPermissions, self).__init__(
            read=read, write=write, delete=delete, list=list
        )


class DirectorySasPermissions(BlobSasPermissions):
    """DirectorySasPermissions class to be used with the
    :func:`~azure.storage.filedatalake.generate_directory_sas` function.

    :param bool read:
        Read the content, properties, metadata etc.
    :param bool create:
        Create a new directory
    :param bool write:
        Create or write content, properties, metadata. Lease the directory.
    :param bool delete:
        Delete the directory.
    """
    def __init__(self, read=False, create=False, write=False,
                 delete=False):
        super(DirectorySasPermissions, self).__init__(
            read=read, create=create, write=write,
            delete=delete
        )


class FileSasPermissions(BlobSasPermissions):
    """FileSasPermissions class to be used with the
    :func:`~azure.storage.filedatalake.generate_file_sas` function.

    :param bool read:
        Read the content, properties, metadata etc. Use the file as
        the source of a read operation.
    :param bool create:
        Write a new file
    :param bool write:
        Create or write content, properties, metadata. Lease the file.
    :param bool delete:
        Delete the file.
    """
    def __init__(self, read=False, create=False, write=False,
                 delete=False):
        super(FileSasPermissions, self).__init__(
            read=read, create=create, write=write,
            delete=delete
        )


class ResourceTypes(BlobResourceTypes):
    """
    Specifies the resource types that are accessible with the account SAS.

    :param bool service:
        Access to service-level APIs (e.g.List File Systems)
    :param bool file_system:
        Access to file_system-level APIs (e.g., Create/Delete file system,
        List Directories/Files)
    :param bool object:
        Access to object-level APIs for
        files(e.g. Create File, etc.)
    """
    def __init__(self, service=False, file_system=False, object=False  # pylint: disable=redefined-builtin
                 ):
        super(ResourceTypes, self).__init__(service=service, container=file_system, object=object)


class UserDelegationKey(BlobUserDelegationKey):
    """
    Represents a user delegation key, provided to the user by Azure Storage
    based on their Azure Active Directory access token.

    The fields are saved as simple strings since the user does not have to interact with this object;
    to generate an identify SAS, the user can simply pass it to the right API.

    :ivar str signed_oid:
        Object ID of this token.
    :ivar str signed_tid:
        Tenant ID of the tenant that issued this token.
    :ivar str signed_start:
        The datetime this token becomes valid.
    :ivar str signed_expiry:
        The datetime this token expires.
    :ivar str signed_service:
        What service this key is valid for.
    :ivar str signed_version:
        The version identifier of the REST service that created this token.
    :ivar str value:
        The user delegation key.
    """
    def _init(self):
        super(UserDelegationKey, self).__init__()


class PublicAccess(str, Enum):
    """
    Specifies whether data in the file system may be accessed publicly and the level of access.
    """

    OFF = 'off'
    """
    Specifies that there is no public read access for both the file systems and files within the file system.
    Clients cannot enumerate the file systems within the storage account as well as the files within the file system.
    """

    File = 'blob'
    """
    Specifies public read access for files. file data within this file system can be read
    via anonymous request, but file system data is not available. Clients cannot enumerate
    files within the container via anonymous request.
    """

    FileSystem = 'container'
    """
    Specifies full public read access for file system and file data. Clients can enumerate
    files within the file system via anonymous request, but cannot enumerate file systems
    within the storage account.
    """

    @classmethod
    def _from_generated(cls, public_access):
        if public_access == "blob":  # pylint:disable=no-else-return
            return cls.File
        elif public_access == "container":
            return cls.FileSystem
        elif public_access == "off":
            return cls.OFF
        return None


class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.
