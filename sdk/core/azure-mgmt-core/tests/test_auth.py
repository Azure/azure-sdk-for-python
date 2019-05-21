#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------
import json
import sys
import time
import unittest
try:
    from unittest import mock
except ImportError:
    import mock

from requests import HTTPError, Session, ConnectionError
import oauthlib
import adal
import httpretty

from msrestazure.azure_active_directory import (
    AADMixin,
    ServicePrincipalCredentials,
    UserPassCredentials,
    AADTokenCredentials,
    AdalAuthentication,
    MSIAuthentication,
    get_msi_token,
    get_msi_token_webapp
)
from msrestazure.azure_cloud import AZURE_CHINA_CLOUD
from msrest.exceptions import TokenExpiredError, AuthenticationError

import pytest

class TestServicePrincipalCredentials(unittest.TestCase):

    def test_convert_token(self):

        mix = AADMixin(None, None)
        token = {'access_token':'abc', 'expires_on':123, 'refresh_token':'asd'}
        self.assertEqual(mix._convert_token(token), token)

        caps = {'accessToken':'abc', 'expiresOn':123, 'refreshToken':'asd'}
        self.assertEqual(mix._convert_token(caps), token)

        caps = {'ACCessToken':'abc', 'Expires_On':123, 'REFRESH_TOKEN':'asd'}
        self.assertEqual(mix._convert_token(caps), token)


    @mock.patch("adal.AuthenticationContext")
    def test_property(self, adal_context):

        adal_context.acquire_token_with_client_credentials = mock.Mock()

        creds = ServicePrincipalCredentials(
            123,
            'secret',
            tenant="private"
        )  # Implicit set_token call

        adal_context.assert_called_with(
            "https://login.microsoftonline.com/private",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.timeout = 12
        assert creds._context is None
        creds.set_token()
        adal_context.assert_called_with(
            "https://login.microsoftonline.com/private",
            timeout=12,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.verify = True
        assert creds._context is None
        creds.set_token()
        adal_context.assert_called_with(
            "https://login.microsoftonline.com/private",
            timeout=12,
            verify_ssl=True,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.proxies = {}
        assert creds._context is None
        creds.set_token()
        adal_context.assert_called_with(
            "https://login.microsoftonline.com/private",
            timeout=12,
            verify_ssl=True,
            proxies={},
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.cloud_environment = AZURE_CHINA_CLOUD
        assert creds._context is None
        creds.set_token()
        adal_context.assert_called_with(
            "https://login.chinacloudapi.cn/private",
            timeout=12,
            verify_ssl=True,
            proxies={},
            validate_authority=True,
            cache=None,
            api_version=None
        )

    @mock.patch("adal.AuthenticationContext")
    def test_service_principal(self, adal_context):

        adal_context.acquire_token_with_client_credentials = mock.Mock()

        # Basic with parameters

        mock_proxies = {
            'http': 'http://myproxy:8080',
            'https': 'https://myproxy:8080',
        }

        creds = ServicePrincipalCredentials(
            123,
            'secret',
            resource="resource",
            timeout=12,
            verify=True,
            proxies=mock_proxies
        )

        adal_context.assert_called_with(
            "https://login.microsoftonline.com/common",
            timeout=12,
            verify_ssl=True,
            proxies=mock_proxies,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.set_token()

        creds._context.acquire_token_with_client_credentials.assert_called_with(
            "resource",
            123,
            "secret"
        )

        # Using default

        creds = ServicePrincipalCredentials(
            123,
            'secret',
            tenant="private"
        )

        adal_context.assert_called_with(
            "https://login.microsoftonline.com/private",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )
        creds.set_token()
        creds._context.acquire_token_with_client_credentials.assert_called_with(
            "https://management.core.windows.net/",
            123,
            "secret"
        )

        # Testing cloud_environment

        creds = ServicePrincipalCredentials(
            123,
            'secret',
            cloud_environment=AZURE_CHINA_CLOUD
        )

        adal_context.assert_called_with(
            "https://login.chinacloudapi.cn/common",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )
        creds.set_token()
        creds._context.acquire_token_with_client_credentials.assert_called_with(
            "https://management.core.chinacloudapi.cn/",
            123,
            "secret"
        )

        # Testing china=True

        creds = ServicePrincipalCredentials(
            123,
            'secret',
            china=True
        )

        adal_context.assert_called_with(
            "https://login.chinacloudapi.cn/common",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )
        creds.set_token()
        creds._context.acquire_token_with_client_credentials.assert_called_with(
            "https://management.core.chinacloudapi.cn/",
            123,
            "secret"
        )

        # ADAL boom

        creds._context.acquire_token_with_client_credentials.side_effect = adal.AdalError("Boom")

        with self.assertRaises(AuthenticationError):
            creds.set_token()

    @mock.patch("adal.AuthenticationContext")
    def test_user_pass_credentials(self, adal_context):

        adal_context.acquire_token_with_username_password = mock.Mock()

        # Basic with parameters

        mock_proxies = {
            'http': 'http://myproxy:8080',
            'https': 'https://myproxy:8080',
        }

        creds = UserPassCredentials(
            'user',
            'pass',
            'id',
            resource="resource",
            timeout=12,
            verify=True,
            validate_authority=True,
            cache=None,
            proxies=mock_proxies
        )

        adal_context.assert_called_with(
            "https://login.microsoftonline.com/common",
            timeout=12,
            verify_ssl=True,
            proxies=mock_proxies,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.set_token()

        creds._context.acquire_token_with_username_password.assert_called_with(
            "resource",
            "user",
            "pass",
            "id"
        )

        # Using default

        creds = UserPassCredentials(
            'user',
            'pass',
        )

        adal_context.assert_called_with(
            "https://login.microsoftonline.com/common",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )

        creds.set_token()

        creds._context.acquire_token_with_username_password.assert_called_with(
            "https://management.core.windows.net/",
            "user",
            "pass",
            "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
        )

        # Testing cloud_environment

        creds = UserPassCredentials(
            'user',
            'pass',
            cloud_environment=AZURE_CHINA_CLOUD
        )

        adal_context.assert_called_with(
            "https://login.chinacloudapi.cn/common",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )
        creds.set_token()
        creds._context.acquire_token_with_username_password.assert_called_with(
            "https://management.core.chinacloudapi.cn/",
            "user",
            "pass",
            "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
        )

        # Testing china=True

        creds = UserPassCredentials(
            'user',
            'pass',
            china=True
        )

        adal_context.assert_called_with(
            "https://login.chinacloudapi.cn/common",
            timeout=None,
            verify_ssl=None,
            proxies=None,
            validate_authority=True,
            cache=None,
            api_version=None
        )
        creds.set_token()
        creds._context.acquire_token_with_username_password.assert_called_with(
            "https://management.core.chinacloudapi.cn/",
            "user",
            "pass",
            "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
        )

        # ADAL boom

        creds._context.acquire_token_with_username_password.side_effect = adal.AdalError("Boom")

        with self.assertRaises(AuthenticationError):
            creds.set_token()

    def test_adal_authentication(self):
        def success_auth():
            return {
                'tokenType': 'https',
                'accessToken': 'cryptictoken'
            }

        credentials = AdalAuthentication(success_auth)
        session = credentials.signed_session()
        self.assertEquals(session.headers['Authorization'], 'https cryptictoken')

        def error():
            raise adal.AdalError("You hacker", {})
        credentials = AdalAuthentication(error)
        with self.assertRaises(AuthenticationError) as cm:
            session = credentials.signed_session()

        def expired():
            raise adal.AdalError("Too late", {'error_description': "AADSTS70008: Expired"})
        credentials = AdalAuthentication(expired)
        with self.assertRaises(TokenExpiredError) as cm:
            session = credentials.signed_session()

        def connection_error():
            raise ConnectionError("Plug the network")
        credentials = AdalAuthentication(connection_error)
        with self.assertRaises(AuthenticationError) as cm:
            session = credentials.signed_session()

    @httpretty.activate
    def test_msi_vm(self):

        # Test legacy MSI, with no MSI_ENDPOINT

        json_payload = {
            'token_type': "TokenType",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.POST,
                               'http://localhost:666/oauth2/token',
                               body=json.dumps(json_payload),
                               content_type="application/json")

        token_type, access_token, token_entry = get_msi_token("whatever", port=666)
        assert token_type == "TokenType"
        assert access_token == "AccessToken"
        assert token_entry == json_payload

        httpretty.register_uri(httpretty.POST,
                               'http://localhost:42/oauth2/token',
                               status=503,
                               content_type="application/json")

        with self.assertRaises(HTTPError):
            get_msi_token("whatever", port=42)

        # Test MSI_ENDPOINT

        json_payload = {
            'token_type': "TokenType",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.POST,
                               'http://random.org/yadadada',
                               body=json.dumps(json_payload),
                               content_type="application/json")

        with mock.patch('os.environ', {'MSI_ENDPOINT': 'http://random.org/yadadada'}):
            token_type, access_token, token_entry = get_msi_token("whatever")
            assert token_type == "TokenType"
            assert access_token == "AccessToken"
            assert token_entry == json_payload

        # Test MSIAuthentication with no MSI_ENDPOINT and no APPSETTING_WEBSITE_SITE_NAME is IMDS

        json_payload = {
            'token_type': "TokenTypeIMDS",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               body=json.dumps(json_payload),
                               content_type="application/json")

        credentials = MSIAuthentication()
        assert credentials.scheme == "TokenTypeIMDS"
        assert credentials.token == json_payload

        # Test MSIAuthentication with MSI_ENDPOINT and no APPSETTING_WEBSITE_SITE_NAME is MSI_ENDPOINT

        json_payload = {
            'token_type': "TokenTypeMSI_ENDPOINT",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.POST,
                               'http://random.org/yadadada',
                               body=json.dumps(json_payload),
                               content_type="application/json")

        with mock.patch('os.environ', {'MSI_ENDPOINT': 'http://random.org/yadadada'}):
            credentials = MSIAuthentication()
            assert credentials.scheme == "TokenTypeMSI_ENDPOINT"
            assert credentials.token == json_payload

        # WebApp

        json_payload = {
            'token_type': "TokenTypeWebApp",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.GET,
                               'http://127.0.0.1:41741/MSI/token/?resource=foo&api-version=2017-09-01',
                               body=json.dumps(json_payload),
                               content_type="application/json")

        app_service_env = {
            'APPSETTING_WEBSITE_SITE_NAME': 'Website name',
            'MSI_ENDPOINT': 'http://127.0.0.1:41741/MSI/token',
            'MSI_SECRET': '69418689F1E342DD946CB82994CDA3CB'
        }
        with mock.patch.dict('os.environ', app_service_env):
            credentials = MSIAuthentication(resource="foo")
            assert credentials.scheme == "TokenTypeWebApp"
            assert credentials.token == json_payload


    @httpretty.activate
    def test_msi_vm_imds_retry(self):

        json_payload = {
            'token_type': "TokenTypeIMDS",
            "access_token": "AccessToken"
        }
        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               status=404)
        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               status=429)
        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               status=599)
        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               body=json.dumps(json_payload),
                               content_type="application/json")
        credentials = MSIAuthentication()
        assert credentials.scheme == "TokenTypeIMDS"
        assert credentials.token == json_payload


    @httpretty.activate
    def test_msi_vm_imds_no_retry_on_bad_error(self):

        httpretty.register_uri(httpretty.GET,
                               'http://169.254.169.254/metadata/identity/oauth2/token',
                               status=499)
        with self.assertRaises(HTTPError) as cm:
            credentials = MSIAuthentication()


@pytest.mark.slow
def test_refresh_userpassword_no_common_session(user_password):
    user, password = user_password

    creds = UserPassCredentials(user, password)

    # Basic scenarion, I recreate the session each time
    session = creds.signed_session()

    response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
    response.raise_for_status() # Should never raise

    try:
        session = creds.signed_session()
        # Hacking the token time
        session.auth._client.token['expires_in'] = session.auth._client.expires_in = -10
        session.auth._client.token['expires_on'] = session.auth._client.expires_on = time.time() -10
        session.auth._client.token['expires_at'] = session.auth._client.expires_at = session.auth._client._expires_at = session.auth._client.expires_on

        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        pytest.fail("Requests should have failed")
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        session = creds.refresh_session()
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        response.raise_for_status() # Should never raise

@pytest.mark.slow
def test_refresh_userpassword_common_session(user_password):
    user, password = user_password

    creds = UserPassCredentials(user, password)
    root_session = Session()

    # Basic scenarion, I recreate the session each time
    session = creds.signed_session(root_session)

    response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
    response.raise_for_status() # Should never raise

    try:
        session = creds.signed_session(root_session)
        # Hacking the token time
        session.auth._client.token['expires_in'] = session.auth._client.expires_in = -10
        session.auth._client.token['expires_on'] = session.auth._client.expires_on = time.time() -10
        session.auth._client.token['expires_at'] = session.auth._client.expires_at = session.auth._client._expires_at = session.auth._client.expires_on

        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        pytest.fail("Requests should have failed")
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        session = creds.refresh_session(root_session)
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        response.raise_for_status() # Should never raise

@pytest.mark.slow
def test_refresh_aadtokencredentials_no_common_session(user_password):
    user, password = user_password

    context = adal.AuthenticationContext('https://login.microsoftonline.com/common')
    token = context.acquire_token_with_username_password(
        'https://management.core.windows.net/',
        user,
        password,
        '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
    )
    creds = AADTokenCredentials(token)

    # Basic scenarion, I recreate the session each time
    session = creds.signed_session()

    response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
    response.raise_for_status() # Should never raise

    # Hacking the token time
    creds.token['expires_on'] = time.time() - 10
    creds.token['expires_at'] = creds.token['expires_on']

    try:
        session = creds.signed_session()
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        pytest.fail("Requests should have failed")
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        session = creds.refresh_session()
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        response.raise_for_status() # Should never raise

@pytest.mark.slow
def test_refresh_aadtokencredentials_common_session(user_password):
    user, password = user_password

    context = adal.AuthenticationContext('https://login.microsoftonline.com/common')
    token = context.acquire_token_with_username_password(
        'https://management.core.windows.net/',
        user,
        password,
        '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
    )
    creds = AADTokenCredentials(token)

    root_session = Session()

    # Basic scenarion, I recreate the session each time
    session = creds.signed_session(root_session)

    response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
    response.raise_for_status() # Should never raise

    # Hacking the token time
    creds.token['expires_on'] = time.time() - 10
    creds.token['expires_at'] = creds.token['expires_on']

    try:
        session = creds.signed_session(root_session)
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        pytest.fail("Requests should have failed")
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        session = creds.refresh_session(root_session)
        response = session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        response.raise_for_status() # Should never raise

@pytest.mark.slow
def test_refresh_aadtokencredentials_existing_session(user_password):
    user, password = user_password

    context = adal.AuthenticationContext('https://login.microsoftonline.com/common')
    token = context.acquire_token_with_username_password(
        'https://management.core.windows.net/',
        user,
        password,
        '04b07795-8ddb-461a-bbee-02f9e1bf7b46'
    )
    creds = AADTokenCredentials(token)

    root_session = Session()

    creds.signed_session(root_session)

    response = root_session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
    response.raise_for_status()  # Should never raise

    # Hacking the token time
    creds.token['expires_on'] = time.time() - 10
    creds.token['expires_at'] = creds.token['expires_on']

    try:
        creds.signed_session(root_session)
        response = root_session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        pytest.fail("Requests should have failed")
    except oauthlib.oauth2.rfc6749.errors.TokenExpiredError:
        creds.refresh_session(root_session)
        response = root_session.get("https://management.azure.com/subscriptions?api-version=2016-06-01")
        response.raise_for_status()  # Should never raise

if __name__ == '__main__':
    unittest.main()
