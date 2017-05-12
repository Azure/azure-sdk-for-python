# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=wrong-import-order

from __future__ import print_function

import collections
import json
import os
import re
import shlex
import sys
import tempfile
import traceback
from random import choice
from string import digits, ascii_lowercase

from six.moves.urllib.parse import urlparse, parse_qs  # pylint: disable=import-error

import unittest
try:
    import unittest.mock as mock
except ImportError:
    import mock

import vcr
import jmespath
from six import StringIO

# TODO Should not depend on azure.cli.main package here.
# Will be ok if this test file is not part of azure.cli.core.utils
from azure.cli.main import main as cli_main

from azure.cli.core import __version__ as core_version
import azure.cli.core._debug as _debug
from azure.cli.core._profile import Profile, CLOUD
from azure.cli.core.util import CLIError

LIVE_TEST_CONTROL_ENV = 'AZURE_CLI_TEST_RUN_LIVE'
COMMAND_COVERAGE_CONTROL_ENV = 'AZURE_CLI_TEST_COMMAND_COVERAGE'
MOCKED_SUBSCRIPTION_ID = '00000000-0000-0000-0000-000000000000'
MOCKED_TENANT_ID = '00000000-0000-0000-0000-000000000000'
MOCKED_STORAGE_ACCOUNT = 'dummystorage'


# MOCK METHODS

# Workaround until https://github.com/kevin1024/vcrpy/issues/293 is fixed.
vcr_connection_request = vcr.stubs.VCRConnection.request


def patch_vcr_connection_request(*args, **kwargs):
    kwargs.pop('encode_chunked', None)
    vcr_connection_request(*args, **kwargs)


vcr.stubs.VCRConnection.request = patch_vcr_connection_request


def _mock_get_mgmt_service_client(client_type, subscription_bound=True, subscription_id=None,
                                  api_version=None, base_url_bound=None, **kwargs):
    # version of _get_mgmt_service_client to use when recording or playing tests
    profile = Profile()
    cred, subscription_id, _ = profile.get_login_credentials(subscription_id=subscription_id)
    client_kwargs = {}

    if base_url_bound:
        client_kwargs = {'base_url': CLOUD.endpoints.resource_manager}
    if api_version:
        client_kwargs['api_version'] = api_version
    if kwargs:
        client_kwargs.update(kwargs)

    if subscription_bound:
        client = client_type(cred, subscription_id, **client_kwargs)
    else:
        client = client_type(cred, **client_kwargs)

    client = _debug.change_ssl_cert_verification(client)

    client.config.add_user_agent("AZURECLI/TEST/{}".format(core_version))

    return (client, subscription_id)


def _mock_generate_deployment_name(namespace):
    if not namespace.deployment_name:
        namespace.deployment_name = 'mock-deployment'


def _mock_handle_exceptions(ex):
    raise ex


def _mock_subscriptions(self):  # pylint: disable=unused-argument
    return [{
        "id": MOCKED_SUBSCRIPTION_ID,
        "user": {
            "name": "example@example.com",
            "type": "user"
        },
        "state": "Enabled",
        "name": "Example",
        "tenantId": MOCKED_TENANT_ID,
        "isDefault": True}]


def _mock_user_access_token(_, _1, _2, _3):  # pylint: disable=unused-argument
    return ('Bearer', 'top-secret-token-for-you')


def _mock_operation_delay(_):
    # don't run time.sleep()
    return


# TEST CHECKS


class JMESPathCheckAssertionError(AssertionError):
    def __init__(self, comparator, actual_result, json_data):
        message = "Actual value '{}' != Expected value '{}'. ".format(
            actual_result,
            comparator.expected_result)
        message += "Query '{}' used on json data '{}'".format(comparator.query, json_data)
        super(JMESPathCheckAssertionError, self).__init__(message)


class JMESPathCheck(object):  # pylint: disable=too-few-public-methods

    def __init__(self, query, expected_result):
        self.query = query
        self.expected_result = expected_result

    def compare(self, json_data):
        actual_result = _search_result_by_jmespath(json_data, self.query)
        if not actual_result == self.expected_result:
            raise JMESPathCheckAssertionError(self, actual_result, json_data)


