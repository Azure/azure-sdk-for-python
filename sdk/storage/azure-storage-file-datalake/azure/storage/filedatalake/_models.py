# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=super-init-not-called, too-many-lines
from datetime import datetime
from enum import Enum

from azure.storage.blob import LeaseProperties as BlobLeaseProperties
from azure.storage.blob import AccountSasPermissions as BlobAccountSasPermissions
from azure.storage.blob import ResourceTypes as BlobResourceTypes
from azure.storage.blob import UserDelegationKey as BlobUserDelegationKey
from azure.storage.blob import ContentSettings as BlobContentSettings
from azure.storage.blob import AccessPolicy as BlobAccessPolicy
from azure.storage.blob import DelimitedTextDialect as BlobDelimitedTextDialect
from azure.storage.blob import DelimitedJsonDialect as BlobDelimitedJSON
from azure.storage.blob import ArrowDialect as BlobArrowDialect
from azure.storage.blob._models import ContainerPropertiesPaged
from ._shared.models import DictMixin


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
    :ivar bool deleted:
        Whether this file system was deleted.
    :ivar str deleted_version:
        The version of a deleted file system.

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
        self.deleted = None
        self.deleted_version = None

    @classmethod
    def _from_generated(cls, generated):
        props = cls()
        props.name = generated.name
        props.last_modified = generated.properties.last_modified
        props.deleted = generated.deleted
        props.deleted_version = generated.version
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
    :ivar dict metadata: Name-value pairs associated with the directory as metadata.
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
        self.name = kwargs.get('name')
        self.etag = kwargs.get('ETag')
        self.deleted = False
        self.metadata = kwargs.get('metadata')
        self.lease = LeaseProperties(**kwargs)
        self.last_modified = kwargs.get('Last-Modified')
        self.creation_time = kwargs.get('x-ms-creation-time')
        self.deleted_time = None
        self.remaining_retention_days = None


class FileProperties(DictMixin):
    """
    :ivar str name: name of the file
    :ivar str etag: The ETag contains a value that you can use to perform operations
        conditionally.
    :ivar bool deleted: if the current file marked as deleted
    :ivar dict metadata: Name-value pairs associated with the file as metadata.
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
        self.name = kwargs.get('name')
        self.etag = kwargs.get('ETag')
        self.deleted = False
        self.metadata = kwargs.get('metadata')
        self.lease = LeaseProperties(**kwargs)
        self.last_modified = kwargs.get('Last-Modified')
        self.creation_time = kwargs.get('x-ms-creation-time')
        self.size = kwargs.get('Content-Length')
        self.deleted_time = None
        self.expiry_time = kwargs.get("x-ms-expiry-time")
        self.remaining_retention_days = None
        self.content_settings = ContentSettings(**kwargs)


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
    :ivar datetime last_modified:  A datetime object representing the last time the directory/file was modified.
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
        path_prop.last_modified = datetime.strptime(generated.last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        path_prop.is_directory = bool(generated.is_directory)
        path_prop.etag = generated.additional_properties.get('etag')
        path_prop.content_length = generated.content_length
        return path_prop


class LeaseProperties(BlobLeaseProperties):
    """DataLake Lease Properties.

    :ivar str status:
        The lease status of the file. Possible values: locked|unlocked
    :ivar str state:
        Lease state of the file. Possible values: available|leased|expired|breaking|broken
    :ivar str duration:
        When a file is leased, specifies whether the lease is of infinite or fixed duration.
    """


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
    :ivar bytearray content_md5:
        If the content_md5 has been set for the file, this response
        header is stored so that the client can check for message content
        integrity.
    :keyword str content_type:
        The content type specified for the file or directory. If no content type was
        specified, the default content type is application/octet-stream.
    :keyword str content_encoding:
        If the content_encoding has previously been set
        for the file, that value is stored.
    :keyword str content_language:
        If the content_language has previously been set
        for the file, that value is stored.
    :keyword str content_disposition:
        content_disposition conveys additional information about how to
        process the response payload, and also can be used to attach
        additional metadata. If content_disposition has previously been set
        for the file, that value is stored.
    :keyword str cache_control:
        If the cache_control has previously been set for
        the file, that value is stored.
    :keyword bytearray content_md5:
        If the content_md5 has been set for the file, this response
        header is stored so that the client can check for message content
        integrity.
    """

    def __init__(
            self, **kwargs):
        super(ContentSettings, self).__init__(
            **kwargs
        )


