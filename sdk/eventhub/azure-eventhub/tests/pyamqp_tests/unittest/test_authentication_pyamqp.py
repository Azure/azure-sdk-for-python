
import pytest
import functools

from unittest.mock import Mock
from azure.eventhub._pyamqp.sasl import SASLAnonymousCredential, SASLPlainCredential
from azure.eventhub._pyamqp.authentication import SASLPlainAuth, JWTTokenAuth, SASTokenAuth


def test_sasl_plain_auth():
    auth = SASLPlainAuth(
        authcid="authcid",
        passwd="passwd",
        authzid="Some Authzid"
    )
    assert auth.auth_type=="AUTH_SASL_PLAIN"
    assert auth.sasl.mechanism==b"PLAIN"
    assert auth.sasl.start() == b'Some Authzid\x00authcid\x00passwd'

def test_jwt_token_auth():
    credential = Mock()
    attr = {"get_token.return_value": "my_token"}
    credential.configure_mock(**attr)
    auth = JWTTokenAuth(
        uri="my_uri",
        audience="my_audience_field",
        get_token=functools.partial(credential.get_token, "my_auth_uri")
    )

    assert auth.uri == "my_uri"
    assert auth.audience == "my_audience_field"

def test_sas_token_auth():
    auth = SASTokenAuth(
        uri="my_uri",
        audience="my_audience",
        username="username",
        password="password"
    )

    assert auth.uri ==  "my_uri"
    assert auth.audience == "my_audience"
    assert auth.username == "username"
    assert auth.password == "password"