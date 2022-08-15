import copy
import inspect
import os

from six.moves import http_client as httplib
import pytest
import yaml

from vcr.compat import mock, contextlib
from vcr.cassette import Cassette
from vcr.errors import UnhandledHTTPRequestError
from vcr.patch import force_reset
from vcr.stubs import VCRHTTPSConnection


def test_cassette_load(tmpdir):
    a_file = tmpdir.join("test_cassette.yml")
    a_file.write(
        yaml.dump(
            {
                "interactions": [
                    {"request": {"body": "", "uri": "foo", "method": "GET", "headers": {}}, "response": "bar"}
                ]
            }
        )
    )
    a_cassette = Cassette.load(path=str(a_file))
    assert len(a_cassette) == 1


def test_cassette_not_played():
    a = Cassette("test")
    assert not a.play_count


def test_cassette_append():
    a = Cassette("test")
    a.append("foo", "bar")
    assert a.requests == ["foo"]
    assert a.responses == ["bar"]


def test_cassette_len():
    a = Cassette("test")
    a.append("foo", "bar")
    a.append("foo2", "bar2")
    assert len(a) == 2


def _mock_requests_match(request1, request2, matchers):
    return request1 == request2


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_contains():
    a = Cassette("test")
    a.append("foo", "bar")
    assert "foo" in a


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_responses_of():
    a = Cassette("test")
    a.append("foo", "bar")
    assert a.responses_of("foo") == ["bar"]


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_get_missing_response():
    a = Cassette("test")
    with pytest.raises(UnhandledHTTPRequestError):
        a.responses_of("foo")


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_cant_read_same_request_twice():
    a = Cassette("test")
    a.append("foo", "bar")
    a.play_response("foo")
    with pytest.raises(UnhandledHTTPRequestError):
        a.play_response("foo")


def make_get_request():
    conn = httplib.HTTPConnection("www.python.org")
    conn.request("GET", "/index.html")
    return conn.getresponse()


@mock.patch("vcr.cassette.requests_match", return_value=True)
@mock.patch(
    "vcr.cassette.FilesystemPersister.load_cassette",
    classmethod(lambda *args, **kwargs: (("foo",), (mock.MagicMock(),))),
)
@mock.patch("vcr.cassette.Cassette.can_play_response_for", return_value=True)
@mock.patch("vcr.stubs.VCRHTTPResponse")
def test_function_decorated_with_use_cassette_can_be_invoked_multiple_times(*args):
    decorated_function = Cassette.use(path="test")(make_get_request)
    for i in range(4):
        decorated_function()


def test_arg_getter_functionality():
    arg_getter = mock.Mock(return_value={"path": "test"})
    context_decorator = Cassette.use_arg_getter(arg_getter)

    with context_decorator as cassette:
        assert cassette._path == "test"

    arg_getter.return_value = {"path": "other"}

    with context_decorator as cassette:
        assert cassette._path == "other"

    arg_getter.return_value = {"path": "other", "filter_headers": ("header_name",)}

    @context_decorator
    def function():
        pass

    with mock.patch.object(Cassette, "load", return_value=mock.MagicMock(inject=False)) as cassette_load:
        function()
        cassette_load.assert_called_once_with(**arg_getter.return_value)


def test_cassette_not_all_played():
    a = Cassette("test")
    a.append("foo", "bar")
    assert not a.all_played


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_all_played():
    a = Cassette("test")
    a.append("foo", "bar")
    a.play_response("foo")
    assert a.all_played


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
def test_cassette_rewound():
    a = Cassette("test")
    a.append("foo", "bar")
    a.play_response("foo")
    assert a.all_played

    a.rewind()
    assert not a.all_played


def test_before_record_response():
    before_record_response = mock.Mock(return_value="mutated")
    cassette = Cassette("test", before_record_response=before_record_response)
    cassette.append("req", "res")

    before_record_response.assert_called_once_with("res")
    assert cassette.responses[0] == "mutated"


def assert_get_response_body_is(value):
    conn = httplib.HTTPConnection("www.python.org")
    conn.request("GET", "/index.html")
    assert conn.getresponse().read().decode("utf8") == value


@mock.patch("vcr.cassette.requests_match", _mock_requests_match)
@mock.patch("vcr.cassette.Cassette.can_play_response_for", return_value=True)
@mock.patch("vcr.cassette.Cassette._save", return_value=True)
def test_nesting_cassette_context_managers(*args):
    first_response = {
        "body": {"string": b"first_response"},
        "headers": {},
        "status": {"message": "m", "code": 200},
    }

    second_response = copy.deepcopy(first_response)
    second_response["body"]["string"] = b"second_response"

    with contextlib.ExitStack() as exit_stack:
        first_cassette = exit_stack.enter_context(Cassette.use(path="test"))
        exit_stack.enter_context(
            mock.patch.object(first_cassette, "play_response", return_value=first_response)
        )
        assert_get_response_body_is("first_response")

        # Make sure a second cassette can supercede the first
        with Cassette.use(path="test") as second_cassette:
            with mock.patch.object(second_cassette, "play_response", return_value=second_response):
                assert_get_response_body_is("second_response")

        # Now the first cassette should be back in effect
        assert_get_response_body_is("first_response")


def test_nesting_context_managers_by_checking_references_of_http_connection():
    original = httplib.HTTPConnection
    with Cassette.use(path="test"):
        first_cassette_HTTPConnection = httplib.HTTPConnection
        with Cassette.use(path="test"):
            second_cassette_HTTPConnection = httplib.HTTPConnection
            assert second_cassette_HTTPConnection is not first_cassette_HTTPConnection
            with Cassette.use(path="test"):
                assert httplib.HTTPConnection is not second_cassette_HTTPConnection
                with force_reset():
                    assert httplib.HTTPConnection is original
            assert httplib.HTTPConnection is second_cassette_HTTPConnection
        assert httplib.HTTPConnection is first_cassette_HTTPConnection


