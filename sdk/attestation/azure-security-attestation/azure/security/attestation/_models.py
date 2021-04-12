from typing import Any, List, TypeVar, Generic, Callable
from cryptography.x509 import Certificate
from ._common import Base64Url
from json import JSONDecoder

T = TypeVar('T')

class AttestationSigner(object):
    """ Represents a signing certificate returned by the Attestation Service.

    """
    def __init__(self, certificates: List[Certificate], key_id : str, **kwargs):
        self.certificates = certificates
        self.key_id = key_id

class TokenValidationOptions(object):
    """ Validation options for an Attestation Token object.
    :keyword bool validate_token: if True, validate the returned token, otherwise return the token unvalidated.
    :keyword Callable[['AttestationToken', 'AttestationSigner'], bool] validation_callback: Callback to allow clients to perform custom validation of the token.
    """
    def __init__(
        self,
        **kwargs):
        self.validate_token = kwargs.get('validate_token') #type: bool
        self.validation_callback = kwargs.get('validation_callback') # Callable[['AttestationToken', AttestationSigner], bool]):

    
class AttestationToken(Generic[T]):
    """ Represents a token returned from the attestation service.
    """
    def __init__(self, token: str):
        self.token = token
        token_parts = token.split('.')
        if len(token_parts) != 3:
            raise ValueError("Malformed JSON Web Token")
        self._raw_header = Base64Url.decode(token_parts[0]).decode('utf-8')
        self._raw_body =Base64Url.decode(token_parts[1]).decode('utf-8')
        self._signature = Base64Url.decode(token_parts[2])
        decoder = JSONDecoder()
        self._body = decoder.decode(self._raw_body)
        self._header = decoder.decode(self._raw_header)


    def validate_token(self, options: TokenValidationOptions, signing_certificates: List[AttestationSigner]):
        if not options.validate_token:
            pass
        pass

    def get_body(self) -> T:
        return self._body

class AttestationResult(Generic[T]):
    def __init__(self, token : AttestationToken, value: T):
        self.token = token
        self.value = value

