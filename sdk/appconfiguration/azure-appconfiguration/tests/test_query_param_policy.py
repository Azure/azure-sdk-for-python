# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


from azure.core.pipeline.transport import HttpRequest
from azure.core.pipeline import PipelineRequest
from azure.appconfiguration._query_param_policy import QueryParamPolicy
import pytest

TEST_URL = "https://example.com"


def test_query_parameters_are_sorted_alphabetically():
    """Test that query parameters are sorted alphabetically."""
    original_url = "?zebra=value1&alpha=value2&beta=value3"
    expected_url = "?alpha=value2&beta=value3&zebra=value1"

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameter_keys_are_converted_to_lowercase():
    """Test that query parameter keys are converted to lowercase."""
    original_url = "?SELECT=field1&FILTER=condition&orderBy=field2"
    expected_url = "?filter=condition&orderby=field2&select=field1"

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameter_o_data_parameters():
    """Test that OData query parameters are handled correctly."""
    original_url = "?$Select=name%2Cvalue&$Filter=startsWith%28key%2C%27test%27%29&api-version=1.0"
    expected_url = "?%24filter=startsWith%28key%2C%27test%27%29&%24select=name%2Cvalue&api-version=1.0"

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameters_with_multiple_values():
    """Test that query parameters with multiple values are handled correctly."""
    original_url = "?key=value1&key=value2&alpha=test"
    expected_url = "?alpha=test&key=value1&key=value2"

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameters_with_special_characters():
    """Test that query parameters with special characters are preserved."""
    original_url = "?filter=name%20eq%20%27test%27&select=*"
    expected_url = "?filter=name%20eq%20%27test%27&select=%2A"

    request = HttpRequest("GET", original_url)
    pipeline_request = PipelineRequest(request, None)

    query_param_policy = QueryParamPolicy()

    # Create a mock next policy
    class MockNext:
        def __init__(self):
            self.captured_url = None

        def send(self, request):
            self.captured_url = request.http_request.url
            return None

    mock_next = MockNext()
    query_param_policy.next = mock_next

    query_param_policy.send(pipeline_request)

    # Note: URL encoding may change the format slightly, but the query params should still be sorted
    assert mock_next.captured_url is not None, "No URL was captured by the mock policy."
    assert "filter=" in mock_next.captured_url
    assert "select=" in mock_next.captured_url
    # The params should be in alphabetical order
    filter_pos = mock_next.captured_url.index("filter=")
    select_pos = mock_next.captured_url.index("select=")
    assert filter_pos < select_pos, "Parameters should be sorted alphabetically"


def test_no_query_parameters():
    """Test that URLs without query parameters are not modified."""
    original_url = ""
    expected_url = ""

    run_query_param_policy_test(original_url, expected_url)


def test_empty_query_parameter_values():
    """Test that empty query parameter values are preserved."""
    original_url = "?zebra=&alpha=value&beta="
    expected_url = "?alpha=value&beta=&zebra="

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameter_with_key_only():
    """Test that query parameters with only a key and no value are preserved and sorted."""
    original_url = "?zebra&alpha=value&beta"
    expected_url = "?alpha=value&beta=&zebra="

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameter_with_empty_key_is_first():
    """Test that query parameters with empty keys are first."""
    original_url = "?alpha=value2&=value1"
    expected_url = "?alpha=value2"

    run_query_param_policy_test(original_url, expected_url)


@pytest.mark.parametrize(
    "original_url,expected_url",
    [
        ("?key=%20value%20&alpha=%20%20", "?alpha=%20%20&key=%20value%20"),
        ("?key=hello%20world&alpha=foo%20bar", "?alpha=foo%20bar&key=hello%20world"),
    ],
)
def test_query_param_policy_whitespace(original_url, expected_url):
    run_query_param_policy_test(original_url, expected_url)


# Unicode and encoded values
@pytest.mark.parametrize(
    "original_url,expected_url",
    [
        ("?key=%E2%9C%93&alpha=%C3%A9", "?alpha=%C3%A9&key=%E2%9C%93"),
        ("?key=val1&key=\u2713", "?key=val1&key=%E2%9C%93"),
        ("?key=val1&key=é", "?key=val1&key=%C3%A9"),
    ],
)
def test_query_param_policy_unicode(original_url, expected_url):
    run_query_param_policy_test(original_url, expected_url)


# Multiple values for same key
@pytest.mark.parametrize(
    "original_url,expected_url",
    [
        ("?key=val1&key=val2&key=val3", "?key=val1&key=val2&key=val3"),
    ],
)
def test_query_param_policy_multiple_values(original_url, expected_url):
    run_query_param_policy_test(original_url, expected_url)


def test_query_parameter_values_are_preserved():
    """Test that query parameter values are preserved correctly."""
    original_url = "?key1=Value%20With%20Spaces&key2=SimpleValue&key3="
    expected_url = "?key1=Value%20With%20Spaces&key2=SimpleValue&key3="

    run_query_param_policy_test(original_url, expected_url)


