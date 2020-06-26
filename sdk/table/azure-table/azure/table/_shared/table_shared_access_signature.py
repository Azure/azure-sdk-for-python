# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.storage.common.sharedaccesssignature import _QueryStringConstants
from azure.table._shared._common_conversion import _sign_string
from azure.table._shared.constants import X_MS_VERSION
from azure.table._shared.shared_access_signature import _SharedAccessHelper, SharedAccessSignature


def generate_table_sas(
        account_name,
        account_key,
        table_name,
        permission=None,
        expiry=None,
        start=None,
        i_d=None,
        ip=None,
        protocol=None,
        start_pk=None,
        start_rk=None,
        end_pk=None,
        end_rk=None
):  # type: (...) -> str

    sas = TableSharedAccessSignature(account_name, account_key)
    return sas.generate_table(
        table_name=table_name,
        permission=permission,
        expiry=expiry,
        start=start,
        i_d=i_d,
        ip=ip,
        protocol=protocol,
        start_pk=start_pk,
        start_rk=start_rk,
        end_pk=end_pk,
        end_rk=end_rk
    )  # type: ignore


class TableSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating file and share access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key):
        """
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        """
        super(TableSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)

    def generate_table(self, table_name, permission=None,
                       expiry=None, start=None, i_d=None,
                       ip=None, protocol=None,
                       start_pk=None, start_rk=None,
                       end_pk=None, end_rk=None):
        """
        Generates a shared access signature for the table.
        Use the returned signature with the sas_token parameter of TableService.

        :param str table_name:
            Name of table.
        :param TablePermissions permission:
            The permissions associated with the shared access signature. The
            user is restricted to operations allowed by the permissions.
            Required unless an id is given referencing a stored access policy
            which contains this field. This field must be omitted if it has been
            specified in an associated stored access policy.
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
        :param str id:
            A unique value up to 64 characters in length that correlates to a
            stored access policy. To create a stored access policy, use
            set_table_service_properties.
        :param str ip:
            Specifies an IP address or a range of IP addresses from which to accept requests.
            If the IP address from which the request originates does not match the IP address
            or address range specified on the SAS token, the request is not authenticated.
            For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
            restricts the request to those IP addresses.
        :param str protocol:
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.cosmosdb.table.common.models.Protocol` for possible values.
        :param str start_pk:
            The minimum partition key accessible with this shared access
            signature. startpk must accompany startrk. Key values are inclusive.
            If omitted, there is no lower bound on the table entities that can
            be accessed.
        :param str start_rk:
            The minimum row key accessible with this shared access signature.
            startpk must accompany startrk. Key values are inclusive. If
            omitted, there is no lower bound on the table entities that can be
            accessed.
        :param str end_pk:
            The maximum partition key accessible with this shared access
            signature. endpk must accompany endrk. Key values are inclusive. If
            omitted, there is no upper bound on the table entities that can be
            accessed.
        :param str end_rk:
            The maximum row key accessible with this shared access signature.
            endpk must accompany endrk. Key values are inclusive. If omitted,
            there is no upper bound on the table entities that can be accessed.
        """
        sas = _TableSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, X_MS_VERSION)
        sas.add_id(i_d)
        sas.add_table_access_ranges(table_name, start_pk, start_rk, end_pk, end_rk)

        # Table names must be signed lower case
        resource_path = table_name.lower()
        sas.add_resource_signature(self.account_name, self.account_key, 'table', resource_path)

        return sas.get_token()


class _TableQueryStringConstants(_QueryStringConstants):
    TABLE_NAME = 'tn'


class _TableSharedAccessHelper(_SharedAccessHelper):

    def __init__(self):
        super().__init__()
        self.query_dict = {}

    def add_table_access_ranges(self, table_name, start_pk, start_rk,
                                end_pk, end_rk):
        self._add_query(_TableQueryStringConstants.TABLE_NAME, table_name)
        self._add_query(_TableQueryStringConstants.START_PK, start_pk)
        self._add_query(_TableQueryStringConstants.START_RK, start_rk)
        self._add_query(_TableQueryStringConstants.END_PK, end_pk)
        self._add_query(_TableQueryStringConstants.END_RK, end_rk)

    def add_resource_signature(self, account_name, account_key, service, path):
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ''
            return return_value + '\n'

        if path[0] != '/':
            path = '/' + path

        canonicalized_resource = '/' + service + '/' + account_name + path + '\n'

        # Form the string to sign from shared_access_policy and canonicalized
        # resource. The order of values is important.
        string_to_sign = \
            (get_value_to_append(_QueryStringConstants.SIGNED_PERMISSION) +
             get_value_to_append(_QueryStringConstants.SIGNED_START) +
             get_value_to_append(_QueryStringConstants.SIGNED_EXPIRY) +
             canonicalized_resource +
             get_value_to_append(_QueryStringConstants.SIGNED_IDENTIFIER) +
             get_value_to_append(_QueryStringConstants.SIGNED_IP) +
             get_value_to_append(_QueryStringConstants.SIGNED_PROTOCOL) +
             get_value_to_append(_QueryStringConstants.SIGNED_VERSION))

        string_to_sign += \
            (get_value_to_append(_QueryStringConstants.START_PK) +
             get_value_to_append(_QueryStringConstants.START_RK) +
             get_value_to_append(_QueryStringConstants.END_PK) +
             get_value_to_append(_QueryStringConstants.END_RK))

        # remove the trailing newline
        if string_to_sign[-1] == '\n':
            string_to_sign = string_to_sign[:-1]

        self._add_query(_QueryStringConstants.SIGNED_SIGNATURE,
                        _sign_string(account_key, string_to_sign))