class JMESPathPatternCheck(object):  # pylint: disable=too-few-public-methods

    def __init__(self, query, expected_result):
        self.query = query
        self.expected_result = expected_result

    def compare(self, json_data):
        actual_result = _search_result_by_jmespath(json_data, self.query)
        if not re.match(self.expected_result, str(actual_result), re.IGNORECASE):
            raise JMESPathCheckAssertionError(self, actual_result, json_data)


class BooleanCheck(object):  # pylint: disable=too-few-public-methods

    def __init__(self, expected_result):
        self.expected_result = expected_result

    def compare(self, data):
        result = str(str(data).lower() in ['yes', 'true', '1'])
        try:
            assert result == str(self.expected_result)
        except AssertionError:
            raise AssertionError("Actual value '{}' != Expected value {}".format(
                result, self.expected_result))


class NoneCheck(object):  # pylint: disable=too-few-public-methods

    def __init__(self):
        pass

    def compare(self, data):  # pylint: disable=no-self-use
        none_strings = ['[]', '{}', 'false']
        try:
            assert not data or data in none_strings
        except AssertionError:
            raise AssertionError("Actual value '{}' != Expected value falsy (None, '', []) or "
                                 "string in {}".format(data, none_strings))


class StringCheck(object):  # pylint: disable=too-few-public-methods

    def __init__(self, expected_result):
        self.expected_result = expected_result

    def compare(self, data):
        try:
            result = data.replace('"', '')
            assert result == self.expected_result
        except AssertionError:
            raise AssertionError("Actual value '{}' != Expected value {}".format(
                data, self.expected_result))


# HELPER METHODS


def _scrub_deployment_name(uri):
    return re.sub('/deployments/([^/?]+)', '/deployments/mock-deployment', uri)


def _scrub_service_principal_name(uri):
    return re.sub('userPrincipalName%20eq%20%27(.+)%27',
                  'userPrincipalName%20eq%20%27example%40example.com%27', uri)


def _search_result_by_jmespath(json_data, query):
    if not json_data:
        json_data = '{}'
    json_val = json.loads(json_data)
    return jmespath.search(
        query,
        json_val,
        jmespath.Options(collections.OrderedDict))


def _custom_request_matcher(r1, r2):
    """ Ensure method, path, and query parameters match. """
    if r1.method != r2.method:
        return False

    url1 = urlparse(r1.uri)
    url2 = urlparse(r2.uri)

    if url1.path != url2.path:
        return False

    q1 = parse_qs(url1.query)
    q2 = parse_qs(url2.query)
    shared_keys = set(q1.keys()).intersection(set(q2.keys()))

    if len(shared_keys) != len(q1) or len(shared_keys) != len(q2):
        return False

    for key in shared_keys:
        if q1[key][0].lower() != q2[key][0].lower():
            return False

    return True


# MAIN CLASS