def test_query_parameters_with_same_key_are_preserved():
    """Test that query parameters with the same key are preserved in order."""
    original_url = "?key=val1&key=val2&key=val3"
    expected_url = "?key=val1&key=val2&key=val3"

    run_query_param_policy_test(original_url, expected_url)


# Empty and malformed cases
@pytest.mark.parametrize(
    "original_url,expected_url",
    [
        ("?key=val1&&key=val2", "?key=val1&key=val2"),
        ("?key=val1&=val2", "?key=val1"),
        ("?key=val1&key=", "?key=val1&key="),
        ("?key=val1&key", "?key=val1&key="),
        ("?key=val1&key= ", "?key=val1&key=%20"),
        ("?key=val1&key=%20", "?key=val1&key=%20"),
        ("?key=val1&key=%E2%9C%93", "?key=val1&key=%E2%9C%93"),
    ],
)
def test_query_param_policy_empty_and_malformed(original_url, expected_url):
    run_query_param_policy_test(original_url, expected_url)


def test_comprehensive_query_parameter_normalization():
    original_url = (
        "?$TOP=10&API-Version=2023-10-01&$select=key,value&label=prod&$filter=startsWith(key,'app')&maxItems=100"
    )
    expected_url = "?%24filter=startsWith%28key%2C%27app%27%29&%24select=key%2Cvalue&%24top=10&api-version=2023-10-01&label=prod&maxitems=100"

    run_query_param_policy_test(original_url, expected_url)


def test_multiple_tags_parameters():
    """Test that multiple tags parameters are handled correctly."""
    original_url = "?api-version=2023-11-01&key=*&label=dev&tags=environment%3Ddev&tags=team%3Dfrontend"
    expected_url = "?api-version=2023-11-01&key=%2A&label=dev&tags=environment%3Ddev&tags=team%3Dfrontend"

    run_query_param_policy_test(original_url, expected_url)


def test_tags_parameters_with_complex_values():
    """Test that tags parameters with complex values are handled correctly."""
    original_url = "?tags=environment%3Dproduction&tags=team%3Dbackend&api-version=2023-11-01"
    expected_url = "?api-version=2023-11-01&tags=environment%3Dproduction&tags=team%3Dbackend"

    run_query_param_policy_test(original_url, expected_url)


def test_tags_parameters_mixed_with_other_parameters():
    """Test that tags parameters mixed with other parameters are handled correctly."""
    original_url = "?$select=key,value&tags=feature%3Dauth&label=*&api-version=2023-11-01&$filter=startsWith(key,'app')&tags=env%3Dtest"
    expected_url = "?%24filter=startsWith%28key%2C%27app%27%29&%24select=key%2Cvalue&api-version=2023-11-01&label=%2A&tags=env%3Dtest&tags=feature%3Dauth"

    run_query_param_policy_test(original_url, expected_url)


def test_tags_parameters_with_special_characters():
    """Test that tags parameters with special characters are handled correctly."""
    original_url = "?TAGS=Priority%3DHigh&api-version=2023-11-01&Tags=Status%3DActive"
    expected_url = "?api-version=2023-11-01&tags=Priority%3DHigh&tags=Status%3DActive"

    run_query_param_policy_test(original_url, expected_url)


def test_key_and_label_filters_with_ampersand_character():
    """Test that key and label filters with ampersand characters are handled correctly."""
    original_url = "?key=app%26config&label=prod%26test&api-version=2023-11-01"
    expected_url = "?api-version=2023-11-01&key=app%26config&label=prod%26test"

    run_query_param_policy_test(original_url, expected_url)


def test_key_and_label_filters_with_space_character():
    """Test that key and label filters with space characters are handled correctly."""
    original_url = "?key=app%20config&label=dev%20environment&api-version=2023-11-01"
    expected_url = "?api-version=2023-11-01&key=app%20config&label=dev%20environment"

    run_query_param_policy_test(original_url, expected_url)


def test_key_and_label_filters_with_hash_character():
    """Test that key and label filters with hash characters are handled correctly."""
    original_url = "?key=app%23config&label=version%23v1&api-version=2023-11-01"
    expected_url = "?api-version=2023-11-01&key=app%23config&label=version%23v1"

    run_query_param_policy_test(original_url, expected_url)


def test_key_and_label_filters_with_mixed_special_characters():
    """Test that key and label filters with mixed special characters are handled correctly."""
    original_url = "?key=app%26config%20test%23v1&label=prod%20%26%20test%23env&api-version=2023-11-01"
    expected_url = "?api-version=2023-11-01&key=app%26config%20test%23v1&label=prod%20%26%20test%23env"

    run_query_param_policy_test(original_url, expected_url)


def run_query_param_policy_test(original_url, expected_url):
    request = HttpRequest("GET", TEST_URL + original_url)
    pipeline_request = PipelineRequest(request, None)
    query_param_policy = QueryParamPolicy()

    class MockNext:
        def __init__(self):
            self.captured_url = None

        def send(self, request):
            self.captured_url = request.http_request.url
            return None

    mock_next = MockNext()
    query_param_policy.next = mock_next
    query_param_policy.send(pipeline_request)
    assert mock_next.captured_url == TEST_URL + expected_url
