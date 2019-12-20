# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.storage.blob import generate_account_sas as generate_blob_account_sas
from azure.storage.blob import generate_container_sas, generate_blob_sas


def generate_account_sas(
        account_name,  # type: str
        account_key,  # type: str
        resource_types,  # type: Union[ResourceTypes, str]
        permission,  # type: Union[AccountSasPermissions, str]
        expiry,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):  # type: (...) -> str
    """Generates a shared access signature for the blob service.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The access key to generate the shared access signature.
    :param resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :type resource_types: str or ~azure.storage.blob.ResourceTypes
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.AccountSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying ip=168.1.5.65 or ip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../tests/test_blob_samples_authentication.py
            :start-after: [START create_sas_token]
            :end-before: [END create_sas_token]
            :language: python
            :dedent: 8
            :caption: Generating a shared access signature.
    """
    return generate_blob_account_sas(
        account_name=account_name,
        account_key=account_key,
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs
    )


def generate_file_system_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        account_key=None,  # type: Optional[str]
        user_delegation_key=None,  # type: Optional[UserDelegationKey]
        permission=None,  # type: Optional[Union[FileSystemSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a container.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str file_system_name:
        The name of the file system.
    :param str account_key:
        The access key to generate the shared access signature. Either `account_key` or
        `user_delegation_key` must be specified.
    :param ~azure.storage.blob.UserDelegationKey user_delegation_key:
        Instead of an account key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.blob.BlobServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, write, delete, list.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.ContainerSasPermissions
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
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../tests/test_blob_samples_containers.py
            :start-after: [START generate_sas_token]
            :end-before: [END generate_sas_token]
            :language: python
            :dedent: 12
            :caption: Generating a sas token.
    """
    return generate_container_sas(
        account_name=account_name,
        container_name=file_system_name,
        account_key=account_key,
        user_delegation_key=user_delegation_key,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs)


def generate_directory_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        account_key=None,  # type: Optional[str]
        user_delegation_key=None,  # type: Optional[UserDelegationKey]
        permission=None,  # type: Optional[Union[BlobSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a blob.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str container_name:
        The name of the container.
    :param str blob_name:
        The name of the blob.
    :param str snapshot:
        An optional blob snapshot ID.
    :param str account_key:
        The access key to generate the shared access signature. Either `account_key` or
        `user_delegation_key` must be specified.
    :param ~azure.storage.blob.UserDelegationKey user_delegation_key:
        Instead of an account key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.blob.BlobServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, write, delete, list.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.BlobSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str ip:
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
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    return generate_blob_sas(
        account_name=account_name,
        container_name=file_system_name,
        blob_name=directory_name,
        account_key=account_key,
        user_delegation_key=user_delegation_key,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs)


def generate_file_sas(
        account_name,  # type: str
        file_system_name,  # type: str
        directory_name,  # type: str
        file_name,  # type: str
        account_key=None,  # type: Optional[str]
        user_delegation_key=None,  # type: Optional[UserDelegationKey]
        permission=None,  # type: Optional[Union[BlobSasPermissions, str]]
        expiry=None,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs # type: Any
    ):
    # type: (...) -> str
    """Generates a shared access signature for a blob.

    Use the returned signature with the credential parameter of any BlobServiceClient,
    ContainerClient or BlobClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str container_name:
        The name of the container.
    :param str blob_name:
        The name of the blob.
    :param str snapshot:
        An optional blob snapshot ID.
    :param str account_key:
        The access key to generate the shared access signature. Either `account_key` or
        `user_delegation_key` must be specified.
    :param ~azure.storage.blob.UserDelegationKey user_delegation_key:
        Instead of an account key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.blob.BlobServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered read, write, delete, list.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or ~azure.storage.blob.BlobSasPermissions
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :type start: ~datetime.datetime or str
    :param str ip:
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
        account_key=account_key,
        user_delegation_key=user_delegation_key,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs)
