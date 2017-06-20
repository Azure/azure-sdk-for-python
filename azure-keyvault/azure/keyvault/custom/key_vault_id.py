# ---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------------------------------------------------------------------------------

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse # pylint: disable=import-error

from enum import Enum


class KeyVaultCollectionType(Enum):
    keys = 'keys'
    secrets = 'secrets'
    certificates = 'certificates'
    certificate_issuers = 'certificates/issuers'


class KeyVaultId(object):
    """ 
    An identifier for an Azure Key Vault resource.
    """
    version_none = ''

    def __init__(self, collection, vault, name, version):
        """
        :param collection: The resource collection type.
        :type collection: str
        :param vault: The vault URI.
        :type vault: str
        :param name: The resource name.
        :type name: str
        :param version: The resource version.
        :type version: str
        """
        self.vault = vault
        self.name = name
        self.collection = collection
        self.version = version or KeyVaultId.version_none

    def __str__(self):
        """
        :return: The identifier string of the current KeyVaultId
        :rtype: str
        """
        return self.id

    @property
    def id(self):
        return '{}/{}'.format(self.base_id, self.version) if self.version != KeyVaultId.version_none else self.base_id

    @property
    def base_id(self):
        return '{}/{}/{}'.format(self.vault, self.collection, self.name)

    @staticmethod
    def create_object_id(collection, vault, name, version):
        """
        :param collection: The resource collection type.
        :type collection: str
        :param vault: The vault URI.
        :type vault: str
        :param name: The resource name.
        :type name: str
        :param version: The resource version.
        :type version: str
        :rtype: KeyVaultId
        """
        collection = _validate_string_argument(collection, 'collection')
        vault = _validate_string_argument(vault, 'vault')
        name = _validate_string_argument(name, 'name')
        version = _validate_string_argument(version, 'version', True)
        _parse_uri_argument(vault)  # check that vault is a valid URI but don't change it
        return KeyVaultIdentifier(collection=collection, vault=vault, name=name, version=version)

    @staticmethod
    def parse_object_id(collection, id):
        """
        :param collection: The resource collection type.
        :type collection: str
        :param id: The resource uri.
        :type id: str
        :rtype: KeyVaultId
        """
        collection = _validate_string_argument(collection, 'collection')
        return KeyVaultIdentifier(uri=id, collection=collection)

    @staticmethod
    def create_key_id(vault, name, version=None):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The key name.
        :type name: str
        :param version: The key version.
        :type version: str
        :rtype: KeyVaultId
        """
        return KeyId(vault=vault, name=name, version=version)

    @staticmethod
    def parse_key_id(id):
        """
        :param id: The key uri.
        :type id: str
        :rtype: KeyVaultId
        """
        return KeyId(id)

    @staticmethod
    def create_secret_id(vault, name, version=None):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The secret name.
        :type name: str
        :param version: The secret version.
        :type version: str
        :rtype: KeyVaultId
        """
        return SecretId(vault=vault, name=name, version=version)

    @staticmethod
    def parse_secret_id(id):
        """
        :param id: The secret uri.
        :type id: str
        :rtype: KeyVaultId
        """
        return SecretId(id)

    @staticmethod
    def create_certificate_id(vault, name, version=None):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The certificate name.
        :type name: str
        :param version: The certificate version.
        :type version: str
        :rtype: KeyVaultId
        """
        return CertificateId(vault=vault, name=name, verion=version)

    @staticmethod
    def parse_certificate_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        return CertificateId(id)

    @staticmethod
    def create_certificate_operation_id(vault, name):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The certificate name.
        :type name: str
        :rtype: KeyVaultId
        """
        return CertificateOperationId(vault=vault, name=name)

    @staticmethod
    def parse_certificate_operation_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        return CertificateOperationId(id)

    @staticmethod
    def create_certificate_issuer_id(vault, name):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The certificate name.
        :type name: str
        :rtype: KeyVaultId
        """
        return CertificateIssuerId(vault=vault, name=name)

    @staticmethod
    def parse_certificate_issuer_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        return CertificateIssuerId(id)


class KeyVaultIdentifier(KeyVaultId):
    _id_format = '{vault}/{collection}/{name}/{version?}'
    version_none = ''

    def __init__(self, uri=None, **kwargs):
        self.version = KeyVaultIdentifier.version_none

        for key, value in kwargs.items():
            self.__dict__[key] = value or ''

        if uri:
            self._parse(uri, kwargs)

    @property
    def id(self):
        return self._format()

    @property
    def base_id(self):
        return self._format(fmt=self._id_format.replace('/{version?}', ''))

    def _format(self, fmt=None):
        fmt = fmt or self._id_format
        segments = []

        for fmt_seg in fmt.split('/'):
            if fmt_seg.startswith('{') and fmt_seg.endswith('}'):
                fmt_seg = fmt_seg[1:-1]
                fmt_prop = fmt_seg.rstrip('?')
                seg_val = getattr(self, fmt_prop)
                if not seg_val:
                    if not fmt_seg.endswith('?'):
                        raise ValueError('invalid id: No value specified for the required segment "{}"'.format(fmt_prop))
                else:
                    segments.append(seg_val.strip('/'))
            else:
                segments.append(fmt_seg)

        return '/'.join(segments)

    def _parse(self, uri, validation_args):
        def format_error():
            ValueError('invalid id: The specified uri "{}", does to match the specified format "{}"'.format(uri, self._id_format))

        uri = _validate_string_argument(uri, 'uri')
        parsed_uri = _parse_uri_argument(uri)

        id_segs = list(filter(None, parsed_uri.path.split('/')))
        id_segs.insert(0, '{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname))

        fmt_segs = list(filter(None, self._id_format.split('/')))

        for ix in range(len(fmt_segs)):
            fmt_seg = fmt_segs[ix]
            id_seg = id_segs[ix] if ix < len(id_segs) else ''

            if fmt_seg.startswith('{') and fmt_seg.endswith('}'):
                prop = fmt_seg[1:-1]
                if not id_seg and not prop.endswith('?'):
                    raise format_error()
                prop = prop.rstrip('?')
                if prop in validation_args and validation_args[prop] and validation_args[prop] != id_seg:
                    raise ValueError('invalid id: The {} "{}" does not match the expected "{}"'.format(prop, id_seg, validation_args[prop]))
                self.__dict__[prop] = id_seg
            else:
                if not fmt_seg == id_seg:
                    raise format_error()


class KeyId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'

    def __init__(self, uri=None, vault=None, name=None, version=None):
        super(KeyId, self).__init__(uri=uri, collection='keys', vault=vault, name=name, version=version)

class SecretId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'

    def __init__(self, uri=None, vault=None, name=None, version=None):
        super(SecretId, self).__init__(uri=uri, collection='secrets', vault=vault, name=name, version=version)


class CertificateId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'

    def __init__(self, uri=None, vault=None, name=None, version=None):
        super(CertificateId, self).__init__(uri=uri, collection='certificates', vault=vault, name=name, version=version)


class CertificateOperationId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/pending'

    def __init__(self, uri=None, vault=None, name=None):
        super(CertificateOperationId, self).__init__(uri=uri, collection='certificates', vault=vault, name=name)


class CertificateIssuerId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/issuers/{name}'

    def __init__(self, uri=None, vault=None, name=None):
        super(CertificateIssuerId, self).__init__(uri=uri, collection='certificates', vault=vault, name=name)


class StorageAccountId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}'

    def __init__(self, uri=None, vault=None, name=None):
        super(StorageAccountId, self).__init__(uri=uri, collection='storage', vault=vault, name=name)


class StorageSasDefinitionId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{account_name}/sas/{sas_definition}'

    def __init__(self, uri=None, vault=None, account_name=None, sas_definition=None):
        super(StorageSasDefinitionId, self).__init__(uri=uri, collection='storage', vault=vault, account_name=account_name, sas_definition=sas_definition)


def _validate_string_argument(prop, name, nullable=False):
    try:
        prop = prop.strip()
    except AttributeError:
        if not nullable:
            raise TypeError("argument '{}' must by of type string".format(name))
    prop = prop if prop else None # force falsy types to None
    if not prop and not nullable:
        raise ValueError("argument '{}' must be specified".format(name))
    return prop


def _parse_uri_argument(uri):
    try:
        parsed_uri = parse.urlparse(uri)
    except Exception: # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid URI".format(uri))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid URI".format(uri))
    return parsed_uri

