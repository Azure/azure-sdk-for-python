# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import os

from azure.keyvault.keys import KeyCurveName, KeyVaultKey
from azure.keyvault.keys.crypto import EncryptionAlgorithm, KeyWrapAlgorithm, SignatureAlgorithm
from azure.keyvault.keys.crypto._providers import get_local_cryptography_provider
import pytest

from keys import EC_KEYS, RSA_KEYS


@pytest.mark.parametrize(
    "key,algorithm,hash_function",
    (
        (EC_KEYS[KeyCurveName.p_256], SignatureAlgorithm.es256, hashlib.sha256),
        (EC_KEYS[KeyCurveName.p_256_k], SignatureAlgorithm.es256_k, hashlib.sha256),
        (EC_KEYS[KeyCurveName.p_384], SignatureAlgorithm.es384, hashlib.sha384),
        (EC_KEYS[KeyCurveName.p_521], SignatureAlgorithm.es512, hashlib.sha512),
    ),
)
def test_ec_sign_verify(key, algorithm, hash_function):
    provider = get_local_cryptography_provider(key)
    digest = hash_function(b"message").digest()
    sign_result = provider.sign(algorithm, digest)
    verify_result = provider.verify(sign_result.algorithm, digest, sign_result.signature)
    assert verify_result.is_valid


@pytest.mark.parametrize("key", RSA_KEYS.values())
@pytest.mark.parametrize("algorithm", (a for a in EncryptionAlgorithm if a.startswith("RSA")))
def test_rsa_encrypt_decrypt(key, algorithm):
    provider = get_local_cryptography_provider(key)
    plaintext = b"plaintext"
    encrypt_result = provider.encrypt(algorithm, plaintext)
    decrypt_result = provider.decrypt(encrypt_result.algorithm, encrypt_result.ciphertext)
    assert decrypt_result.plaintext == plaintext


@pytest.mark.parametrize("key", RSA_KEYS.values())
@pytest.mark.parametrize(
    "algorithm,hash_function",
    (
        (
            (SignatureAlgorithm.ps256, hashlib.sha256),
            (SignatureAlgorithm.ps384, hashlib.sha384),
            (SignatureAlgorithm.ps512, hashlib.sha512),
            (SignatureAlgorithm.rs256, hashlib.sha256),
            (SignatureAlgorithm.rs384, hashlib.sha384),
            (SignatureAlgorithm.rs512, hashlib.sha512),
        )
    ),
)
def test_rsa_sign_verify(key, algorithm, hash_function):
    message = b"message"
    provider = get_local_cryptography_provider(key)
    digest = hash_function(message).digest()
    sign_result = provider.sign(algorithm, digest)
    verify_result = provider.verify(sign_result.algorithm, digest, sign_result.signature)
    assert verify_result.is_valid


@pytest.mark.parametrize("key", RSA_KEYS.values())
@pytest.mark.parametrize("algorithm", (a for a in KeyWrapAlgorithm if a.startswith("RSA")))
def test_rsa_wrap_unwrap(key, algorithm):
    plaintext = b"arbitrary bytes"
    provider = get_local_cryptography_provider(key)

    wrap_result = provider.wrap_key(algorithm, plaintext)
    assert wrap_result.key_id == key.id

    unwrap_result = provider.unwrap_key(wrap_result.algorithm, wrap_result.encrypted_key)
    assert unwrap_result.key == plaintext


def test_symmetric_wrap_unwrap():
    jwk = {"k": os.urandom(32), "kty": "oct", "key_ops": ("unwrapKey", "wrapKey")}
    key = KeyVaultKey(key_id="http://localhost/keys/key/version", jwk=jwk)
    provider = get_local_cryptography_provider(key)
    key_bytes = os.urandom(32)

    wrap_result = provider.wrap_key(KeyWrapAlgorithm.aes_256, key_bytes)
    assert wrap_result.key_id == key.id

    unwrap_result = provider.unwrap_key(wrap_result.algorithm, wrap_result.encrypted_key)
    assert unwrap_result.key == key_bytes


@pytest.mark.parametrize("key", RSA_KEYS.values())
@pytest.mark.parametrize(
    "algorithm",
    [a for a in KeyWrapAlgorithm if not a.startswith("RSA")] + [a for a in SignatureAlgorithm if a.startswith("ES")],
)
def test_unsupported_rsa_operations(key, algorithm):
    """The crypto provider should raise NotImplementedError when a key doesn't support an operation or algorithm"""

    provider = get_local_cryptography_provider(key)
    if isinstance(algorithm, EncryptionAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.encrypt(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.decrypt(algorithm, b"...")
    if isinstance(algorithm, KeyWrapAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.wrap_key(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.unwrap_key(algorithm, b"...")
    elif isinstance(algorithm, SignatureAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.sign(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.verify(algorithm, b"...", b"...")


@pytest.mark.parametrize("key", EC_KEYS.values())
@pytest.mark.parametrize(
    "algorithm",
    [a for a in KeyWrapAlgorithm if a.startswith("RSA")]
    + [a for a in SignatureAlgorithm if not a.startswith("ES")]
    + list(EncryptionAlgorithm),
)
def test_unsupported_ec_operations(key, algorithm):
    """The crypto provider should raise NotImplementedError when a key doesn't support an operation or algorithm"""

    provider = get_local_cryptography_provider(key)
    if isinstance(algorithm, EncryptionAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.encrypt(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.decrypt(algorithm, b"...")
    if isinstance(algorithm, KeyWrapAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.wrap_key(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.unwrap_key(algorithm, b"...")
    elif isinstance(algorithm, SignatureAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.sign(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.verify(algorithm, b"...", b"...")


@pytest.mark.parametrize(
    "algorithm",
    [a for a in KeyWrapAlgorithm if a != KeyWrapAlgorithm.aes_256]
    + list(SignatureAlgorithm)
    + list(EncryptionAlgorithm),
)
def test_unsupported_symmetric_operations(algorithm):
    """The crypto provider should raise NotImplementedError when a key doesn't support an operation or algorithm"""

    jwk = {"k": os.urandom(32), "kty": "oct", "key_ops": ("unwrapKey", "wrapKey")}
    key = KeyVaultKey(key_id="http://localhost/keys/key/version", jwk=jwk)
    provider = get_local_cryptography_provider(key)
    if isinstance(algorithm, EncryptionAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.encrypt(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.decrypt(algorithm, b"...")
    if isinstance(algorithm, KeyWrapAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.wrap_key(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.unwrap_key(algorithm, b"...")
    elif isinstance(algorithm, SignatureAlgorithm):
        with pytest.raises(NotImplementedError):
            provider.sign(algorithm, b"...")
        with pytest.raises(NotImplementedError):
            provider.verify(algorithm, b"...", b"...")
