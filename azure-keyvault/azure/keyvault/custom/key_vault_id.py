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
        return KeyVaultId(collection, vault, name, version)

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
        id = _validate_string_argument(id, 'id')

        parsed_uri = _parse_uri_argument(id)
        segments = list(filter(None, parsed_uri.path.split('/')))  # eliminate empty segments

        num_coll_segs = len(collection.split('/'))
        num_segments = len(segments)
        name_index = num_coll_segs
        version_index = name_index + 1
        min_segments = num_coll_segs + 1  # must have collection and name at minimum
        max_segments = min_segments + 1  # may also have version

        if num_segments < min_segments or num_segments > max_segments:
            raise ValueError("invalid id: {}. Bad number of segments: {}".format(id, num_segments))

        expected_collection = '/'.join(segments[0:num_coll_segs])
        if collection != expected_collection:
            raise ValueError("invalid id: {}. Collection should be {}, found {}".format(
                id, collection, expected_collection))

        vault = '{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname)
        name = segments[name_index]
        version = segments[version_index] if num_segments == max_segments else None
        return KeyVaultId(collection, vault, name, version)

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
        return KeyVaultId.create_object_id(KeyVaultCollectionType.keys.value, vault, name, version)

    @staticmethod
    def parse_key_id(id):
        """
        :param id: The key uri.
        :type id: str
        :rtype: KeyVaultId
        """
        return KeyVaultId.parse_object_id(KeyVaultCollectionType.keys.value, id)

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
        return KeyVaultId.create_object_id(KeyVaultCollectionType.secrets.value, vault, name, version)

    @staticmethod
    def parse_secret_id(id):
        """
        :param id: The secret uri.
        :type id: str
        :rtype: KeyVaultId
        """
        return KeyVaultId.parse_object_id(KeyVaultCollectionType.secrets.value, id)

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
        return KeyVaultId.create_object_id(KeyVaultCollectionType.certificates.value, vault, name, version)

    @staticmethod
    def parse_certificate_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        return KeyVaultId.parse_object_id(KeyVaultCollectionType.certificates.value, id)

    @staticmethod
    def create_certificate_operation_id(vault, name):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The certificate name.
        :type name: str
        :rtype: KeyVaultId
        """
        obj_id = KeyVaultId.create_object_id(KeyVaultCollectionType.certificates.value, vault, name, 'pending')
        return obj_id

    @staticmethod
    def parse_certificate_operation_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        obj_id = KeyVaultId.parse_object_id(KeyVaultCollectionType.certificates.value, id)
        return obj_id

    @staticmethod
    def create_certificate_issuer_id(vault, name):
        """
        :param vault: The vault uri.
        :type vault: str
        :param name: The certificate name.
        :type name: str
        :rtype: KeyVaultId
        """
        return KeyVaultId.create_object_id(KeyVaultCollectionType.certificate_issuers.value, vault, name, None)

    @staticmethod
    def parse_certificate_issuer_id(id):
        """
        :param id: The resource collection type.
        :type id: str
        :rtype: KeyVaultId
        """
        return KeyVaultId.parse_object_id(KeyVaultCollectionType.certificate_issuers.value, id)


class KeyVaultIdentifier(object):
    _id_format = '{vault}/{collection}/{name}/{version?}'
    _validation = {}
    version_none = ''

    def __init__(self, uri=None, **kwargs):
        self.version = KeyVaultIdentifier.version_none

        for key, value in self._validation.items():
            self.__dict__[key] = value

        for key, value in kwargs.items():
            self.__dict__[key] = value
        if uri:
            self._parse(uri)

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

    def _parse(self, uri):
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
                if prop in self._validation and self._validation[prop] != id_seg:
                    raise ValueError('invalid id: The {} "{}" does not match the expected "{}"'.format(prop, id_seg, self._validation[prop]))
                self.__dict__[prop] = id_seg
            else:
                if not fmt_seg == id_seg:
                    raise format_error()


    def _build(self, **kwargs):
        pass


class KeyId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'
    _validation = {'collection': 'keys'}


class SecretId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'
    _validation = {'collection': 'secrets'}


class CertificateId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/{version?}'
    _validation = {'collection': 'certificates'}


class CertificateOperationId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}/pending'
    _validation = {'collection': 'certificates'}


class CertificateIssuerId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/issuers/{name}'
    _validation = {'collection': 'certificates'}


class StorageAccountId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{name}'
    _validation = {'collection': 'storage'}


class StorageSasDefinitionId(KeyVaultIdentifier):
    _id_format = '{vault}/{collection}/{account_name}/sas/{sas_definition}'
    _validation = {'collection': 'storage'}


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

