from ..algorithm import Algorithm, SignatureAlgorithm
from ..transform import SignatureTransform
from cryptography.hazmat.primitives import padding, hashes

class _Rs256SignatureTransform(SignatureTransform):
    def __init__(self, key):
        self._key = key
        self._padding = padding.PKCS1v15()
        self._hash_algo = hashes.SHA256()

    def sign(self, data):
        return self._key.sign(data, self._padding, self._hash_algo)

    def verify(self, data, signature):
        return self._key.verify(signature, data, self._padding, self._hash_algo)

    def dispose(self):
        self._key = None
        self._padding = None
        self._hash_algo = None


class Rs256(SignatureAlgorithm):
    _name = 'RS256'
    _default_hash_algoritm = hashes.SHA256()

    def create_signature_transform(self, key):
        return _Rs256SignatureTransform(key)


Rs256.register()
