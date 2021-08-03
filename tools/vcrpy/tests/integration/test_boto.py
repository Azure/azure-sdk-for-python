import pytest

boto = pytest.importorskip("boto")

import boto  # NOQA
import boto.iam  # NOQA
from boto.s3.connection import S3Connection  # NOQA
from boto.s3.key import Key  # NOQA
import vcr  # NOQA

try:  # NOQA
    from ConfigParser import DuplicateSectionError  # NOQA
except ImportError:  # NOQA
    # python3
    from configparser import DuplicateSectionError  # NOQA


def test_boto_stubs(tmpdir):
    with vcr.use_cassette(str(tmpdir.join("boto-stubs.yml"))):
        # Perform the imports within the patched context so that
        # CertValidatingHTTPSConnection refers to the patched version.
        from boto.https_connection import CertValidatingHTTPSConnection
        from vcr.stubs.boto_stubs import VCRCertValidatingHTTPSConnection

        # Prove that the class was patched by the stub and that we can instantiate it.
        assert issubclass(CertValidatingHTTPSConnection, VCRCertValidatingHTTPSConnection)
        CertValidatingHTTPSConnection("hostname.does.not.matter")


def test_boto_without_vcr():
    s3_conn = S3Connection()
    s3_bucket = s3_conn.get_bucket("boto-demo-1394171994")  # a bucket you can access
    k = Key(s3_bucket)
    k.key = "test.txt"
    k.set_contents_from_string("hello world i am a string")


def test_boto_medium_difficulty(tmpdir):
    s3_conn = S3Connection()
    s3_bucket = s3_conn.get_bucket("boto-demo-1394171994")  # a bucket you can access
    with vcr.use_cassette(str(tmpdir.join("boto-medium.yml"))):
        k = Key(s3_bucket)
        k.key = "test.txt"
        k.set_contents_from_string("hello world i am a string")

    with vcr.use_cassette(str(tmpdir.join("boto-medium.yml"))):
        k = Key(s3_bucket)
        k.key = "test.txt"
        k.set_contents_from_string("hello world i am a string")


def test_boto_hardcore_mode(tmpdir):
    with vcr.use_cassette(str(tmpdir.join("boto-hardcore.yml"))):
        s3_conn = S3Connection()
        s3_bucket = s3_conn.get_bucket("boto-demo-1394171994")  # a bucket you can access
        k = Key(s3_bucket)
        k.key = "test.txt"
        k.set_contents_from_string("hello world i am a string")

    with vcr.use_cassette(str(tmpdir.join("boto-hardcore.yml"))):
        s3_conn = S3Connection()
        s3_bucket = s3_conn.get_bucket("boto-demo-1394171994")  # a bucket you can access
        k = Key(s3_bucket)
        k.key = "test.txt"
        k.set_contents_from_string("hello world i am a string")


def test_boto_iam(tmpdir):
    try:
        boto.config.add_section("Boto")
    except DuplicateSectionError:
        pass
    # Ensure that boto uses HTTPS
    boto.config.set("Boto", "is_secure", "true")
    # Ensure that boto uses CertValidatingHTTPSConnection
    boto.config.set("Boto", "https_validate_certificates", "true")

    with vcr.use_cassette(str(tmpdir.join("boto-iam.yml"))):
        iam_conn = boto.iam.connect_to_region("universal")
        iam_conn.get_all_users()

    with vcr.use_cassette(str(tmpdir.join("boto-iam.yml"))):
        iam_conn = boto.iam.connect_to_region("universal")
        iam_conn.get_all_users()
