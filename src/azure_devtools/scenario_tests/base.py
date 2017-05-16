# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import print_function
import datetime
import unittest
import os
import inspect
import subprocess
import json
import shlex
import tempfile
import shutil
import logging
import six
import vcr

from .patches import (patch_load_cached_subscriptions, patch_main_exception_handler,
                      patch_retrieve_token_for_user, patch_long_run_operation_delay,
                      patch_time_sleep_api)
from .exceptions import CliExecutionError
from .const import (ENV_LIVE_TEST, ENV_SKIP_ASSERT, ENV_TEST_DIAGNOSE, MOCKED_SUBSCRIPTION_ID)
from .recording_processors import (SubscriptionRecordingProcessor, OAuthRequestResponsesFilter,
                                   GeneralNameReplacer, LargeRequestBodyProcessor,
                                   LargeResponseBodyProcessor, LargeResponseBodyReplacer,
                                   DeploymentNameReplacer)
from .utilities import create_random_name
from .decorators import live_only

logger = logging.getLogger('azuer.cli.testsdk')


class IntegrationTestBase(unittest.TestCase):
    def __init__(self, method_name):
        super(IntegrationTestBase, self).__init__(method_name)
        self.diagnose = os.environ.get(ENV_TEST_DIAGNOSE, None) == 'True'

    def cmd(self, command, checks=None, expect_failure=False):
        if self.diagnose:
            begin = datetime.datetime.now()
            print('\nExecuting command: {}'.format(command))

        result = execute(command, expect_failure=expect_failure)

        if self.diagnose:
            duration = datetime.datetime.now() - begin
            print('\nCommand accomplished in {} s. Exit code {}.\n{}'.format(
                duration.total_seconds(), result.exit_code, result.output))

        return result.assert_with_checks(checks)

    def create_random_name(self, prefix, length):  # pylint: disable=no-self-use
        return create_random_name(prefix=prefix, length=length)

    def create_temp_file(self, size_kb, full_random=False):
        """
        Create a temporary file for testing. The test harness will delete the file during tearing
        down.
        """
        fd, path = tempfile.mkstemp()
        os.close(fd)
        self.addCleanup(lambda: os.remove(path))

        with open(path, mode='r+b') as f:
            if full_random:
                chunk = os.urandom(1024)
            else:
                chunk = bytearray([0] * 1024)
            for _ in range(size_kb):
                f.write(chunk)

        return path

    def create_temp_dir(self):
        """
        Create a temporary directory for testing. The test harness will delete the directory during
        tearing down.
        """
        temp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

        return temp_dir

    @classmethod
    def set_env(cls, key, val):
        os.environ[key] = val

    @classmethod
    def pop_env(cls, key):
        return os.environ.pop(key, None)


@live_only()
class LiveTest(IntegrationTestBase):
    pass


