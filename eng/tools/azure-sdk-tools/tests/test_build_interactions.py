import os, tempfile, shutil
import sys
import ssl
from pathlib import Path
from subprocess import CalledProcessError
from types import SimpleNamespace

import certifi
import pytest

import ci_tools.build as build_module
from ci_tools.build import discover_targeted_packages, build_packages, build

repo_root = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")
integration_folder = os.path.join(os.path.dirname(__file__), "integration")
pyproject_folder = os.path.join(integration_folder, "scenarios", "pyproject_build_config")
pyproject_file = os.path.join(integration_folder, "scenarios", "pyproject_build_config", "pyproject.toml")


def test_build_core():
    pass


def test_discover_targeted_packages():
    pass


def test_build_packages():
    pass


def test_venv_helpers_importable():
    from ci_tools.venv import (
        get_venv_call,
        get_pip_command,
        get_venv_python,
        install_into_venv,
        uninstall_from_venv,
        pip_install,
        pip_uninstall,
        pip_install_requirements_file,
        run_pip_freeze,
        get_pip_list_output,
    )

    # Verify re-exports from ci_tools.functions still work
    from ci_tools.functions import get_venv_call as f_get_venv_call

    assert f_get_venv_call is get_venv_call


@pytest.fixture
def proxy_ca_environment(tmp_path, monkeypatch):
    roots = ssl.create_default_context(cafile=certifi.where()).get_ca_certs(binary_form=True)
    baseline = tmp_path / "baseline.pem"
    proxy_ca = tmp_path / "HttpProxyRootCa-123.pem"
    baseline.write_text(ssl.DER_cert_to_PEM_cert(roots[0]).rstrip(), encoding="ascii")
    proxy_ca.write_text(ssl.DER_cert_to_PEM_cert(roots[1]), encoding="ascii")
    monkeypatch.setattr(build_module, "_ONE_ES_PROXY_CA_DIRECTORY", str(tmp_path))
    monkeypatch.setattr(sys, "platform", "win32")
    for name, value in {
        "TF_BUILD": "True",
        "BUILD_BUILDID": "123",
        "1ESNI_CONFIG_PATH": str(tmp_path),
        "HTTPS_PROXY": "http://proxy.example.invalid:18080",
        "SSL_CERT_FILE": str(baseline),
        "NODE_EXTRA_CA_CERTS": str(tmp_path / "arbitrary-unreadable-node-ca.pem"),
        "REQUESTS_CA_BUNDLE": "unchanged-requests-ca.pem",
        "PIP_INDEX_URL": "https://example.invalid/cfs",
        "UV_DEFAULT_INDEX": "https://example.invalid/cfs",
        "UV_SYSTEM_CERTS": "1",
        "CIBW_BUILD": "cp310* pp*",
        "CIBW_SKIP": "*-musllinux*",
        "CIBW_BUILD_FRONTEND": "build",
        "CIBW_ARCHS_WINDOWS": "AMD64 ARM64",
        "CIBW_ENVIRONMENT": 'CFLAGS="-DSTORAGE_TEST"',
    }.items():
        monkeypatch.setenv(name, value)
    return baseline, proxy_ca, {roots[0], roots[1]}


@pytest.mark.parametrize("explicit_baseline", [False, True])
def test_cibuildwheel_proxy_bundle(proxy_ca_environment, explicit_baseline, monkeypatch):
    baseline, proxy_ca, expected_roots = proxy_ca_environment
    if not explicit_baseline:
        monkeypatch.delenv("SSL_CERT_FILE")
        baseline = Path(certifi.where())
        expected_roots = set(ssl.create_default_context(cafile=str(baseline)).get_ca_certs(binary_form=True))
    before = os.environ.copy()

    with build_module._cibuildwheel_environment() as environment:
        bundle = Path(environment["SSL_CERT_FILE"])
        assert bundle.read_bytes() == baseline.read_bytes() + b"\n" + proxy_ca.read_bytes() + b"\n"
        context = ssl.create_default_context(cafile=str(bundle))
        assert set(context.get_ca_certs(binary_form=True)) == expected_roots
        assert context.verify_mode == ssl.CERT_REQUIRED
        assert context.check_hostname
        assert environment == {**before, "SSL_CERT_FILE": str(bundle)}
        assert os.environ == before

    assert not bundle.parent.exists()
    assert os.environ == before


@pytest.mark.parametrize(
    "platform,name,value",
    [
        ("linux", None, None),
        ("darwin", None, None),
        ("win32", "TF_BUILD", None),
        ("win32", "TF_BUILD", "False"),
        ("win32", "1ESNI_CONFIG_PATH", None),
        ("win32", "HTTPS_PROXY", None),
        ("win32", "HTTPS_PROXY", ""),
    ],
)
def test_cibuildwheel_proxy_bundle_inactive(proxy_ca_environment, platform, name, value, monkeypatch):
    monkeypatch.setattr(sys, "platform", platform)
    if name:
        if value is None:
            monkeypatch.delenv(name)
        else:
            monkeypatch.setenv(name, value)
    before = os.environ.copy()
    with build_module._cibuildwheel_environment() as environment:
        assert environment is None
    assert os.environ == before


