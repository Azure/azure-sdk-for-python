# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import OrderedDict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC

from ._common_conversion import (
    _encode_base64,
    _decode_base64_to_bytes,
)
from ._constants import (
    _ENCRYPTION_PROTOCOL_V1,
    __version__,
)
from ._error import (
    _ERROR_UNSUPPORTED_ENCRYPTION_VERSION,
    _validate_not_none,
    _validate_encryption_protocol_version,
    _validate_key_encryption_key_unwrap,
    _validate_kek_id,
)


class _EncryptionAlgorithm(object):
    '''
    Specifies which client encryption algorithm is used.
    '''
    AES_CBC_256 = 'AES_CBC_256'


class _WrappedContentKey:
    '''
    Represents the envelope key details stored on the service.
    '''

    def __init__(self, algorithm, encrypted_key, key_id):
        '''
        :param str algorithm:
            The algorithm used for wrapping.
        :param bytes encrypted_key:
            The encrypted content-encryption-key.
        :param str key_id:
            The key-encryption-key identifier string.
        '''

        _validate_not_none('algorithm', algorithm)
        _validate_not_none('encrypted_key', encrypted_key)
        _validate_not_none('key_id', key_id)

        self.algorithm = algorithm
        self.encrypted_key = encrypted_key
        self.key_id = key_id


class _EncryptionAgent:
    '''
    Represents the encryption agent stored on the service.
    It consists of the encryption protocol version and encryption algorithm used.
    '''

    def __init__(self, encryption_algorithm, protocol):
        '''
        :param _EncryptionAlgorithm encryption_algorithm:
            The algorithm used for encrypting the message contents.
        :param str protocol:
            The protocol version used for encryption.
        '''

        _validate_not_none('encryption_algorithm', encryption_algorithm)
        _validate_not_none('protocol', protocol)

        self.encryption_algorithm = str(encryption_algorithm)
        self.protocol = protocol


class _EncryptionData:
    '''
    Represents the encryption data that is stored on the service.
    '''

    def __init__(self, content_encryption_IV, encryption_agent, wrapped_content_key,
                 key_wrapping_metadata):
        '''
        :param bytes content_encryption_IV:
            The content encryption initialization vector.
        :param _EncryptionAgent encryption_agent:
            The encryption agent.
        :param _WrappedContentKey wrapped_content_key:
            An object that stores the wrapping algorithm, the key identifier, 
            and the encrypted key bytes.
        :param dict key_wrapping_metadata:
            A dict containing metadata related to the key wrapping.
        '''

        _validate_not_none('content_encryption_IV', content_encryption_IV)
        _validate_not_none('encryption_agent', encryption_agent)
        _validate_not_none('wrapped_content_key', wrapped_content_key)

        self.content_encryption_IV = content_encryption_IV
        self.encryption_agent = encryption_agent
        self.wrapped_content_key = wrapped_content_key
        self.key_wrapping_metadata = key_wrapping_metadata


def _generate_encryption_data_dict(kek, cek, iv):
    '''
    Generates and returns the encryption metadata as a dict.

    :param object kek: The key encryption key. See calling functions for more information.
    :param bytes cek: The content encryption key.
    :param bytes iv: The initialization vector.
    :return: A dict containing all the encryption metadata.
    :rtype: dict
    '''
    # Encrypt the cek.
    wrapped_cek = kek.wrap_key(cek)

    # Build the encryption_data dict.
    # Use OrderedDict to comply with Java's ordering requirement.
    wrapped_content_key = OrderedDict()
    wrapped_content_key['KeyId'] = kek.get_kid()
    wrapped_content_key['EncryptedKey'] = _encode_base64(wrapped_cek)
    wrapped_content_key['Algorithm'] = kek.get_key_wrap_algorithm()

    encryption_agent = OrderedDict()
    encryption_agent['Protocol'] = _ENCRYPTION_PROTOCOL_V1
    encryption_agent['EncryptionAlgorithm'] = _EncryptionAlgorithm.AES_CBC_256

    encryption_data_dict = OrderedDict()
    encryption_data_dict['WrappedContentKey'] = wrapped_content_key
    encryption_data_dict['EncryptionAgent'] = encryption_agent
    encryption_data_dict['ContentEncryptionIV'] = _encode_base64(iv)
    encryption_data_dict['KeyWrappingMetadata'] = {'EncryptionLibrary': 'Python ' + __version__}

    return encryption_data_dict


