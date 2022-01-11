import os

import pytest
from six.moves import http_client as httplib

from vcr import VCR, use_cassette
from vcr.compat import mock
from vcr.request import Request
from vcr.stubs import VCRHTTPSConnection
from vcr.patch import _HTTPConnection, force_reset


def test_vcr_use_cassette():
    record_mode = mock.Mock()
    test_vcr = VCR(record_mode=record_mode)
    with mock.patch(
        "vcr.cassette.Cassette.load", return_value=mock.MagicMock(inject=False)
    ) as mock_cassette_load:

        @test_vcr.use_cassette("test")
        def function():
            pass

        assert mock_cassette_load.call_count == 0
        function()
        assert mock_cassette_load.call_args[1]["record_mode"] is record_mode

        # Make sure that calls to function now use cassettes with the
        # new filter_header_settings
        test_vcr.record_mode = mock.Mock()
        function()
        assert mock_cassette_load.call_args[1]["record_mode"] == test_vcr.record_mode

        # Ensure that explicitly provided arguments still supercede
        # those on the vcr.
        new_record_mode = mock.Mock()

    with test_vcr.use_cassette("test", record_mode=new_record_mode) as cassette:
        assert cassette.record_mode == new_record_mode


def test_vcr_before_record_request_params():
    base_path = "http://httpbin.org/"

    def before_record_cb(request):
        if request.path != "/get":
            return request

    test_vcr = VCR(
        filter_headers=("cookie", ("bert", "ernie")),
        before_record_request=before_record_cb,
        ignore_hosts=("www.test.com",),
        ignore_localhost=True,
        filter_query_parameters=("foo", ("tom", "jerry")),
        filter_post_data_parameters=("posted", ("no", "trespassing")),
    )

    with test_vcr.use_cassette("test") as cassette:
        # Test explicit before_record_cb
        request_get = Request("GET", base_path + "get", "", {})
        assert cassette.filter_request(request_get) is None
        request = Request("GET", base_path + "get2", "", {})
        assert cassette.filter_request(request) is not None

        # Test filter_query_parameters
        request = Request("GET", base_path + "?foo=bar", "", {})
        assert cassette.filter_request(request).query == []
        request = Request("GET", base_path + "?tom=nobody", "", {})
        assert cassette.filter_request(request).query == [("tom", "jerry")]

        # Test filter_headers
        request = Request(
            "GET", base_path + "?foo=bar", "", {"cookie": "test", "other": "fun", "bert": "nobody"}
        )
        assert cassette.filter_request(request).headers == {"other": "fun", "bert": "ernie"}

        # Test ignore_hosts
        request = Request("GET", "http://www.test.com" + "?foo=bar", "", {"cookie": "test", "other": "fun"})
        assert cassette.filter_request(request) is None

        # Test ignore_localhost
        request = Request("GET", "http://localhost:8000" + "?foo=bar", "", {"cookie": "test", "other": "fun"})
        assert cassette.filter_request(request) is None

    with test_vcr.use_cassette("test", before_record_request=None) as cassette:
        # Test that before_record can be overwritten in context manager.
        assert cassette.filter_request(request_get) is not None


def test_vcr_before_record_response_iterable():
    # Regression test for #191

    request = Request("GET", "/", "", {})
    response = object()  # just can't be None

    # Prevent actually saving the cassette
    with mock.patch("vcr.cassette.FilesystemPersister.save_cassette"):

        # Baseline: non-iterable before_record_response should work
        mock_filter = mock.Mock()
        vcr = VCR(before_record_response=mock_filter)
        with vcr.use_cassette("test") as cassette:
            assert mock_filter.call_count == 0
            cassette.append(request, response)
            assert mock_filter.call_count == 1

        # Regression test: iterable before_record_response should work too
        mock_filter = mock.Mock()
        vcr = VCR(before_record_response=(mock_filter,))
        with vcr.use_cassette("test") as cassette:
            assert mock_filter.call_count == 0
            cassette.append(request, response)
            assert mock_filter.call_count == 1


def test_before_record_response_as_filter():
    request = Request("GET", "/", "", {})
    response = object()  # just can't be None

    # Prevent actually saving the cassette
    with mock.patch("vcr.cassette.FilesystemPersister.save_cassette"):

        filter_all = mock.Mock(return_value=None)
        vcr = VCR(before_record_response=filter_all)
        with vcr.use_cassette("test") as cassette:
            cassette.append(request, response)
            assert cassette.data == []
            assert not cassette.dirty


def test_vcr_path_transformer():
    # Regression test for #199

    # Prevent actually saving the cassette
    with mock.patch("vcr.cassette.FilesystemPersister.save_cassette"):

        # Baseline: path should be unchanged
        vcr = VCR()
        with vcr.use_cassette("test") as cassette:
            assert cassette._path == "test"

        # Regression test: path_transformer=None should do the same.
        vcr = VCR(path_transformer=None)
        with vcr.use_cassette("test") as cassette:
            assert cassette._path == "test"

        # and it should still work with cassette_library_dir
        vcr = VCR(cassette_library_dir="/foo")
        with vcr.use_cassette("test") as cassette:
            assert os.path.abspath(cassette._path) == os.path.abspath("/foo/test")


@pytest.fixture
def random_fixture():
    return 1


@use_cassette("test")
def test_fixtures_with_use_cassette(random_fixture):
    # Applying a decorator to a test function that requests features can cause
    # problems if the decorator does not preserve the signature of the original
    # test function.

    # This test ensures that use_cassette preserves the signature of
    # the original test function, and thus that use_cassette is
    # compatible with py.test fixtures. It is admittedly a bit strange
    # because the test would never even run if the relevant feature
    # were broken.
    pass