@pytest.mark.parametrize("build_id", [None, "", "../123", "123\\other", "abc", "\u0661\u0662\u0663"])
def test_cibuildwheel_proxy_bundle_invalid_build_id(proxy_ca_environment, build_id, monkeypatch):
    if build_id is None:
        monkeypatch.delenv("BUILD_BUILDID")
    else:
        monkeypatch.setenv("BUILD_BUILDID", build_id)
    before = os.environ.copy()
    with pytest.raises(ValueError, match="ASCII numeric BUILD_BUILDID"):
        with build_module._cibuildwheel_environment():
            pytest.fail("An invalid build ID must not enable proxy trust.")
    assert os.environ == before


@pytest.mark.parametrize("source", ["baseline", "proxy"])
@pytest.mark.parametrize("state", ["missing", "empty", "invalid"])
def test_cibuildwheel_proxy_bundle_invalid_certificates(proxy_ca_environment, source, state, tmp_path, monkeypatch):
    baseline, proxy_ca, _ = proxy_ca_environment
    certificate = baseline if source == "baseline" else proxy_ca
    if state == "missing":
        certificate.unlink()
        expected_error = FileNotFoundError
    else:
        certificate.write_text("" if state == "empty" else "not a certificate", encoding="ascii")
        expected_error = ssl.SSLError
    real_temporary_directory = build_module.TemporaryDirectory
    monkeypatch.setattr(
        build_module, "TemporaryDirectory", lambda **kwargs: real_temporary_directory(dir=tmp_path, **kwargs)
    )
    before = os.environ.copy()
    with pytest.raises(expected_error):
        with build_module._cibuildwheel_environment():
            pytest.fail("Missing or invalid CA certificates must fail the build.")
    assert not list(tmp_path.glob("cibuildwheel-proxy-ca-*"))
    assert os.environ == before


@pytest.mark.parametrize("is_pyproject", [False, True])
@pytest.mark.parametrize("fail", [False, True])
@pytest.mark.parametrize("enable_sdist", [False, True])
def test_create_compiled_package_proxy_environment(
    proxy_ca_environment, is_pyproject, fail, enable_sdist, tmp_path, monkeypatch
):
    package = SimpleNamespace(is_pyproject=is_pyproject, ext_modules=True, folder=str(tmp_path))
    monkeypatch.setattr(build_module.ParsedSetup, "from_path", lambda _: package)
    dist = str(tmp_path / "dist")
    monkeypatch.setattr(build_module, "get_artifact_directory", lambda _: dist)
    before = os.environ.copy()
    calls = []
    bundle = None

    def run_build(command, **kwargs):
        nonlocal bundle
        calls.append(command)
        assert kwargs["cwd"] == package.folder
        assert kwargs["check"] is True
        if command[2] == "cibuildwheel":
            bundle = Path(kwargs["env"]["SSL_CERT_FILE"])
            assert bundle.is_file()
            assert kwargs["env"] == {**before, "SSL_CERT_FILE": str(bundle)}
            if fail:
                raise CalledProcessError(1, command)
        else:
            assert kwargs.get("env") is None
            assert not bundle.exists()
        assert os.environ == before

    monkeypatch.setattr(build_module, "run_logged", run_build)
    if fail:
        with pytest.raises(CalledProcessError):
            build_module.create_package(package.folder, dist, enable_sdist=enable_sdist)
    else:
        build_module.create_package(package.folder, dist, enable_sdist=enable_sdist)

    assert calls[0] == [sys.executable, "-m", "cibuildwheel", "--output-dir", dist]
    assert len(calls) == (1 if fail or not enable_sdist else 2)
    if not fail and enable_sdist:
        assert calls[1] == (
            [sys.executable, "-m", "build", "-s", "-o", dist]
            if is_pyproject
            else [sys.executable, "setup.py", "sdist", "-d", dist]
        )
    assert not bundle.parent.exists()
    assert os.environ == before


@pytest.mark.parametrize("is_pyproject", [False, True])
@pytest.mark.parametrize("ext_modules,enable_wheel", [(False, True), (True, False)])
def test_non_cibuildwheel_builds_preserve_trust(
    proxy_ca_environment, is_pyproject, ext_modules, enable_wheel, tmp_path, monkeypatch
):
    package = SimpleNamespace(is_pyproject=is_pyproject, ext_modules=ext_modules, folder=str(tmp_path), requires=[])
    monkeypatch.setattr(build_module.ParsedSetup, "from_path", lambda _: package)
    monkeypatch.setattr(build_module, "get_artifact_directory", lambda _: str(tmp_path / "dist"))
    monkeypatch.setattr(build_module, "get_pip_list_output", lambda _: {})
    before = os.environ.copy()
    calls = []

    def run_build(command, **kwargs):
        calls.append(command)
        assert "cibuildwheel" not in command
        assert kwargs.get("env") is None
        assert os.environ == before

    monkeypatch.setattr(build_module, "run_logged", run_build)
    build_module.create_package(package.folder, str(tmp_path / "dist"), enable_wheel=enable_wheel)
    assert len(calls) == (2 if is_pyproject or enable_wheel else 1)
    assert os.environ == before
