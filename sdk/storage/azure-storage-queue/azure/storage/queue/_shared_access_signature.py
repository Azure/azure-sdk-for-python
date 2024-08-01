# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=docstring-keyword-should-match-keyword-only

from typing import (
    Any, Callable, Optional, Union,
    TYPE_CHECKING
)
from urllib.parse import parse_qs

from azure.storage.queue._shared import sign_string
from azure.storage.queue._shared.constants import X_MS_VERSION
from azure.storage.queue._shared.models import Services
from azure.storage.queue._shared.shared_access_signature import (
    QueryStringConstants,
    SharedAccessSignature,
    _SharedAccessHelper
)

if TYPE_CHECKING:
    from azure.storage.queue import (
        AccountSasPermissions,
        QueueSasPermissions,
        ResourceTypes
    )
    from datetime import datetime

class QueueSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating queue shares access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name: str, account_key: str) -> None:
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        '''
        super(QueueSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)

    def generate_queue(
        self, queue_name: str,
        permission: Optional[Union["QueueSasPermissions", str]] = None,
        expiry: Optional[Union["datetime", str]] = None,
        start: Optional[Union["datetime", str]] = None,
        policy_id: Optional[str] = None,
        ip: Optional[str] = None,
        protocol: Optional[str] = None,
        sts_hook: Optional[Callable[[str], None]] = None
    ) -> str:
        '''
        Generates a shared access signature for the queue.
        Use the returned signature with the sas_token parameter of QueueService.
        :param str queue_name:
            Name of queue.
        :param permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Permissions must be ordered read, add, update, process.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :type permission: ~azure.storage.queue.QueueSasPermissions or str
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
            storage service receives the request. The provided datetime will always
            be interpreted as UTC.
        :type start: ~datetime.datetime or str
        :param str policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        :param sts_hook:
            For debugging purposes only. If provided, the hook is called with the string to sign
            that was used to generate the SAS.
        :type sts_hook: Optional[Callable[[str], None]]
        :return: A Shared Access Signature (sas) token.
        :rtype: str
        '''
        sas = _QueueSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_id(policy_id)
        sas.add_resource_signature(self.account_name, self.account_key, queue_name)

        if sts_hook is not None:
            sts_hook(sas.string_to_sign)

        return sas.get_token()


class _QueueSharedAccessHelper(_SharedAccessHelper):

    def add_resource_signature(self, account_name: str, account_key: str, path: str):  # pylint: disable=arguments-differ
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ''
            return return_value + '\n'

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/queue/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (get_value_to_append(QueryStringConstants.SIGNED_PERMISSION) +
             get_value_to_append(QueryStringConstants.SIGNED_START) +
             get_value_to_append(QueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource +
             get_value_to_append(QueryStringConstants.SIGNED_IDENTIFIER) +
             get_value_to_append(QueryStringConstants.SIGNED_IP) +
             get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL) +
             get_value_to_append(QueryStringConstants.SIGNED_VERSION))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(QueryStringConstants.SIGNED_SIGNATURE,
                        sign_string(account_key, string_to_sign))
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
    services: Union[Services, str] = Services(queue=True),
    sts_hook: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> str:
    """Generates a shared access signature for the queue service.

    Use the returned signature with the credential parameter of any Queue Service.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param ~azure.storage.queue.ResourceTypes resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
    :type permission: ~azure.storage.queue.AccountSasPermissions or str
    :param expiry:
        The time at which the shared access signature becomes invalid.
        The provided datetime will always be interpreted as UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword Union[Services, str] services:
        Specifies the services that the Shared Access Signature (sas) token will be able to be utilized with.
        Will default to only this package (i.e. queue) if not provided.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword sts_hook:
        For debugging purposes only. If provided, the hook is called with the string to sign
        that was used to generate the SAS.
    :paramtype sts_hook: Optional[Callable[[str], None]]
    :return: A Shared Access Signature (sas) token.
    :rtype: str
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


def generate_queue_sas(
    account_name: str,
    queue_name: str,
    account_key: str,
    permission: Optional[Union["QueueSasPermissions", str]] = None,
    expiry: Optional[Union["datetime", str]] = None,
    start: Optional[Union["datetime", str]] = None,
    policy_id: Optional[str] = None,
    ip: Optional[str] = None,
    *,
    sts_hook: Optional[Callable[[str], None]] = None,
    **kwargs: Any
) -> str:
    """Generates a shared access signature for a queue.

    Use the returned signature with the credential parameter of any Queue Service.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str queue_name:
        The name of the queue.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless a policy_id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: ~azure.storage.queue.QueueSasPermissions or str
    :param expiry:
        The time at which the shared access signature becomes invalid.
        Required unless a policy_id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :type expiry: ~datetime.datetime or str
    :param start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. The provided datetime will always
        be interpreted as UTC.
    :type start: ~datetime.datetime or str
    :param str policy_id:
        A unique value up to 64 characters in length that correlates to a
        stored access policy. To create a stored access policy, use
        :func:`~azure.storage.queue.QueueClient.set_queue_access_policy`.
    :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip='168.1.5.65' or sip='168.1.5.60-168.1.5.70' on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :keyword sts_hook:
        For debugging purposes only. If provided, the hook is called with the string to sign
        that was used to generate the SAS.
    :paramtype sts_hook: Optional[Callable[[str], None]]
    :return: A Shared Access Signature (sas) token.
    :rtype: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/queue_samples_message.py
            :start-after: [START queue_client_sas_token]
            :end-before: [END queue_client_sas_token]
            :language: python
            :dedent: 12
            :caption: Generate a sas token.
    """
    if not policy_id:
        if not expiry:
            raise ValueError("'expiry' parameter must be provided when not using a stored access policy.")
        if not permission:
            raise ValueError("'permission' parameter must be provided when not using a stored access policy.")
    sas = QueueSharedAccessSignature(account_name, account_key)
    return sas.generate_queue(
        queue_name,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip=ip,
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