def _dict_to_encryption_data(encryption_data_dict):
    '''
    Converts the specified dictionary to an EncryptionData object for
    eventual use in decryption.
    
    :param dict encryption_data_dict:
        The dictionary containing the encryption data.
    :return: an _EncryptionData object built from the dictionary.
    :rtype: _EncryptionData
    '''
    try:
        if encryption_data_dict['EncryptionAgent']['Protocol'] != _ENCRYPTION_PROTOCOL_V1:
            raise ValueError(_ERROR_UNSUPPORTED_ENCRYPTION_VERSION)
    except KeyError:
        raise ValueError(_ERROR_UNSUPPORTED_ENCRYPTION_VERSION)
    wrapped_content_key = encryption_data_dict['WrappedContentKey']
    wrapped_content_key = _WrappedContentKey(wrapped_content_key['Algorithm'],
                                             _decode_base64_to_bytes(wrapped_content_key['EncryptedKey']),
                                             wrapped_content_key['KeyId'])

    encryption_agent = encryption_data_dict['EncryptionAgent']
    encryption_agent = _EncryptionAgent(encryption_agent['EncryptionAlgorithm'],
                                        encryption_agent['Protocol'])

    if 'KeyWrappingMetadata' in encryption_data_dict:
        key_wrapping_metadata = encryption_data_dict['KeyWrappingMetadata']
    else:
        key_wrapping_metadata = None

    encryption_data = _EncryptionData(_decode_base64_to_bytes(encryption_data_dict['ContentEncryptionIV']),
                                      encryption_agent,
                                      wrapped_content_key,
                                      key_wrapping_metadata)

    return encryption_data


def _generate_AES_CBC_cipher(cek, iv):
    '''
    Generates and returns an encryption cipher for AES CBC using the given cek and iv.

    :param bytes[] cek: The content encryption key for the cipher.
    :param bytes[] iv: The initialization vector for the cipher.
    :return: A cipher for encrypting in AES256 CBC.
    :rtype: ~cryptography.hazmat.primitives.ciphers.Cipher
    '''

    backend = default_backend()
    algorithm = AES(cek)
    mode = CBC(iv)
    return Cipher(algorithm, mode, backend)


def _validate_and_unwrap_cek(encryption_data, key_encryption_key=None, key_resolver=None):
    '''
    Extracts and returns the content_encryption_key stored in the encryption_data object
    and performs necessary validation on all parameters.
    :param _EncryptionData encryption_data:
        The encryption metadata of the retrieved value.
    :param obj key_encryption_key:
        The key_encryption_key used to unwrap the cek. Please refer to high-level service object
        instance variables for more details.
    :param func key_resolver:
        A function used that, given a key_id, will return a key_encryption_key. Please refer 
        to high-level service object instance variables for more details.
    :return: the content_encryption_key stored in the encryption_data object.
    :rtype: bytes[]
    '''

    _validate_not_none('content_encryption_IV', encryption_data.content_encryption_IV)
    _validate_not_none('encrypted_key', encryption_data.wrapped_content_key.encrypted_key)

    _validate_encryption_protocol_version(encryption_data.encryption_agent.protocol)

    content_encryption_key = None

    # If the resolver exists, give priority to the key it finds.
    if key_resolver is not None:
        key_encryption_key = key_resolver(encryption_data.wrapped_content_key.key_id)

    _validate_not_none('key_encryption_key', key_encryption_key)
    _validate_key_encryption_key_unwrap(key_encryption_key)
    _validate_kek_id(encryption_data.wrapped_content_key.key_id, key_encryption_key.get_kid())

    # Will throw an exception if the specified algorithm is not supported.
    content_encryption_key = key_encryption_key.unwrap_key(encryption_data.wrapped_content_key.encrypted_key,
                                                           encryption_data.wrapped_content_key.algorithm)
    _validate_not_none('content_encryption_key', content_encryption_key)

    return content_encryption_key
