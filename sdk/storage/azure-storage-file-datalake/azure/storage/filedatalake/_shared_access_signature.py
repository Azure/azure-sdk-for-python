# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (  # pylint: disable=unused-import
    Union, Optional, Any, TYPE_CHECKING
)

from azure.storage.blob import generate_account_sas as generate_blob_account_sas
from azure.storage.blob import generate_container_sas, generate_blob_sas
if TYPE_CHECKING:
    from datetime import datetime
    from ._models import AccountSasPermissions, FileSystemSasPermissions, FileSasPermissions, ResourceTypes, \
        UserDelegationKey


def generate_account_sas(
        account_name,  # type: str
        account_key,  # type: str
        resource_types,  # type: Union[ResourceTypes, str]
        permission,  # type: Union[AccountSasPermissions, str]
        expiry,  # type: Optional[Union[datetime, str]]
        **kwargs # type: Any
    ):  # type: (...) -> str
    """Generates a shared access signature for the DataLake service.

    Use the returned signature as the credential parameter of any DataLakeServiceClient,
    FileSystemClient, DataLakeDirectoryClient or DataLakeFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The access key to generate the shared access signature.
    :param resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :type resource_types: str or ~azure.storage.filedatalake.ResourceTypes
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.filedatalake.AccountSasPermissions
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
    :keyword str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str encryption_scope:
        Specifies the encryption scope for a request made so that all write operations will be service encrypted.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    return generate_blob_account_sas(
        account_name=account_name,
        account_key=account_key,
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        **kwargs
    )


def generate_file_system_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        credential,  # type: Union[str, UserDelegationKey]
        permission=None,  # type: Optional[Union[FileSystemSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a file system.

    Use the returned signature with the credential parameter of any DataLakeServiceClient,
    FileSystemClient, DataLakeDirectoryClient or DataLakeFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str file_system_name:
        The name of the file system.
    :param str credential:
        Credential could be either account key or user delegation key.
        If use account key is used as credential, then the credential type should be a str.
        Instead of an account key, the user could also pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished
        by calling :func:`~azure.storage.filedatalake.DataLakeServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :type credential: str or ~azure.storage.filedatalake.UserDelegationKey
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered racwdlmeop.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.filedatalake.FileSystemSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: datetime or str
    :keyword start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :paramtype start: datetime or str
    :keyword str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str cache_control:
        Response header value for Cache-Control when resource is accessed
        using this shared access signature.
    :keyword str content_disposition:
        Response header value for Content-Disposition when resource is accessed
        using this shared access signature.
    :keyword str content_encoding:
        Response header value for Content-Encoding when resource is accessed
        using this shared access signature.
    :keyword str content_language:
        Response header value for Content-Language when resource is accessed
        using this shared access signature.
    :keyword str content_type:
        Response header value for Content-Type when resource is accessed
        using this shared access signature.
    :keyword str preauthorized_agent_object_id:
        The AAD object ID of a user assumed to be authorized by the owner of the user delegation key to perform
        the action granted by the SAS token. The service will validate the SAS token and ensure that the owner of the
        user delegation key has the required permissions before granting access but no additional permission check for
        the agent object id will be performed.
    :keyword str agent_object_id:
        The AAD object ID of a user assumed to be unauthorized by the owner of the user delegation key to
        perform the action granted by the SAS token. The service will validate the SAS token and ensure that the owner
        of the user delegation key has the required permissions before granting access and the service will perform an
        additional POSIX ACL check to determine if this user is authorized to perform the requested operation.
    :keyword str correlation_id:
        The correlation id to correlate the storage audit logs with the audit logs used by the principal
        generating and distributing the SAS.
    :keyword str encryption_scope:
        Specifies the encryption scope for a request made so that all write operations will be service encrypted.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    return generate_container_sas(
        account_name=account_name,
        container_name=file_system_name,
        account_key=credential if isinstance(credential, str) else None,
        user_delegation_key=credential if not isinstance(credential, str) else None,
        permission=permission,
        expiry=expiry,
        **kwargs)


def generate_directory_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        credential,  # type: Union[str, UserDelegationKey]
        permission=None,  # type: Optional[Union[FileSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a directory.

    Use the returned signature with the credential parameter of any DataLakeServiceClient,
    FileSystemClient, DataLakeDirectoryClient or DataLakeFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str file_system_name:
        The name of the file system.
    :param str directory_name:
        The name of the directory.
    :param str credential:
        Credential could be either account key or user delegation key.
        If use account key is used as credential, then the credential type should be a str.
        Instead of an account key, the user could also pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished
        by calling :func:`~azure.storage.filedatalake.DataLakeServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :type credential: str or ~azure.storage.filedatalake.UserDelegationKey
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered racwdlmeop.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.filedatalake.FileSasPermissions
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
    :keyword str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str cache_control:
        Response header value for Cache-Control when resource is accessed
        using this shared access signature.
    :keyword str content_disposition:
        Response header value for Content-Disposition when resource is accessed
        using this shared access signature.
    :keyword str content_encoding:
        Response header value for Content-Encoding when resource is accessed
        using this shared access signature.
    :keyword str content_language:
        Response header value for Content-Language when resource is accessed
        using this shared access signature.
    :keyword str content_type:
        Response header value for Content-Type when resource is accessed
        using this shared access signature.
    :keyword str preauthorized_agent_object_id:
        The AAD object ID of a user assumed to be authorized by the owner of the user delegation key to perform
        the action granted by the SAS token. The service will validate the SAS token and ensure that the owner of the
        user delegation key has the required permissions before granting access but no additional permission check for
        the agent object id will be performed.
    :keyword str agent_object_id:
        The AAD object ID of a user assumed to be unauthorized by the owner of the user delegation key to
        perform the action granted by the SAS token. The service will validate the SAS token and ensure that the owner
        of the user delegation key has the required permissions before granting access and the service will perform an
        additional POSIX ACL check to determine if this user is authorized to perform the requested operation.
    :keyword str correlation_id:
        The correlation id to correlate the storage audit logs with the audit logs used by the principal
        generating and distributing the SAS.
    :keyword str encryption_scope:
        Specifies the encryption scope for a request made so that all write operations will be service encrypted.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    depth = len(directory_name.strip("/").split("/"))
    return generate_blob_sas(
        account_name=account_name,
        container_name=file_system_name,
        blob_name=directory_name,
        account_key=credential if isinstance(credential, str) else None,
        user_delegation_key=credential if not isinstance(credential, str) else None,
        permission=permission,
        expiry=expiry,
        sdd=depth,
        is_directory=True,
        **kwargs)


def generate_file_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        file_name,  # type: str
        credential,  # type: Union[str, UserDelegationKey]
        permission=None,  # type: Optional[Union[FileSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        **kwargs  # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a file.

    Use the returned signature with the credential parameter of any BDataLakeServiceClient,
    FileSystemClient, DataLakeDirectoryClient or DataLakeFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str file_system_name:
        The name of the file system.
    :param str directory_name:
        The name of the directory.
    :param str file_name:
        The name of the file.
    :param str credential:
        Credential could be either account key or user delegation key.
        If use account key is used as credential, then the credential type should be a str.
        Instead of an account key, the user could also pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished
        by calling :func:`~azure.storage.filedatalake.DataLakeServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :type credential: str or ~azure.storage.filedatalake.UserDelegationKey
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered racwdmeop.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.filedatalake.FileSasPermissions
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
    :keyword str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword str cache_control:
        Response header value for Cache-Control when resource is accessed
        using this shared access signature.
    :keyword str content_disposition:
        Response header value for Content-Disposition when resource is accessed
        using this shared access signature.
    :keyword str content_encoding:
        Response header value for Content-Encoding when resource is accessed
        using this shared access signature.
    :keyword str content_language:
        Response header value for Content-Language when resource is accessed
        using this shared access signature.
    :keyword str content_type:
        Response header value for Content-Type when resource is accessed
        using this shared access signature.
    :keyword str preauthorized_agent_object_id:
        The AAD object ID of a user assumed to be authorized by the owner of the user delegation key to perform
        the action granted by the SAS token. The service will validate the SAS token and ensure that the owner of the
        user delegation key has the required permissions before granting access but no additional permission check for
        the agent object id will be performed.
    :keyword str agent_object_id:
        The AAD object ID of a user assumed to be unauthorized by the owner of the user delegation key to
        perform the action granted by the SAS token. The service will validate the SAS token and ensure that the owner
        of the user delegation key has the required permissions before granting access and the service will perform an
        additional POSIX ACL check to determine if this user is authorized to perform the requested operation.
    :keyword str correlation_id:
        The correlation id to correlate the storage audit logs with the audit logs used by the principal
        generating and distributing the SAS. This can only be used when to generate sas with delegation key.
    :keyword str encryption_scope:
        Specifies the encryption scope for a request made so that all write operations will be service encrypted.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    if directory_name:
        path = directory_name.rstrip('/') + "/" + file_name
    else:
        path = file_name
    return generate_blob_sas(
        account_name=account_name,
        container_name=file_system_name,
        blob_name=path,
        account_key=credential if isinstance(credential, str) else None,
        user_delegation_key=credential if not isinstance(credential, str) else None,
        permission=permission,
        expiry=expiry,
        **kwargs)