def test_custom_patchers():
    class Test(object):
        attribute = None
        attribute2 = None

    test_vcr = VCR(custom_patches=((Test, "attribute", VCRHTTPSConnection),))
    with test_vcr.use_cassette("custom_patches"):
        assert issubclass(Test.attribute, VCRHTTPSConnection)
        assert VCRHTTPSConnection is not Test.attribute

    with test_vcr.use_cassette("custom_patches", custom_patches=((Test, "attribute2", VCRHTTPSConnection),)):
        assert issubclass(Test.attribute, VCRHTTPSConnection)
        assert VCRHTTPSConnection is not Test.attribute
        assert Test.attribute is Test.attribute2


def test_inject_cassette():
    vcr = VCR(inject_cassette=True)

    @vcr.use_cassette("test", record_mode="once")
    def with_cassette_injected(cassette):
        assert cassette.record_mode == "once"

    @vcr.use_cassette("test", record_mode="once", inject_cassette=False)
    def without_cassette_injected():
        pass

    with_cassette_injected()
    without_cassette_injected()


def test_with_current_defaults():
    vcr = VCR(inject_cassette=True, record_mode="once")

    @vcr.use_cassette("test", with_current_defaults=False)
    def changing_defaults(cassette, checks):
        checks(cassette)

    @vcr.use_cassette("test", with_current_defaults=True)
    def current_defaults(cassette, checks):
        checks(cassette)

    def assert_record_mode_once(cassette):
        assert cassette.record_mode == "once"

    def assert_record_mode_all(cassette):
        assert cassette.record_mode == "all"

    changing_defaults(assert_record_mode_once)
    current_defaults(assert_record_mode_once)

    vcr.record_mode = "all"
    changing_defaults(assert_record_mode_all)
    current_defaults(assert_record_mode_once)


def test_cassette_library_dir_with_decoration_and_no_explicit_path():
    library_dir = "/libary_dir"
    vcr = VCR(inject_cassette=True, cassette_library_dir=library_dir)

    @vcr.use_cassette()
    def function_name(cassette):
        assert cassette._path == os.path.join(library_dir, "function_name")

    function_name()


def test_cassette_library_dir_with_decoration_and_explicit_path():
    library_dir = "/libary_dir"
    vcr = VCR(inject_cassette=True, cassette_library_dir=library_dir)

    @vcr.use_cassette(path="custom_name")
    def function_name(cassette):
        assert cassette._path == os.path.join(library_dir, "custom_name")

    function_name()


def test_cassette_library_dir_with_decoration_and_super_explicit_path():
    library_dir = "/libary_dir"
    vcr = VCR(inject_cassette=True, cassette_library_dir=library_dir)

    @vcr.use_cassette(path=os.path.join(library_dir, "custom_name"))
    def function_name(cassette):
        assert cassette._path == os.path.join(library_dir, "custom_name")

    function_name()


def test_cassette_library_dir_with_path_transformer():
    library_dir = "/libary_dir"
    vcr = VCR(
        inject_cassette=True, cassette_library_dir=library_dir, path_transformer=lambda path: path + ".json"
    )

    @vcr.use_cassette()
    def function_name(cassette):
        assert cassette._path == os.path.join(library_dir, "function_name.json")

    function_name()


def test_use_cassette_with_no_extra_invocation():
    vcr = VCR(inject_cassette=True, cassette_library_dir="/")

    @vcr.use_cassette
    def function_name(cassette):
        assert cassette._path == os.path.join("/", "function_name")

    function_name()


def test_path_transformer():
    vcr = VCR(inject_cassette=True, cassette_library_dir="/", path_transformer=lambda x: x + "_test")

    @vcr.use_cassette
    def function_name(cassette):
        assert cassette._path == os.path.join("/", "function_name_test")

    function_name()


def test_cassette_name_generator_defaults_to_using_module_function_defined_in():
    vcr = VCR(inject_cassette=True)

    @vcr.use_cassette
    def function_name(cassette):
        assert cassette._path == os.path.join(os.path.dirname(__file__), "function_name")

    function_name()


def test_ensure_suffix():
    vcr = VCR(inject_cassette=True, path_transformer=VCR.ensure_suffix(".yaml"))

    @vcr.use_cassette
    def function_name(cassette):
        assert cassette._path == os.path.join(os.path.dirname(__file__), "function_name.yaml")

    function_name()


def test_additional_matchers():
    vcr = VCR(match_on=("uri",), inject_cassette=True)

    @vcr.use_cassette
    def function_defaults(cassette):
        assert set(cassette._match_on) == {vcr.matchers["uri"]}

    @vcr.use_cassette(additional_matchers=("body",))
    def function_additional(cassette):
        assert set(cassette._match_on) == {vcr.matchers["uri"], vcr.matchers["body"]}

    function_defaults()
    function_additional()


def test_decoration_should_respect_function_return_value():
    vcr = VCR()
    ret = "a-return-value"

    @vcr.use_cassette
    def function_with_return():
        return ret

    assert ret == function_with_return()


class TestVCRClass(VCR().test_case()):
    def no_decoration(self):
        assert httplib.HTTPConnection == _HTTPConnection
        self.test_dynamically_added()
        assert httplib.HTTPConnection == _HTTPConnection

    def test_one(self):
        with force_reset():
            self.no_decoration()
        with force_reset():
            self.test_two()
        assert httplib.HTTPConnection != _HTTPConnection

    def test_two(self):
        assert httplib.HTTPConnection != _HTTPConnection


def test_dynamically_added(self):
    assert httplib.HTTPConnection != _HTTPConnection


TestVCRClass.test_dynamically_added = test_dynamically_added
del test_dynamically_added
