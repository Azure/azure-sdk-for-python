import asyncio
import functools

from .. import StorageTestCase, StorageRecordedTestCase
from ...fake_credentials_async import AsyncFakeCredential

from azure_devtools.scenario_tests.patches import mock_in_unit_test
from azure_devtools.scenario_tests.utilities import trim_kwargs_from_test_function


def patch_play_responses(unit_test):
    """Fixes a bug affecting blob tests by applying https://github.com/kevin1024/vcrpy/pull/511 to vcrpy 3.0.0"""

    try:
        from vcr.stubs.aiohttp_stubs import _serialize_headers, build_response, Request, URL
    except ImportError:
        # return a do-nothing patch when importing from vcr fails
        return lambda _: None

    def fixed_play_responses(cassette, vcr_request):
        history = []
        vcr_response = cassette.play_response(vcr_request)
        response = build_response(vcr_request, vcr_response, history)
        while 300 <= response.status <= 399:
            if "location" not in response.headers:
                break
            next_url = URL(response.url).with_path(response.headers["location"])
            vcr_request = Request("GET", str(next_url), None, _serialize_headers(response.request_info.headers))
            vcr_request = cassette.find_requests_with_most_matches(vcr_request)[0][0]
            history.append(response)
            vcr_response = cassette.play_response(vcr_request)
            response = build_response(vcr_request, vcr_response, history)
        return response

    return mock_in_unit_test(unit_test, "vcr.stubs.aiohttp_stubs.play_responses", fixed_play_responses)


class AsyncStorageTestCase(StorageTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replay_patches.append(patch_play_responses)

    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity.aio import ClientSecretCredential

            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return AsyncFakeCredential()


class AsyncStorageTestCase(StorageRecordedTestCase):
    
    @staticmethod
    def await_prepared_test(test_fn):
        """Synchronous wrapper for async test methods. Used to avoid making changes
        upstream to AbstractPreparer (which doesn't await the functions it wraps)
        """

        @functools.wraps(test_fn)
        def run(test_class_instance, *args, **kwargs):
            trim_kwargs_from_test_function(test_fn, kwargs)
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(test_fn(test_class_instance, **kwargs))

        return run

    def generate_oauth_token(self):
        if self.is_live:
            from azure.identity.aio import ClientSecretCredential

            return ClientSecretCredential(
                self.get_settings_value("TENANT_ID"),
                self.get_settings_value("CLIENT_ID"),
                self.get_settings_value("CLIENT_SECRET"),
            )
        return self.generate_fake_token()

    def generate_fake_token(self):
        return AsyncFakeCredential()