class AccountSasPermissions(BlobAccountSasPermissions):
    def __init__(self, read=False, write=False, delete=False, list=False,  # pylint: disable=redefined-builtin
                 create=False):
        super(AccountSasPermissions, self).__init__(
            read=read, create=create, write=write, list=list,
            delete=delete
        )


class FileSystemSasPermissions(object):
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
    :keyword bool move:
        Move any file in the directory to a new location.
        Note the move operation can optionally be restricted to the child file or directory owner or
        the parent directory owner if the saoid parameter is included in the token and the sticky bit is set
        on the parent directory.
    :keyword bool execute:
        Get the status (system defined properties) and ACL of any file in the directory.
        If the caller is the owner, set access control on any file in the directory.
    :keyword bool manage_ownership:
        Allows the user to set owner, owning group, or act as the owner when renaming or deleting a file or directory
        within a folder that has the sticky bit set.
    :keyword bool manage_access_control:
         Allows the user to set permissions and POSIX ACLs on files and directories.
    """

    def __init__(self, read=False, write=False, delete=False, list=False,  # pylint: disable=redefined-builtin
                 **kwargs):
        self.read = read
        self.write = write
        self.delete = delete
        self.list = list
        self.move = kwargs.pop('move', None)
        self.execute = kwargs.pop('execute', None)
        self.manage_ownership = kwargs.pop('manage_ownership', None)
        self.manage_access_control = kwargs.pop('manage_access_control', None)
        self._str = (('r' if self.read else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else '') +
                     ('m' if self.move else '') +
                     ('e' if self.execute else '') +
                     ('o' if self.manage_ownership else '') +
                     ('p' if self.manage_access_control else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission):
        """Create a FileSystemSasPermissions from a string.

        To specify read, write, or delete permissions you need only to
        include the first letter of the word in the string. E.g. For read and
        write permissions, you would provide a string "rw".

        :param str permission: The string which dictates the read, add, create,
            write, or delete permissions.
        :return: A FileSystemSasPermissions object
        :rtype: ~azure.storage.fildatalake.FileSystemSasPermissions
        """
        p_read = 'r' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission
        p_move = 'm' in permission
        p_execute = 'e' in permission
        p_manage_ownership = 'o' in permission
        p_manage_access_control = 'p' in permission

        parsed = cls(read=p_read, write=p_write, delete=p_delete,
                     list=p_list, move=p_move, execute=p_execute, manage_ownership=p_manage_ownership,
                     manage_access_control=p_manage_access_control)
        return parsed


class DirectorySasPermissions(object):
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
    :keyword bool list:
        List any files in the directory. Implies Execute.
    :keyword bool move:
        Move any file in the directory to a new location.
        Note the move operation can optionally be restricted to the child file or directory owner or
        the parent directory owner if the saoid parameter is included in the token and the sticky bit is set
        on the parent directory.
    :keyword bool execute:
        Get the status (system defined properties) and ACL of any file in the directory.
        If the caller is the owner, set access control on any file in the directory.
    :keyword bool manage_ownership:
        Allows the user to set owner, owning group, or act as the owner when renaming or deleting a file or directory
        within a folder that has the sticky bit set.
    :keyword bool manage_access_control:
         Allows the user to set permissions and POSIX ACLs on files and directories.
    """

    def __init__(self, read=False, create=False, write=False,
                 delete=False, **kwargs):
        self.read = read
        self.create = create
        self.write = write
        self.delete = delete
        self.list = kwargs.pop('list', None)
        self.move = kwargs.pop('move', None)
        self.execute = kwargs.pop('execute', None)
        self.manage_ownership = kwargs.pop('manage_ownership', None)
        self.manage_access_control = kwargs.pop('manage_access_control', None)
        self._str = (('r' if self.read else '') +
                     ('c' if self.create else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('l' if self.list else '') +
                     ('m' if self.move else '') +
                     ('e' if self.execute else '') +
                     ('o' if self.manage_ownership else '') +
                     ('p' if self.manage_access_control else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission):
        """Create a DirectorySasPermissions from a string.

        To specify read, create, write, or delete permissions you need only to
        include the first letter of the word in the string. E.g. For read and
        write permissions, you would provide a string "rw".

        :param str permission: The string which dictates the read, add, create,
            write, or delete permissions.
        :return: A DirectorySasPermissions object
        :rtype: ~azure.storage.filedatalake.DirectorySasPermissions
        """
        p_read = 'r' in permission
        p_create = 'c' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_list = 'l' in permission
        p_move = 'm' in permission
        p_execute = 'e' in permission
        p_manage_ownership = 'o' in permission
        p_manage_access_control = 'p' in permission

        parsed = cls(read=p_read, create=p_create, write=p_write, delete=p_delete,
                     list=p_list, move=p_move, execute=p_execute, manage_ownership=p_manage_ownership,
                     manage_access_control=p_manage_access_control)
        return parsed


class FileSasPermissions(object):
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
    :keyword bool move:
        Move any file in the directory to a new location.
        Note the move operation can optionally be restricted to the child file or directory owner or
        the parent directory owner if the saoid parameter is included in the token and the sticky bit is set
        on the parent directory.
    :keyword bool execute:
        Get the status (system defined properties) and ACL of any file in the directory.
        If the caller is the owner, set access control on any file in the directory.
    :keyword bool manage_ownership:
        Allows the user to set owner, owning group, or act as the owner when renaming or deleting a file or directory
        within a folder that has the sticky bit set.
    :keyword bool manage_access_control:
         Allows the user to set permissions and POSIX ACLs on files and directories.
    """

    def __init__(self, read=False, create=False, write=False, delete=False, **kwargs):
        self.read = read
        self.create = create
        self.write = write
        self.delete = delete
        self.list = list
        self.move = kwargs.pop('move', None)
        self.execute = kwargs.pop('execute', None)
        self.manage_ownership = kwargs.pop('manage_ownership', None)
        self.manage_access_control = kwargs.pop('manage_access_control', None)
        self._str = (('r' if self.read else '') +
                     ('c' if self.create else '') +
                     ('w' if self.write else '') +
                     ('d' if self.delete else '') +
                     ('m' if self.move else '') +
                     ('e' if self.execute else '') +
                     ('o' if self.manage_ownership else '') +
                     ('p' if self.manage_access_control else ''))

    def __str__(self):
        return self._str

    @classmethod
    def from_string(cls, permission):
        """Create a FileSasPermissions from a string.

        To specify read, write, or delete permissions you need only to
        include the first letter of the word in the string. E.g. For read and
        write permissions, you would provide a string "rw".

        :param str permission: The string which dictates the read, add, create,
            write, or delete permissions.
        :return: A FileSasPermissions object
        :rtype: ~azure.storage.fildatalake.FileSasPermissions
        """
        p_read = 'r' in permission
        p_create = 'c' in permission
        p_write = 'w' in permission
        p_delete = 'd' in permission
        p_move = 'm' in permission
        p_execute = 'e' in permission
        p_manage_ownership = 'o' in permission
        p_manage_access_control = 'p' in permission

        parsed = cls(read=p_read, create=p_create, write=p_write, delete=p_delete,
                     move=p_move, execute=p_execute, manage_ownership=p_manage_ownership,
                     manage_access_control=p_manage_access_control)
        return parsed


class AccessPolicy(BlobAccessPolicy):
    """Access Policy class used by the set and get access policy methods in each service.

    A stored access policy can specify the start time, expiry time, and
    permissions for the Shared Access Signatures with which it's associated.
    Depending on how you want to control access to your resource, you can
    specify all of these parameters within the stored access policy, and omit
    them from the URL for the Shared Access Signature. Doing so permits you to
    modify the associated signature's behavior at any time, as well as to revoke
    it. Or you can specify one or more of the access policy parameters within
    the stored access policy, and the others on the URL. Finally, you can
    specify all of the parameters on the URL. In this case, you can use the
    stored access policy to revoke the signature, but not to modify its behavior.

    Together the Shared Access Signature and the stored access policy must
    include all fields required to authenticate the signature. If any required
    fields are missing, the request will fail. Likewise, if a field is specified
    both in the Shared Access Signature URL and in the stored access policy, the
    request will fail with status code 400 (Bad Request).

    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.datalake.FileSystemSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :keyword start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :paramtype start: ~datetime.datetime or str
    """

    def __init__(self, permission=None, expiry=None, **kwargs):
        super(AccessPolicy, self).__init__(
            permission=permission, expiry=expiry, start=kwargs.pop('start', None)
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

    @classmethod
    def _from_generated(cls, generated):
        delegation_key = cls()
        delegation_key.signed_oid = generated.signed_oid
        delegation_key.signed_tid = generated.signed_tid
        delegation_key.signed_start = generated.signed_start
        delegation_key.signed_expiry = generated.signed_expiry
        delegation_key.signed_service = generated.signed_service
        delegation_key.signed_version = generated.signed_version
        delegation_key.value = generated.value
        return delegation_key


class PublicAccess(str, Enum):
    """
    Specifies whether data in the file system may be accessed publicly and the level of access.
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

        return None


class LocationMode(object):
    """
    Specifies the location the request should be sent to. This mode only applies
    for RA-GRS accounts which allow secondary read access. All other account types
    must use PRIMARY.
    """

    PRIMARY = 'primary'  #: Requests should be sent to the primary location.
    SECONDARY = 'secondary'  #: Requests should be sent to the secondary location, if possible.


class DelimitedJsonDialect(BlobDelimitedJSON):
    """Defines the input or output JSON serialization for a datalake query.

    :keyword str delimiter: The line separator character, default value is '\n'
    """


class DelimitedTextDialect(BlobDelimitedTextDialect):
    """Defines the input or output delimited (CSV) serialization for a datalake query request.

    :keyword str delimiter:
        Column separator, defaults to ','.
    :keyword str quotechar:
        Field quote, defaults to '"'.
    :keyword str lineterminator:
        Record separator, defaults to '\n'.
    :keyword str escapechar:
        Escape char, defaults to empty.
    :keyword bool has_header:
        Whether the blob data includes headers in the first line. The default value is False, meaning that the
        data will be returned inclusive of the first line. If set to True, the data will be returned exclusive
        of the first line.
    """


class ArrowDialect(BlobArrowDialect):
    """field of an arrow schema.

    All required parameters must be populated in order to send to Azure.

    :param str type: Required.
    :keyword str name: The name of the field.
    :keyword int precision: The precision of the field.
    :keyword int scale: The scale of the field.
    """


class ArrowType(str, Enum):

    INT64 = "int64"
    BOOL = "bool"
    TIMESTAMP_MS = "timestamp[ms]"
    STRING = "string"
    DOUBLE = "double"
    DECIMAL = 'decimal'


class DataLakeFileQueryError(object):
    """The error happened during quick query operation.

    :ivar str error:
        The name of the error.
    :ivar bool is_fatal:
        If true, this error prevents further query processing. More result data may be returned,
        but there is no guarantee that all of the original data will be processed.
        If false, this error does not prevent further query processing.
    :ivar str description:
        A description of the error.
    :ivar int position:
        The blob offset at which the error occurred.
    """

    def __init__(self, error=None, is_fatal=False, description=None, position=None):
        self.error = error
        self.is_fatal = is_fatal
        self.description = description
        self.position = position


class AccessControlChangeCounters(DictMixin):
    """
    AccessControlChangeCounters contains counts of operations that change Access Control Lists recursively.

    :ivar int directories_successful:
        Number of directories where Access Control List has been updated successfully.
    :ivar int files_successful:
        Number of files where Access Control List has been updated successfully.
    :ivar int failure_count:
        Number of paths where Access Control List update has failed.
    """

    def __init__(self, directories_successful, files_successful, failure_count):
        self.directories_successful = directories_successful
        self.files_successful = files_successful
        self.failure_count = failure_count


class AccessControlChangeResult(DictMixin):
    """
    AccessControlChangeResult contains result of operations that change Access Control Lists recursively.

    :ivar ~azure.storage.filedatalake.AccessControlChangeCounters counters:
        Contains counts of paths changed from start of the operation.
    :ivar str continuation:
        Optional continuation token.
        Value is present when operation is split into multiple batches and can be used to resume progress.
    """

    def __init__(self, counters, continuation):
        self.counters = counters
        self.continuation = continuation


class AccessControlChangeFailure(DictMixin):
    """
    Represents an entry that failed to update Access Control List.

    :ivar str name:
        Name of the entry.
    :ivar bool is_directory:
        Indicates whether the entry is a directory.
    :ivar str error_message:
        Indicates the reason why the entry failed to update.
    """

    def __init__(self, name, is_directory, error_message):
        self.name = name
        self.is_directory = is_directory
        self.error_message = error_message


class AccessControlChanges(DictMixin):
    """
    AccessControlChanges contains batch and cumulative counts of operations
    that change Access Control Lists recursively.
    Additionally it exposes path entries that failed to update while these operations progress.

    :ivar ~azure.storage.filedatalake.AccessControlChangeCounters batch_counters:
        Contains counts of paths changed within single batch.
    :ivar ~azure.storage.filedatalake.AccessControlChangeCounters aggregate_counters:
        Contains counts of paths changed from start of the operation.
    :ivar list(~azure.storage.filedatalake.AccessControlChangeFailure) batch_failures:
        List of path entries that failed to update Access Control List within single batch.
    :ivar str continuation:
        An opaque continuation token that may be used to resume the operations in case of failures.
    """

    def __init__(self, batch_counters, aggregate_counters, batch_failures, continuation):
        self.batch_counters = batch_counters
        self.aggregate_counters = aggregate_counters
        self.batch_failures = batch_failures
        self.continuation = continuation
