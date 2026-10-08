import os
import re
import ssl
import subprocess
import sys
from pathlib import Path

import certifi
import pytest

from ci_tools.certificates import cibuildwheel_environment


@pytest.fixture
def ca_files(tmp_path, monkeypatch):
    for name in ("NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "PIP_CERT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("ci_tools.certificates.sys.platform", "win32")
    certificates = re.findall(
        rb"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
        Path(certifi.where()).read_bytes(),
        re.DOTALL,
    )
    paths = []
    for name, certificate in zip(("proxy", "ssl", "requests"), certificates[:3]):
        path = tmp_path / f"{name}.pem"
        path.write_bytes(certificate)
        paths.append(path)
    assert len(paths) == 3
    return paths


def _trusted_certificates(path):
    return set(ssl.create_default_context(cafile=str(path)).get_ca_certs(binary_form=True))


def test_no_proxy_preserves_environment(ca_files, monkeypatch):
    monkeypatch.setenv("SSL_CERT_FILE", "unused-invalid-path")
    before = os.environ.copy()
    with cibuildwheel_environment() as env:
        assert env is None
        assert os.environ == before
    assert os.environ == before


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_non_windows_preserves_environment(ca_files, monkeypatch, platform):
    monkeypatch.setattr("ci_tools.certificates.sys.platform", platform)
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", "unused-invalid-path")
    before = os.environ.copy()
    with cibuildwheel_environment() as env:
        assert env is None
    assert os.environ == before


def test_default_roots_and_proxy_are_trusted(ca_files, monkeypatch):
    proxy, _, _ = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("PIP_INDEX_URL", "https://example.invalid/cfs/simple")
    before = os.environ.copy()
    original_certifi = Path(certifi.where()).read_bytes()

    with cibuildwheel_environment() as env:
        bundle = Path(env["SSL_CERT_FILE"])
        assert env["REQUESTS_CA_BUNDLE"] == str(bundle)
        assert _trusted_certificates(bundle) == _trusted_certificates(certifi.where()) | _trusted_certificates(proxy)
        assert env["PIP_INDEX_URL"] == before["PIP_INDEX_URL"]
        assert os.environ == before
        assert bundle.parent.is_absolute()
    assert not bundle.exists()
    assert Path(certifi.where()).read_bytes() == original_certifi
    assert os.environ == before


@pytest.mark.parametrize("requests_variable", ["REQUESTS_CA_BUNDLE", "CURL_CA_BUNDLE", "PIP_CERT"])
def test_custom_roots_are_preserved_independently(ca_files, monkeypatch, requests_variable):
    proxy, ssl_roots, requests_roots = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("SSL_CERT_FILE", str(ssl_roots))
    monkeypatch.setenv(requests_variable, str(requests_roots))
    before = os.environ.copy()
    originals = [path.read_bytes() for path in ca_files]

    with cibuildwheel_environment() as env:
        ssl_bundle = Path(env["SSL_CERT_FILE"])
        requests_bundle = Path(env["REQUESTS_CA_BUNDLE"])
        proxy_certificates = _trusted_certificates(proxy)
        assert _trusted_certificates(ssl_bundle) == _trusted_certificates(ssl_roots) | proxy_certificates
        assert _trusted_certificates(requests_bundle) == _trusted_certificates(requests_roots) | proxy_certificates
        assert ssl_bundle != requests_bundle
        assert os.environ == before
    assert not ssl_bundle.exists()
    assert not requests_bundle.exists()
    assert [path.read_bytes() for path in ca_files] == originals
    assert os.environ == before


def test_requests_override_precedence(ca_files, monkeypatch):
    proxy, ssl_roots, requests_roots = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("REQUESTS_CA_BUNDLE", str(requests_roots))
    monkeypatch.setenv("CURL_CA_BUNDLE", str(ssl_roots))
    monkeypatch.setenv("PIP_CERT", str(ssl_roots))
    with cibuildwheel_environment() as env:
        assert _trusted_certificates(env["REQUESTS_CA_BUNDLE"]) == (
            _trusted_certificates(requests_roots) | _trusted_certificates(proxy)
        )


def test_valid_ca_bundle_with_utf8_comment(ca_files, monkeypatch):
    proxy, ssl_roots, _ = ca_files
    ssl_roots.write_bytes("# CA bundle \N{COPYRIGHT SIGN}\n".encode("utf-8") + ssl_roots.read_bytes())
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("SSL_CERT_FILE", str(ssl_roots))
    with cibuildwheel_environment() as env:
        assert _trusted_certificates(env["SSL_CERT_FILE"]) == (
            _trusted_certificates(ssl_roots) | _trusted_certificates(proxy)
        )


@pytest.mark.parametrize("variable", ["NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE"])
@pytest.mark.parametrize("contents", [None, b"", b"not a certificate", b"-----BEGIN CERTIFICATE-----\ninvalid"])
def test_missing_or_invalid_ca_fails_explicitly(ca_files, tmp_path, monkeypatch, variable, contents):
    proxy, _, _ = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    invalid_path = tmp_path / "invalid.pem"
    if contents is not None:
        invalid_path.write_bytes(contents)
    monkeypatch.setenv(variable, str(invalid_path))
    before = os.environ.copy()
    with pytest.raises(ValueError, match=variable):
        with cibuildwheel_environment():
            pytest.fail("Invalid configuration must fail before starting cibuildwheel")
    assert os.environ == before


@pytest.mark.parametrize("variable", ["NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE"])
def test_empty_ca_path_fails_explicitly(ca_files, monkeypatch, variable):
    proxy, _, _ = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv(variable, "")
    with pytest.raises(ValueError, match=variable):
        with cibuildwheel_environment():
            pytest.fail("An explicitly empty CA path is invalid")


def test_bundle_survives_descendant_process_and_is_cleaned_on_failure(ca_files, monkeypatch):
    proxy, ssl_roots, _ = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("SSL_CERT_FILE", str(ssl_roots))
    before = os.environ.copy()
    probe = (
        "import os, ssl; "
        "assert ssl.create_default_context(cafile=os.environ['SSL_CERT_FILE']).cert_store_stats()['x509_ca'] == 2; "
        "assert ssl.create_default_context(cafile=os.environ['REQUESTS_CA_BUNDLE']).cert_store_stats()['x509_ca'] == 2"
    )
    descendant = f"import subprocess, sys; subprocess.run([sys.executable, '-c', {probe!r}], check=True)"
    with pytest.raises(RuntimeError, match="build failed"):
        with cibuildwheel_environment() as env:
            bundle = Path(env["SSL_CERT_FILE"])
            subprocess.run([sys.executable, "-c", descendant], env=env, check=True)
            raise RuntimeError("build failed")
    assert not bundle.exists()
    assert os.environ == before


def test_pinned_cibuildwheel_bootstrap_and_pip_use_combined_trust(ca_files, tmp_path, monkeypatch):
    proxy, ssl_roots, _ = ca_files
    monkeypatch.setenv("NODE_EXTRA_CA_CERTS", str(proxy))
    monkeypatch.setenv("SSL_CERT_FILE", str(ssl_roots))
    probe = """
import os
from pathlib import Path
from unittest.mock import patch
from cibuildwheel.util import download
from pip._vendor.requests.sessions import Session

with patch("cibuildwheel.util.urllib.request.urlopen") as urlopen:
    urlopen.return_value.__enter__.return_value.read.return_value = b"offline bootstrap"
    destination = Path(os.environ["BOOTSTRAP_DESTINATION"])
    download("https://example.invalid/virtualenv.pyz", destination)
    context = urlopen.call_args.kwargs["context"]
    assert context.cert_store_stats()["x509_ca"] == 2
    assert destination.read_bytes() == b"offline bootstrap"

settings = Session().merge_environment_settings("https://example.invalid/cfs", {}, None, None, None)
assert settings["verify"] == os.environ["REQUESTS_CA_BUNDLE"]
"""
    with cibuildwheel_environment() as env:
        env["BOOTSTRAP_DESTINATION"] = str(tmp_path / "virtualenv.pyz")
        subprocess.run([sys.executable, "-c", probe], env=env, check=True, capture_output=True, text=True)
