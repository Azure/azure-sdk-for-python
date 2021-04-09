from typing import Any, List
from cryptography.x509 import Certificate

class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    """
    def __init__(self, certificates: List[Certificate], key_id : str, **kwargs):
        self.certificates = certificates
        self.key_id = key_id
