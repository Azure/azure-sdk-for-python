# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=docstring-keyword-should-match-keyword-only

from typing import (
    Any, Callable, List, Optional, Union,
    TYPE_CHECKING
)
from urllib.parse import parse_qs

from ._shared import sign_string
from ._shared.constants import X_MS_VERSION
from ._shared.models import Services, UserDelegationKey
from ._shared.shared_access_signature import QueryStringConstants, SharedAccessSignature, _SharedAccessHelper

if TYPE_CHECKING:
    from datetime import datetime
    from azure.storage.fileshare import (
        AccountSasPermissions,
        FileSasPermissions,
        ShareSasPermissions,
        ResourceTypes
    )


class FileSharedAccessSignature(SharedAccessSignature):
    """
    Provides a factory for creating file and share access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    """

    def __init__(
        self,
        account_name: str,
        account_key: Optional[str] = None,
        user_delegation_key: Optional[UserDelegationKey] = None,
    ) -> None:
        """
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param Optional[str] account_key:
            The access key to generate the shares access signatures.
        :param Optional[~azure.storage.fileshare.models.UserDelegationKey] user_delegation_key:
            Instead of an account key, the user could pass in a user delegation key.
            A user delegation key can be obtained from the service by authenticating with an AAD identity;
            this can be accomplished by calling get_user_delegation_key on any Share service object.
        """
        super(FileSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)
        self.user_delegation_key = user_delegation_key

    def generate_file(
        self, share_name: str,
        directory_name: Optional[str] = None,
        file_name: Optional[str] = None,
        permission: Optional[Union["FileSasPermissions", str]] = None,
        expiry: Optional[Union["datetime", str]] = None,
        start: Optional[Union["datetime", str]] = None,
        policy_id: Optional[str] = None,
        ip: Optional[str] = None,
        protocol: Optional[str] = None,
        cache_control: Optional[str] = None,
        content_disposition: Optional[str] = None,
        content_encoding: Optional[str] = None,
        content_language: Optional[str] = None,
        content_type: Optional[str] = None,
        user_delegation_oid: Optional[str] = None,
        sts_hook: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Generates a shared access signature for the file.
        Use the returned signature with the sas_token parameter of FileService.

        :param str share_name:
            Name of share.
        :param Optional[str] directory_name:
            Name of directory. SAS tokens cannot be created for directories, so
            this parameter should only be present if file_name is provided.
        :param Optional[str] file_name:
            Name of file.
        :param permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered rcwd.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :type permission: str or FileSasPermissions or None
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: ~datetime.datetime or str or None
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. The provided datetime will always
            be interpreted as UTC.
        :type start: ~datetime.datetime or str or None
        :param Optional[str] policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_file_service_properties.
        :param Optional[str] ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param Optional[str] protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param Optional[str] cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param Optional[str] content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param Optional[str] content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param Optional[str] content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param Optional[str] content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :param Optional[str] user_delegation_oid:
            Specifies the Entra ID of the user that is authorized to use the resulting SAS URL.
            The resulting SAS URL must be used in conjunction with an Entra ID token that has been
            issued to the user specified in this value.
        :param sts_hook:
            For debugging purposes only. If provided, the hook is called with the string to sign
            that was used to generate the SAS.
        :type sts_hook: Optional[Callable[[str], None]]
        :returns: The generated SAS token for the account.
        :rtype: str
        """
        resource_path = share_name
        if directory_name is not None:
            resource_path += '/' + str(directory_name)
        if file_name is not None:
            resource_path += '/' + str(file_name)

        sas = _FileSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_user_delegation_oid(user_delegation_oid)
        sas.add_resource('f')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, resource_path,
                                   user_delegation_key=self.user_delegation_key)

        if sts_hook is not None:
            sts_hook(sas.string_to_sign)

        return sas.get_token()

    def generate_share(
        self, share_name: str,
        permission: Optional[Union["ShareSasPermissions", str]] = None,
        expiry: Optional[Union["datetime", str]] = None,
        start: Optional[Union["datetime", str]] = None,
        policy_id: Optional[str] = None,
        ip: Optional[str] = None,
        protocol: Optional[str] = None,
        cache_control: Optional[str] = None,
        content_disposition: Optional[str] = None,
        content_encoding: Optional[str] = None,
        content_language: Optional[str] = None,
        content_type: Optional[str] = None,
        user_delegation_oid: Optional[str] = None,
        sts_hook: Optional[Callable[[str], None]] = None,
    ) -> str:
        '''
        Generates a shared access signature for the share.
        Use the returned signature with the sas_token parameter of FileService.

        :param str share_name:
            Name of share.
        :param permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered rcwdl.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :type permission: ~azure.storage.fileshare.ShareSasPermissions or str or None
        :param expiry:
            The time at which the shared access signature becomes invalid.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has
            been specified in an associated stored access policy. Azure will always
            convert values to UTC. If a date is passed in without timezone info, it
            is assumed to be UTC.
        :type expiry: ~datetime.datetime or str or None
        :param start:
            The time at which the shared access signature becomes valid. If
            omitted, start time for this call is assumed to be the time when the
            storage service receives the request. The provided datetime will always
            be interpreted as UTC.
        :type start: ~datetime.datetime or str or None
        :param Optional[str] policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_file_service_properties.
        :param Optional[str] ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param Optional[str] protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param Optional[str] cache_control:
            Response header value for Cache-Control when resource is accessed
            using this shared access signature.
        :param Optional[str] content_disposition:
            Response header value for Content-Disposition when resource is accessed
            using this shared access signature.
        :param Optional[str] content_encoding:
            Response header value for Content-Encoding when resource is accessed
            using this shared access signature.
        :param Optional[str] content_language:
            Response header value for Content-Language when resource is accessed
            using this shared access signature.
        :param Optional[str] content_type:
            Response header value for Content-Type when resource is accessed
            using this shared access signature.
        :param Optional[str] user_delegation_oid:
            Specifies the Entra ID of the user that is authorized to use the resulting SAS URL.
            The resulting SAS URL must be used in conjunction with an Entra ID token that has been
            issued to the user specified in this value.
        :param sts_hook:
            For debugging purposes only. If provided, the hook is called with the string to sign
            that was used to generate the SAS.
        :type sts_hook: Optional[Callable[[str], None]]
        :returns: The generated SAS token for the account.
        :rtype: str
        '''
        sas = _FileSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_user_delegation_oid(user_delegation_oid)
        sas.add_resource('s')
        sas.add_override_response_headers(cache_control, content_disposition,
                                          content_encoding, content_language,
                                          content_type)
        sas.add_resource_signature(self.account_name, self.account_key, share_name,
                                   user_delegation_key=self.user_delegation_key)

        if sts_hook is not None:
            sts_hook(sas.string_to_sign)

        return sas.get_token()


class _FileSharedAccessHelper(_SharedAccessHelper):

    def add_resource_signature(self, account_name, account_key, path, user_delegation_key=None):
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ''
            return return_value + '\n'

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/file/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (get_value_to_append(QueryStringConstants.SIGNED_PERMISSION) +
             get_value_to_append(QueryStringConstants.SIGNED_START) +
             get_value_to_append(QueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource)

        if user_delegation_key is not None:
            self._add_query(QueryStringConstants.SIGNED_OID, user_delegation_key.signed_oid)
            self._add_query(QueryStringConstants.SIGNED_TID, user_delegation_key.signed_tid)
            self._add_query(QueryStringConstants.SIGNED_KEY_START, user_delegation_key.signed_start)
            self._add_query(QueryStringConstants.SIGNED_KEY_EXPIRY, user_delegation_key.signed_expiry)
            self._add_query(QueryStringConstants.SIGNED_KEY_SERVICE, user_delegation_key.signed_service)
            self._add_query(QueryStringConstants.SIGNED_KEY_VERSION, user_delegation_key.signed_version)

            string_to_sign += \
                (get_value_to_append(QueryStringConstants.SIGNED_OID) +
                 get_value_to_append(QueryStringConstants.SIGNED_TID) +
                 get_value_to_append(QueryStringConstants.SIGNED_KEY_START) +
                 get_value_to_append(QueryStringConstants.SIGNED_KEY_EXPIRY) +
                 get_value_to_append(QueryStringConstants.SIGNED_KEY_SERVICE) +
                 get_value_to_append(QueryStringConstants.SIGNED_KEY_VERSION) +
                 get_value_to_append(QueryStringConstants.SIGNED_KEY_DELEGATED_USER_TID) +
                 get_value_to_append(QueryStringConstants.SIGNED_DELEGATED_USER_OID))
        else:
            string_to_sign += get_value_to_append(QueryStringConstants.SIGNED_IDENTIFIER)

        string_to_sign += \
            (get_value_to_append(QueryStringConstants.SIGNED_IP) +
             get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL) +
             get_value_to_append(QueryStringConstants.SIGNED_VERSION) +
             get_value_to_append(QueryStringConstants.SIGNED_CACHE_CONTROL) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_DISPOSITION) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_ENCODING) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_LANGUAGE) +
             get_value_to_append(QueryStringConstants.SIGNED_CONTENT_TYPE))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(QueryStringConstants.SIGNED_SIGNATURE,
                        sign_string(account_key if user_delegation_key is None else user_delegation_key.value,
                                    string_to_sign))
        self.string_to_sign = string_to_sign


def generate_account_sas(
    account_name: str,
    account_key: str,
    resource_types: Union["ResourceTypes", str],
    permission: Union["AccountSasPermissions", str],
    expiry: Union["datetime", str],
    start: Optional[Union["datetime", str]] = None,
    ip: Optional[str] = None,
    *,
    services: Union[Services, str] = Services(fileshare=True),
    sts_hook: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> str:
    """Generates a shared access signature for the file service.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :type resource_types: ~azure.storage.fileshare.ResourceTypes or str
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
    :type permission: ~azure.storage.fileshare.AccountSasPermissions or str
    :param expiry:
        The time at which the shared access signature becomes invalid.
        The provided datetime will always be interpreted as UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str or None
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword Union[Services, str] services:
        Specifies the services that the Shared Access Signature (sas) token will be able to be utilized with.
        Will default to only this package (i.e. fileshare) if not provided.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword sts_hook:
        For debugging purposes only. If provided, the hook is called with the string to sign
        that was used to generate the SAS.
    :paramtype sts_hook: Optional[Callable[[str], None]]
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/file_samples_authentication.py
            :start-after: [START generate_sas_token]
            :end-before: [END generate_sas_token]
            :language: python
            :dedent: 8
            :caption: Generate a sas token.
    """
    sas = SharedAccessSignature(account_name, account_key)
    return sas.generate_account(
        services=services,
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        sts_hook=sts_hook,
        **kwargs
    )


def generate_share_sas(
    account_name: str,
    share_name: str,
    account_key: Optional[str] = None,
    permission: Optional[Union["ShareSasPermissions", str]] = None,
    expiry: Optional[Union["datetime", str]] = None,
    start: Optional[Union["datetime", str]] = None,
    policy_id: Optional[str] = None,
    ip: Optional[str] = None,
    *,
    user_delegation_key: Optional[UserDelegationKey] = None,
    user_delegation_oid: Optional[str] = None,
    sts_hook: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> str:
    """Generates a shared access signature for a share.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str share_name:
        The name of the share.
    :param Optional[str] account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered rcwdl.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: ~azure.storage.fileshare.ShareSasPermissions or str or None
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str or None
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str or None
    :param Optional[str] policy_id:
        A unique value up to 64 characters in length that correlates to a
        stored access policy. To create a stored access policy, use
        :func:`~azure.storage.fileshare.ShareClient.set_share_access_policy`.
    :param Optional[str] ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
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
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword ~azure.storage.fileshare.UserDelegationKey user_delegation_key:
        Instead of an account shared key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.fileshare.ShareServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :paramtype user_delegation_key: ~azure.storage.fileshare.UserDelegationKey
    :keyword str user_delegation_oid:
        Specifies the Entra ID of the user that is authorized to use the resulting SAS URL.
        The resulting SAS URL must be used in conjunction with an Entra ID token that has been
        issued to the user specified in this value.
    :keyword sts_hook:
        For debugging purposes only. If provided, the hook is called with the string to sign
        that was used to generate the SAS.
    :paramtype sts_hook: Optional[Callable[[str], None]]
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    if not policy_id:
        if not expiry:
            raise ValueError("'expiry' parameter must be provided when not using a stored access policy.")
        if not permission:
            raise ValueError("'permission' parameter must be provided when not using a stored access policy.")
    if not user_delegation_key and not account_key:
        raise ValueError("Either user_delegation_key or account_key must be provided.")
    sas = FileSharedAccessSignature(account_name, account_key=account_key, user_delegation_key=user_delegation_key)
    return sas.generate_share(
        share_name=share_name,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        user_delegation_oid=user_delegation_oid,
        sts_hook=sts_hook,
        **kwargs
    )


def generate_file_sas(
    account_name: str,
    share_name: str,
    file_path: List[str],
    account_key: Optional[str] = None,
    permission: Optional[Union["FileSasPermissions", str]] = None,
    expiry: Optional[Union["datetime", str]] = None,
    start: Optional[Union["datetime", str]] = None,
    policy_id: Optional[str] = None,
    ip: Optional[str] = None,
    *,
    user_delegation_key: Optional[UserDelegationKey] = None,
    user_delegation_oid: Optional[str] = None,
    sts_hook: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> str:
    """Generates a shared access signature for a file.

    Use the returned signature with the credential parameter of any ShareServiceClient,
    ShareClient, ShareDirectoryClient, or ShareFileClient.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str share_name:
        The name of the share.
    :param file_path:
        The file path represented as a list of path segments, including the file name.
    :type file_path: List[str]
    :param Optional[str] account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Permissions must be ordered rcwd.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: ~azure.storage.fileshare.FileSasPermissions or str or None
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str or None
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str or None
    :param Optional[str] policy_id:
        A unique value up to 64 characters in length that correlates to a
        stored access policy.
    :param Optional[str] ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
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
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword Optional[~azure.storage.fileshare.UserDelegationKey] user_delegation_key:
        Instead of an account shared key, the user could pass in a user delegation key.
        A user delegation key can be obtained from the service by authenticating with an AAD identity;
        this can be accomplished by calling :func:`~azure.storage.fileshare.ShareServiceClient.get_user_delegation_key`.
        When present, the SAS is signed with the user delegation key instead.
    :keyword str user_delegation_oid:
        Specifies the Entra ID of the user that is authorized to use the resulting SAS URL.
        The resulting SAS URL must be used in conjunction with an Entra ID token that has been
        issued to the user specified in this value.
    :keyword sts_hook:
        For debugging purposes only. If provided, the hook is called with the string to sign
        that was used to generate the SAS.
    :paramtype sts_hook: Optional[Callable[[str], None]]
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    if not policy_id:
        if not expiry:
            raise ValueError("'expiry' parameter must be provided when not using a stored access policy.")
        if not permission:
            raise ValueError("'permission' parameter must be provided when not using a stored access policy.")
    if not user_delegation_key and not account_key:
        raise ValueError("Either user_delegation_key or account_key must be provided.")
    sas = FileSharedAccessSignature(account_name, account_key=account_key, user_delegation_key=user_delegation_key)
    if len(file_path) > 1:
        dir_path = '/'.join(file_path[:-1])
    else:
        dir_path = None
    return sas.generate_file(
        share_name=share_name,
        directory_name=dir_path,
        file_name=file_path[-1],
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
        user_delegation_oid=user_delegation_oid,
        sts_hook=sts_hook,
        **kwargs
    )


def _is_credential_sastoken(credential: Any) -> bool:
    if not credential or not isinstance(credential, str):
        return False

    sas_values = QueryStringConstants.to_list()
    parsed_query = parse_qs(credential.lstrip("?"))
    if parsed_query and all(k in sas_values for k in parsed_query):
        return True
    return False