def test_custom_patchers():
    class Test(object):
        attribute = None

    with Cassette.use(path="custom_patches", custom_patches=((Test, "attribute", VCRHTTPSConnection),)):
        assert issubclass(Test.attribute, VCRHTTPSConnection)
        assert VCRHTTPSConnection is not Test.attribute
        old_attribute = Test.attribute

        with Cassette.use(path="custom_patches", custom_patches=((Test, "attribute", VCRHTTPSConnection),)):
            assert issubclass(Test.attribute, VCRHTTPSConnection)
            assert VCRHTTPSConnection is not Test.attribute
            assert Test.attribute is not old_attribute

        assert issubclass(Test.attribute, VCRHTTPSConnection)
        assert VCRHTTPSConnection is not Test.attribute
        assert Test.attribute is old_attribute


def test_decorated_functions_are_reentrant():
    info = {"second": False}
    original_conn = httplib.HTTPConnection

    @Cassette.use(path="whatever", inject=True)
    def test_function(cassette):
        if info["second"]:
            assert httplib.HTTPConnection is not info["first_conn"]
        else:
            info["first_conn"] = httplib.HTTPConnection
            info["second"] = True
            test_function()
            assert httplib.HTTPConnection is info["first_conn"]

    test_function()
    assert httplib.HTTPConnection is original_conn


def test_cassette_use_called_without_path_uses_function_to_generate_path():
    @Cassette.use(inject=True)
    def function_name(cassette):
        assert cassette._path == "function_name"

    function_name()


def test_path_transformer_with_function_path():
    def path_transformer(path):
        return os.path.join("a", path)

    @Cassette.use(inject=True, path_transformer=path_transformer)
    def function_name(cassette):
        assert cassette._path == os.path.join("a", "function_name")

    function_name()


def test_path_transformer_with_context_manager():
    with Cassette.use(path="b", path_transformer=lambda *args: "a") as cassette:
        assert cassette._path == "a"


def test_path_transformer_None():
    with Cassette.use(path="a", path_transformer=None) as cassette:
        assert cassette._path == "a"


def test_func_path_generator():
    def generator(function):
        return os.path.join(os.path.dirname(inspect.getfile(function)), function.__name__)

    @Cassette.use(inject=True, func_path_generator=generator)
    def function_name(cassette):
        assert cassette._path == os.path.join(os.path.dirname(__file__), "function_name")

    function_name()


def test_use_as_decorator_on_coroutine():
    original_http_connetion = httplib.HTTPConnection

    @Cassette.use(inject=True)
    def test_function(cassette):
        assert httplib.HTTPConnection.cassette is cassette
        assert httplib.HTTPConnection is not original_http_connetion
        value = yield 1
        assert value == 1
        assert httplib.HTTPConnection.cassette is cassette
        assert httplib.HTTPConnection is not original_http_connetion
        value = yield 2
        assert value == 2

    coroutine = test_function()
    value = next(coroutine)
    while True:
        try:
            value = coroutine.send(value)
        except StopIteration:
            break


def test_use_as_decorator_on_generator():
    original_http_connetion = httplib.HTTPConnection

    @Cassette.use(inject=True)
    def test_function(cassette):
        assert httplib.HTTPConnection.cassette is cassette
        assert httplib.HTTPConnection is not original_http_connetion
        yield 1
        assert httplib.HTTPConnection.cassette is cassette
        assert httplib.HTTPConnection is not original_http_connetion
        yield 2

    assert list(test_function()) == [1, 2]


@mock.patch("vcr.cassette.get_matchers_results")
def test_find_requests_with_most_matches_one_similar_request(mock_get_matchers_results):
    mock_get_matchers_results.side_effect = [
        (["method"], [("path", "failed : path"), ("query", "failed : query")]),
        (["method", "path"], [("query", "failed : query")]),
        ([], [("method", "failed : method"), ("path", "failed : path"), ("query", "failed : query")]),
    ]

    cassette = Cassette("test")
    for request in range(1, 4):
        cassette.append(request, "response")
    result = cassette.find_requests_with_most_matches("fake request")
    assert result == [(2, ["method", "path"], [("query", "failed : query")])]


@mock.patch("vcr.cassette.get_matchers_results")
def test_find_requests_with_most_matches_no_similar_requests(mock_get_matchers_results):
    mock_get_matchers_results.side_effect = [
        ([], [("path", "failed : path"), ("query", "failed : query")]),
        ([], [("path", "failed : path"), ("query", "failed : query")]),
        ([], [("path", "failed : path"), ("query", "failed : query")]),
    ]

    cassette = Cassette("test")
    for request in range(1, 4):
        cassette.append(request, "response")
    result = cassette.find_requests_with_most_matches("fake request")
    assert result == []


@mock.patch("vcr.cassette.get_matchers_results")
def test_find_requests_with_most_matches_many_similar_requests(mock_get_matchers_results):
    mock_get_matchers_results.side_effect = [
        (["method", "path"], [("query", "failed : query")]),
        (["method"], [("path", "failed : path"), ("query", "failed : query")]),
        (["method", "path"], [("query", "failed : query")]),
    ]

    cassette = Cassette("test")
    for request in range(1, 4):
        cassette.append(request, "response")
    result = cassette.find_requests_with_most_matches("fake request")
    assert result == [
        (1, ["method", "path"], [("query", "failed : query")]),
        (3, ["method", "path"], [("query", "failed : query")]),
    ]