class VCRTestBase(unittest.TestCase):  # pylint: disable=too-many-instance-attributes

    FILTER_HEADERS = [
        'authorization',
        'client-request-id',
        'x-ms-client-request-id',
        'x-ms-correlation-request-id',
        'x-ms-ratelimit-remaining-subscription-reads',
        'x-ms-request-id',
        'x-ms-routing-request-id',
        'x-ms-gateway-service-instanceid',
        'x-ms-ratelimit-remaining-tenant-reads',
        'x-ms-served-by',
    ]

    def __init__(self, test_file, test_name, run_live=False, debug=False, debug_vcr=False,
                 skip_setup=False, skip_teardown=False):
        super(VCRTestBase, self).__init__(test_name)
        self.test_name = test_name
        self.recording_dir = os.path.join(os.path.dirname(test_file), 'recordings')
        self.cassette_path = os.path.join(self.recording_dir, '{}.yaml'.format(test_name))
        self.playback = os.path.isfile(self.cassette_path)

        if os.environ.get(LIVE_TEST_CONTROL_ENV, None) == 'True':
            self.run_live = True
        else:
            self.run_live = run_live

        self.skip_setup = skip_setup
        self.skip_teardown = skip_teardown
        self.success = False
        self.exception = None
        self.track_commands = os.environ.get(COMMAND_COVERAGE_CONTROL_ENV, None)
        self._debug = debug

        if not self.playback and ('--buffer' in sys.argv) and not run_live:
            self.exception = CLIError('No recorded result provided for {}.'.format(self.test_name))

        if debug_vcr:
            import logging
            logging.basicConfig()
            vcr_log = logging.getLogger('vcr')
            vcr_log.setLevel(logging.INFO)
        self.my_vcr = vcr.VCR(
            cassette_library_dir=self.recording_dir,
            before_record_request=self._before_record_request,
            before_record_response=self._before_record_response,
            decode_compressed_response=True
        )
        self.my_vcr.register_matcher('custom', _custom_request_matcher)
        self.my_vcr.match_on = ['custom']

    def _track_executed_commands(self, command):
        if self.track_commands:
            with open(self.track_commands, 'a+') as f:
                f.write(' '.join(command))
                f.write('\n')

    def _before_record_request(self, request):  # pylint: disable=no-self-use
        # scrub subscription from the uri
        request.uri = re.sub('/subscriptions/([^/]+)/',
                             '/subscriptions/{}/'.format(MOCKED_SUBSCRIPTION_ID), request.uri)
        # scrub jobId from uri, required for ADLA
        request.uri = re.sub('/Jobs/([^/]+)',
                             '/Jobs/{}'.format(MOCKED_SUBSCRIPTION_ID), request.uri)
        request.uri = re.sub('/graph.windows.net/([^/]+)/',
                             '/graph.windows.net/{}/'.format(MOCKED_TENANT_ID), request.uri)
        request.uri = re.sub('/sig=([^/]+)&', '/sig=0000&', request.uri)
        request.uri = _scrub_deployment_name(request.uri)
        request.uri = _scrub_service_principal_name(request.uri)

        # replace random storage account name with dummy name
        request.uri = re.sub(r'(vcrstorage[\d]+)', MOCKED_STORAGE_ACCOUNT, request.uri)
        # prevents URI mismatch between Python 2 and 3 if request URI has extra / chars
        request.uri = re.sub('//', '/', request.uri)
        request.uri = re.sub('/', '//', request.uri, count=1)
        # do not record requests sent for token refresh'
        if (request.body and 'grant-type=refresh_token' in str(request.body)) or \
                ('/oauth2/token' in request.uri):
            request = None
        return request

    def _before_record_response(self, response):  # pylint: disable=no-self-use
        for key in VCRTestBase.FILTER_HEADERS:
            if key in response['headers']:
                del response['headers'][key]

        def _scrub_body_parameters(value):
            value = re.sub('/subscriptions/([^/]+)/',
                           '/subscriptions/{}/'.format(MOCKED_SUBSCRIPTION_ID), value)
            value = re.sub('\"jobId\": \"([^/]+)\"',
                           '\"jobId\": \"{}\"'.format(MOCKED_SUBSCRIPTION_ID), value)
            return value

        for key in response['body']:
            value = response['body'][key].decode('utf-8')
            value = _scrub_body_parameters(value)
            try:
                response['body'][key] = bytes(value, 'utf-8')
            except TypeError:
                response['body'][key] = value.encode('utf-8')

        return response

    @mock.patch('azure.cli.main.handle_exception', _mock_handle_exceptions)
    @mock.patch('azure.cli.core.commands.client_factory._get_mgmt_service_client',
                _mock_get_mgmt_service_client)  # pylint: disable=line-too-long
    def _execute_live_or_recording(self):
        # pylint: disable=no-member
        try:
            set_up = getattr(self, "set_up", None)
            if callable(set_up) and not self.skip_setup:
                self.set_up()

            if self.run_live:
                self.body()
            else:
                with self.my_vcr.use_cassette(self.cassette_path):
                    self.body()
            self.success = True
        except Exception as ex:
            raise ex
        finally:
            tear_down = getattr(self, "tear_down", None)
            if callable(tear_down) and not self.skip_teardown:
                self.tear_down()

    @mock.patch('azure.cli.core._profile.Profile.load_cached_subscriptions', _mock_subscriptions)
    @mock.patch('azure.cli.core._profile.CredsCache.retrieve_token_for_user',
                _mock_user_access_token)  # pylint: disable=line-too-long
    @mock.patch('azure.cli.main.handle_exception', _mock_handle_exceptions)
    @mock.patch('azure.cli.core.commands.client_factory._get_mgmt_service_client',
                _mock_get_mgmt_service_client)  # pylint: disable=line-too-long
    @mock.patch('msrestazure.azure_operation.AzureOperationPoller._delay', _mock_operation_delay)
    @mock.patch('time.sleep', _mock_operation_delay)
    @mock.patch('azure.cli.core.commands.LongRunningOperation._delay', _mock_operation_delay)
    @mock.patch('azure.cli.core.commands.validators.generate_deployment_name',
                _mock_generate_deployment_name)
    def _execute_playback(self):
        # pylint: disable=no-member
        with self.my_vcr.use_cassette(self.cassette_path):
            self.body()
        self.success = True

    def _post_recording_scrub(self):
        """ Perform post-recording cleanup on the YAML file that can't be accomplished with the
        VCR recording hooks. """
        src_path = self.cassette_path
        rg_name = getattr(self, 'resource_group', None)
        rg_original = getattr(self, 'resource_group_original', None)

        t = tempfile.NamedTemporaryFile('r+')
        with open(src_path, 'r') as f:
            for line in f:
                # scrub resource group names
                if rg_name != rg_original:
                    line = line.replace(rg_name, rg_original)
                # omit bearer tokens
                if 'authorization:' not in line.lower():
                    t.write(line)
        t.seek(0)
        with open(src_path, 'w') as f:
            for line in t:
                f.write(line)
        t.close()

    # COMMAND METHODS

    def cmd(self, command, checks=None, allowed_exceptions=None,
            debug=False):  # pylint: disable=no-self-use
        allowed_exceptions = allowed_exceptions or []
        if not isinstance(allowed_exceptions, list):
            allowed_exceptions = [allowed_exceptions]

        if self._debug or debug:
            print('\n\tRUNNING: {}'.format(command))
        command_list = shlex.split(command)
        output = StringIO()
        try:
            cli_main(command_list, file=output)
        except Exception as ex:  # pylint: disable=broad-except
            ex_msg = str(ex)
            if not next((x for x in allowed_exceptions if x in ex_msg), None):
                raise ex
        self._track_executed_commands(command_list)
        result = output.getvalue().strip()
        output.close()

        if self._debug or debug:
            print('\tRESULT: {}\n'.format(result))

        if checks:
            checks = [checks] if not isinstance(checks, list) else checks
            for check in checks:
                check.compare(result)

        if '-o' in command_list and 'tsv' in command_list:
            return result
        else:
            try:
                result = result or '{}'
                return json.loads(result)
            except Exception:  # pylint: disable=broad-except
                return result

    def set_env(self, key, val):  # pylint: disable=no-self-use
        os.environ[key] = val

    def pop_env(self, key):  # pylint: disable=no-self-use
        return os.environ.pop(key, None)

    def execute(self):
        ''' Method to actually start execution of the test. Must be called from the test_<name>
        method of the test class. '''
        try:
            if self.run_live:
                print('RUN LIVE: {}'.format(self.test_name))
                self._execute_live_or_recording()
            elif self.playback:
                print('PLAYBACK: {}'.format(self.test_name))
                self._execute_playback()
            else:
                print('RECORDING: {}'.format(self.test_name))
                self._execute_live_or_recording()
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            if not self.success and not self.playback and os.path.isfile(self.cassette_path):
                print('DISCARDING RECORDING: {}'.format(self.cassette_path))
                os.remove(self.cassette_path)
            elif self.success and not self.playback and os.path.isfile(self.cassette_path):
                try:
                    self._post_recording_scrub()
                except Exception:  # pylint: disable=broad-except
                    os.remove(self.cassette_path)


class ResourceGroupVCRTestBase(VCRTestBase):

    def __init__(self, test_file, test_name, resource_group='vcr_resource_group', run_live=False,
                 debug=False, debug_vcr=False, skip_setup=False, skip_teardown=False,
                 random_tag_format=None):
        super(ResourceGroupVCRTestBase, self).__init__(test_file, test_name, run_live=run_live,
                                                       debug=debug, debug_vcr=debug_vcr,
                                                       skip_setup=skip_setup,
                                                       skip_teardown=skip_teardown)
        self.resource_group_original = resource_group
        random_tag = (random_tag_format or '_{}_').format(
            ''.join((choice(ascii_lowercase + digits) for _ in range(4))))
        self.resource_group = '{}{}'.format(resource_group, '' if self.playback else random_tag)
        self.location = 'westus'

    def set_up(self):
        self.cmd('group create --location {} --name {} --tags use=az-test'.format(
            self.location, self.resource_group))

    def tear_down(self):
        self.cmd('group delete --name {} --no-wait --yes'.format(self.resource_group))
