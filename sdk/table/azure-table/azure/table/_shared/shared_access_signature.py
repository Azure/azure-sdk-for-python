# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import date

from azure.storage.common import SharedAccessSignature
from azure.storage.common.sharedaccesssignature import _QueryStringConstants, _SharedAccessHelper
from azure.table._models import TableServices
from azure.table._shared._common_conversion import _sign_string
from azure.table._shared.encryption import _validate_not_none
from azure.table._shared.models import Services

from .parser import _str, _to_utc_datetime
from .constants import X_MS_VERSION
from . import sign_string, url_quote


def generate_table_sas(
        account_name,
        account_key,
        table_name,
        permission=None,
        expiry=None,
        start=None,
        id=None,
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
        id=id,
        ip=ip,
        protocol=protocol,
        start_pk=start_pk,
        start_rk=start_rk,
        end_pk=end_pk,
        end_rk=end_rk
    )  # type: ignore


def generate_account_sas(
        account_name,  # type: str
        account_key,  # type: str
        resource_types,  # type: Union[ResourceTypes, str]
        permission,  # type: Union[AccountSasPermissions, str]
        expiry,  # type: Optional[Union[datetime, str]]
        start=None,  # type: Optional[Union[datetime, str]]
        ip=None,  # type: Optional[str]
        **kwargs  # type: Any
):  # type: (...) -> str
    """Generates a shared access signature for the queue service.

    Use the returned signature with the credential parameter of any Queue Service.

    :param str account_name:
        The storage account name used to generate the shared access signature.
    :param str account_key:
        The account key, also called shared key or access key, to generate the shared access signature.
    :param ~azure.storage.queue.ResourceTypes resource_types:
        Specifies the resource types that are accessible with the account SAS.
    :param ~azure.storage.queue.AccountSasPermissions permission:
        The permissions associated with the shared access signature. The
        user is restricted to operations allowed by the permissions.
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
        For example, specifying sip=168.1.5.65 or sip=168.1.5.60-168.1.5.70 on the SAS
        restricts the request to those IP addresses.
    :keyword str protocol:
        Specifies the protocol permitted for a request made. The default value is https.
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    """
    sas = SharedAccessSignature(account_name, account_key)
    return sas.generate_account(
        services=TableServices(),
        resource_types=resource_types,
        permission=permission,
        expiry=expiry,
        start=start,
        ip=ip,
        **kwargs
    )  # type: ignore


class TableSharedAccessSignature(SharedAccessSignature):
    '''
    Provides a factory for creating file and share access
    signature tokens with a common account name and account key.  Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key):
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        '''
        super(TableSharedAccessSignature, self).__init__(account_name, account_key, x_ms_version=X_MS_VERSION)

    def generate_table(self, table_name, permission=None,
                       expiry=None, start=None, id=None,
                       ip=None, protocol=None,
                       start_pk=None, start_rk=None,
                       end_pk=None, end_rk=None):
        '''
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
        '''
        sas = _TableSharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, X_MS_VERSION)
        sas.add_id(id)
        sas.add_table_access_ranges(table_name, start_pk, start_rk, end_pk, end_rk)

        # Table names must be signed lower case
        resource_path = table_name.lower()
        sas.add_resource_signature(self.account_name, self.account_key, 'table', resource_path)

        return sas.get_token()


class _TableQueryStringConstants(_QueryStringConstants):
    TABLE_NAME = 'tn'


class _TableSharedAccessHelper(_SharedAccessHelper):

    def __init__(self):
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

    def generate_table_shared_access_signature(self, table_name, permission=None,
                                               expiry=None, start=None, id=None,
                                               ip=None, protocol=None,
                                               start_pk=None, start_rk=None,
                                               end_pk=None, end_rk=None):
        '''
        Generates a shared access signature for the table.
        Use the returned signature with the sas_token parameter of TableService.

        :param str table_name:
           The name of the table to create a SAS token for.
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
        stored access policy. To create a stored access policy, use :func:`~set_table_acl`.
        :param str ip:
        Specifies an IP address or a range of IP addresses from which to accept requests.
        If the IP address from which the request originates does not match the IP address
        or address range specified on the SAS token, the request is not authenticated.
        For example, specifying sip='168.1.5.65' or sip='168.1.5.60-168.1.5.70' on the SAS
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
    :return: A Shared Access Signature (sas) token.
    :rtype: str
    '''
        _validate_not_none('table_name', table_name)
        _validate_not_none('self.account_name', self.account_name)
        _validate_not_none('self.account_key', self.account_key)

        sas = TableSharedAccessSignature(self.account_name, self.account_key)
        return sas.generate_table(
            table_name,
            permission=permission,
            expiry=expiry,
            start=start,
            id=id,
            ip=ip,
            protocol=protocol,
            start_pk=start_pk,
            start_rk=start_rk,
            end_pk=end_pk,
            end_rk=end_rk,
        )