class ScenarioTest(IntegrationTestBase):  # pylint: disable=too-many-instance-attributes
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

    def __init__(self, method_name):
        super(ScenarioTest, self).__init__(method_name)
        self.name_replacer = GeneralNameReplacer()
        self.recording_processors = [SubscriptionRecordingProcessor(MOCKED_SUBSCRIPTION_ID),
                                     OAuthRequestResponsesFilter(),
                                     LargeRequestBodyProcessor(),
                                     LargeResponseBodyProcessor(),
                                     DeploymentNameReplacer(),
                                     self.name_replacer]
        self.replay_processors = [LargeResponseBodyReplacer(), DeploymentNameReplacer()]

        test_file_path = inspect.getfile(self.__class__)
        recordings_dir = os.path.join(os.path.dirname(test_file_path), 'recordings')
        live_test = os.environ.get(ENV_LIVE_TEST, None) == 'True'

        self.vcr = vcr.VCR(
            cassette_library_dir=recordings_dir,
            before_record_request=self._process_request_recording,
            before_record_response=self._process_response_recording,
            decode_compressed_response=True,
            record_mode='once' if not live_test else 'all',
            filter_headers=self.FILTER_HEADERS
        )
        self.vcr.register_matcher('query', self._custom_request_query_matcher)

        self.recording_file = os.path.join(recordings_dir, '{}.yaml'.format(method_name))
        if live_test and os.path.exists(self.recording_file):
            os.remove(self.recording_file)

        self.in_recording = live_test or not os.path.exists(self.recording_file)
        self.test_resources_count = 0
        self.original_env = os.environ.copy()

    def setUp(self):
        super(ScenarioTest, self).setUp()

        # set up cassette
        cm = self.vcr.use_cassette(self.recording_file)
        self.cassette = cm.__enter__()
        self.addCleanup(cm.__exit__)

        # set up mock patches
        patch_main_exception_handler(self)

        if not self.in_recording:
            patch_time_sleep_api(self)
            patch_long_run_operation_delay(self)
            patch_load_cached_subscriptions(self)
            patch_retrieve_token_for_user(self)

    def tearDown(self):
        os.environ = self.original_env

    def create_random_name(self, prefix, length):
        self.test_resources_count += 1
        moniker = '{}{:06}'.format(prefix, self.test_resources_count)

        if self.in_recording:
            name = create_random_name(prefix, length)
            self.name_replacer.register_name_pair(name, moniker)
            return name
        else:
            return moniker

    def _process_request_recording(self, request):
        if self.in_recording:
            for processor in self.recording_processors:
                request = processor.process_request(request)
                if not request:
                    break
        else:
            for processor in self.replay_processors:
                request = processor.process_request(request)
                if not request:
                    break

        return request

    def _process_response_recording(self, response):
        if self.in_recording:
            # make header name lower case and filter unwanted headers
            headers = {}
            for key in response['headers']:
                if key.lower() not in self.FILTER_HEADERS:
                    headers[key.lower()] = response['headers'][key]
            response['headers'] = headers

            body = response['body']['string']
            if body and not isinstance(body, six.string_types):
                response['body']['string'] = body.decode('utf-8')

            for processor in self.recording_processors:
                response = processor.process_response(response)
                if not response:
                    break
        else:
            for processor in self.replay_processors:
                response = processor.process_response(response)
                if not response:
                    break

        return response

    @classmethod
    def _custom_request_query_matcher(cls, r1, r2):
        """ Ensure method, path, and query parameters match. """
        from six.moves.urllib_parse import urlparse, parse_qs  # pylint: disable=import-error

        url1 = urlparse(r1.uri)
        url2 = urlparse(r2.uri)

        q1 = parse_qs(url1.query)
        q2 = parse_qs(url2.query)
        shared_keys = set(q1.keys()).intersection(set(q2.keys()))

        if len(shared_keys) != len(q1) or len(shared_keys) != len(q2):
            return False

        for key in shared_keys:
            if q1[key][0].lower() != q2[key][0].lower():
                return False

        return True


class ExecutionResult(object):  # pylint: disable=too-few-public-methods
    def __init__(self, command, expect_failure=False, in_process=True):
        logger.info('Execute command %s', command)
        if in_process:
            self._in_process_execute(command)
        else:
            self._out_of_process_execute(command)

        if expect_failure and self.exit_code == 0:
            raise AssertionError('The command is expected to fail but it doesn\'.')
        elif not expect_failure and self.exit_code != 0:
            raise AssertionError('The command failed. Exit code: {}'.format(self.exit_code))

        self.json_value = None
        self.skip_assert = os.environ.get(ENV_SKIP_ASSERT, None) == 'True'

    def assert_with_checks(self, *args):
        checks = []
        for each in args:
            if isinstance(each, list):
                checks.extend(each)
            elif callable(each):
                checks.append(each)

        logger.info('Checkers to be executed %s', len(checks))

        if not self.skip_assert:
            for c in checks:
                c(self)

        return self

    def get_output_in_json(self):
        if not self.json_value:
            self.json_value = json.loads(self.output)

        if self.json_value is None:
            raise AssertionError('The command output cannot be parsed in json.')

        return self.json_value

    def _in_process_execute(self, command):
        # from azure.cli import  as cli_main
        from azure.cli.main import main as cli_main
        from six import StringIO
        from vcr.errors import CannotOverwriteExistingCassetteException

        if command.startswith('az '):
            command = command[3:]

        output_buffer = StringIO()
        try:
            # issue: stderr cannot be redirect in this form, as a result some failure information
            # is lost when command fails.
            self.exit_code = cli_main(shlex.split(command), file=output_buffer) or 0
            self.output = output_buffer.getvalue()
        except CannotOverwriteExistingCassetteException as ex:
            raise AssertionError(ex)
        except CliExecutionError as ex:
            if ex.exception:
                raise ex.exception
            else:
                raise ex
        except Exception as ex:  # pylint: disable=broad-except
            self.exit_code = 1
            self.output = output_buffer.getvalue()
            self.process_error = ex
        finally:
            output_buffer.close()

    def _out_of_process_execute(self, command):
        try:
            self.output = subprocess.check_output(shlex.split(command)).decode('utf-8')
            self.exit_code = 0
        except subprocess.CalledProcessError as error:
            self.exit_code, self.output = error.returncode, error.output.decode('utf-8')
            self.process_error = error


execute = ExecutionResult
