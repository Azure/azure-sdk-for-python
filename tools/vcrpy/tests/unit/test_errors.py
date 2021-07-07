import pytest

from vcr.compat import mock
from vcr import errors
from vcr.cassette import Cassette


@mock.patch("vcr.cassette.Cassette.find_requests_with_most_matches")
@pytest.mark.parametrize(
    "most_matches, expected_message",
    [
        # No request match found
        ([], "No similar requests, that have not been played, found."),
        # One matcher failed
        (
            [("similar request", ["method", "path"], [("query", "failed : query")])],
            "Found 1 similar requests with 1 different matcher(s) :\n"
            "\n1 - ('similar request').\n"
            "Matchers succeeded : ['method', 'path']\n"
            "Matchers failed :\n"
            "query - assertion failure :\n"
            "failed : query\n",
        ),
        # Multiple failed matchers
        (
            [("similar request", ["method"], [("query", "failed : query"), ("path", "failed : path")])],
            "Found 1 similar requests with 2 different matcher(s) :\n"
            "\n1 - ('similar request').\n"
            "Matchers succeeded : ['method']\n"
            "Matchers failed :\n"
            "query - assertion failure :\n"
            "failed : query\n"
            "path - assertion failure :\n"
            "failed : path\n",
        ),
        # Multiple similar requests
        (
            [
                ("similar request", ["method"], [("query", "failed : query")]),
                ("similar request 2", ["method"], [("query", "failed : query 2")]),
            ],
            "Found 2 similar requests with 1 different matcher(s) :\n"
            "\n1 - ('similar request').\n"
            "Matchers succeeded : ['method']\n"
            "Matchers failed :\n"
            "query - assertion failure :\n"
            "failed : query\n"
            "\n2 - ('similar request 2').\n"
            "Matchers succeeded : ['method']\n"
            "Matchers failed :\n"
            "query - assertion failure :\n"
            "failed : query 2\n",
        ),
    ],
)
def test_CannotOverwriteExistingCassetteException_get_message(
    mock_find_requests_with_most_matches, most_matches, expected_message
):
    mock_find_requests_with_most_matches.return_value = most_matches
    cassette = Cassette("path")
    failed_request = "request"
    exception_message = errors.CannotOverwriteExistingCassetteException._get_message(cassette, "request")
    expected = (
        "Can't overwrite existing cassette (%r) in your current record mode (%r).\n"
        "No match for the request (%r) was found.\n"
        "%s" % (cassette._path, cassette.record_mode, failed_request, expected_message)
    )
    assert exception_message == expected