class QueryStringConstants(object):
    SIGNED_SIGNATURE = 'sig'
    SIGNED_PERMISSION = 'sp'
    SIGNED_START = 'st'
    SIGNED_EXPIRY = 'se'
    SIGNED_RESOURCE = 'sr'
    SIGNED_IDENTIFIER = 'si'
    SIGNED_IP = 'sip'
    TABLE_NAME = 'tn'
    SIGNED_PROTOCOL = 'spr'
    SIGNED_VERSION = 'sv'
    SIGNED_CACHE_CONTROL = 'rscc'
    SIGNED_CONTENT_DISPOSITION = 'rscd'
    SIGNED_CONTENT_ENCODING = 'rsce'
    SIGNED_CONTENT_LANGUAGE = 'rscl'
    SIGNED_CONTENT_TYPE = 'rsct'
    START_PK = 'spk'
    START_RK = 'srk'
    END_PK = 'epk'
    END_RK = 'erk'
    SIGNED_RESOURCE_TYPES = 'srt'
    SIGNED_SERVICES = 'ss'
    SIGNED_OID = 'skoid'
    SIGNED_TID = 'sktid'
    SIGNED_KEY_START = 'skt'
    SIGNED_KEY_EXPIRY = 'ske'
    SIGNED_KEY_SERVICE = 'sks'
    SIGNED_KEY_VERSION = 'skv'

    @staticmethod
    def to_list():
        return [
            QueryStringConstants.TABLE_NAME,
            QueryStringConstants.SIGNED_SIGNATURE,
            QueryStringConstants.SIGNED_PERMISSION,
            QueryStringConstants.SIGNED_START,
            QueryStringConstants.SIGNED_EXPIRY,
            QueryStringConstants.SIGNED_RESOURCE,
            QueryStringConstants.SIGNED_IDENTIFIER,
            QueryStringConstants.SIGNED_IP,
            QueryStringConstants.SIGNED_PROTOCOL,
            QueryStringConstants.SIGNED_VERSION,
            QueryStringConstants.SIGNED_CACHE_CONTROL,
            QueryStringConstants.SIGNED_CONTENT_DISPOSITION,
            QueryStringConstants.SIGNED_CONTENT_ENCODING,
            QueryStringConstants.SIGNED_CONTENT_LANGUAGE,
            QueryStringConstants.SIGNED_CONTENT_TYPE,
            QueryStringConstants.START_PK,
            QueryStringConstants.START_RK,
            QueryStringConstants.END_PK,
            QueryStringConstants.END_RK,
            QueryStringConstants.SIGNED_RESOURCE_TYPES,
            QueryStringConstants.SIGNED_SERVICES,
            QueryStringConstants.SIGNED_OID,
            QueryStringConstants.SIGNED_TID,
            QueryStringConstants.SIGNED_KEY_START,
            QueryStringConstants.SIGNED_KEY_EXPIRY,
            QueryStringConstants.SIGNED_KEY_SERVICE,
            QueryStringConstants.SIGNED_KEY_VERSION,
        ]


