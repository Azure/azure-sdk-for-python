# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime
from typing import Optional, Union
from azure.core.credentials import AzureNamedKeyCredential

from ._models import AccountSasPermissions, TableSasPermissions, ResourceTypes, SASProtocol
from ._common_conversion import _sign_string
from ._error import _validate_not_none
from ._constants import X_MS_VERSION
from ._shared_access_signature import (
    _SharedAccessHelper,
    SharedAccessSignature,
    QueryStringConstants,
)


def generate_account_sas(
    credential: AzureNamedKeyCredential,
    resource_types: ResourceTypes,
    permission: Union[str, AccountSasPermissions],
    expiry: Union[datetime, str],
    *,
    start: Optional[Union[datetime, str]] = None,
    ip_address_or_range: Optional[str] = None,
    protocol: Optional[Union[SASProtocol, str]] = None,
) -> str:
    """
    Generates a shared access signature for the table service.
    Use the returned signature with the sas_token parameter of TableService.

    :param credential: Credential for the Azure account
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    :param resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :type resource_types: ResourceTypes
    :param permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :type permission: str or AccountSasPermissions
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
    :paramtype start: ~datetime.datetime or str or None
    :keyword ip_address_or_range:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :paramtype ip_address_or_range: str or None
    :keyword protocol:
        Specifies the protocol permitted for a request made.
    :paramtype protocol: str or ~azure.data.tables.SASProtocol or None
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    _validate_not_none("account_name", credential.named_key.name)
    _validate_not_none("account_key", credential.named_key.key)
    if isinstance(permission, str):
        permission = AccountSasPermissions.from_string(permission=permission)
    sas = TableSharedAccessSignature(credential)
    return sas.generate_account(
        "t",
        resource_types,
        permission,
        expiry,
        start=start,
        ip_address_or_range=ip_address_or_range,
        protocol=protocol,
    )


def generate_table_sas(
    credential: AzureNamedKeyCredential,
    table_name: str,
    *,
    permission: Optional[Union[TableSasPermissions, str]] = None,
    expiry: Optional[Union[datetime, str]] = None,
    start: Optional[Union[datetime, str]] = None,
    ip_address_or_range: Optional[str] = None,
    policy_id: Optional[str] = None,
    protocol: Optional[Union[SASProtocol, str]] = None,
    start_pk: Optional[str] = None,
    start_rk: Optional[str] = None,
    end_pk: Optional[str] = None,
    end_rk: Optional[str] = None,
) -> str:
    """
    Generates a shared access signature for the table service.
    Use the returned signature with the sas_token parameter of TableService.


    :param credential: Credential used for creating Shared Access Signature
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    :param table_name: Table name
    :type table_name: str
    :keyword permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has been
        specified in an associated stored access policy.
    :paramtype permission: ~azure.data.tables.TableSasPermissions or str or None
    :keyword expiry:
        The time at which the shared access signature becomes invalid.
        Required unless an id is given referencing a stored access policy
        which contains this field. This field must be omitted if it has
        been specified in an associated stored access policy. Azure will always
        convert values to UTC. If a date is passed in without timezone info, it
        is assumed to be UTC.
    :paramtype expiry: ~datetime.datetime or str or None
    :keyword start:
        The time at which the shared access signature becomes valid. If
        omitted, start time for this call is assumed to be the time when the
        storage service receives the request. Azure will always convert values
        to UTC. If a date is passed in without timezone info, it is assumed to
        be UTC.
    :paramtype start: ~datetime.datetime or str or None
    :keyword ip_address_or_range:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :paramtype ip_address_or_range: str or None
    :keyword policy_id: Access policy ID.
    :paramtype policy_id: str or None
    :keyword protocol:
        Specifies the protocol permitted for a request made.
    :paramtype protocol: str or ~azure.data.tables.SASProtocol or None
    :keyword start_rk: Starting row key.
    :paramtype start_rk: str or None
    :keyword start_pk: Starting partition key.
    :paramtype start_pk: str or None
    :keyword end_rk: End row key.
    :paramtype end_rk: str or None
    :keyword end_pk: End partition key.
    :paramtype end_pk: str or None
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """

    sas = TableSharedAccessSignature(credential)
    return sas.generate_table(
        table_name=table_name,
        permission=permission,
        expiry=expiry,
        start=start,
        policy_id=policy_id,
        ip_address_or_range=ip_address_or_range,
        protocol=protocol,
        start_pk=start_pk,
        start_rk=start_rk,
        end_pk=end_pk,
        end_rk=end_rk,
    )


class TableSharedAccessSignature(SharedAccessSignature):
    """
    Provides a factory for creating file and share access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.

    :param credential: The credential used for authenticating requests.
    :type credential: ~azure.core.credentials.AzureNamedKeyCredential
    """

    def __init__(self, credential: AzureNamedKeyCredential):
        super(TableSharedAccessSignature, self).__init__(credential, x_ms_version=X_MS_VERSION)

    def generate_table(
        self,
        table_name,
        permission: Optional[Union[TableSasPermissions, str]] = None,
        expiry: Optional[Union[datetime, str]] = None,
        start: Optional[Union[datetime, str]] = None,
        policy_id: Optional[str] = None,
        ip_address_or_range: Optional[str] = None,
        protocol: Optional[Union[str, SASProtocol]] = None,
        start_pk: Optional[str] = None,
        start_rk: Optional[str] = None,
        end_pk: Optional[str] = None,
        end_rk: Optional[str] = None,
    ) -> str:
        """
        Generates a shared access signature for the table.
        Use the returned signature with the sas_token parameter of TableService.

        :param str table_name:
            Name of table.
        :param permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
        :type permission: ~azure.data.table.TableSasPermissions or str or None
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
            storage service receives the request. Azure will always convert values
            to UTC. If a date is passed in without timezone info, it is assumed to
            be UTC.
        :type start: ~datetime.datetime or str or None
        :param policy_id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_table_service_properties.
        :type policy_id: str or None
        :param ip_address_or_range:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :type ip_address_or_range: str or None
        :param protocol:
            Specifies the protocol permitted for a request made.
            See :class:`~azure.data.tables.SASProtocol` for possible values.
        :type protocol: str or ~azure.data.tables.SASProtocol or None
        :param start_pk:
            The minimum partition key accessible with this shared access
            signature. startpk must accompany start_rk. Key values are inclusive.
            If omitted, there is no lower bound on the table entities that can
            be accessed.
        :type start_pk: str or None
        :param start_rk:
            The minimum row key accessible with this shared access signature.
            startpk must accompany start_rk. Key values are inclusive. If
            omitted, there is no lower bound on the table entities that can be
            accessed.
        :type start_rk: str or None
        :param end_pk:
            The maximum partition key accessible with this shared access
            signature. end_pk must accompany end_rk. Key values are inclusive. If
            omitted, there is no upper bound on the table entities that can be
            accessed.
        :type end_pk: str or None
        :param end_rk:
            The maximum row key accessible with this shared access signature.
            end_pk must accompany end_rk. Key values are inclusive. If omitted,
            there is no upper bound on the table entities that can be accessed.
        :type end_rk: str or None
        :return: A shared access signature for the table.
        :rtype: str
        """
        sas = _TableSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip_address_or_range, protocol, X_MS_VERSION)
        sas.add_id(policy_id)
        sas.add_table_access_ranges(table_name, start_pk, start_rk, end_pk, end_rk)

        # Table names must be signed lower case
        resource_path = table_name.lower()
        sas.add_resource_signature(self.account_name, self.account_key, "table", resource_path)

        return sas.get_token()


class _TableQueryStringConstants(QueryStringConstants):
    TABLE_NAME = "tn"


class _TableSharedAccessHelper(_SharedAccessHelper):
    def __init__(self):
        super(_TableSharedAccessHelper, self).__init__()
        self.query_dict = {}

    def add_table_access_ranges(self, table_name, start_pk, start_rk, end_pk, end_rk):
        self._add_query(_TableQueryStringConstants.TABLE_NAME, table_name)
        self._add_query(_TableQueryStringConstants.START_PK, start_pk)
        self._add_query(_TableQueryStringConstants.START_RK, start_rk)
        self._add_query(_TableQueryStringConstants.END_PK, end_pk)
        self._add_query(_TableQueryStringConstants.END_RK, end_rk)

    def add_resource_signature(self, account_name, account_key, service, path):
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ""
            return return_value + "\n"

        if path[0] != "/":
            path = "/" + path

        canonicalized_resource = "/" + service + "/" + account_name + path + "\n"

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = (
            get_value_to_append(QueryStringConstants.SIGNED_PERMISSION)
            + get_value_to_append(QueryStringConstants.SIGNED_START)
            + get_value_to_append(QueryStringConstants.SIGNED_EXPIRY)
            + canonicalized_resource
            + get_value_to_append(QueryStringConstants.SIGNED_IDENTIFIER)
            + get_value_to_append(QueryStringConstants.SIGNED_IP)
            + get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL)
            + get_value_to_append(QueryStringConstants.SIGNED_VERSION)
        )

        string_to_sign += (
            get_value_to_append(QueryStringConstants.START_PK)
            + get_value_to_append(QueryStringConstants.START_RK)
            + get_value_to_append(QueryStringConstants.END_PK)
            + get_value_to_append(QueryStringConstants.END_RK)
        )

        # remove the trailing newline
        if string_to_sign[-1] == "\n":
            string_to_sign = string_to_sign[:-1]

        self._add_query(
            QueryStringConstants.SIGNED_SIGNATURE,
            _sign_string(account_key, string_to_sign),
        )
