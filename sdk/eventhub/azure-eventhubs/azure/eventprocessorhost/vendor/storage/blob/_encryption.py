# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from json import (
    dumps,
    loads,
)
from os import urandom

from cryptography.hazmat.primitives.padding import PKCS7

from ..common._encryption import (
    _generate_encryption_data_dict,
    _generate_AES_CBC_cipher,
    _dict_to_encryption_data,
    _validate_and_unwrap_cek,
    _EncryptionAlgorithm,
)
from ..common._error import (
    _validate_not_none,
    _validate_key_encryption_key_wrap,
    _ERROR_DATA_NOT_ENCRYPTED,
    _ERROR_UNSUPPORTED_ENCRYPTION_ALGORITHM,
)


def _encrypt_blob(blob, key_encryption_key):
    '''
    Encrypts the given blob using AES256 in CBC mode with 128 bit padding.
    Wraps the generated content-encryption-key using the user-provided key-encryption-key (kek). 
    Returns a json-formatted string containing the encryption metadata. This method should
    only be used when a blob is small enough for single shot upload. Encrypting larger blobs
    is done as a part of the _upload_blob_chunks method.

    :param bytes blob:
        The blob to be encrypted.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        wrap_key(key)--wraps the specified key using an algorithm of the user's choice.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
    :return: A tuple of json-formatted string containing the encryption metadata and the encrypted blob data.
    :rtype: (str, bytes)
    '''

    _validate_not_none('blob', blob)
    _validate_not_none('key_encryption_key', key_encryption_key)
    _validate_key_encryption_key_wrap(key_encryption_key)

    # AES256 uses 256 bit (32 byte) keys and always with 16 byte blocks
    content_encryption_key = urandom(32)
    initialization_vector = urandom(16)

    cipher = _generate_AES_CBC_cipher(content_encryption_key, initialization_vector)

    # PKCS7 with 16 byte blocks ensures compatibility with AES.
    padder = PKCS7(128).padder()
    padded_data = padder.update(blob) + padder.finalize()

    # Encrypt the data.
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    encryption_data = _generate_encryption_data_dict(key_encryption_key, content_encryption_key,
                                                     initialization_vector)
    encryption_data['EncryptionMode'] = 'FullBlob'

    return dumps(encryption_data), encrypted_data


def _generate_blob_encryption_data(key_encryption_key):
    '''
    Generates the encryption_metadata for the blob.
    
    :param bytes key_encryption_key:
        The key-encryption-key used to wrap the cek associate with this blob.
    :return: A tuple containing the cek and iv for this blob as well as the 
        serialized encryption metadata for the blob.
    :rtype: (bytes, bytes, str)
    '''
    encryption_data = None
    content_encryption_key = None
    initialization_vector = None
    if key_encryption_key:
        _validate_key_encryption_key_wrap(key_encryption_key)
        content_encryption_key = urandom(32)
        initialization_vector = urandom(16)
        encryption_data = _generate_encryption_data_dict(key_encryption_key,
                                                         content_encryption_key,
                                                         initialization_vector)
        encryption_data['EncryptionMode'] = 'FullBlob'
        encryption_data = dumps(encryption_data)

    return content_encryption_key, initialization_vector, encryption_data


def _decrypt_blob(require_encryption, key_encryption_key, key_resolver,
                  response, start_offset, end_offset):
    '''
    Decrypts the given blob contents and returns only the requested range.
    
    :param bool require_encryption:
        Whether or not the calling blob service requires objects to be decrypted.
    :param object key_encryption_key:
        The user-provided key-encryption-key. Must implement the following methods:
        wrap_key(key)--wraps the specified key using an algorithm of the user's choice.
        get_key_wrap_algorithm()--returns the algorithm used to wrap the specified symmetric key.
        get_kid()--returns a string key id for this key-encryption-key.
    :param key_resolver(kid):
        The user-provided key resolver. Uses the kid string to return a key-encryption-key 
        implementing the interface defined above.
    :return: The decrypted blob content.
    :rtype: bytes
    '''
    _validate_not_none('response', response)
    content = response.body
    _validate_not_none('content', content)

    try:
        encryption_data = _dict_to_encryption_data(loads(response.headers['x-ms-meta-encryptiondata']))
    except:
        if require_encryption:
            raise ValueError(_ERROR_DATA_NOT_ENCRYPTED)
        else:
            return content

    if not (encryption_data.encryption_agent.encryption_algorithm == _EncryptionAlgorithm.AES_CBC_256):
        raise ValueError(_ERROR_UNSUPPORTED_ENCRYPTION_ALGORITHM)

    blob_type = response.headers['x-ms-blob-type']

    iv = None
    unpad = False
    start_range, end_range = 0, len(content)
    if 'content-range' in response.headers:
        content_range = response.headers['content-range']
        # Format: 'bytes x-y/size'

        # Ignore the word 'bytes'
        content_range = content_range.split(' ')

        content_range = content_range[1].split('-')
        start_range = int(content_range[0])
        content_range = content_range[1].split('/')
        end_range = int(content_range[0])
        blob_size = int(content_range[1])

        if start_offset >= 16:
            iv = content[:16]
            content = content[16:]
            start_offset -= 16
        else:
            iv = encryption_data.content_encryption_IV

        if end_range == blob_size - 1:
            unpad = True
    else:
        unpad = True
        iv = encryption_data.content_encryption_IV

    if blob_type == 'PageBlob':
        unpad = False

    content_encryption_key = _validate_and_unwrap_cek(encryption_data, key_encryption_key, key_resolver)
    cipher = _generate_AES_CBC_cipher(content_encryption_key, iv)
    decryptor = cipher.decryptor()

    content = decryptor.update(content) + decryptor.finalize()
    if unpad:
        unpadder = PKCS7(128).unpadder()
        content = unpadder.update(content) + unpadder.finalize()

    return content[start_offset: len(content) - end_offset]


def _get_blob_encryptor_and_padder(cek, iv, should_pad):
    encryptor = None
    padder = None

    if cek is not None and iv is not None:
        cipher = _generate_AES_CBC_cipher(cek, iv)
        encryptor = cipher.encryptor()
        padder = PKCS7(128).padder() if should_pad else None

    return encryptor, padder