class SharedAccessSignature(object):
    '''
    Provides a factory for creating account access
    signature tokens with an account name and account key. Users can either
    use the factory or can construct the appropriate service and use the
    generate_*_shared_access_signature method directly.
    '''

    def __init__(self, account_name, account_key, x_ms_version=X_MS_VERSION):
        '''
        :param str account_name:
            The storage account name used to generate the shared access signatures.
        :param str account_key:
            The access key to generate the shares access signatures.
        :param str x_ms_version:
            The service version used to generate the shared access signatures.
        '''
        self.account_name = account_name
        self.account_key = account_key
        self.x_ms_version = x_ms_version

    def generate_account(self, services, resource_types, permission, expiry, start=None,
                         ip=None, protocol=None):
        '''
        Generates a shared access signature for the account.
        Use the returned signature with the sas_token parameter of the service
        or to create a new account object.

        :param ResourceTypes resource_types:
            Specifies the resource types that are accessible with the account
            SAS. You can combine values to provide access to more than one
            resource type.
        :param AccountSasPermissions permission:
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
            Specifies the protocol permitted for a request made. The default value
            is https,http. See :class:`~azure.storage.common.models.Protocol` for possible values.
        '''
        sas = _SharedAccessHelper()
        sas.add_base(permission, expiry, start, ip, protocol, self.x_ms_version)
        sas.add_account(services, resource_types)
        sas.add_account_signature(self.account_name, self.account_key)

        return sas.get_token()


class _SharedAccessHelper(object):
    def __init__(self):
        self.query_dict = {}

    def _add_query(self, name, val):
        if val:
            self.query_dict[name] = _str(val) if val is not None else None

    def add_base(self, permission, expiry, start, ip, protocol, x_ms_version):
        if isinstance(start, date):
            start = _to_utc_datetime(start)

        if isinstance(expiry, date):
            expiry = _to_utc_datetime(expiry)

        self._add_query(QueryStringConstants.SIGNED_START, start)
        self._add_query(QueryStringConstants.SIGNED_EXPIRY, expiry)
        self._add_query(QueryStringConstants.SIGNED_PERMISSION, permission)
        self._add_query(QueryStringConstants.SIGNED_IP, ip)
        self._add_query(QueryStringConstants.SIGNED_PROTOCOL, protocol)
        self._add_query(QueryStringConstants.SIGNED_VERSION, x_ms_version)

    def add_resource(self, resource):
        self._add_query(QueryStringConstants.SIGNED_RESOURCE, resource)

    def add_id(self, policy_id):
        self._add_query(QueryStringConstants.SIGNED_IDENTIFIER, policy_id)

    def add_account(self, services, resource_types):
        self._add_query(QueryStringConstants.SIGNED_SERVICES, services)
        self._add_query(QueryStringConstants.SIGNED_RESOURCE_TYPES, resource_types)

    def add_override_response_headers(self, cache_control,
                                      content_disposition,
                                      content_encoding,
                                      content_language,
                                      content_type):
        self._add_query(QueryStringConstants.SIGNED_CACHE_CONTROL, cache_control)
        self._add_query(QueryStringConstants.SIGNED_CONTENT_DISPOSITION, content_disposition)
        self._add_query(QueryStringConstants.SIGNED_CONTENT_ENCODING, content_encoding)
        self._add_query(QueryStringConstants.SIGNED_CONTENT_LANGUAGE, content_language)
        self._add_query(QueryStringConstants.SIGNED_CONTENT_TYPE, content_type)

    def add_account_signature(self, account_name, account_key):
        def get_value_to_append(query):
            return_value = self.query_dict.get(query) or ''
            return return_value + '\n'

        string_to_sign = \
            (account_name + '\n' +
             get_value_to_append(QueryStringConstants.SIGNED_PERMISSION) +
             get_value_to_append(QueryStringConstants.SIGNED_SERVICES) +
             get_value_to_append(QueryStringConstants.SIGNED_RESOURCE_TYPES) +
             get_value_to_append(QueryStringConstants.SIGNED_START) +
             get_value_to_append(QueryStringConstants.SIGNED_EXPIRY) +
             get_value_to_append(QueryStringConstants.SIGNED_IP) +
             get_value_to_append(QueryStringConstants.SIGNED_PROTOCOL) +
             get_value_to_append(QueryStringConstants.SIGNED_VERSION))

        self._add_query(QueryStringConstants.SIGNED_SIGNATURE,
                        sign_string(account_key, string_to_sign))

    def get_token(self):
        return '&'.join(['{0}={1}'.format(n, url_quote(v)) for n, v in self.query_dict.items() if v is not None])
