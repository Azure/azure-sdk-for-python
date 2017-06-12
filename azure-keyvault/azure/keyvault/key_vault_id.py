#---------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#---------------------------------------------------------------------------------------------

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse # pylint: disable=import-error

class KeyVaultId(object):
    """ An identifier for an Azure Key Vault resource. """

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
        self.version = version
        self.base_id = '{}/{}/{}'.format(vault, collection, name)
        self.id = '{}/{}'.format(self.base_id, version) if version else self.base_id

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
    _parse_uri_argument(vault) # check that vault is a valid URI but don't change it
    return KeyVaultId(collection, vault, name, version)

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
    segments = list(filter(None, parsed_uri.path.split('/'))) # eliminate empty segments
    
    num_coll_segs = len(collection.split('/'))
    num_segments = len(segments)
    name_index = num_coll_segs
    version_index = name_index + 1
    min_segments = num_coll_segs + 1 # must have collection and name at minimum
    max_segments = min_segments + 1 # may also have version

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
    return create_object_id('keys', vault, name, version)

def parse_key_id(id):
    """
    :param id: The key uri.
    :type id: str
    :rtype: KeyVaultId
    """
    return parse_object_id('keys', id)

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
    return create_object_id('secrets', vault, name, version)

def parse_secret_id(id):
    """
    :param id: The secret uri.
    :type id: str
    :rtype: KeyVaultId
    """
    return parse_object_id('secrets', id)

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
    return create_object_id('certificates', vault, name, version)

def parse_certificate_id(id):
    """
    :param id: The resource collection type.
    :type id: str
    :rtype: KeyVaultId
    """
    return parse_object_id('certificates', id)

def create_certificate_operation_id(vault, name):
    """
    :param vault: The vault uri.
    :type vault: str
    :param name: The certificate name.
    :type name: str
    :rtype: KeyVaultId
    """
    obj_id = create_object_id('certificates', vault, name, 'pending')
    obj_id.base_id = obj_id.id
    obj_id.version = None
    return obj_id

def parse_certificate_operation_id(id):
    """
    :param id: The resource collection type.
    :type id: str
    :rtype: KeyVaultId
    """
    obj_id = parse_object_id('certificates', id)
    obj_id.base_id = obj_id.id
    obj_id.version = None
    return obj_id

def create_certificate_issuer_id(vault, name):
    """
    :param vault: The vault uri.
    :type vault: str
    :param name: The certificate name.
    :type name: str
    :rtype: KeyVaultId
    """
    return create_object_id('certificates/issuers', vault, name, None)

def parse_certificate_issuer_id(id):
    """
    :param id: The resource collection type.
    :type id: str
    :rtype: KeyVaultId
    """
    return parse_object_id('certificates/issuers', id)
