# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
from azure.appconfiguration._audience_policy import AudiencePolicy

NO_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. No authentication token audience was provided. "
    "Please set an Audience in your ConfigurationClientBuilder for the target cloud. "
    "For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
INCORRECT_AUDIENCE_ERROR_MESSAGE = (
    "Unable to authenticate to Azure App Configuration. An incorrect token audience was provided. "
    "Please set the Audience in your ConfigurationClientBuilder to the appropriate audience for this cloud. "
    "For details on how to configure the authentication token audience visit "
    "https://aka.ms/appconfig/client-token-audience."
)
AAD_AUDIENCE_ERROR_CODE = "AADSTS500011"


class DummyRequest:
    def __init__(self, exception=None):
        self.context = type("ctx", (), {"options": {"exception": exception}})()


class DummyResponse:
    pass


def make_exception(message):
    return HttpResponseError(message=message, response=None)


def test_on_exception_no_audience():
    policy = AudiencePolicy(audience=None)
    ex = make_exception(f"{AAD_AUDIENCE_ERROR_CODE} some error")
    req = DummyRequest(exception=ex)
    result = policy.on_exception(req)
    assert isinstance(result, HttpResponseError)
    assert NO_AUDIENCE_ERROR_MESSAGE in str(result)


def test_on_exception_incorrect_audience():
    policy = AudiencePolicy(audience="some_audience")
    ex = make_exception(f"{AAD_AUDIENCE_ERROR_CODE} some error")
    req = DummyRequest(exception=ex)
    result = policy.on_exception(req)
    assert isinstance(result, HttpResponseError)
    assert INCORRECT_AUDIENCE_ERROR_MESSAGE in str(result)


def test_on_exception_non_audience_error():
    policy = AudiencePolicy(audience=None)
    ex = make_exception("Some other error")
    req = DummyRequest(exception=ex)
    result = policy.on_exception(req)
    assert result is ex


def test_on_response_noop():
    policy = AudiencePolicy()
    req = DummyRequest()
    resp = DummyResponse()
    assert policy.on_response(req, resp) is None
