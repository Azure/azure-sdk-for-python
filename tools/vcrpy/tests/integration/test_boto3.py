import pytest
import os

boto3 = pytest.importorskip("boto3")

import boto3  # NOQA
import botocore  # NOQA
import vcr  # NOQA

try:
    from botocore import awsrequest  # NOQA

    botocore_awsrequest = True
except ImportError:
    botocore_awsrequest = False

# skip tests if boto does not use vendored requests anymore
# https://github.com/boto/botocore/pull/1495
boto3_skip_vendored_requests = pytest.mark.skipif(
    botocore_awsrequest,
    reason="botocore version {ver} does not use vendored requests anymore.".format(ver=botocore.__version__),
)

boto3_skip_awsrequest = pytest.mark.skipif(
    not botocore_awsrequest,
    reason="botocore version {ver} still uses vendored requests.".format(ver=botocore.__version__),
)

IAM_USER_NAME = "vcrpy"


@pytest.fixture
def iam_client():
    def _iam_client(boto3_session=None):
        if boto3_session is None:
            boto3_session = boto3.Session(
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "default"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "default"),
                aws_session_token=None,
                region_name=os.environ.get("AWS_DEFAULT_REGION", "default"),
            )
        return boto3_session.client("iam")

    return _iam_client


@pytest.fixture
def get_user(iam_client):
    def _get_user(client=None, user_name=IAM_USER_NAME):
        if client is None:
            # Default client set with fixture `iam_client`
            client = iam_client()
        return client.get_user(UserName=user_name)

    return _get_user


@boto3_skip_vendored_requests
def test_boto_vendored_stubs(tmpdir):
    with vcr.use_cassette(str(tmpdir.join("boto3-stubs.yml"))):
        # Perform the imports within the patched context so that
        # HTTPConnection, VerifiedHTTPSConnection refers to the patched version.
        from botocore.vendored.requests.packages.urllib3.connectionpool import (
            HTTPConnection,
            VerifiedHTTPSConnection,
        )
        from vcr.stubs.boto3_stubs import VCRRequestsHTTPConnection, VCRRequestsHTTPSConnection

        # Prove that the class was patched by the stub and that we can instantiate it.
        assert issubclass(HTTPConnection, VCRRequestsHTTPConnection)
        assert issubclass(VerifiedHTTPSConnection, VCRRequestsHTTPSConnection)
        HTTPConnection("hostname.does.not.matter")
        VerifiedHTTPSConnection("hostname.does.not.matter")


@pytest.mark.skipif(
    os.environ.get("TRAVIS_PULL_REQUEST") != "false",
    reason="Encrypted Environment Variables from Travis Repository Settings"
    " are disabled on PRs from forks. "
    "https://docs.travis-ci.com/user/pull-requests/#pull-requests-and-security-restrictions",
)
def test_boto_medium_difficulty(tmpdir, get_user):

    with vcr.use_cassette(str(tmpdir.join("boto3-medium.yml"))):
        response = get_user()
        assert response["User"]["UserName"] == IAM_USER_NAME

    with vcr.use_cassette(str(tmpdir.join("boto3-medium.yml"))) as cass:
        response = get_user()
        assert response["User"]["UserName"] == IAM_USER_NAME
        assert cass.all_played


@pytest.mark.skipif(
    os.environ.get("TRAVIS_PULL_REQUEST") != "false",
    reason="Encrypted Environment Variables from Travis Repository Settings"
    " are disabled on PRs from forks. "
    "https://docs.travis-ci.com/user/pull-requests/#pull-requests-and-security-restrictions",
)
def test_boto_hardcore_mode(tmpdir, iam_client, get_user):
    with vcr.use_cassette(str(tmpdir.join("boto3-hardcore.yml"))):
        ses = boto3.Session(
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_DEFAULT_REGION"),
        )
        client = iam_client(ses)
        response = get_user(client=client)
        assert response["User"]["UserName"] == IAM_USER_NAME

    with vcr.use_cassette(str(tmpdir.join("boto3-hardcore.yml"))) as cass:
        ses = boto3.Session(
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=None,
            region_name=os.environ.get("AWS_DEFAULT_REGION"),
        )

        client = iam_client(ses)
        response = get_user(client=client)
        assert response["User"]["UserName"] == IAM_USER_NAME
        assert cass.all_played
